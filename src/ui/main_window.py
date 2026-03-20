from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)

from src.ui.members_widget import MembersWidget
from src.ui.events_widget import EventsWidget

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Newsletter App")
        self.resize(900, 600)

        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel("Newsletter Information Gathering App")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Starter shell for Milestone 1")
        subtitle.setStyleSheet("color: blue;")
        layout.addWidget(subtitle)

        members_button = QPushButton("Members")
        members_button.clicked.connect(self.show_members)
        layout.addWidget(members_button)

        events_button = QPushButton("Events")
        events_button.clicked.connect(self.show_events)
        layout.addWidget(events_button)

        solicitation_button = QPushButton("Generate Solicitation Text")
        solicitation_button.clicked.connect(self.show_placeholder)
        layout.addWidget(solicitation_button)

        newsletter_button = QPushButton("Generate Newsletter File")
        newsletter_button.clicked.connect(self.show_placeholder)
        layout.addWidget(newsletter_button)

        layout.addStretch()
        self.setCentralWidget(central)

    def show_members(self) -> None:
        self.members_window = MembersWidget()
        self.members_window.show()

    def show_events(self) -> None:
        self.events_window = EventsWidget()
        self.events_window.show()

    def show_placeholder(self) -> None:
        QMessageBox.information(
            self,
            "Coming Soon",
            "This workflow will be added in a later milestone.",
        )
