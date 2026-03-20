from PySide6.QtWidgets import QApplication
from src.storage.database import initialize_database
from src.ui.main_window import MainWindow
import sys

def main() -> int:
    initialize_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
