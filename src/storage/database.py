from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "newsletter_app.sqlite3"


EVENT_COLUMN_MIGRATIONS: dict[str, str] = {
    "solicitation_status": (
        "ALTER TABLE events ADD COLUMN solicitation_status TEXT NOT NULL "
        "DEFAULT 'not_started' CHECK (solicitation_status IN ('not_started', 'draft_ready', 'sent', 'responded', 'closed'))"
    ),
    "solicitation_last_generated_at": "ALTER TABLE events ADD COLUMN solicitation_last_generated_at TEXT",
    "solicitation_last_sent_at": "ALTER TABLE events ADD COLUMN solicitation_last_sent_at TEXT",
    "solicitation_notes": "ALTER TABLE events ADD COLUMN solicitation_notes TEXT",
}


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
        _migrate_events_table(conn)
        conn.commit()


def _migrate_events_table(conn: sqlite3.Connection) -> None:
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(events)").fetchall()
    }

    for column_name, statement in EVENT_COLUMN_MIGRATIONS.items():
        if column_name not in columns:
            conn.execute(statement)
