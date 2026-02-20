"""
Модуль конфигурации приложения.
Загружает и валидирует переменные окружения из .env файла.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Загружаем переменные окружения из .env файла
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Класс для хранения и валидации конфигурации приложения"""
    
    # Google Sheets настройки
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    SHEET_NAME: str = os.getenv("SHEET_NAME", "Sheet1")
    
    # Путь к credentials файлу
    CREDENTIALS_FILE: str = os.getenv("CREDENTIALS_FILE", "creds.json")
    
    # Настройки сервера
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Опциональные настройки
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def validate(cls) -> None:
        """
        Валидация обязательных переменных окружения.
        
        Raises:
            ValueError: если обязательные переменные не заданы
            FileNotFoundError: если credentials файл не найден
        """
        errors = []
        
        # Проверка обязательных переменных
        if not cls.SPREADSHEET_ID:
            errors.append("SPREADSHEET_ID is not set in .env file")
        
        if not cls.SHEET_NAME:
            errors.append("SHEET_NAME is not set in .env file")
        
        # Проверка существования credentials файла
        credentials_path = Path(cls.CREDENTIALS_FILE)
        if not credentials_path.exists():
            errors.append(
                f"Credentials file not found: {cls.CREDENTIALS_FILE}\n"
                f"Please create it from creds.json.example"
            )
        
        # Если есть ошибки, выбросить исключение
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            logger.error(error_message)
            raise ValueError(error_message)
        
        logger.info("Configuration validated successfully")
    
    @classmethod
    def get_info(cls) -> dict:
        """
        Получить информацию о конфигурации (безопасная версия без секретов).
        
        Returns:
            dict: Словарь с настройками (ID таблицы замаскирован)
        """
        spreadsheet_id_masked = (
            f"{cls.SPREADSHEET_ID[:4]}...{cls.SPREADSHEET_ID[-4:]}"
            if len(cls.SPREADSHEET_ID) > 8
            else "***"
        )
        
        return {
            "spreadsheet_id": spreadsheet_id_masked,
            "sheet_name": cls.SHEET_NAME,
            "port": cls.PORT,
            "host": cls.HOST,
            "log_level": cls.LOG_LEVEL,
            "environment": cls.ENVIRONMENT,
            "credentials_file": cls.CREDENTIALS_FILE,
        }


# Валидация конфигурации при импорте модуля
try:
    Config.validate()
except ValueError as e:
    # В production можно перехватывать и логировать, 
    # но для разработки лучше сразу упасть
    logger.warning(f"Config validation skipped or failed: {e}")
    # raise  # Раскомментировать в production
