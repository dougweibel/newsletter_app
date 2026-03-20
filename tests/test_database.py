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
