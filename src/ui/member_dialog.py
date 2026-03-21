from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
)

from src.models.member import Member


class MemberDialog(QDialog):
    def __init__(self, parent=None, member: Member | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Member" if member is None else "Edit Member")
        self.resize(420, 260)

        self.original_member = member

        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.notes_edit = QTextEdit()

        if member is not None:
            self.name_edit.setText(member.name)
            self.email_edit.setText(member.email)
            self.notes_edit.setPlainText(member.notes)

        layout = QFormLayout(self)
        layout.addRow("Name", self.name_edit)
        layout.addRow("Email", self.email_edit)
        layout.addRow("Notes", self.notes_edit)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def validate_and_accept(self) -> None:
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return

        if not email:
            QMessageBox.warning(self, "Validation Error", "Email is required.")
            return

        if "@" not in email:
            QMessageBox.warning(self, "Validation Error", "Email must contain '@'.")
            return

        self.accept()

    def get_member_data(self) -> Member:
        member_id = None if self.original_member is None else self.original_member.id

        return Member(
            id=member_id,
            name=self.name_edit.text().strip(),
            email=self.email_edit.text().strip(),
            notes=self.notes_edit.toPlainText().strip(),
        )