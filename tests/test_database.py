from src.storage.database import initialize_database, get_connection


def test_database_initializes() -> None:
    initialize_database()
    with get_connection() as conn:
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ).fetchall()
        }

    assert "members" in tables
    assert "events" in tables
    assert "member_events" in tables


def test_database_adds_solicitation_columns() -> None:
    initialize_database()
    with get_connection() as conn:
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(events)").fetchall()
        }

    assert "solicitation_status" in columns
    assert "solicitation_last_generated_at" in columns
    assert "solicitation_last_sent_at" in columns
    assert "solicitation_notes" in columns
    assert "solicitation_subject" in columns
    assert "solicitation_body" in columns
