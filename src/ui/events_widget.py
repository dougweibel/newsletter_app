from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget

class EventsWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Events")
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Events screen placeholder"))

        self.event_list = QListWidget()
        self.event_list.addItem("No events loaded yet")
        layout.addWidget(self.event_list)

        self.add_button = QPushButton("Add Event")
        layout.addWidget(self.add_button)
