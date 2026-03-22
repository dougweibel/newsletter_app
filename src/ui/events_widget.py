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

from src.storage.event_repository import EventRepository
from src.storage.member_event_repository import MemberEventRepository
from src.ui.event_dialog import EventDialog
from src.ui.event_list_item_widget import EventListItemWidget


class EventsWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Events")
        self.resize(800, 540)

        self.repository = EventRepository()
        self.member_event_repository = MemberEventRepository()

        layout = QVBoxLayout(self)

        title = QLabel("Events")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.event_list = QListWidget()
        self.event_list.setSpacing(4)
        layout.addWidget(self.event_list)

        button_row = QHBoxLayout()

        self.add_button = QPushButton("Add Event")
        self.add_button.clicked.connect(self.add_event)
        button_row.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Event")
        self.edit_button.clicked.connect(self.edit_event)
        button_row.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Event")
        self.delete_button.clicked.connect(self.delete_event)
        button_row.addWidget(self.delete_button)

        layout.addLayout(button_row)

        self.refresh_events()

    def refresh_events(self) -> None:
        self.event_list.clear()
        events = self.repository.list_events()

        if not events:
            self.event_list.addItem(QListWidgetItem("No events yet"))
            return

        for event_record in events:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, event_record.id)
            item.setToolTip(event_record.description or event_record.other_info or "")

            associated_member_names = []
            if event_record.id is not None:
                associated_member_names = self.member_event_repository.list_member_names_for_event(event_record.id)

            line_count = 1
            if associated_member_names:
                line_count += 1
            if event_record.description or event_record.other_info:
                line_count += 1
            item.setSizeHint(QSize(0, 34 + (line_count - 1) * 24))

            widget = EventListItemWidget(event_record, associated_member_names)
            self.event_list.addItem(item)
            self.event_list.setItemWidget(item, widget)

    def get_selected_event_id(self) -> int | None:
        item = self.event_list.currentItem()
        if item is None:
            return None

        event_id = item.data(Qt.UserRole)
        if event_id is None:
            return None

        return int(event_id)

    def add_event(self) -> None:
        dialog = EventDialog(self)
        if dialog.exec():
            event_record = dialog.get_event_data()
            event_id = self.repository.create_event(event_record)
            self.member_event_repository.replace_members_for_event(
                event_id, dialog.selected_member_ids()
            )
            self.refresh_events()
            QMessageBox.information(self, "Saved", "Event added successfully.")

    def edit_event(self) -> None:
        event_id = self.get_selected_event_id()
        if event_id is None:
            QMessageBox.warning(self, "No Selection", "Please select an event to edit.")
            return

        event_record = self.repository.get_event(event_id)
        if event_record is None:
            QMessageBox.warning(self, "Not Found", "Selected event could not be found.")
            self.refresh_events()
            return

        dialog = EventDialog(self, event_record)
        if dialog.exec():
            updated_event = dialog.get_event_data()
            self.repository.update_event(updated_event)
            self.member_event_repository.replace_members_for_event(
                event_id, dialog.selected_member_ids()
            )
            self.refresh_events()
            QMessageBox.information(self, "Saved", "Event updated successfully.")

    def delete_event(self) -> None:
        event_id = self.get_selected_event_id()
        if event_id is None:
            QMessageBox.warning(self, "No Selection", "Please select an event to delete.")
            return

        event_record = self.repository.get_event(event_id)
        if event_record is None:
            QMessageBox.warning(self, "Not Found", "Selected event could not be found.")
            self.refresh_events()
            return

        response = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete event '{event_record.title}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if response == QMessageBox.Yes:
            self.repository.delete_event(event_id)
            self.refresh_events()
            QMessageBox.information(self, "Deleted", "Event deleted successfully.")
