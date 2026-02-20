# План разработки Google Sheets JSON API

## Выбор технологий

### FastAPI vs Flask
**Выбран: FastAPI**

**Обоснование:**
- ✅ **Автоматическая документация** (Swagger UI / ReDoc) - не нужно писать вручную
- ✅ **Встроенная валидация** через Pydantic - безопасность из коробки
- ✅ **Type hints** - требование проекта, FastAPI основан на них
- ✅ **Современный** - async/await поддержка (хотя для текущей задачи не критично)
- ✅ **Производительность** - быстрее Flask благодаря Starlette
- ✅ **Легкий переход к async** если потребуется масштабирование

Flask хорош для простых проектов, но FastAPI даёт больше из коробки без усложнения кода.

## Структура проекта

```
gsheets-json-api/
├── app.py                   # Основной файл с FastAPI приложением
├── sheets_client.py         # Класс GoogleSheetsClient для работы с Google Sheets
├── config.py                # Загрузка и валидация настроек из .env
├── requirements.txt         # Зависимости проекта
├── requirements-dev.txt     # Зависимости для разработки (опционально)
├── .env.example             # Пример переменных окружения
├── .env                     # Реальные переменные (создаётся локально, не в git)
├── .gitignore               # Игнорируемые файлы
├── creds.json.example       # Заглушка для credentials
├── creds.json               # Реальные credentials (создаётся локально, не в git)
├── Dockerfile               # Для контейнеризации
├── .dockerignore            # Исключения при сборке Docker образа
├── docker-compose.yml       # Локальная разработка со всеми сервисами
├── nginx.conf               # Конфигурация Nginx (опционально)
├── README.md                # Подробная документация
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD пайплайн
├── tests/                   # Тесты (опционально)
│   ├── __init__.py
│   ├── conftest.py          # Фикстуры pytest
│   ├── test_api.py          # Тесты эндпоинтов
│   └── test_sheets_client.py # Тесты клиента
└── venv/                    # Виртуальное окружение (не в git)
```

## План разработки

### Этап 1: Инфраструктура
1. ✅ Создать структуру проекта
2. ✅ Создать `requirements.txt` с зависимостями
3. ✅ Создать `.env.example` с примерами переменных
4. ✅ Создать `.gitignore` для Python проекта
5. ✅ Создать `creds.json.example` как заглушку

### Этап 2: Конфигурация
1. ✅ Разработать `config.py`:
   - Загрузка переменных из `.env` через python-dotenv
   - Валидация обязательных переменных (SPREADSHEET_ID, SHEET_NAME)
   - Проверка существования `creds.json`
   - Type hints для всех переменных

### Этап 3: Клиент Google Sheets
1. ✅ Разработать `sheets_client.py`:
   - Класс `GoogleSheetsClient`
   - Метод `__init__()` - инициализация gspread клиента
   - Метод `get_data()` - получение данных из таблицы
   - Обработка ошибок (аутентификация, доступ, формат)
   - Логирование всех операций
   - Type hints для методов

### Этап 4: API
1. ✅ Разработать `app.py`:
   - Инициализация FastAPI приложения
   - Настройка CORS (т.к. может запрашиваться из браузера)
   - Настройка логирования
   - Эндпоинт `GET /api/data`
   - Обработка исключений с правильными HTTP статусами
   - Health check эндпоинт `/health` (для Cloud Run)

### Этап 5: Документация
1. ✅ Создать подробный `README.md`:
   - Описание проекта
   - Как получить credentials в Google Cloud Console
   - Как расшарить таблицу с сервисным аккаунтом
   - Настройка `.env`
   - Создание и активация venv
   - Установка зависимостей
   - Запуск локально
   - Примеры запросов (curl, httpie, браузер)
   - Примеры ответов
   - Troubleshooting (типичные ошибки)
   - Деплой на Google Cloud Run

### Этап 6: Контейнеризация
1. ✅ Создать `Dockerfile`:
   - Multi-stage build для оптимизации размера
   - Python 3.10+ slim образ
   - Копирование только необходимых файлов
   - Запуск через uvicorn
2. ✅ Создать `.dockerignore`

## Зависимости (requirements.txt)

**Базовые зависимости:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
gspread==5.12.3
google-auth==2.27.0
python-dotenv==1.0.0
```

**С продвинутыми фичами:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
gspread==5.12.3
google-auth==2.27.0
python-dotenv==1.0.0
slowapi==0.1.9  # Rate limiting
redis==5.0.1    # Кэширование (опционально)
```

**Для разработки (requirements-dev.txt):**
```
pytest==7.4.3
httpx==0.26.0
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-asyncio==0.23.3  # Для async тестов
black==24.1.0           # Форматирование кода
flake8==7.0.0           # Линтинг
mypy==1.8.0             # Проверка типов
isort==5.13.2           # Сортировка импортов
```

## Переменные окружения (.env)

```
SPREADSHEET_ID=your_spreadsheet_id_here
SHEET_NAME=Sheet1
PORT=8000
```

## Формат данных

### Входные данные (Google Sheets):
```
| Name    | Age | City     |
|---------|-----|----------|
| Alice   | 30  | Moscow   |
| Bob     | 25  | SPb      |
```

### Выходные данные (JSON):
```json
[
  {
    "Name": "Alice",
    "Age": "30",
    "City": "Moscow"
  },
  {
    "Name": "Bob",
    "Age": "25",
    "City": "SPb"
  }
]
```

## Обработка ошибок

| Ошибка | HTTP статус | Описание |
|--------|-------------|----------|
| Credentials не найдены | 500 | `creds.json` отсутствует |
| Нет доступа к таблице | 500 | Таблица не расшарена или неверный ID |
| Лист не найден | 500 | Неверное имя листа |
| Пустая таблица | 200 | Вернуть пустой массив `[]` |
| Таблица без заголовков | 200 | Вернуть пустой массив `[]` |

## Логирование

- **INFO**: Запуск приложения, успешные запросы
- **ERROR**: Ошибки доступа к Google Sheets, ошибки парсинга
- **DEBUG**: Детали запросов (при разработке)

Формат: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Деплой на Google Cloud Run

### Краткая инструкция:
1. Установить gcloud CLI
2. Аутентифицироваться: `gcloud auth login`
3. Создать проект или выбрать существующий
4. Включить Cloud Run API
5. Собрать и загрузить образ в GCR:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/gsheets-api
   ```
6. Деплой:
   ```bash
   gcloud run deploy gsheets-api \
     --image gcr.io/PROJECT_ID/gsheets-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars SPREADSHEET_ID=xxx,SHEET_NAME=xxx \
     --set-secrets /app/creds.json=gsheets-creds:latest
   ```
7. Создать Secret в Secret Manager для `creds.json`

Подробнее:
- https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service
- https://cloud.google.com/run/docs/configuring/secrets

## Продвинутые фичи (опционально)

### 1. Rate Limiting - защита от DDoS

**Проблема:** Бесплатный тир Cloud Run может быть заддосен, что приведёт к расходам или блокировке сервиса.

**Решение:** Использовать `slowapi` (порт Flask-Limiter для FastAPI):

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/data")
@limiter.limit("10/minute")  # 10 запросов в минуту с одного IP
async def get_data():
    ...
```

**Зависимости:**
```
slowapi==0.1.9
```

**Альтернативы:**
- Nginx rate limiting (если используется обратный прокси)
- Cloud Armor на уровне GCP (платно)
- API Gateway с квотами

### 2. Фильтрация данных - Query Parameters

**Пример:** `GET /api/data?city=Moscow&age=30`

**Реализация:**

```python
from typing import Optional

@app.get("/api/data")
async def get_data(
    city: Optional[str] = None,
    age: Optional[int] = None,
    name: Optional[str] = None
):
    """
    Получить данные с фильтрацией
    
    - **city**: фильтр по городу (регистронезависимый)
    - **age**: фильтр по возрасту (точное совпадение)
    - **name**: фильтр по имени (частичное совпадение)
    """
    data = sheets_client.get_data()
    
    # Применяем фильтры
    if city:
        data = [row for row in data if row.get('City', '').lower() == city.lower()]
    if age is not None:
        data = [row for row in data if row.get('Age') == str(age)]
    if name:
        data = [row for row in data if name.lower() in row.get('Name', '').lower()]
    
    return data
```

**Пример запроса:**
```bash
curl "http://localhost:8000/api/data?city=Moscow"
```

**Swagger UI** автоматически отобразит все параметры!

### 3. Pagination - для больших таблиц

**Проблема:** Если в таблице 10,000+ строк, ответ будет огромным.

**Решение:** Пагинация через `limit` и `offset`:

```python
from fastapi import Query

@app.get("/api/data")
async def get_data(
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение от начала"),
):
    """
    Пагинация:
    - limit: максимум 1000 записей за раз (по умолчанию 100)
    - offset: пропустить первые N записей
    """
    data = sheets_client.get_data()
    total = len(data)
    
    # Применяем пагинацию
    paginated_data = data[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": paginated_data
    }
```

**Примеры:**
```bash
# Первые 10 записей
curl "http://localhost:8000/api/data?limit=10&offset=0"

# Следующие 10 записей
curl "http://localhost:8000/api/data?limit=10&offset=10"
```

**Альтернативы:**
- Cursor-based pagination (для очень больших данных)
- Page-based: `?page=1&per_page=100`

### 4. Тесты - pytest примеры

**Структура:**
```
gsheets-json-api/
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_sheets_client.py
│   └── conftest.py
```

**tests/conftest.py** - фикстуры:
```python
import pytest
from fastapi.testclient import TestClient
from app import app

@pytest.fixture
def client():
    """Тестовый клиент FastAPI"""
    return TestClient(app)

@pytest.fixture
def mock_sheets_data():
    """Моковые данные из Google Sheets"""
    return [
        {"Name": "Alice", "Age": "30", "City": "Moscow"},
        {"Name": "Bob", "Age": "25", "City": "SPb"},
    ]
```

**tests/test_api.py** - тесты эндпоинтов:
```python
from unittest.mock import patch

def test_get_data_success(client, mock_sheets_data):
    """Тест успешного получения данных"""
    with patch('app.sheets_client.get_data', return_value=mock_sheets_data):
        response = client.get("/api/data")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["Name"] == "Alice"

def test_get_data_with_filter(client, mock_sheets_data):
    """Тест фильтрации по городу"""
    with patch('app.sheets_client.get_data', return_value=mock_sheets_data):
        response = client.get("/api/data?city=Moscow")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["City"] == "Moscow"

def test_health_endpoint(client):
    """Тест health check эндпоинта"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_data_sheets_error(client):
    """Тест обработки ошибки при недоступности Google Sheets"""
    with patch('app.sheets_client.get_data', side_effect=Exception("Connection error")):
        response = client.get("/api/data")
        assert response.status_code == 500
        assert "error" in response.json()
```

**tests/test_sheets_client.py** - тесты клиента:
```python
import pytest
from unittest.mock import Mock, patch
from sheets_client import GoogleSheetsClient

def test_sheets_client_initialization():
    """Тест инициализации клиента"""
    with patch('gspread.service_account') as mock_sa:
        client = GoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        mock_sa.assert_called_once_with(filename="fake_creds.json")

def test_get_data_transforms_to_dict():
    """Тест преобразования данных в словари"""
    with patch('gspread.service_account') as mock_sa:
        # Мокаем структуру Google Sheets
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ["Name", "Age"],
            ["Alice", "30"],
            ["Bob", "25"]
        ]
        mock_sa.return_value.open_by_key.return_value.worksheet.return_value = mock_sheet
        
        client = GoogleSheetsClient("fake_creds.json", "fake_id", "Sheet1")
        data = client.get_data()
        
        assert len(data) == 2
        assert data[0] == {"Name": "Alice", "Age": "30"}
```

**Запуск тестов:**
```bash
# Установить зависимости для тестирования
pip install pytest httpx pytest-cov

# Запустить все тесты
pytest

# С покрытием кода
pytest --cov=. --cov-report=html

# Конкретный файл
pytest tests/test_api.py -v
```

**requirements-dev.txt:**
```
pytest==7.4.3
httpx==0.26.0
pytest-cov==4.1.0
pytest-mock==3.12.0
```

### 5. Docker Compose - локальная разработка

**Проблема:** Сложно тестировать весь стек локально с зависимостями.

**Решение:** `docker-compose.yml` для запуска всех сервисов одной командой:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: gsheets-api
    ports:
      - "8000:8000"
    environment:
      - SPREADSHEET_ID=${SPREADSHEET_ID}
      - SHEET_NAME=${SHEET_NAME}
      - LOG_LEVEL=DEBUG
    volumes:
      - ./creds.json:/app/creds.json:ro
      - ./app.py:/app/app.py:ro  # Hot reload для разработки
      - ./sheets_client.py:/app/sheets_client.py:ro
      - ./config.py:/app/config.py:ro
    command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - gsheets-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Опционально: Redis для кэширования (если добавить кэш)
  redis:
    image: redis:7-alpine
    container_name: gsheets-redis
    ports:
      - "6379:6379"
    networks:
      - gsheets-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Опционально: Nginx как reverse proxy
  nginx:
    image: nginx:alpine
    container_name: gsheets-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
    networks:
      - gsheets-network

networks:
  gsheets-network:
    driver: bridge

volumes:
  redis-data:
```

**Команды:**
```bash
# Запустить все сервисы
docker-compose up -d

# Посмотреть логи
docker-compose logs -f api

# Остановить
docker-compose down

# Пересобрать после изменений
docker-compose up -d --build
```

**Файл `.env` для docker-compose:**
```bash
SPREADSHEET_ID=your_spreadsheet_id
SHEET_NAME=Sheet1
COMPOSE_PROJECT_NAME=gsheets-api
```

**Опционально: `nginx.conf` для reverse proxy:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api:8000;
    }

    # Rate limiting zone
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name localhost;

        # Логирование
        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        # Gzip сжатие
        gzip on;
        gzip_types application/json text/plain;

        # API эндпоинт с rate limiting
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeout настройки
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Swagger UI (без rate limiting)
        location /docs {
            proxy_pass http://api_backend/docs;
            proxy_set_header Host $host;
        }

        location /openapi.json {
            proxy_pass http://api_backend/openapi.json;
            proxy_set_header Host $host;
        }

        # Health check (без rate limiting)
        location /health {
            proxy_pass http://api_backend/health;
            proxy_set_header Host $host;
        }

        # Статика (если добавите frontend)
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
    }
}
```

### 6. GitHub Actions - CI/CD автоматизация

**Файл:** `.github/workflows/ci.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Lint with flake8
      run: |
        # Остановить сборку при синтаксических ошибках
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # Все предупреждения (можно игнорировать)
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Type check with mypy
      run: |
        mypy app.py sheets_client.py config.py --ignore-missing-imports
      continue-on-error: true  # Не останавливать при ошибках типов

    - name: Format check with black
      run: |
        black --check .

    - name: Run tests with pytest
      run: |
        pytest tests/ -v --cov=. --cov-report=xml --cov-report=html

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/gsheets-api:latest
          ${{ secrets.DOCKER_USERNAME }}/gsheets-api:${{ github.sha }}
        cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/gsheets-api:buildcache
        cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/gsheets-api:buildcache,mode=max

  deploy:
    name: Deploy to Cloud Run
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy gsheets-api \
          --image ${{ secrets.DOCKER_USERNAME }}/gsheets-api:${{ github.sha }} \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated \
          --set-env-vars SPREADSHEET_ID=${{ secrets.SPREADSHEET_ID }},SHEET_NAME=${{ secrets.SHEET_NAME }} \
          --set-secrets /app/creds.json=gsheets-creds:latest
```

**Секреты GitHub (Settings → Secrets):**
- `DOCKER_USERNAME` - логин Docker Hub
- `DOCKER_PASSWORD` - токен Docker Hub
- `GCP_SA_KEY` - JSON ключ сервисного аккаунта GCP
- `SPREADSHEET_ID` - ID таблицы
- `SHEET_NAME` - имя листа

### 7. OpenAPI/Swagger - кастомизация документации

**Улучшенный `app.py` с детальной документацией:**

```python
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging

# Метаданные для OpenAPI
tags_metadata = [
    {
        "name": "data",
        "description": "Операции с данными из Google Sheets",
    },
    {
        "name": "health",
        "description": "Проверка состояния сервиса",
    },
]

app = FastAPI(
    title="Google Sheets JSON API",
    description="""
    🚀 REST API для получения данных из Google Sheets в JSON формате.
    
    ## Возможности
    
    * **Чтение данных** из Google Sheets
    * **Фильтрация** по любым колонкам
    * **Пагинация** для больших таблиц
    * **Rate Limiting** для защиты от DDoS
    
    ## Аутентификация
    
    API использует сервисный аккаунт Google для доступа к таблицам.
    Убедитесь, что таблица расшарена с email сервисного аккаунта.
    
    ## Формат данных
    
    Первая строка таблицы = заголовки (ключи JSON).
    Остальные строки = данные (значения JSON).
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "url": "https://github.com/yourname/gsheets-json-api",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

@app.get(
    "/api/data",
    tags=["data"],
    summary="Получить данные из Google Sheets",
    response_description="Список записей в JSON формате",
    responses={
        200: {
            "description": "Успешный запрос",
            "content": {
                "application/json": {
                    "example": {
                        "total": 2,
                        "limit": 100,
                        "offset": 0,
                        "data": [
                            {"Name": "Alice", "Age": "30", "City": "Moscow"},
                            {"Name": "Bob", "Age": "25", "City": "SPb"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Ошибка сервера (недоступна таблица)",
            "content": {
                "application/json": {
                    "example": {"error": "Failed to fetch data from Google Sheets"}
                }
            },
        },
    },
)
async def get_data(
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Количество записей на странице",
        example=10
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Смещение от начала (для пагинации)",
        example=0
    ),
    city: Optional[str] = Query(
        None,
        description="Фильтр по городу (регистронезависимый)",
        example="Moscow"
    ),
    name: Optional[str] = Query(
        None,
        description="Поиск по имени (частичное совпадение)",
        example="Alice"
    ),
) -> Dict[str, Any]:
    """
    Получить данные из Google Sheets с фильтрацией и пагинацией.
    
    **Пример использования:**
    ```bash
    # Все данные
    curl http://localhost:8000/api/data
    
    # С фильтром
    curl "http://localhost:8000/api/data?city=Moscow"
    
    # С пагинацией
    curl "http://localhost:8000/api/data?limit=10&offset=20"
    ```
    """
    try:
        data = sheets_client.get_data()
        
        # Фильтрация
        if city:
            data = [row for row in data if row.get('City', '').lower() == city.lower()]
        if name:
            data = [row for row in data if name.lower() in row.get('Name', '').lower()]
        
        total = len(data)
        paginated_data = data[offset:offset + limit]
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": paginated_data
        }
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch data from Google Sheets"
        )

@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    response_description="Статус сервиса",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """
    Проверка работоспособности API.
    
    Используется для мониторинга и Load Balancer health checks.
    """
    return {
        "status": "ok",
        "service": "gsheets-json-api",
        "version": "1.0.0"
    }
```

**Результат:** Swagger UI доступен на `http://localhost:8000/docs` с полной документацией!

### 8. Async реализация - современный подход

**Зачем:** Async позволяет обрабатывать больше запросов параллельно (если добавить внешние API, БД и т.д.)

**sheets_client.py с async:**

```python
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict
import logging
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

class AsyncGoogleSheetsClient:
    """
    Асинхронный клиент для работы с Google Sheets.
    
    Примечание: gspread сам по себе синхронный, поэтому мы используем
    asyncio.to_thread() для выполнения блокирующих операций в отдельном потоке.
    """
    
    def __init__(self, credentials_file: str, spreadsheet_id: str, sheet_name: str):
        """
        Инициализация клиента Google Sheets.
        
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
                self._client = gspread.service_account(filename=self.credentials_file)
                logger.info("Successfully authenticated with Google Sheets")
            except Exception as e:
                logger.error(f"Failed to authenticate: {e}")
                raise
        return self._client
    
    async def get_data(self) -> List[Dict[str, str]]:
        """
        Асинхронно получить данные из Google Sheets.
        
        Returns:
            Список словарей, где ключи - заголовки из первой строки
        """
        try:
            # Выполняем синхронную операцию в отдельном потоке
            data = await asyncio.to_thread(self._fetch_data_sync)
            logger.info(f"Successfully fetched {len(data)} rows")
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    def _fetch_data_sync(self) -> List[Dict[str, str]]:
        """Синхронная функция для получения данных (запускается в отдельном потоке)"""
        client = self._get_client()
        spreadsheet = client.open_by_key(self.spreadsheet_id)
        worksheet = spreadsheet.worksheet(self.sheet_name)
        
        # Получаем все значения
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return []
        
        # Первая строка - заголовки
        headers = all_values[0]
        data_rows = all_values[1:]
        
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
        """
        return await self.get_data()
```

**app.py с async эндпоинтами:**

```python
from fastapi import FastAPI, BackgroundTasks
from typing import List
import asyncio

@app.get("/api/data")
async def get_data_async(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Асинхронный эндпоинт с возможностью параллельной обработки"""
    # Используем async клиент
    data = await sheets_client.get_data()
    
    total = len(data)
    paginated = data[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": paginated
    }

@app.post("/api/webhooks/notify")
async def notify_webhook(background_tasks: BackgroundTasks, url: str):
    """
    Пример использования background tasks для долгих операций.
    
    Отправляет webhook в фоне, не блокируя ответ.
    """
    background_tasks.add_task(send_webhook_background, url)
    return {"status": "Notification scheduled"}

async def send_webhook_background(url: str):
    """Фоновая задача для отправки webhook"""
    await asyncio.sleep(2)  # Имитация долгой операции
    logger.info(f"Webhook sent to {url}")
```

**Преимущества async:**
- ✅ Обрабатывает больше запросов одновременно
- ✅ Готов к интеграции с async БД (asyncpg, motor)
- ✅ Background tasks для долгих операций
- ✅ Не блокирует event loop при ожидании I/O

### 9. Дополнительные улучшения

- [ ] **Кэширование** с Redis и TTL
- [ ] **Запись данных** (POST/PUT эндпоинты)
- [ ] **Аутентификация API** (API keys / JWT)
- [ ] **Prometheus metrics** для мониторинга
- [ ] **Версионирование API** (/v1/api/data)
- [ ] **WebSocket** для real-time обновлений
- [ ] **GraphQL** вместо REST

## Временные оценки

### Базовая реализация (MVP):
- Этап 1-2 (Инфраструктура + Конфигурация): 30 минут
- Этап 3 (Клиент Google Sheets): 45 минут
- Этап 4 (API): 30 минут
- Этап 5 (Документация): 45 минут
- Этап 6 (Контейнеризация): 20 минут

**Итого MVP: ~3 часа** (включая тестирование и отладку)

### Продвинутые фичи:
- Rate Limiting: 15 минут
- Фильтрация: 30 минут
- Pagination: 20 минут
- Тесты (базовые): 45 минут
- Docker Compose: 30 минут
- GitHub Actions CI/CD: 40 минут
- OpenAPI документация: 20 минут
- Async реализация: 45 минут

**Итого с фичами: ~6-7 часов** (полноценный production-ready проект)

### Enterprise-уровень (всё вместе):
- Полное тестовое покрытие: 2 часа
- Мониторинг (Prometheus): 1 час
- Кэширование (Redis): 45 минут
- Аутентификация (JWT): 1 час

**Итого enterprise: ~10-12 часов** (коммерческий проект с полным набором)

---

## Быстрый старт для разработчика

### Локальная разработка (традиционный способ):
```bash
# 1. Клонировать репозиторий
git clone https://github.com/yourname/gsheets-json-api.git
cd gsheets-json-api

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# 3. Установить зависимости
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Настроить окружение
cp .env.example .env
# Отредактировать .env и добавить свои данные

# 5. Добавить credentials
# Поместить creds.json в корень проекта

# 6. Запустить сервер
uvicorn app:app --reload --port 8000

# 7. Открыть документацию
# http://localhost:8000/docs
```

### Docker Compose (рекомендуемый способ):
```bash
# 1. Настроить .env
cp .env.example .env

# 2. Запустить все сервисы
docker-compose up -d

# 3. Посмотреть логи
docker-compose logs -f api

# 4. Остановить
docker-compose down
```

### Запуск тестов:
```bash
# Все тесты
pytest

# С покрытием
pytest --cov=. --cov-report=html

# Конкретный файл
pytest tests/test_api.py -v

# Watch mode (требует pytest-watch)
ptw -- -v
```

### Форматирование и линтинг:
```bash
# Форматирование кода
black .
isort .

# Проверка стиля
flake8 .

# Проверка типов
mypy app.py sheets_client.py config.py
```

### Деплой на Cloud Run:
```bash
# 1. Аутентификация
gcloud auth login

# 2. Сборка и пуш образа
gcloud builds submit --tag gcr.io/PROJECT_ID/gsheets-api

# 3. Деплой
gcloud run deploy gsheets-api \
  --image gcr.io/PROJECT_ID/gsheets-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Полезные ссылки

- [FastAPI документация](https://fastapi.tiangolo.com/)
- [gspread документация](https://docs.gspread.org/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Cloud Run документация](https://cloud.google.com/run/docs)
- [Docker Compose документация](https://docs.docker.com/compose/)
- [GitHub Actions документация](https://docs.github.com/en/actions)
- [pytest документация](https://docs.pytest.org/)

---

## Следующие шаги после завершения проекта

1. ✅ Протестировать локально с реальной таблицей
2. ✅ Запустить все тесты и добиться 80%+ покрытия
3. ✅ Проверить документацию Swagger UI
4. ✅ Запушить в GitHub
5. ✅ Настроить GitHub Actions (тесты будут запускаться автоматически)
6. ✅ Задеплоить на Cloud Run
7. ✅ Протестировать production URL
8. ✅ Добавить в портфолио 🎉
