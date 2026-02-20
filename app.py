"""
Main FastAPI application for Google Sheets JSON API.
Provides REST API for retrieving data from Google Sheets in JSON format.
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

# Logging configuration
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Metadata for OpenAPI documentation
tags_metadata = [
    {
        "name": "data",
        "description": "Operations with data from Google Sheets. "
                      "Supports filtering and pagination.",
    },
    {
        "name": "health",
        "description": "Service health and readiness checks.",
    },
]

# Initialize FastAPI application
app = FastAPI(
    title="Google Sheets JSON API",
    description="""
    🚀 **REST API for retrieving data from Google Sheets in JSON format.**
    
    ## Features
    
    * **Read data** from Google Sheets in real-time
    * **Filtering** by any columns (query parameters)
    * **Pagination** for handling large spreadsheets
    * **Rate Limiting** to protect against abuse
    * **Async processing** for high performance
    
    ## Authentication
    
    API uses Google service account to access spreadsheets.
    Make sure the Google Sheets spreadsheet is shared with your service account email.
    
    ## Data Format
    
    - **First row** of the spreadsheet = headers (JSON object keys)
    - **Other rows** = data (JSON object values)
    
    ## Usage Examples
    
    ```bash
    # Get all data
    curl http://localhost:8000/api/data
    
    # Filter by city
    curl "http://localhost:8000/api/data?city=Moscow"
    
    # Pagination (first 10 records)
    curl "http://localhost:8000/api/data?limit=10&offset=0"
    
    # Combined filters
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
    redoc_url="/redoc",  # ReDoc alternative documentation
)

# CORS (Cross-Origin Resource Sharing) configuration
# Allows requests from browsers on other domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting configuration
# Protection against DDoS and API abuse
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Initialize Google Sheets client
sheets_client = AsyncGoogleSheetsClient(
    credentials_file=Config.CREDENTIALS_FILE,
    spreadsheet_id=Config.SPREADSHEET_ID,
    sheet_name=Config.SHEET_NAME
)

logger.info("Starting Google Sheets JSON API")
logger.info(f"Configuration: {Config.get_info()}")


@app.on_event("startup")
async def startup_event():
    """Actions on application startup"""
    logger.info("Application startup complete")
    logger.info(f"Swagger UI available at: http://{Config.HOST}:{Config.PORT}/docs")
    logger.info(f"ReDoc available at: http://{Config.HOST}:{Config.PORT}/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions on application shutdown"""
    logger.info("Application shutdown")


@app.get(
    "/",
    include_in_schema=False,
    response_class=JSONResponse,
)
async def root():
    """Root endpoint - redirect to documentation"""
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
    response_description="Service health status",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """
    API health check.
    
    Used for:
    - Service monitoring
    - Health checks in Kubernetes/Cloud Run
    - Load Balancer checks
    
    Returns:
        dict: Service status and metadata
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
    summary="Get data from Google Sheets",
    response_description="List of records in JSON format with pagination metadata",
    responses={
        200: {
            "description": "Successful request - data retrieved",
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
            "description": "Too many requests - rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"error": "Rate limit exceeded"}
                }
            },
        },
        500: {
            "description": "Server error - spreadsheet unavailable or other issue",
            "content": {
                "application/json": {
                    "example": {"error": "Failed to fetch data from Google Sheets"}
                }
            },
        },
    },
)
@limiter.limit("60/minute")  # 60 requests per minute per IP
async def get_data(
    request: Request,  # Required for rate limiter
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of records per page (1-1000)",
        example=10
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of records to skip (for pagination)",
        example=0
    ),
    # Dynamic filters - can add any as needed
    city: Optional[str] = Query(
        None,
        description="Filter by 'City' column (case-insensitive search)",
        example="Moscow"
    ),
    age: Optional[str] = Query(
        None,
        description="Filter by 'Age' column (exact match)",
        example="30"
    ),
    name: Optional[str] = Query(
        None,
        description="Search by 'Name' column (partial match, case-insensitive)",
        example="Alice"
    ),
) -> Dict[str, Any]:
    """
    Get data from Google Sheets with filtering and pagination support.
    
    ## Filtering
    
    You can combine multiple filters:
    - **city**: exact match (case-insensitive)
    - **age**: exact match
    - **name**: partial match (substring search)
    
    ## Pagination
    
    Use `limit` and `offset` for page navigation:
    - Page 1: `?limit=10&offset=0`
    - Page 2: `?limit=10&offset=10`
    - Page 3: `?limit=10&offset=20`
    
    ## Examples
    
    ```bash
    # All data (first 100)
    curl http://localhost:8000/api/data
    
    # Filter by city
    curl "http://localhost:8000/api/data?city=Moscow"
    
    # Search by name
    curl "http://localhost:8000/api/data?name=Alice"
    
    # Pagination
    curl "http://localhost:8000/api/data?limit=10&offset=20"
    
    # Combined filters
    curl "http://localhost:8000/api/data?city=Moscow&limit=5"
    ```
    
    ## Response
    
    Returns a JSON object with fields:
    - `total`: total number of records after filtering
    - `limit`: applied limit
    - `offset`: applied offset
    - `filters_applied`: applied filters
    - `data`: array of records
    """
    try:
        logger.info(f"Fetching data with limit={limit}, offset={offset}")
        
        # Get data from Google Sheets (async)
        data = await sheets_client.get_data()
        
        # Collect information about applied filters
        filters_applied = {}
        
        # Apply filters
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
        
        # Count total after filtering
        total = len(data)
        
        # Apply pagination
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


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
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
    
    # Start server (for local development)
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True if Config.ENVIRONMENT == "development" else False,
        log_level=Config.LOG_LEVEL.lower()
    )
