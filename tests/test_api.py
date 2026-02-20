"""
Тесты для API эндпоинтов (app.py).
Проверяют корректность работы FastAPI приложения.
"""

from unittest.mock import patch, AsyncMock


def test_root_endpoint(client):
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


def test_health_endpoint(client):
    """Тест health check эндпоинта"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "gsheets-json-api"
    assert data["version"] == "1.0.0"


def test_get_data_success(client, mock_sheets_data):
    """Тест успешного получения данных"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        response = client.get("/api/data")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "data" in data
        
        assert data["total"] == 3
        assert len(data["data"]) == 3
        assert data["data"][0]["Name"] == "Alice"


def test_get_data_with_city_filter(client, mock_sheets_data):
    """Тест фильтрации по городу"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        response = client.get("/api/data?city=Moscow")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 2  # Alice и Charlie из Moscow
        assert len(data["data"]) == 2
        assert all(item["City"] == "Moscow" for item in data["data"])
        assert data["filters_applied"]["city"] == "Moscow"


def test_get_data_with_age_filter(client, mock_sheets_data):
    """Тест фильтрации по возрасту"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        response = client.get("/api/data?age=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["Name"] == "Alice"
        assert data["data"][0]["Age"] == "30"


def test_get_data_with_name_search(client, mock_sheets_data):
    """Тест поиска по имени (частичное совпадение)"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        response = client.get("/api/data?name=li")  # Найдет Alice и Charlie
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 2
        assert any("li" in item["Name"].lower() for item in data["data"])


def test_get_data_with_pagination(client, mock_sheets_data):
    """Тест пагинации"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        # Первая страница (2 записи)
        response = client.get("/api/data?limit=2&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert len(data["data"]) == 2
        
        # Вторая страница (1 запись)
        response = client.get("/api/data?limit=2&offset=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["data"]) == 1


def test_get_data_with_combined_filters(client, mock_sheets_data):
    """Тест комбинации фильтров"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        response = client.get("/api/data?city=Moscow&age=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["Name"] == "Alice"
        assert data["filters_applied"]["city"] == "Moscow"
        assert data["filters_applied"]["age"] == "30"


def test_get_data_empty_result(client):
    """Тест пустого результата"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = []
        
        response = client.get("/api/data")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert len(data["data"]) == 0


def test_get_data_no_matches_filter(client, mock_sheets_data):
    """Тест фильтра без совпадений"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        response = client.get("/api/data?city=NonExistentCity")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert len(data["data"]) == 0


def test_get_data_sheets_error(client):
    """Тест обработки ошибки при недоступности Google Sheets"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.side_effect = Exception("Connection error")
        
        response = client.get("/api/data")
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data


def test_pagination_limits(client, mock_sheets_data):
    """Тест граничных значений пагинации"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        # Минимальный limit
        response = client.get("/api/data?limit=1")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1
        
        # Максимальный limit
        response = client.get("/api/data?limit=1000")
        assert response.status_code == 200
        
        # Невалидный limit (меньше 1) - должен вернуть ошибку валидации
        response = client.get("/api/data?limit=0")
        assert response.status_code == 422
        
        # Невалидный limit (больше 1000) - должен вернуть ошибку валидации
        response = client.get("/api/data?limit=1001")
        assert response.status_code == 422


def test_case_insensitive_filters(client, mock_sheets_data):
    """Тест регистронезависимых фильтров"""
    with patch('app.sheets_client.get_data', new_callable=AsyncMock) as mock_get_data:
        mock_get_data.return_value = mock_sheets_data
        
        # Фильтр по городу в разных регистрах
        response1 = client.get("/api/data?city=moscow")
        response2 = client.get("/api/data?city=MOSCOW")
        response3 = client.get("/api/data?city=Moscow")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # Все должны вернуть одинаковый результат
        assert response1.json()["total"] == response2.json()["total"] == response3.json()["total"] == 2
