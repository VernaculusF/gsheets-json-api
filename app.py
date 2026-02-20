"""
Основное FastAPI приложение для Google Sheets JSON API.
Предоставляет REST API для получения данных из Google Sheets в JSON формате.
"""

from fastapi import FastAPI, Query, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional, Dict, Any
import logging
import sys

from config import Config
from sheets_client import AsyncGoogleSheetsClient

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Метаданные для OpenAPI документации
tags_metadata = [
    {
        "name": "data",
        "description": "Операции с данными из Google Sheets. "
                      "Поддерживается фильтрация и пагинация.",
    },
    {
        "name": "health",
        "description": "Проверка состояния сервиса и готовности к работе.",
    },
]

# Инициализация FastAPI приложения
app = FastAPI(
    title="Google Sheets JSON API",
    description="""
    🚀 **REST API для получения данных из Google Sheets в JSON формате.**
    
    ## Возможности
    
    * **Чтение данных** из Google Sheets в реальном времени
    * **Фильтрация** по любым колонкам (query parameters)
    * **Пагинация** для работы с большими таблицами
    * **Rate Limiting** для защиты от злоупотреблений
    * **Асинхронная обработка** запросов для высокой производительности
    
    ## Аутентификация
    
    API использует сервисный аккаунт Google для доступа к таблицам.
    Убедитесь, что Google Sheets таблица расшарена с email вашего сервисного аккаунта.
    
    ## Формат данных
    
    - **Первая строка** таблицы = заголовки (ключи JSON объектов)
    - **Остальные строки** = данные (значения JSON объектов)
    
    ## Примеры использования
    
    ```bash
    # Получить все данные
    curl http://localhost:8000/api/data
    
    # Фильтрация по городу
    curl "http://localhost:8000/api/data?city=Moscow"
    
    # Пагинация (первые 10 записей)
    curl "http://localhost:8000/api/data?limit=10&offset=0"
    
    # Комбинация фильтров
    curl "http://localhost:8000/api/data?city=Moscow&limit=5"
    ```
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
    redoc_url="/redoc",  # ReDoc альтернативная документация
)

# Настройка CORS (Cross-Origin Resource Sharing)
# Позволяет запросы из браузера с других доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка Rate Limiting
# Защита от DDoS и злоупотреблений API
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Инициализация Google Sheets клиента
sheets_client = AsyncGoogleSheetsClient(
    credentials_file=Config.CREDENTIALS_FILE,
    spreadsheet_id=Config.SPREADSHEET_ID,
    sheet_name=Config.SHEET_NAME
)

logger.info("Starting Google Sheets JSON API")
logger.info(f"Configuration: {Config.get_info()}")


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    logger.info("Application startup complete")
    logger.info(f"Swagger UI available at: http://{Config.HOST}:{Config.PORT}/docs")
    logger.info(f"ReDoc available at: http://{Config.HOST}:{Config.PORT}/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    logger.info("Application shutdown")


@app.get(
    "/",
    include_in_schema=False,
    response_class=JSONResponse,
)
async def root():
    """Корневой эндпоинт - редирект на документацию"""
    return {
        "message": "Google Sheets JSON API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api": "/api/data"
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    response_description="Статус работоспособности сервиса",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """
    Проверка работоспособности API.
    
    Используется для:
    - Мониторинга сервиса
    - Health checks в Kubernetes/Cloud Run
    - Load Balancer проверок
    
    Returns:
        dict: Статус сервиса и метаданные
    """
    return {
        "status": "ok",
        "service": "gsheets-json-api",
        "version": "1.0.0",
        "environment": Config.ENVIRONMENT
    }


@app.get(
    "/api/data",
    tags=["data"],
    summary="Получить данные из Google Sheets",
    response_description="Список записей в JSON формате с метаданными пагинации",
    responses={
        200: {
            "description": "Успешный запрос - данные получены",
            "content": {
                "application/json": {
                    "example": {
                        "total": 2,
                        "limit": 100,
                        "offset": 0,
                        "filters_applied": {"city": "Moscow"},
                        "data": [
                            {"Name": "Alice", "Age": "30", "City": "Moscow"},
                            {"Name": "Bob", "Age": "25", "City": "Moscow"}
                        ]
                    }
                }
            },
        },
        429: {
            "description": "Слишком много запросов - превышен rate limit",
            "content": {
                "application/json": {
                    "example": {"error": "Rate limit exceeded"}
                }
            },
        },
        500: {
            "description": "Ошибка сервера - таблица недоступна или другая проблема",
            "content": {
                "application/json": {
                    "example": {"error": "Failed to fetch data from Google Sheets"}
                }
            },
        },
    },
)
@limiter.limit("60/minute")  # 60 запросов в минуту с одного IP
async def get_data(
    request: Request,  # Нужен для rate limiter
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Максимальное количество записей на странице (1-1000)",
        example=10
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Количество записей для пропуска (для пагинации)",
        example=0
    ),
    # Динамические фильтры - можно добавить любые по необходимости
    city: Optional[str] = Query(
        None,
        description="Фильтр по колонке 'City' (регистронезависимый поиск)",
        example="Moscow"
    ),
    age: Optional[str] = Query(
        None,
        description="Фильтр по колонке 'Age' (точное совпадение)",
        example="30"
    ),
    name: Optional[str] = Query(
        None,
        description="Поиск по колонке 'Name' (частичное совпадение, регистронезависимый)",
        example="Alice"
    ),
) -> Dict[str, Any]:
    """
    Получить данные из Google Sheets с поддержкой фильтрации и пагинации.
    
    ## Фильтрация
    
    Можно комбинировать несколько фильтров:
    - **city**: точное совпадение (регистронезависимое)
    - **age**: точное совпадение
    - **name**: частичное совпадение (поиск подстроки)
    
    ## Пагинация
    
    Используйте `limit` и `offset` для постраничной навигации:
    - Страница 1: `?limit=10&offset=0`
    - Страница 2: `?limit=10&offset=10`
    - Страница 3: `?limit=10&offset=20`
    
    ## Примеры
    
    ```bash
    # Все данные (первые 100)
    curl http://localhost:8000/api/data
    
    # Фильтр по городу
    curl "http://localhost:8000/api/data?city=Moscow"
    
    # Поиск по имени
    curl "http://localhost:8000/api/data?name=Alice"
    
    # Пагинация
    curl "http://localhost:8000/api/data?limit=10&offset=20"
    
    # Комбинация фильтров
    curl "http://localhost:8000/api/data?city=Moscow&limit=5"
    ```
    
    ## Ответ
    
    Возвращает JSON объект с полями:
    - `total`: общее количество записей после фильтрации
    - `limit`: примененный лимит
    - `offset`: примененное смещение
    - `filters_applied`: примененные фильтры
    - `data`: массив записей
    """
    try:
        logger.info(f"Fetching data with limit={limit}, offset={offset}")
        
        # Получаем данные из Google Sheets (асинхронно)
        data = await sheets_client.get_data()
        
        # Собираем информацию о примененных фильтрах
        filters_applied = {}
        
        # Применяем фильтры
        if city:
            data = [
                row for row in data 
                if row.get('City', '').lower() == city.lower()
            ]
            filters_applied['city'] = city
            logger.debug(f"Applied city filter: {city}")
        
        if age:
            data = [
                row for row in data 
                if row.get('Age', '') == age
            ]
            filters_applied['age'] = age
            logger.debug(f"Applied age filter: {age}")
        
        if name:
            data = [
                row for row in data 
                if name.lower() in row.get('Name', '').lower()
            ]
            filters_applied['name'] = name
            logger.debug(f"Applied name filter: {name}")
        
        # Подсчитываем общее количество после фильтрации
        total = len(data)
        
        # Применяем пагинацию
        paginated_data = data[offset:offset + limit]
        
        logger.info(
            f"Returning {len(paginated_data)} records "
            f"(total: {total}, limit: {limit}, offset: {offset})"
        )
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "filters_applied": filters_applied if filters_applied else None,
            "data": paginated_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching data from Google Sheets: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data from Google Sheets: {str(e)}"
        )


# Обработчик глобальных исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Обработка всех неперехваченных исключений"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if Config.ENVIRONMENT == "development" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Запуск сервера (для локальной разработки)
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True if Config.ENVIRONMENT == "development" else False,
        log_level=Config.LOG_LEVEL.lower()
    )
