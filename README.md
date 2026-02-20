# Google Sheets JSON API

🚀 REST API for retrieving data from Google Sheets in JSON format with filtering and pagination support.

## 📋 Description

This project provides a simple and powerful REST API for reading data from Google Sheets. Perfect for:

- Creating public APIs based on Google Sheets
- Integrating Google Sheets with web applications
- Rapid API prototyping without a database
- CMS based on Google Sheets

## ✨ Features

- ✅ **Real-time data reading** from Google Sheets
- ✅ **Filtering** by any columns via query parameters
- ✅ **Pagination** for handling large spreadsheets
- ✅ **Rate Limiting** - DDoS protection (60 requests/minute per IP)
- ✅ **Automatic documentation** - Swagger UI and ReDoc
- ✅ **Async processing** - high performance
- ✅ **CORS** - browser request support
- ✅ **Docker** - containerization ready
- ✅ **Type hints** - fully typed code

## 🛠 Technologies

- **Python 3.10+**
- **FastAPI** - modern web framework
- **gspread** - Google Sheets API client
- **google-auth** - service account authentication
- **uvicorn** - ASGI server
- **slowapi** - rate limiting

## 📦 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourname/gsheets-json-api.git
cd gsheets-json-api
```

### 2. Create virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get credentials from Google Cloud

#### Step 1: Create a project in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **Google Sheets API**:
   - In the menu, select "APIs & Services" → "Enable APIs and Services"
   - Search for "Google Sheets API" and enable it

#### Step 2: Create a service account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in:
   - **Service account name**: `gsheets-api-service`
   - **Service account ID**: auto-generated
   - Click "Create and Continue"
4. Role: can be skipped (not required for Sheets API)
5. Click "Done"

#### Step 3: Create a key (credentials)

1. In the service accounts list, click on the created account
2. Go to the "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select **JSON** format
5. Download the file - this is your `creds.json`

#### Step 4: Save credentials

```bash
# Move the downloaded file to the project root
mv ~/Downloads/your-project-xxxxx.json creds.json
```

⚠️ **Important**: Don't commit `creds.json` to git! The file is already added to `.gitignore`.

### 5. Share the Google Sheets spreadsheet

1. Open your Google Sheets spreadsheet
2. Click the "Share" button
3. Copy the **email** of the service account from `creds.json`:
   ```json
   "client_email": "gsheets-api-service@your-project.iam.gserviceaccount.com"
   ```
4. Paste this email into the "Add people and groups" field
5. Set permissions to **Viewer** (read-only)
6. Click "Send"

### 6. Configure environment variables

```bash
# Copy the example
cp .env.example .env

# Edit the .env file
```

Fill in `.env`:

```env
# Spreadsheet ID (from Google Sheets URL)
# https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
#                                     ^^^^^^^^ this is SPREADSHEET_ID ^^^^^^^^
SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

# Sheet name in the spreadsheet (default "Sheet1")
SHEET_NAME=Sheet1

# Server port
PORT=8000

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 7. Google Sheets format

The spreadsheet must have **headers in the first row**:

| Name    | Age | City     | Email              |
|---------|-----|----------|--------------------|
| Alice   | 30  | Moscow   | alice@example.com  |
| Bob     | 25  | SPb      | bob@example.com    |
| Charlie | 35  | Kazan    | charlie@example.com|

- **First row** = headers (JSON keys)
- **Other rows** = data (JSON values)

## 🚀 Running

### Local run

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Start the server
python app.py

# Or via uvicorn directly
uvicorn app:app --reload --port 8000
```

The server will be available at `http://localhost:8000`

### API Documentation

After starting, open in your browser:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Usage

### Basic request

```bash
# Get all data (first 100 records)
curl http://localhost:8000/api/data
```

**Response:**
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

### Filtering

```bash
# Filter by city
curl "http://localhost:8000/api/data?city=Moscow"

# Filter by age
curl "http://localhost:8000/api/data?age=30"

# Search by name (partial match)
curl "http://localhost:8000/api/data?name=Ali"

# Combined filters
curl "http://localhost:8000/api/data?city=Moscow&age=30"
```

### Pagination

```bash
# First 10 records
curl "http://localhost:8000/api/data?limit=10&offset=0"

# Next 10 records
curl "http://localhost:8000/api/data?limit=10&offset=10"

# With filter and pagination
curl "http://localhost:8000/api/data?city=Moscow&limit=5&offset=0"
```

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "gsheets-json-api",
  "version": "1.0.0",
  "environment": "development"
}
```

## 🐳 Docker

### Build image

```bash
docker build -t gsheets-json-api .
```

### Run container

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
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

## ☁️ Deploy to Google Cloud Run

### Preparation

1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Authenticate:
   ```bash
   gcloud auth login
   ```

### Create Secret for credentials

```bash
# Create secret with creds.json contents
gcloud secrets create gsheets-creds \
  --data-file=creds.json \
  --replication-policy=automatic
```

### Deploy

```bash
# Build and upload image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gsheets-api

# Deploy to Cloud Run
gcloud run deploy gsheets-api \
  --image gcr.io/YOUR_PROJECT_ID/gsheets-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SPREADSHEET_ID=your_spreadsheet_id,SHEET_NAME=Sheet1 \
  --set-secrets /app/creds.json=gsheets-creds:latest
```

After deployment, you'll get a URL like:
```
https://gsheets-api-xxxxx-uc.a.run.app
```

### Updating

```bash
# Repeat build and deploy commands
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gsheets-api
gcloud run deploy gsheets-api --image gcr.io/YOUR_PROJECT_ID/gsheets-api
```

## 🧪 Testing

### Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

### Run tests

```bash
# All tests
pytest

# With code coverage
pytest --cov=. --cov-report=html

# Specific file
pytest tests/test_api.py -v
```

### Linting and formatting

```bash
# Code formatting
black .
isort .

# Style check
flake8 .

# Type checking
mypy app.py sheets_client.py config.py
```

## 🔧 Troubleshooting

### Error: "Failed to authenticate with Google Sheets"

**Cause**: Invalid or missing `creds.json`

**Solution**:
- Check that the `creds.json` file exists
- Verify JSON format (must be valid)
- Ensure Google Sheets API is enabled in the project

### Error: "Spreadsheet not found or not shared"

**Cause**: Spreadsheet is not shared with the service account

**Solution**:
- Open the Google Sheets spreadsheet
- Click "Share"
- Add the email from `client_email` in `creds.json`
- Set Viewer permissions

### Error: "Worksheet 'SheetName' not found"

**Cause**: Incorrect sheet name in `.env`

**Solution**:
- Check the exact sheet name in Google Sheets (case-sensitive)
- Update `SHEET_NAME` in the `.env` file

### Rate Limit Exceeded (429)

**Cause**: Rate limit exceeded (60/minute)

**Solution**:
- Wait 1 minute
- Reduce request frequency
- Configure a different limit in `app.py` (`@limiter.limit("60/minute")`)

### Empty response (empty data array)

**Causes**:
1. The spreadsheet is actually empty
2. The first row doesn't contain headers
3. All data is filtered out

**Solution**:
- Check the spreadsheet contents
- Ensure the first row contains headers
- Check the filters in the request

## 📚 Additional Resources

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [gspread documentation](https://docs.gspread.org/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Cloud Run documentation](https://cloud.google.com/run/docs)

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss.

## 📄 License

[MIT](https://opensource.org/licenses/MIT)

## 👤 Author

Your Name - [@yourhandle](https://github.com/yourhandle)

## ⭐ Support

If you found this project helpful, give it a star ⭐ on GitHub!

---

**Made with ❤️ and FastAPI**
