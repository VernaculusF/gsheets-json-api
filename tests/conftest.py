"""
Фикстуры pytest для тестирования.
Содержит общие тестовые объекты и моки.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_sheets_data():
    """
    Моковые данные из Google Sheets для тестирования.
    
    Имитирует структуру данных возвращаемую sheets_client.get_data()
    """
    return [
        {"Name": "Alice", "Age": "30", "City": "Moscow", "Email": "alice@test.com"},
        {"Name": "Bob", "Age": "25", "City": "SPb", "Email": "bob@test.com"},
        {"Name": "Charlie", "Age": "35", "City": "Moscow", "Email": "charlie@test.com"},
    ]


@pytest.fixture
def client():
    """
    Тестовый клиент FastAPI.
    
    Используется для отправки HTTP запросов к приложению в тестах.
    """
    # Мокаем конфигурацию чтобы не требовать реальные credentials
    with patch('config.Config.validate'):
        with patch('app.sheets_client'):
            from app import app
            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
def mock_gspread_client():
    """
    Мок gspread клиента для тестирования sheets_client.
    """
    mock_client = Mock()
    mock_spreadsheet = Mock()
    mock_worksheet = Mock()
    
    # Настройка цепочки моков
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.return_value = mock_worksheet
    
    return {
        'client': mock_client,
        'spreadsheet': mock_spreadsheet,
        'worksheet': mock_worksheet
    }


@pytest.fixture
def sample_sheet_values():
    """
    Пример данных как они приходят из Google Sheets API.
    """
    return [
        ["Name", "Age", "City", "Email"],  # Headers
        ["Alice", "30", "Moscow", "alice@test.com"],
        ["Bob", "25", "SPb", "bob@test.com"],
        ["Charlie", "35", "Moscow", "charlie@test.com"],
    ]
