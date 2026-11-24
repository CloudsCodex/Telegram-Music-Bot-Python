# Developer by : Mr_Manas_Op
"""Database package exposing a single shared ``db`` instance."""

from config import get_config
from database.db import Database

db = Database(get_config().database_path)

__all__ = ["db", "Database"]
