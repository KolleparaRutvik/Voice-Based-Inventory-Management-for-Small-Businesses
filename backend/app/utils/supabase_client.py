"""Supabase / PostgreSQL client singleton with live database connectivity."""
import os
import re
import logging
from dotenv import load_dotenv
from app.utils.postgres_client import PostgresDbClient
from app.utils.local_db import LocalDbClient

load_dotenv()
logger = logging.getLogger(__name__)

_client = None
_local_db = None
_postgres_db = None


def get_supabase():
    """Get or create the database client.
    Priority 1: Live Supabase PostgreSQL database (via DATABASE_URL)
    Priority 2: Supabase Python Client (if valid JWT key)
    Priority 3: Embedded Local Database engine fallback
    """
    global _client, _postgres_db
    if _client is not None:
        return _client

    db_url = os.getenv('DATABASE_URL')
    if db_url:
        try:
            if _postgres_db is None:
                _postgres_db = PostgresDbClient(db_url)
            logger.info("Connected directly to live Supabase PostgreSQL database.")
            _client = _postgres_db
            return _client
        except Exception as e:
            logger.warning(f"Direct PostgreSQL connection failed: {e}. Trying Supabase API...")

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
    jwt_pattern = r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$"
    if url and key and re.match(jwt_pattern, key):
        try:
            from supabase import create_client
            _client = create_client(url, key)
            return _client
        except Exception as e:
            logger.warning(f"Supabase SDK connection failed: {e}")

    global _local_db
    if _local_db is None:
        _local_db = LocalDbClient()
    _client = _local_db
    return _client


def get_supabase_admin():
    """Get Supabase admin client."""
    return get_supabase()
