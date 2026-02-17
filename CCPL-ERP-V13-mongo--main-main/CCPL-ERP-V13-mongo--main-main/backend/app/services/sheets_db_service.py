"""Google Sheets Database Service — replaces MongoDB/Beanie for the entire ERP.
Uses in-memory cache for reads, write-through for mutations.
"""
import os
import re
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

from ..config import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials as OAuthCredentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    OAUTH_FLOW_AVAILABLE = True
except ImportError:
    OAUTH_FLOW_AVAILABLE = False

logger = logging.getLogger(__name__)


def _retry_on_rate_limit(func, max_retries=3):
    """Execute a Google API call with retry on 429 rate limit errors."""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except HttpError as e:
            if e.resp.status == 429 and attempt < max_retries:
                wait = 10 * (attempt + 1)  # 10s, 20s, 30s
                logger.warning(f"Rate limit hit, waiting {wait}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise


class SheetsDBService:
    """Core database engine backed by Google Sheets with in-memory cache."""

    def __init__(self, spreadsheet_id: str, credentials_path: str):
        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = credentials_path
        self.service = None
        self.demo_mode = False
        self.error_message = None
        self._api_key_mode = False  # True = read-only via API key

        # In-memory cache: tab_name -> list of row dicts
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        # Headers per tab
        self._headers: Dict[str, List[str]] = {}
        # Row number mapping: tab_name -> {_id -> sheet_row_number}
        self._row_map: Dict[str, Dict[str, int]] = {}

    def _init_google(self):
        """Initialize Google Sheets API connection.
        Priority: saved token > service account > API key.
        Skips interactive OAuth flows during server startup.
        """
        if not self.spreadsheet_id:
            self.demo_mode = True
            self.error_message = "Spreadsheet ID not configured."
            return

        if not GOOGLE_AVAILABLE:
            self.demo_mode = True
            self.error_message = "Google API libraries not installed."
            return

        # Resolve paths relative to backend directory
        cred_path = self.credentials_path
        if not os.path.isabs(cred_path):
            cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), cred_path)

        token_path = os.path.join(os.path.dirname(cred_path), 'token.json')
        api_key = getattr(settings, 'GOOGLE_API_KEY', '') or ''

        creds = None

        # 1. Try loading saved OAuth2 token
        if os.path.exists(token_path):
            try:
                creds = OAuthCredentials.from_authorized_user_file(token_path, SCOPES)
                logger.info("Loaded saved OAuth2 token")
                if creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        with open(token_path, 'w') as f:
                            f.write(creds.to_json())
                        logger.info("Refreshed OAuth2 token")
                    except Exception as e:
                        logger.warning(f"Token refresh failed: {e}")
                        creds = None
            except Exception as e:
                logger.warning(f"Failed to load saved token: {e}")
                creds = None

        # 2. Try service account key (non-interactive)
        if not creds or not creds.valid:
            if os.path.exists(cred_path):
                try:
                    with open(cred_path, 'r') as f:
                        cred_data = json.load(f)
                    if cred_data.get('type') == 'service_account':
                        creds = service_account.Credentials.from_service_account_file(
                            cred_path, scopes=SCOPES
                        )
                        logger.info("Using service account credentials")
                except Exception as e:
                    logger.warning(f"Service account auth failed: {e}")

        # 3. Use OAuth/service account creds if available
        if creds and (not hasattr(creds, 'valid') or creds.valid):
            try:
                self.service = build('sheets', 'v4', credentials=creds)
                logger.info("Google Sheets API initialized with full read/write access")
                return
            except Exception as e:
                logger.warning(f"Failed to build service with credentials: {e}")

        # 4. Use API key
        if api_key:
            try:
                self.service = build('sheets', 'v4', developerKey=api_key)
                self._api_key_mode = True
                logger.info("Google Sheets API initialized with API key")
                return
            except Exception as e:
                logger.warning(f"API key init failed: {e}")

        # 5. Nothing worked
        self.demo_mode = True
        self.error_message = "No valid Google credentials found. Set GOOGLE_API_KEY in .env or provide a service account key."

    def _sheets(self):
        """Get spreadsheets API resource."""
        if not self.service:
            raise Exception("Google Sheets not initialized")
        return self.service.spreadsheets()

    async def initialize(self):
        """Initialize the service: connect to Google, load all _-prefixed tabs."""
        self._init_google()

        if self.demo_mode:
            logger.warning(f"SheetsDB running in DEMO MODE: {self.error_message}")
            return

        try:
            # Get all sheet tabs
            meta = self._sheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_names = [s['properties']['title'] for s in meta.get('sheets', [])]

            # Load all _-prefixed tabs into cache
            for name in sheet_names:
                if name.startswith('_'):
                    self._load_tab(name)

            logger.info(f"SheetsDB loaded {len(self._cache)} tabs into cache")
        except Exception as e:
            logger.error(f"SheetsDB initialization error: {e}")
            raise

    def _load_tab(self, tab_name: str):
        """Load a single tab into the cache."""
        try:
            result = self._sheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{tab_name}'!A:ZZ"
            ).execute()
            rows = result.get('values', [])

            if not rows:
                self._cache[tab_name] = []
                self._headers[tab_name] = []
                self._row_map[tab_name] = {}
                return

            headers = rows[0]
            self._headers[tab_name] = headers
            self._cache[tab_name] = []
            self._row_map[tab_name] = {}

            for i, row in enumerate(rows[1:], start=2):  # row 2 in sheet
                row_dict = {}
                for j, header in enumerate(headers):
                    row_dict[header] = row[j] if j < len(row) else ''
                self._cache[tab_name].append(row_dict)
                doc_id = row_dict.get('_id', '')
                if doc_id:
                    self._row_map[tab_name][doc_id] = i

        except HttpError as e:
            if e.resp.status == 400:
                # Tab might not exist yet
                self._cache[tab_name] = []
                self._headers[tab_name] = []
                self._row_map[tab_name] = {}
            else:
                raise

    def ensure_tab(self, tab_name: str, headers: List[str]):
        """Create tab if it doesn't exist and set headers."""
        if self.demo_mode:
            # In demo mode, just init empty cache
            if tab_name not in self._cache:
                self._cache[tab_name] = []
                self._headers[tab_name] = headers
                self._row_map[tab_name] = {}
            return

        if tab_name in self._headers and self._headers[tab_name]:
            return  # Already exists with headers

        try:
            # Try to create the sheet tab
            _retry_on_rate_limit(lambda: self._sheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': [{'addSheet': {'properties': {'title': tab_name}}}]}
            ).execute())
            logger.info(f"Created sheet tab: {tab_name}")
        except HttpError as e:
            if 'already exists' not in str(e):
                raise
            # Tab exists but wasn't loaded (maybe empty)

        # Write headers to row 1
        try:
            _retry_on_rate_limit(lambda: self._sheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{tab_name}'!A1",
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute())
        except Exception as e:
            logger.warning(f"Could not write headers for {tab_name}: {e}")

        self._headers[tab_name] = headers
        if tab_name not in self._cache:
            self._cache[tab_name] = []
            self._row_map[tab_name] = {}

    # ==================== READ OPERATIONS ====================

    def find(self, tab_name: str, filter_fn: Optional[Callable] = None) -> List[Dict]:
        """Find all rows matching a filter function. Returns list of dicts."""
        rows = self._cache.get(tab_name, [])
        if filter_fn is None:
            return list(rows)  # Return copy
        return [r for r in rows if filter_fn(r)]

    def find_one(self, tab_name: str, filter_fn: Callable) -> Optional[Dict]:
        """Find first row matching filter."""
        for row in self._cache.get(tab_name, []):
            if filter_fn(row):
                return row
        return None

    def get_by_id(self, tab_name: str, doc_id: str) -> Optional[Dict]:
        """Get a row by its _id."""
        for row in self._cache.get(tab_name, []):
            if row.get('_id') == doc_id:
                return row
        return None

    def count(self, tab_name: str, filter_fn: Optional[Callable] = None) -> int:
        """Count matching rows."""
        if filter_fn is None:
            return len(self._cache.get(tab_name, []))
        return sum(1 for r in self._cache.get(tab_name, []) if filter_fn(r))

    # ==================== WRITE OPERATIONS ====================

    def insert(self, tab_name: str, row_data: Dict) -> Dict:
        """Insert a new row. Generates _id if missing."""
        if '_id' not in row_data or not row_data['_id']:
            row_data['_id'] = uuid.uuid4().hex

        # Add to cache
        if tab_name not in self._cache:
            self._cache[tab_name] = []
            self._row_map[tab_name] = {}

        self._cache[tab_name].append(row_data)
        next_row = len(self._cache[tab_name]) + 1  # +1 for header row
        self._row_map.setdefault(tab_name, {})[row_data['_id']] = next_row

        if not self.demo_mode:
            # Write to sheet
            headers = self._headers.get(tab_name, [])
            if headers:
                values = [str(row_data.get(h, '')) for h in headers]
                try:
                    _retry_on_rate_limit(lambda: self._sheets().values().append(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"'{tab_name}'!A:A",
                        valueInputOption='RAW',
                        insertDataOption='INSERT_ROWS',
                        body={'values': [values]}
                    ).execute())
                except Exception as e:
                    logger.error(f"Sheet write error ({tab_name}): {e}")

        return row_data

    def insert_many(self, tab_name: str, rows: List[Dict]) -> List[Dict]:
        """Insert multiple rows at once (batch). Returns the inserted rows."""
        if not rows:
            return []

        headers = self._headers.get(tab_name, [])
        sheet_rows = []

        for row_data in rows:
            if '_id' not in row_data or not row_data['_id']:
                row_data['_id'] = uuid.uuid4().hex

            if tab_name not in self._cache:
                self._cache[tab_name] = []
                self._row_map[tab_name] = {}

            self._cache[tab_name].append(row_data)
            next_row = len(self._cache[tab_name]) + 1
            self._row_map.setdefault(tab_name, {})[row_data['_id']] = next_row

            if headers:
                sheet_rows.append([str(row_data.get(h, '')) for h in headers])

        if not self.demo_mode and sheet_rows:
            try:
                _retry_on_rate_limit(lambda: self._sheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"'{tab_name}'!A:A",
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': sheet_rows}
                ).execute())
            except Exception as e:
                logger.error(f"Sheet batch write error ({tab_name}): {e}")

        return rows

    def update(self, tab_name: str, doc_id: str, row_data: Dict):
        """Update an existing row by _id."""
        # Update cache
        rows = self._cache.get(tab_name, [])
        for i, row in enumerate(rows):
            if row.get('_id') == doc_id:
                rows[i] = row_data
                break

        if not self.demo_mode:
            # Find sheet row number
            row_num = self._row_map.get(tab_name, {}).get(doc_id)
            if row_num:
                headers = self._headers.get(tab_name, [])
                if headers:
                    values = [str(row_data.get(h, '')) for h in headers]
                    try:
                        _retry_on_rate_limit(lambda: self._sheets().values().update(
                            spreadsheetId=self.spreadsheet_id,
                            range=f"'{tab_name}'!A{row_num}",
                            valueInputOption='RAW',
                            body={'values': [values]}
                        ).execute())
                    except Exception as e:
                        logger.error(f"Sheet update error ({tab_name}): {e}")

    def delete(self, tab_name: str, doc_id: str):
        """Delete a row by _id."""
        rows = self._cache.get(tab_name, [])
        self._cache[tab_name] = [r for r in rows if r.get('_id') != doc_id]

        if not self.demo_mode:
            row_num = self._row_map.get(tab_name, {}).get(doc_id)
            if row_num:
                # Clear the row in sheet (write empty values)
                headers = self._headers.get(tab_name, [])
                if headers:
                    empty = [''] * len(headers)
                    try:
                        _retry_on_rate_limit(lambda: self._sheets().values().update(
                            spreadsheetId=self.spreadsheet_id,
                            range=f"'{tab_name}'!A{row_num}",
                            valueInputOption='RAW',
                            body={'values': [empty]}
                        ).execute())
                    except Exception as e:
                        logger.error(f"Sheet delete error ({tab_name}): {e}")

        # Remove from row map
        self._row_map.get(tab_name, {}).pop(doc_id, None)


# Singleton
_db_instance: Optional[SheetsDBService] = None


def get_sheets_db() -> SheetsDBService:
    """Get the singleton SheetsDBService instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = SheetsDBService(
            spreadsheet_id=settings.ERP_SPREADSHEET_ID or settings.BOM_SPREADSHEET_ID,
            credentials_path=settings.ERP_CREDENTIALS_PATH if hasattr(settings, 'ERP_CREDENTIALS_PATH') else settings.BOM_GOOGLE_CREDENTIALS_PATH,
        )
    return _db_instance


async def init_sheets_db() -> SheetsDBService:
    """Initialize and return the SheetsDBService."""
    db = get_sheets_db()
    await db.initialize()
    return db
