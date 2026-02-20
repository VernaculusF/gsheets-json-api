# Google Sheets JSON API

🚀 REST API для получения данных из Google Sheets в JSON формате с поддержкой фильтрации и пагинации.

## 📋 Описание

Этот проект предоставляет простой и мощный REST API для чтения данных из Google Sheets таблиц. Идеально подходит для:

- Создания публичных API на основе Google Sheets
- Интеграции Google Sheets с веб-приложениями
- Быстрого прототипирования API без базы данных
- CMS на основе Google Sheets

## ✨ Возможности

- ✅ **Чтение данных** из Google Sheets в реальном времени
- ✅ **Фильтрация** по любым колонкам через query parameters
- ✅ **Пагинация** для работы с большими таблицами
- ✅ **Rate Limiting** - защита от DDoS (60 запросов/минуту с IP)
- ✅ **Автоматическая документация** - Swagger UI и ReDoc
- ✅ **Асинхронная обработка** - высокая производительность
- ✅ **CORS** - поддержка запросов из браузера
- ✅ **Docker** - готов к контейнеризации
- ✅ **Type hints** - полная типизация кода

> **Примечание:** Это **read-only API**. Оно получает данные из Google Sheets, но не поддерживает операции записи (POST/PUT/DELETE). Сервисному аккаунту требуются только права Viewer.

## 🛠 Технологии

- **Python 3.10+**
- **FastAPI** - современный веб-фреймворк
- **gspread** - клиент для Google Sheets API
- **google-auth** - аутентификация через сервисный аккаунт
- **uvicorn** - ASGI сервер
- **slowapi** - rate limiting

## 📦 Установка и настройка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/VernaculusF/gsheets-json-api.git
cd gsheets-json-api
```

### 2. Создать виртуальное окружение

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Получить credentials от Google Cloud

#### Шаг 1: Создать проект в Google Cloud Console

1. Перейти на [Google Cloud Console](https://console.cloud.google.com/)
2. Создать новый проект или выбрать существующий
3. Включить **Google Sheets API**:
   - В меню выбрать "APIs & Services" → "Enable APIs and Services"
   - Найти "Google Sheets API" и включить

#### Шаг 2: Создать сервисный аккаунт

1. Перейти в "APIs & Services" → "Credentials"
2. Нажать "Create Credentials" → "Service Account"
3. Заполнить:
   - **Service account name**: `gsheets-api-service`
   - **Service account ID**: автогенерируется
   - Нажать "Create and Continue"
4. Роль: можно пропустить (не требуется для Sheets API)
5. Нажать "Done"

#### Шаг 3: Создать ключ (credentials)

1. В списке сервисных аккаунтов кликнуть на созданный аккаунт
2. Перейти на вкладку "Keys"
3. Нажать "Add Key" → "Create new key"
4. Выбрать формат **JSON**
5. Скачать файл - это ваш `creds.json`

#### Шаг 4: Сохранить credentials

```bash
# Переместить скачанный файл в корень проекта
mv ~/Downloads/your-project-xxxxx.json creds.json
```

⚠️ **Важно**: Не коммитьте `creds.json` в git! Файл уже добавлен в `.gitignore`.

### 5. Расшарить Google Sheets таблицу

1. Открыть вашу Google Sheets таблицу
2. Нажать кнопку "Share" (Поделиться)
3. Скопировать **email** сервисного аккаунта из `creds.json`:
   ```json
   "client_email": "gsheets-api-service@your-project.iam.gserviceaccount.com"
   ```
4. Вставить этот email в поле "Add people and groups"
5. Установить права **Viewer** (только чтение)
6. Нажать "Send"

### 6. Настроить переменные окружения

```bash
# Скопировать пример
cp .env.example .env

# Отредактировать .env файл
```

Заполнить `.env`:

```env
# ID таблицы (из URL Google Sheets)
# https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
#                                     ^^^^^^^^ это SPREADSHEET_ID ^^^^^^^^
SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

# Название листа в таблице (по умолчанию "Sheet1")
SHEET_NAME=Sheet1

# Порт сервера
PORT=8000

# Уровень логирования (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 7. Формат Google Sheets таблицы

Таблица должна иметь **заголовки в первой строке**:

| Name    | Age | City     | Email              |
|---------|-----|----------|--------------------|
| Alice   | 30  | Moscow   | alice@example.com  |
| Bob     | 25  | SPb      | bob@example.com    |
| Charlie | 35  | Kazan    | charlie@example.com|

- **Первая строка** = заголовки (ключи JSON)
- **Остальные строки** = данные (значения JSON)

## 🚀 Запуск

### Локальный запуск

```bash
# Активировать виртуальное окружение
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Запустить сервер
python app.py

# Или через uvicorn напрямую
uvicorn app:app --reload --port 8000
```

Сервер будет доступен на `http://localhost:8000`

### Документация API

После запуска откройте в браузере:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 Использование API

### Базовый запрос

```bash
# Получить все данные (первые 100 записей)
curl http://localhost:8000/api/data
```

**Ответ:**
```json
{
  "total": 3,
  "limit": 100,
  "offset": 0,
  "filters_applied": null,
  "data": [
    {
      "Name": "Alice",
      "Age": "30",
      "City": "Moscow",
      "Email": "alice@example.com"
    },
    {
      "Name": "Bob",
      "Age": "25",
      "City": "SPb",
      "Email": "bob@example.com"
    },
    {
      "Name": "Charlie",
      "Age": "35",
      "City": "Kazan",
      "Email": "charlie@example.com"
    }
  ]
}
```

### Фильтрация

```bash
# Фильтр по городу
curl "http://localhost:8000/api/data?city=Moscow"

# Фильтр по возрасту
curl "http://localhost:8000/api/data?age=30"

# Поиск по имени (частичное совпадение)
curl "http://localhost:8000/api/data?name=Ali"

# Комбинация фильтров
curl "http://localhost:8000/api/data?city=Moscow&age=30"
```

### Пагинация

```bash
# Первые 10 записей
curl "http://localhost:8000/api/data?limit=10&offset=0"

# Следующие 10 записей
curl "http://localhost:8000/api/data?limit=10&offset=10"

# С фильтром и пагинацией
curl "http://localhost:8000/api/data?city=Moscow&limit=5&offset=0"
```

### Health Check

```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "ok",
  "service": "gsheets-json-api",
  "version": "1.0.0",
  "environment": "development"
}
```

## 🐳 Docker

### Сборка образа

```bash
docker build -t gsheets-json-api .
```

### Запуск контейнера

```bash
docker run -d \
  -p 8000:8000 \
  -e SPREADSHEET_ID=your_spreadsheet_id \
  -e SHEET_NAME=Sheet1 \
  -v $(pwd)/creds.json:/app/creds.json:ro \
  --name gsheets-api \
  gsheets-json-api
```

### Docker Compose

```bash
# Запустить все сервисы
docker-compose up -d

# Посмотреть логи
docker-compose logs -f api

# Остановить
docker-compose down
```

## ☁️ Деплой на Google Cloud Run

### Подготовка

1. Установить [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Аутентифицироваться:
   ```bash
   gcloud auth login
   ```

### Создать Secret для credentials

```bash
# Создать secret с содержимым creds.json
gcloud secrets create gsheets-creds \
  --data-file=creds.json \
  --replication-policy=automatic
```

### Деплой

```bash
# Собрать и загрузить образ
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gsheets-api

# Задеплоить на Cloud Run
gcloud run deploy gsheets-api \
  --image gcr.io/YOUR_PROJECT_ID/gsheets-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SPREADSHEET_ID=your_spreadsheet_id,SHEET_NAME=Sheet1 \
  --set-secrets /app/creds.json=gsheets-creds:latest
```

После деплоя вы получите URL типа:
```
https://gsheets-api-xxxxx-uc.a.run.app
```

### Обновление

```bash
# Повторить команды build и deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gsheets-api
gcloud run deploy gsheets-api --image gcr.io/YOUR_PROJECT_ID/gsheets-api
```

## 🧪 Тестирование

### Установить dev-зависимости

```bash
pip install -r requirements-dev.txt
```

### Запустить тесты

```bash
# Все тесты
pytest

# С покрытием кода
pytest --cov=. --cov-report=html

# Конкретный файл
pytest tests/test_api.py -v
```

### Линтинг и форматирование

```bash
# Форматирование кода
black .
isort .

# Проверка стиля
flake8 .

# Проверка типов
mypy app.py sheets_client.py config.py
```

## 🔧 Troubleshooting

### Ошибка: "Failed to authenticate with Google Sheets"

**Причина**: Неверный или отсутствующий `creds.json`

**Решение**:
- Проверить, что файл `creds.json` существует
- Проверить формат JSON (должен быть валидным)
- Убедиться, что Google Sheets API включен в проекте

### Ошибка: "Spreadsheet not found or not shared"

**Причина**: Таблица не расшарена с сервисным аккаунтом

**Решение**:
- Открыть Google Sheets таблицу
- Нажать "Share"
- Добавить email из `client_email` в `creds.json`
- Установить права Viewer

### Ошибка: "Worksheet 'SheetName' not found"

**Причина**: Неверное название листа в `.env`

**Решение**:
- Проверить точное название листа в Google Sheets (с учетом регистра)
- Обновить `SHEET_NAME` в `.env` файле

### Rate Limit Exceeded (429)

**Причина**: Превышен лимит запросов (60/минуту)

**Решение**:
- Подождать 1 минуту
- Уменьшить частоту запросов
- Настроить другой лимит в `app.py` (`@limiter.limit("60/minute")`)

### Пустой ответ (empty data array)

**Причины**:
1. Таблица действительно пуста
2. Первая строка не содержит заголовков
3. Все данные отфильтрованы

**Решение**:
- Проверить содержимое таблицы
- Убедиться, что первая строка содержит заголовки
- Проверить фильтры в запросе

## 📚 Дополнительные ресурсы

- [FastAPI документация](https://fastapi.tiangolo.com/)
- [gspread документация](https://docs.gspread.org/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Cloud Run документация](https://cloud.google.com/run/docs)

## 🤝 Вклад в проект

Pull requests приветствуются! Для серьезных изменений откройте issue для обсуждения.

## 📄 Лицензия

[MIT](https://opensource.org/licenses/MIT)

## 👤 Автор

Ваше имя - [@yourhandle](https://github.com/yourhandle)

## ⭐ Поддержка

Если проект оказался полезным, поставьте звезду ⭐ на GitHub!

---

**Сделано с ❤️ и FastAPI**
