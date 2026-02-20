"""
Application configuration module.
Loads and validates environment variables from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Class for storing and validating application configuration"""
    
    # Google Sheets settings
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    SHEET_NAME: str = os.getenv("SHEET_NAME", "Sheet1")
    
    # Path to credentials file
    CREDENTIALS_FILE: str = os.getenv("CREDENTIALS_FILE", "creds.json")
    
    # Server settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Optional settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate required environment variables.
        
        Raises:
            ValueError: if required variables are not set
            FileNotFoundError: if credentials file not found
        """
        errors = []
        
        # Check required variables
        if not cls.SPREADSHEET_ID:
            errors.append("SPREADSHEET_ID is not set in .env file")
        
        if not cls.SHEET_NAME:
            errors.append("SHEET_NAME is not set in .env file")
        
        # Check credentials file existence
        credentials_path = Path(cls.CREDENTIALS_FILE)
        if not credentials_path.exists():
            errors.append(
                f"Credentials file not found: {cls.CREDENTIALS_FILE}\n"
                f"Please create it from creds.json.example"
            )
        
        # If there are errors, raise exception
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            logger.error(error_message)
            raise ValueError(error_message)
        
        logger.info("Configuration validated successfully")
    
    @classmethod
    def get_info(cls) -> dict:
        """
        Get configuration information (safe version without secrets).
        
        Returns:
            dict: Dictionary with settings (spreadsheet ID masked)
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


# Validate configuration on module import
try:
    Config.validate()
except ValueError as e:
    # In production, can catch and log,
    # but for development better to fail immediately
    logger.warning(f"Config validation skipped or failed: {e}")
    # raise  # Uncomment in production
