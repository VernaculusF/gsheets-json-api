"""
Module for working with Google Sheets API.
Contains clients for synchronous and asynchronous access to spreadsheets.
"""

import gspread
from typing import List, Dict
import logging
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """
    Synchronous client for working with Google Sheets.
    Uses gspread and service account for authentication.
    """
    
    def __init__(self, credentials_file: str, spreadsheet_id: str, sheet_name: str):
        """
        Initialize Google Sheets client.
        
        Args:
            credentials_file: Path to JSON file with service account credentials
            spreadsheet_id: Google Spreadsheet ID (from URL)
            sheet_name: Sheet name in the spreadsheet
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self._client = None
        
        logger.info(f"Initializing GoogleSheetsClient for sheet: {sheet_name}")
    
    def _get_client(self) -> gspread.Client:
        """
        Lazy initialization of gspread client.
        Client is created only on first access.
        
        Returns:
            gspread.Client: Authenticated client
        
        Raises:
            Exception: If authentication failed
        """
        if self._client is None:
            try:
                from pathlib import Path
                self._client = gspread.service_account(filename=Path(self.credentials_file))
                logger.info("Successfully authenticated with Google Sheets API")
            except Exception as e:
                logger.error(f"Failed to authenticate with Google Sheets: {e}")
                raise
        return self._client
    
    def get_data(self) -> List[Dict[str, str]]:
        """
        Get all data from Google Sheets spreadsheet.
        First row is considered headers (JSON keys).
        
        Returns:
            List[Dict[str, str]]: List of dictionaries where keys are headers from first row
        
        Raises:
            Exception: On errors accessing spreadsheet or sheet
        """
        try:
            client = self._get_client()
            
            # Open spreadsheet by ID
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            logger.debug(f"Opened spreadsheet: {spreadsheet.title}")
            
            # Get sheet by name
            worksheet = spreadsheet.worksheet(self.sheet_name)
            logger.debug(f"Opened worksheet: {self.sheet_name}")
            
            # Get all values
            all_values = worksheet.get_all_values()
            
            if not all_values:
                logger.warning("Spreadsheet is empty")
                return []
            
            if len(all_values) < 1:
                logger.warning("Spreadsheet has no headers")
                return []
            
            # First row - headers
            headers = all_values[0]
            data_rows = all_values[1:]
            
            if not headers:
                logger.warning("Headers row is empty")
                return []
            
            # Convert to list of dictionaries
            result = []
            for row_index, row in enumerate(data_rows, start=2):  # +2 because numbering from 1 and skip headers
                # Pad short rows with empty values
                padded_row = row + [''] * (len(headers) - len(row))
                
                # Create dictionary, linking headers with values
                row_dict = dict(zip(headers, padded_row))
                result.append(row_dict)
            
            logger.info(f"Successfully fetched {len(result)} rows from sheet '{self.sheet_name}'")
            return result
            
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet '{self.sheet_name}' not found in spreadsheet")
            raise
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet with ID '{self.spreadsheet_id}' not found or not shared")
            raise
        except gspread.exceptions.APIError as e:
            logger.error(f"Google Sheets API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching data: {e}")
            raise


class AsyncGoogleSheetsClient:
    """
    Asynchronous client for working with Google Sheets.
    
    Note: gspread itself is synchronous, so we use
    asyncio.to_thread() to execute blocking operations in a separate thread.
    This allows not blocking FastAPI's event loop.
    """
    
    def __init__(self, credentials_file: str, spreadsheet_id: str, sheet_name: str):
        """
        Initialize asynchronous Google Sheets client.
        
        Args:
            credentials_file: Path to JSON file with credentials
            spreadsheet_id: Google Spreadsheet ID
            sheet_name: Sheet name
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self._client = None
        
        logger.info(f"Initializing AsyncGoogleSheetsClient for sheet: {sheet_name}")
    
    def _get_client(self) -> gspread.Client:
        """Lazy initialization of gspread client"""
        if self._client is None:
            try:
                from pathlib import Path
                self._client = gspread.service_account(filename=Path(self.credentials_file))
                logger.info("Successfully authenticated with Google Sheets API (async)")
            except Exception as e:
                logger.error(f"Failed to authenticate: {e}")
                raise
        return self._client
    
    async def get_data(self) -> List[Dict[str, str]]:
        """
        Asynchronously get data from Google Sheets.
        
        Returns:
            List[Dict[str, str]]: List of dictionaries where keys are headers from first row
        
        Raises:
            Exception: On errors accessing spreadsheet
        """
        try:
            # Execute synchronous operation in a separate thread
            # to not block the event loop
            data = await asyncio.to_thread(self._fetch_data_sync)
            logger.info(f"Successfully fetched {len(data)} rows (async)")
            return data
        except Exception as e:
            logger.error(f"Error fetching data (async): {e}")
            raise
    
    def _fetch_data_sync(self) -> List[Dict[str, str]]:
        """
        Synchronous function for getting data.
        Runs in a separate thread via asyncio.to_thread().
        
        Returns:
            List[Dict[str, str]]: List of dictionaries with data
        """
        client = self._get_client()
        spreadsheet = client.open_by_key(self.spreadsheet_id)
        worksheet = spreadsheet.worksheet(self.sheet_name)
        
        # Get all values
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) < 1:
            return []
        
        # First row - headers
        headers = all_values[0]
        data_rows = all_values[1:]
        
        if not headers:
            return []
        
        # Convert to list of dictionaries
        result = []
        for row in data_rows:
            # Pad short rows with empty values
            padded_row = row + [''] * (len(headers) - len(row))
            row_dict = dict(zip(headers, padded_row))
            result.append(row_dict)
        
        return result
    
    @lru_cache(maxsize=128)
    async def get_data_cached(self, cache_key: str) -> List[Dict[str, str]]:
        """
        Cached version of get_data() to reduce API requests.
        
        Args:
            cache_key: Unique cache key (e.g., timestamp with rounding)
        
        Returns:
            List[Dict[str, str]]: Cached or fresh data
        """
        return await self.get_data()
