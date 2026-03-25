from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def isolated_test_database(tmp_path, monkeypatch):
    from src.storage import database

    test_data_dir = tmp_path / "data"
    test_db_path = test_data_dir / "newsletter_app_test.sqlite3"
    monkeypatch.setattr(database, "DATA_DIR", test_data_dir)
    monkeypatch.setattr(database, "DB_PATH", test_db_path)
