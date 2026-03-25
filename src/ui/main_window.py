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
from src.ui.solicitation_widget import SolicitationWidget
from src.ui.newsletter_widget import NewsletterWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Newsletter App")
        self.resize(900, 600)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Newsletter Information Gathering App")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        subtitle = QLabel("Members, events, and solicitation workflow")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)

        members_button = QPushButton("Members")
        members_button.clicked.connect(self.show_members)
        layout.addWidget(members_button)

        events_button = QPushButton("Events")
        events_button.clicked.connect(self.show_events)
        layout.addWidget(events_button)

        solicitation_button = QPushButton("Solicitation Workflow")
        solicitation_button.clicked.connect(self.show_solicitation)
        layout.addWidget(solicitation_button)

        newsletter_button = QPushButton("Generate Newsletter File")
        newsletter_button.clicked.connect(self.show_newsletter)
        layout.addWidget(newsletter_button)

        layout.addStretch()
        self.setCentralWidget(central)

        self.apply_styles()

    def apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #e9eef2;
            }

            QWidget {
                background-color: #e9eef2;
                color: #1f2933;
                font-size: 14px;
            }

            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #102a43;
                margin-bottom: 4px;
            }

            QLabel#subtitleLabel {
                color: "blue";
                margin-bottom: 12px;
            }

            QPushButton {
                background-color: #486581;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 14px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #334e68;
            }

            QPushButton:pressed {
                background-color: #243b53;
            }
            """
        )

    def show_members(self) -> None:
        self.members_window = MembersWidget()
        self.members_window.show()

    def show_events(self) -> None:
        self.events_window = EventsWidget()
        self.events_window.show()

    def show_solicitation(self) -> None:
        self.solicitation_window = SolicitationWidget()
        self.solicitation_window.show()

    def show_newsletter(self) -> None:
        self.newsletter_window = NewsletterWidget()
        self.newsletter_window.show()
