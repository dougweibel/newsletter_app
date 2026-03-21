from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QHBoxLayout,
)

from src.storage.member_repository import MemberRepository
from src.ui.member_dialog import MemberDialog
from src.ui.member_list_item_widget import MemberListItemWidget


class MembersWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Members")
        self.resize(650, 460)

        self.repository = MemberRepository()

        layout = QVBoxLayout(self)

        title = QLabel("Members")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.member_list = QListWidget()
        self.member_list.setSpacing(4)
        layout.addWidget(self.member_list)

        button_row = QHBoxLayout()

        self.add_button = QPushButton("Add Member")
        self.add_button.clicked.connect(self.add_member)
        button_row.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Member")
        self.edit_button.clicked.connect(self.edit_member)
        button_row.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Member")
        self.delete_button.clicked.connect(self.delete_member)
        button_row.addWidget(self.delete_button)

        layout.addLayout(button_row)

        self.refresh_members()

    def refresh_members(self) -> None:
        self.member_list.clear()
        members = self.repository.list_members()

        if not members:
            item = QListWidgetItem("No members yet")
            self.member_list.addItem(item)
            return

        for member in members:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, member.id)
            item.setToolTip(member.notes or "")
            item.setSizeHint(QSize(0, 58 if member.notes else 34))

            widget = MemberListItemWidget(member)

            self.member_list.addItem(item)
            self.member_list.setItemWidget(item, widget)

    def get_selected_member_id(self) -> int | None:
        item = self.member_list.currentItem()
        if item is None:
            return None

        member_id = item.data(Qt.UserRole)
        if member_id is None:
            return None

        return int(member_id)

    def add_member(self) -> None:
        dialog = MemberDialog(self)
        if dialog.exec():
            member = dialog.get_member_data()
            self.repository.create_member(member)
            self.refresh_members()
            QMessageBox.information(self, "Saved", "Member added successfully.")

    def edit_member(self) -> None:
        member_id = self.get_selected_member_id()
        if member_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a member to edit.")
            return

        member = self.repository.get_member(member_id)
        if member is None:
            QMessageBox.warning(self, "Not Found", "Selected member could not be found.")
            self.refresh_members()
            return

        dialog = MemberDialog(self, member)
        if dialog.exec():
            updated_member = dialog.get_member_data()
            self.repository.update_member(updated_member)
            self.refresh_members()
            QMessageBox.information(self, "Saved", "Member updated successfully.")

    def delete_member(self) -> None:
        member_id = self.get_selected_member_id()
        if member_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a member to delete.")
            return

        member = self.repository.get_member(member_id)
        if member is None:
            QMessageBox.warning(self, "Not Found", "Selected member could not be found.")
            self.refresh_members()
            return

        response = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete member '{member.full_name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if response == QMessageBox.Yes:
            self.repository.delete_member(member_id)
            self.refresh_members()
            QMessageBox.information(self, "Deleted", "Member deleted successfully.")