"""
Модуль для работы с Google Sheets API.
Содержит клиенты для синхронного и асинхронного доступа к таблицам.
"""

import gspread
from typing import List, Dict
import logging
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """
    Синхронный клиент для работы с Google Sheets.
    Использует gspread и service account для аутентификации.
    """
    
    def __init__(self, credentials_file: str, spreadsheet_id: str, sheet_name: str):
        """
        Инициализация клиента Google Sheets.
        
        Args:
            credentials_file: Путь к JSON файлу с credentials сервисного аккаунта
            spreadsheet_id: ID Google Spreadsheet (из URL)
            sheet_name: Название листа в таблице
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self._client = None
        
        logger.info(f"Initializing GoogleSheetsClient for sheet: {sheet_name}")
    
    def _get_client(self) -> gspread.Client:
        """
        Ленивая инициализация gspread клиента.
        Клиент создаётся только при первом обращении.
        
        Returns:
            gspread.Client: Аутентифицированный клиент
        
        Raises:
            Exception: Если не удалось аутентифицироваться
        """
        if self._client is None:
            try:
                from pathlib import Path
                self._client = gspread.service_account(filename=Path(self.credentials_file))
                logger.info("Successfully authenticated with Google Sheets API")
            except Exception as e:
                logger.error(f"Failed to authenticate with Google Sheets: {e}")
                raise
        return self._client
    
    def get_data(self) -> List[Dict[str, str]]:
        """
        Получить все данные из Google Sheets таблицы.
        Первая строка считается заголовками (ключи JSON).
        
        Returns:
            List[Dict[str, str]]: Список словарей, где ключи - заголовки из первой строки
        
        Raises:
            Exception: При ошибках доступа к таблице или листу
        """
        try:
            client = self._get_client()
            
            # Открываем таблицу по ID
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            logger.debug(f"Opened spreadsheet: {spreadsheet.title}")
            
            # Получаем лист по названию
            worksheet = spreadsheet.worksheet(self.sheet_name)
            logger.debug(f"Opened worksheet: {self.sheet_name}")
            
            # Получаем все значения
            all_values = worksheet.get_all_values()
            
            if not all_values:
                logger.warning("Spreadsheet is empty")
                return []
            
            if len(all_values) < 1:
                logger.warning("Spreadsheet has no headers")
                return []
            
            # Первая строка - заголовки
            headers = all_values[0]
            data_rows = all_values[1:]
            
            if not headers:
                logger.warning("Headers row is empty")
                return []
            
            # Преобразуем в список словарей
            result = []
            for row_index, row in enumerate(data_rows, start=2):  # +2 т.к. нумерация с 1 и пропускаем заголовки
                # Дополняем короткие строки пустыми значениями
                padded_row = row + [''] * (len(headers) - len(row))
                
                # Создаём словарь, связывая заголовки со значениями
                row_dict = dict(zip(headers, padded_row))
                result.append(row_dict)
            
            logger.info(f"Successfully fetched {len(result)} rows from sheet '{self.sheet_name}'")
            return result
            
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet '{self.sheet_name}' not found in spreadsheet")
            raise
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet with ID '{self.spreadsheet_id}' not found or not shared")
            raise
        except gspread.exceptions.APIError as e:
            logger.error(f"Google Sheets API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching data: {e}")
            raise


class AsyncGoogleSheetsClient:
    """
    Асинхронный клиент для работы с Google Sheets.
    
    Примечание: gspread сам по себе синхронный, поэтому мы используем
    asyncio.to_thread() для выполнения блокирующих операций в отдельном потоке.
    Это позволяет не блокировать event loop FastAPI.
    """
    
    def __init__(self, credentials_file: str, spreadsheet_id: str, sheet_name: str):
        """
        Инициализация асинхронного клиента Google Sheets.
        
        Args:
            credentials_file: Путь к JSON файлу с credentials
            spreadsheet_id: ID Google Spreadsheet
            sheet_name: Название листа
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self._client = None
        
        logger.info(f"Initializing AsyncGoogleSheetsClient for sheet: {sheet_name}")
    
    def _get_client(self) -> gspread.Client:
        """Ленивая инициализация gspread клиента"""
        if self._client is None:
            try:
                from pathlib import Path
                self._client = gspread.service_account(filename=Path(self.credentials_file))
                logger.info("Successfully authenticated with Google Sheets API (async)")
            except Exception as e:
                logger.error(f"Failed to authenticate: {e}")
                raise
        return self._client
    
    async def get_data(self) -> List[Dict[str, str]]:
        """
        Асинхронно получить данные из Google Sheets.
        
        Returns:
            List[Dict[str, str]]: Список словарей, где ключи - заголовки из первой строки
        
        Raises:
            Exception: При ошибках доступа к таблице
        """
        try:
            # Выполняем синхронную операцию в отдельном потоке
            # чтобы не блокировать event loop
            data = await asyncio.to_thread(self._fetch_data_sync)
            logger.info(f"Successfully fetched {len(data)} rows (async)")
            return data
        except Exception as e:
            logger.error(f"Error fetching data (async): {e}")
            raise
    
    def _fetch_data_sync(self) -> List[Dict[str, str]]:
        """
        Синхронная функция для получения данных.
        Запускается в отдельном потоке через asyncio.to_thread().
        
        Returns:
            List[Dict[str, str]]: Список словарей с данными
        """
        client = self._get_client()
        spreadsheet = client.open_by_key(self.spreadsheet_id)
        worksheet = spreadsheet.worksheet(self.sheet_name)
        
        # Получаем все значения
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) < 1:
            return []
        
        # Первая строка - заголовки
        headers = all_values[0]
        data_rows = all_values[1:]
        
        if not headers:
            return []
        
        # Преобразуем в список словарей
        result = []
        for row in data_rows:
            # Дополняем короткие строки пустыми значениями
            padded_row = row + [''] * (len(headers) - len(row))
            row_dict = dict(zip(headers, padded_row))
            result.append(row_dict)
        
        return result
    
    @lru_cache(maxsize=128)
    async def get_data_cached(self, cache_key: str) -> List[Dict[str, str]]:
        """
        Кэшированная версия get_data() для уменьшения запросов к API.
        
        Args:
            cache_key: Уникальный ключ для кэша (например, timestamp с округлением)
        
        Returns:
            List[Dict[str, str]]: Кэшированные или свежие данные
        """
        return await self.get_data()
