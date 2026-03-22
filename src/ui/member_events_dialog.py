from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from src.models.member import Member
from src.storage.event_repository import EventRepository
from src.storage.member_event_repository import MemberEventRepository


class MemberEventsDialog(QDialog):
    def __init__(self, parent=None, member: Member | None = None) -> None:
        super().__init__(parent)
        if member is None or member.id is None:
            raise ValueError("Member with id is required to edit event associations.")

        self.member = member
        self.event_repository = EventRepository()
        self.member_event_repository = MemberEventRepository()

        self.setWindowTitle(f"Associated Events - {member.full_name}")
        self.resize(560, 460)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Select the events associated with {member.full_name}."))

        self.events_list = QListWidget()
        layout.addWidget(self.events_list)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self._load_events()

    def _load_events(self) -> None:
        selected_event_ids = set(self.member_event_repository.list_event_ids_for_member(self.member.id))
        events = self.event_repository.list_events()

        for event in events:
            label = self._format_event_label(event)
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, event.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if event.id in selected_event_ids else Qt.Unchecked)
            item.setToolTip(event.description or event.other_info or "")
            self.events_list.addItem(item)

    def selected_event_ids(self) -> list[int]:
        event_ids: list[int] = []
        for index in range(self.events_list.count()):
            item = self.events_list.item(index)
            event_id = item.data(Qt.UserRole)
            if event_id is not None and item.checkState() == Qt.Checked:
                event_ids.append(int(event_id))
        return event_ids

    @staticmethod
    def _format_event_label(event) -> str:
        parts = [event.title]
        if event.event_kind == "one_time" and event.one_time_date:
            parts.append(f"({event.one_time_date})")
        elif event.event_kind == "recurring":
            parts.append(f"[{event.recurrence_frequency or 'recurring'}]")
        if event.location:
            parts.append(f"- {event.location}")
        return " ".join(parts)
