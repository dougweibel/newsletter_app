from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from src.models.event import Event
from src.storage.member_event_repository import MemberEventRepository
from src.storage.member_repository import MemberRepository


class EventMembersDialog(QDialog):
    def __init__(self, parent=None, event_record: Event | None = None) -> None:
        super().__init__(parent)
        if event_record is None or event_record.id is None:
            raise ValueError("Event with id is required to edit member associations.")

        # Do not assign to self.event; QWidget/QDialog already has an event() method.
        self.event_record = event_record
        self.member_repository = MemberRepository()
        self.member_event_repository = MemberEventRepository()

        self.setWindowTitle(f"Associated Members - {event_record.title}")
        self.resize(560, 460)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Select the members associated with '{event_record.title}'."))

        self.members_list = QListWidget()
        layout.addWidget(self.members_list)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self._load_members()

    def _load_members(self) -> None:
        selected_member_ids = set(
            self.member_event_repository.list_member_ids_for_event(self.event_record.id)
        )
        members = self.member_repository.list_members()

        for member in members:
            item = QListWidgetItem(f"{member.full_name} - {member.email}")
            item.setData(Qt.UserRole, member.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if member.id in selected_member_ids else Qt.Unchecked)
            item.setToolTip(member.notes or "")
            self.members_list.addItem(item)

    def selected_member_ids(self) -> list[int]:
        member_ids: list[int] = []
        for index in range(self.members_list.count()):
            item = self.members_list.item(index)
            member_id = item.data(Qt.UserRole)
            if member_id is not None and item.checkState() == Qt.Checked:
                member_ids.append(int(member_id))
        return member_ids
