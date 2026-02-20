"""
Тесты для Google Sheets клиента (sheets_client.py).
Проверяют корректность работы с Google Sheets API.
"""

import pytest
from unittest.mock import Mock, patch
import gspread


def test_google_sheets_client_initialization():
    """Тест инициализации синхронного клиента"""
    with patch('gspread.service_account'):
        from sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient(
            credentials_file="fake_creds.json",
            spreadsheet_id="fake_id",
            sheet_name="Sheet1"
        )
        
        assert client.credentials_file == "fake_creds.json"
        assert client.spreadsheet_id == "fake_id"
        assert client.sheet_name == "Sheet1"
        assert client._client is None  # Ленивая инициализация


def test_google_sheets_client_get_data(sample_sheet_values):
    """Тест получения данных из Google Sheets"""
    with patch('gspread.service_account') as mock_sa:
        from sheets_client import GoogleSheetsClient
        
        # Мокаем структуру Google Sheets API
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_sa.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_values.return_value = sample_sheet_values
        
        # Создаём клиент и получаем данные
        client = GoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        data = client.get_data()
        
        # Проверки
        assert len(data) == 3  # 3 строки данных (без заголовков)
        assert data[0] == {
            "Name": "Alice",
            "Age": "30",
            "City": "Moscow",
            "Email": "alice@test.com"
        }
        assert data[1]["Name"] == "Bob"
        assert data[2]["Name"] == "Charlie"
        
        # Проверяем вызовы
        from pathlib import Path
        mock_sa.assert_called_once_with(filename=Path("fake_creds.json"))
        mock_client.open_by_key.assert_called_once_with("fake_id")
        mock_spreadsheet.worksheet.assert_called_once_with("Sheet1")


def test_google_sheets_client_empty_sheet():
    """Тест обработки пустой таблицы"""
    with patch('gspread.service_account') as mock_sa:
        from sheets_client import GoogleSheetsClient
        
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_sa.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_values.return_value = []  # Пустая таблица
        
        client = GoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        data = client.get_data()
        
        assert data == []


def test_google_sheets_client_only_headers():
    """Тест таблицы только с заголовками (без данных)"""
    with patch('gspread.service_account') as mock_sa:
        from sheets_client import GoogleSheetsClient
        
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_sa.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_values.return_value = [["Name", "Age", "City"]]
        
        client = GoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        data = client.get_data()
        
        assert data == []


def test_google_sheets_client_uneven_rows():
    """Тест обработки строк разной длины"""
    with patch('gspread.service_account') as mock_sa:
        from sheets_client import GoogleSheetsClient
        
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_sa.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Строки разной длины
        mock_worksheet.get_all_values.return_value = [
            ["Name", "Age", "City"],
            ["Alice", "30"],  # Короткая строка
            ["Bob", "25", "SPb", "Extra"],  # Длинная строка
        ]
        
        client = GoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        data = client.get_data()
        
        # Короткая строка дополняется пустыми значениями
        assert data[0] == {"Name": "Alice", "Age": "30", "City": ""}
        # Длинная строка обрезается по количеству заголовков
        assert data[1] == {"Name": "Bob", "Age": "25", "City": "SPb"}


def test_google_sheets_client_worksheet_not_found():
    """Тест ошибки когда лист не найден"""
    with patch('gspread.service_account') as mock_sa:
        from sheets_client import GoogleSheetsClient
        
        mock_client = Mock()
        mock_spreadsheet = Mock()
        
        mock_sa.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound("Sheet not found")
        
        client = GoogleSheetsClient("fake_creds.json", "fake_id", "NonExistentSheet")
        
        with pytest.raises(gspread.exceptions.WorksheetNotFound):
            client.get_data()


def test_google_sheets_client_spreadsheet_not_found():
    """Тест ошибки когда таблица не найдена или не расшарена"""
    with patch('gspread.service_account') as mock_sa:
        from sheets_client import GoogleSheetsClient
        
        mock_client = Mock()
        mock_sa.return_value = mock_client
        mock_client.open_by_key.side_effect = gspread.exceptions.SpreadsheetNotFound("Spreadsheet not found")
        
        client = GoogleSheetsClient("fake_creds.json", "invalid_id", "Sheet1")
        
        with pytest.raises(gspread.exceptions.SpreadsheetNotFound):
            client.get_data()


@pytest.mark.asyncio
async def test_async_google_sheets_client_initialization():
    """Тест инициализации асинхронного клиента"""
    with patch('gspread.service_account'):
        from sheets_client import AsyncGoogleSheetsClient
        
        client = AsyncGoogleSheetsClient(
            credentials_file="fake_creds.json",
            spreadsheet_id="fake_id",
            sheet_name="Sheet1"
        )
        
        assert client.credentials_file == "fake_creds.json"
        assert client.spreadsheet_id == "fake_id"
        assert client.sheet_name == "Sheet1"


@pytest.mark.asyncio
async def test_async_google_sheets_client_get_data(sample_sheet_values):
    """Тест асинхронного получения данных"""
    with patch('gspread.service_account') as mock_sa:
        from sheets_client import AsyncGoogleSheetsClient
        
        # Мокаем структуру
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_sa.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_values.return_value = sample_sheet_values
        
        # Создаём асинхронный клиент
        client = AsyncGoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        data = await client.get_data()
        
        # Проверки
        assert len(data) == 3
        assert data[0]["Name"] == "Alice"
        assert data[1]["Name"] == "Bob"
        assert data[2]["Name"] == "Charlie"


@pytest.mark.asyncio
async def test_async_google_sheets_client_empty_result():
    """Тест асинхронного клиента с пустой таблицей"""
    with patch('gspread.service_account') as mock_sa:
        from sheets_client import AsyncGoogleSheetsClient
        
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_sa.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_values.return_value = []
        
        client = AsyncGoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        data = await client.get_data()
        
        assert data == []


def test_client_lazy_initialization():
    """Тест ленивой инициализации клиента"""
    with patch('gspread.service_account') as mock_sa_init:
        from sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        
        # service_account не должен вызываться при создании объекта
        mock_sa_init.assert_not_called()
        
        # Мокаем остальное для get_data
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_sa_init.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_values.return_value = [["Name"], ["Alice"]]
        
        # Теперь вызываем get_data
        client.get_data()
        
        # service_account должен быть вызван один раз
        mock_sa_init.assert_called_once()
        
        # При повторном вызове не должен создавать новый клиент
        client.get_data()
        mock_sa_init.assert_called_once()  # Всё ещё один раз
