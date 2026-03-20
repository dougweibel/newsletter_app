from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "newsletter_app.sqlite3"

def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database() -> None:
    schema = PROJECT_ROOT / "src" / "storage" / "schema.sql"
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema.read_text(encoding="utf-8"))
        conn.commit()
