import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Render provides DATABASE_URL automatically for PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'postforge.db'}"
