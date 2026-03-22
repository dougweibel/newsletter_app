from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QTextEdit,
)

from src.models.member import Member
from src.storage.event_repository import EventRepository
from src.storage.member_event_repository import MemberEventRepository


class MemberDialog(QDialog):
    def __init__(self, parent=None, member: Member | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Member" if member is None else "Edit Member")
        self.resize(520, 520)

        self.original_member = member
        self.event_repository = EventRepository()
        self.member_event_repository = MemberEventRepository()

        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        self.associated_events_list = QListWidget()
        self.associated_events_list.setMinimumHeight(180)

        if member is not None:
            self.first_name_edit.setText(member.first_name)
            self.last_name_edit.setText(member.last_name)
            self.email_edit.setText(member.email)
            self.notes_edit.setPlainText(member.notes)

        layout = QFormLayout(self)
        layout.addRow("First Name", self.first_name_edit)
        layout.addRow("Last Name", self.last_name_edit)
        layout.addRow("Email", self.email_edit)
        layout.addRow("Notes", self.notes_edit)
        layout.addRow(QLabel("Associated Events"), self.associated_events_list)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

        self._load_event_choices()

    def _load_event_choices(self) -> None:
        selected_event_ids: set[int] = set()
        if self.original_member is not None and self.original_member.id is not None:
            selected_event_ids = set(
                self.member_event_repository.list_event_ids_for_member(self.original_member.id)
            )

        for event_record in self.event_repository.list_events():
            item = QListWidgetItem(self._format_event_label(event_record))
            item.setData(Qt.UserRole, event_record.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(
                Qt.Checked if event_record.id in selected_event_ids else Qt.Unchecked
            )
            item.setToolTip(event_record.description or event_record.other_info or "")
            self.associated_events_list.addItem(item)

    def selected_event_ids(self) -> list[int]:
        event_ids: list[int] = []
        for index in range(self.associated_events_list.count()):
            item = self.associated_events_list.item(index)
            event_id = item.data(Qt.UserRole)
            if event_id is not None and item.checkState() == Qt.Checked:
                event_ids.append(int(event_id))
        return event_ids

    def validate_and_accept(self) -> None:
        first_name = self.first_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        email = self.email_edit.text().strip()

        if not first_name:
            QMessageBox.warning(self, "Validation Error", "First name is required.")
            return

        if not last_name:
            QMessageBox.warning(self, "Validation Error", "Last name is required.")
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
            first_name=self.first_name_edit.text().strip(),
            last_name=self.last_name_edit.text().strip(),
            email=self.email_edit.text().strip(),
            notes=self.notes_edit.toPlainText().strip(),
        )

    @staticmethod
    def _format_event_label(event_record) -> str:
        parts = [event_record.title]
        if event_record.event_kind == "one_time" and event_record.one_time_date:
            parts.append(f"({event_record.one_time_date})")
        elif event_record.event_kind == "recurring":
            parts.append(f"[{event_record.recurrence_frequency or 'recurring'}]")
        if event_record.location:
            parts.append(f"- {event_record.location}")
        return " ".join(parts)
