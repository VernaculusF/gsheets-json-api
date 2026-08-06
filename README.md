# Google Sheets JSON API

Read-only REST API for exposing Google Sheets rows as JSON. The service supports filtering and pagination and authenticates through a Google service account.

## Features

- Reading worksheet rows through a JSON endpoint
- Filtering by column values through query parameters
- Pagination with `limit` and `offset`
- Rate limiting, CORS, health checks, Swagger UI, and ReDoc
- Local and Docker-based execution

## Stack

- Python 3.10+
- FastAPI and Uvicorn
- gspread and google-auth
- SlowAPI
- pytest

## Quick start

Create a Google Cloud service account with access to the target spreadsheet, download its key as `creds.json`, and share the spreadsheet with the service account email. The first worksheet row must contain the JSON field names.

```bash
git clone https://github.com/VernaculusF/gsheets-json-api.git
cd gsheets-json-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cp creds.json.example creds.json
uvicorn app:app --reload --port 8000
```

Replace the example values in `.env` and `creds.json` before starting the service. Neither file should be committed.

Request data and inspect service status:

```bash
curl "http://localhost:8000/api/data?limit=10&offset=0"
curl "http://localhost:8000/api/data?city=Moscow"
curl http://localhost:8000/health
```

Interactive API documentation is available at `http://localhost:8000/docs` and `http://localhost:8000/redoc`.

Run the test suite with development dependencies:

```bash
pip install -r requirements-dev.txt
pytest
```

Docker Compose can be used after configuration:

```bash
docker compose up --build
```

## Project structure

- `app.py` — FastAPI application and HTTP routes
- `config.py` — environment-based configuration
- `sheets_client.py` — Google Sheets access and data processing
- `tests/` — API and client tests
- `.env.example` — environment variable template
- `creds.json.example` — service account key template
- `Dockerfile`, `docker-compose.yml`, `nginx.conf` — container deployment files

## License

MIT
