from PySide6.QtCore import Qt
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
from src.ui.event_dialog import EventDialog


class EventsWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Events")
        self.resize(760, 500)

        self.repository = EventRepository()

        layout = QVBoxLayout(self)

        title = QLabel("Events")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.event_list = QListWidget()
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

        for event in events:
            summary_parts = [event.title]
            if event.event_kind == "one_time" and event.one_time_date:
                summary_parts.append(f"({event.one_time_date})")
            elif event.event_kind == "recurring":
                frequency = event.recurrence_frequency or "recurring"
                summary_parts.append(f"[{frequency}]")
            if event.location:
                summary_parts.append(f"- {event.location}")

            item = QListWidgetItem(" ".join(summary_parts))
            item.setData(Qt.UserRole, event.id)
            item.setToolTip(event.description or event.other_info or "")
            self.event_list.addItem(item)

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
            event = dialog.get_event_data()
            self.repository.create_event(event)
            self.refresh_events()
            QMessageBox.information(self, "Saved", "Event added successfully.")

    def edit_event(self) -> None:
        event_id = self.get_selected_event_id()
        if event_id is None:
            QMessageBox.warning(self, "No Selection", "Please select an event to edit.")
            return

        event = self.repository.get_event(event_id)
        if event is None:
            QMessageBox.warning(self, "Not Found", "Selected event could not be found.")
            self.refresh_events()
            return

        dialog = EventDialog(self, event)
        if dialog.exec():
            updated_event = dialog.get_event_data()
            self.repository.update_event(updated_event)
            self.refresh_events()
            QMessageBox.information(self, "Saved", "Event updated successfully.")

    def delete_event(self) -> None:
        event_id = self.get_selected_event_id()
        if event_id is None:
            QMessageBox.warning(self, "No Selection", "Please select an event to delete.")
            return

        event = self.repository.get_event(event_id)
        if event is None:
            QMessageBox.warning(self, "Not Found", "Selected event could not be found.")
            self.refresh_events()
            return

        response = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete event '{event.title}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if response == QMessageBox.Yes:
            self.repository.delete_event(event_id)
            self.refresh_events()
            QMessageBox.information(self, "Deleted", "Event deleted successfully.")
