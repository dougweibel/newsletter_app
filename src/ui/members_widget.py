from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget

class MembersWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Members")
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Members screen placeholder"))

        self.member_list = QListWidget()
        self.member_list.addItem("No members loaded yet")
        layout.addWidget(self.member_list)

        self.add_button = QPushButton("Add Member")
        layout.addWidget(self.add_button)
