from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.models.event import Event
from src.services.solicitation_service import SolicitationService
from src.storage.event_repository import EventRepository
from src.storage.member_event_repository import MemberEventRepository


class SolicitationWidget(QWidget):
    STATUS_LABELS = {
        "not_started": "Not started",
        "draft_ready": "Draft ready",
        "sent": "Sent",
        "responded": "Responded",
        "closed": "Closed",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Solicitation Workflow")
        self.resize(1100, 700)

        self.event_repository = EventRepository()
        self.member_event_repository = MemberEventRepository()
        self.current_event: Event | None = None

        root = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        root.addLayout(left_panel, 2)

        title = QLabel("Solicitation Workflow")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_panel.addWidget(title)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Needs attention",
            "All active events",
            "Sent or later",
            "All events",
        ])
        self.filter_combo.currentIndexChanged.connect(self.refresh_events)
        left_panel.addWidget(self.filter_combo)

        self.event_list = QListWidget()
        self.event_list.currentItemChanged.connect(self.load_selected_event)
        left_panel.addWidget(self.event_list)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_events)
        left_panel.addWidget(self.refresh_button)

        right_panel = QVBoxLayout()
        root.addLayout(right_panel, 3)

        self.summary_label = QLabel("Select an event to begin.")
        self.summary_label.setWordWrap(True)
        right_panel.addWidget(self.summary_label)

        details_form = QFormLayout()
        self.members_label = QLabel("")
        self.members_label.setWordWrap(True)
        self.timeline_label = QLabel("")
        self.timeline_label.setWordWrap(True)
        self.status_combo = QComboBox()
        self.status_combo.addItems(list(self.STATUS_LABELS.keys()))
        self.status_combo.currentTextChanged.connect(self._status_combo_changed)
        self.generated_at_label = QLabel("")
        self.sent_at_label = QLabel("")
        details_form.addRow("Associated Members", self.members_label)
        details_form.addRow("Suggested Timing", self.timeline_label)
        details_form.addRow("Workflow Status", self.status_combo)
        details_form.addRow("Last Draft Generated", self.generated_at_label)
        details_form.addRow("Last Marked Sent", self.sent_at_label)
        right_panel.addLayout(details_form)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Workflow notes about outreach, responses, or follow-up.")
        right_panel.addWidget(QLabel("Workflow Notes"))
        right_panel.addWidget(self.notes_edit, 1)

        self.subject_edit = QTextEdit()
        self.subject_edit.setMaximumHeight(70)
        right_panel.addWidget(QLabel("Solicitation Subject"))
        right_panel.addWidget(self.subject_edit)

        self.body_edit = QTextEdit()
        right_panel.addWidget(QLabel("Solicitation Body"))
        right_panel.addWidget(self.body_edit, 2)

        button_row = QHBoxLayout()
        self.generate_button = QPushButton("Generate Draft")
        self.generate_button.clicked.connect(self.generate_draft)
        button_row.addWidget(self.generate_button)

        self.save_button = QPushButton("Save Notes / Status")
        self.save_button.clicked.connect(self.save_workflow_state)
        button_row.addWidget(self.save_button)

        self.mark_draft_ready_button = QPushButton("Mark Draft Ready")
        self.mark_draft_ready_button.clicked.connect(self.mark_draft_ready)
        button_row.addWidget(self.mark_draft_ready_button)

        self.mark_sent_button = QPushButton("Mark Sent")
        self.mark_sent_button.clicked.connect(self.mark_sent)
        button_row.addWidget(self.mark_sent_button)

        self.mark_responded_button = QPushButton("Mark Response Received")
        self.mark_responded_button.clicked.connect(self.mark_responded)
        button_row.addWidget(self.mark_responded_button)

        self.reset_button = QPushButton("Reset Workflow")
        self.reset_button.clicked.connect(self.reset_workflow)
        button_row.addWidget(self.reset_button)

        right_panel.addLayout(button_row)

        self.refresh_events()

    def refresh_events(self) -> None:
        selected_event_id = self.current_event.id if self.current_event is not None else None
        self.event_list.clear()
        events = self._filtered_events(self.event_repository.list_events())

        if not events:
            self.event_list.addItem(QListWidgetItem("No events match this filter"))
            self.current_event = None
            self._clear_details()
            return

        for event in events:
            members = self.member_event_repository.list_members_for_event(event.id) if event.id else []
            due_text = self._due_text(event)
            member_count_text = f"{len(members)} member{'s' if len(members) != 1 else ''}"
            label = (
                f"{event.title} | {self.STATUS_LABELS.get(event.solicitation_status, event.solicitation_status)}"
                f" | {member_count_text} | {due_text}"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, event.id)
            self.event_list.addItem(item)

        if selected_event_id is not None and self._reselect_event(selected_event_id):
            return
        self.event_list.setCurrentRow(0)

    def load_selected_event(self) -> None:
        item = self.event_list.currentItem()
        if item is None:
            self.current_event = None
            self._clear_details()
            return

        event_id = item.data(Qt.UserRole)
        if event_id is None:
            self.current_event = None
            self._clear_details()
            return

        event = self.event_repository.get_event(int(event_id))
        if event is None:
            self.current_event = None
            self._clear_details()
            return

        self.current_event = event
        self._populate_from_event(event, clear_generated_text=True)

    def generate_draft(self) -> None:
        if self.current_event is None or self.current_event.id is None:
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return

        members = self.member_event_repository.list_members_for_event(self.current_event.id)
        subject = SolicitationService.build_subject(self.current_event)
        body = SolicitationService.build_body(self.current_event, members)
        self.subject_edit.setPlainText(subject)
        self.body_edit.setPlainText(body)

        self.current_event.solicitation_status = SolicitationService.recommended_status_after_generate()
        self.current_event.solicitation_last_generated_at = SolicitationService.now_timestamp()
        self.status_combo.setCurrentText(self.current_event.solicitation_status)
        self.generated_at_label.setText(self.current_event.solicitation_last_generated_at)
        self._persist_current_event(
            show_message=True,
            message="Solicitation draft generated and workflow state saved.",
            preserve_generated_text=True,
        )

    def save_workflow_state(self) -> None:
        if self.current_event is None:
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return
        self._persist_current_event(show_message=True, message="Workflow state saved.", preserve_generated_text=True)

    def mark_draft_ready(self) -> None:
        if self.current_event is None:
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return

        self.status_combo.setCurrentText("draft_ready")
        if not self.current_event.solicitation_last_generated_at:
            self.current_event.solicitation_last_generated_at = SolicitationService.now_timestamp()
            self.generated_at_label.setText(self.current_event.solicitation_last_generated_at)
        self._persist_current_event(show_message=True, message="Event marked as draft ready.", preserve_generated_text=True)

    def mark_sent(self) -> None:
        if self.current_event is None:
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return

        self.status_combo.setCurrentText("sent")
        self.current_event.solicitation_last_sent_at = SolicitationService.now_timestamp()
        self.sent_at_label.setText(self.current_event.solicitation_last_sent_at)
        self._persist_current_event(show_message=True, message="Event marked as sent.", preserve_generated_text=True)

    def mark_responded(self) -> None:
        if self.current_event is None:
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return

        self.status_combo.setCurrentText("responded")
        self._persist_current_event(show_message=True, message="Event marked as responded.", preserve_generated_text=True)

    def reset_workflow(self) -> None:
        if self.current_event is None:
            QMessageBox.warning(self, "No Event", "Please select an event first.")
            return

        answer = QMessageBox.question(
            self,
            "Reset Workflow",
            "Reset this event's solicitation workflow to Not started and clear generated/sent timestamps?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.status_combo.setCurrentText("not_started")
        self.current_event.solicitation_last_generated_at = ""
        self.current_event.solicitation_last_sent_at = ""
        self.generated_at_label.setText("—")
        self.sent_at_label.setText("—")
        self._persist_current_event(show_message=True, message="Solicitation workflow reset.", preserve_generated_text=True)

    def _persist_current_event(
        self,
        *,
        show_message: bool,
        message: str,
        preserve_generated_text: bool,
    ) -> None:
        if self.current_event is None:
            return

        subject_text = self.subject_edit.toPlainText()
        body_text = self.body_edit.toPlainText()

        self.current_event.solicitation_status = self.status_combo.currentText()
        self.current_event.solicitation_notes = self.notes_edit.toPlainText().strip()
        self._normalize_workflow_fields_for_status(self.current_event)
        self.event_repository.update_event(self.current_event)

        event_id = self.current_event.id
        self.refresh_events()
        reloaded_event = self.event_repository.get_event(event_id) if event_id is not None else None
        if reloaded_event is not None:
            self.current_event = reloaded_event
            self._populate_from_event(reloaded_event, clear_generated_text=not preserve_generated_text)
            if preserve_generated_text:
                self.subject_edit.setPlainText(subject_text)
                self.body_edit.setPlainText(body_text)

        if show_message:
            QMessageBox.information(self, "Saved", message)

    def _populate_from_event(self, event: Event, *, clear_generated_text: bool) -> None:
        members = self.member_event_repository.list_members_for_event(event.id) if event.id else []
        due_text = self._due_text(event)
        self.summary_label.setText(
            f"{event.title}\nEvent status: {event.status}\nSolicitation status: {self.STATUS_LABELS.get(event.solicitation_status, event.solicitation_status)}"
        )
        self.members_label.setText(
            ", ".join(f"{member.full_name} <{member.email}>" for member in members) or "No associated members"
        )
        self.timeline_label.setText(due_text)
        self.status_combo.setCurrentText(event.solicitation_status)
        self.generated_at_label.setText(event.solicitation_last_generated_at or "—")
        self.sent_at_label.setText(event.solicitation_last_sent_at or "—")
        self.notes_edit.setPlainText(event.solicitation_notes)
        if clear_generated_text:
            self.subject_edit.setPlainText("")
            self.body_edit.setPlainText("")

    def _normalize_workflow_fields_for_status(self, event: Event) -> None:
        status = event.solicitation_status
        if status == "not_started":
            event.solicitation_last_generated_at = ""
            event.solicitation_last_sent_at = ""
        elif status == "draft_ready":
            event.solicitation_last_sent_at = ""
            if not event.solicitation_last_generated_at:
                event.solicitation_last_generated_at = SolicitationService.now_timestamp()
        elif status == "sent":
            if not event.solicitation_last_generated_at:
                event.solicitation_last_generated_at = SolicitationService.now_timestamp()
            if not event.solicitation_last_sent_at:
                event.solicitation_last_sent_at = SolicitationService.now_timestamp()
        elif status in {"responded", "closed"}:
            if not event.solicitation_last_generated_at:
                event.solicitation_last_generated_at = SolicitationService.now_timestamp()
            if not event.solicitation_last_sent_at:
                event.solicitation_last_sent_at = SolicitationService.now_timestamp()

    def _reselect_event(self, event_id: int | None) -> bool:
        if event_id is None:
            return False
        for index in range(self.event_list.count()):
            item = self.event_list.item(index)
            if item.data(Qt.UserRole) == event_id:
                self.event_list.setCurrentRow(index)
                return True
        return False

    def _clear_details(self) -> None:
        self.summary_label.setText("Select an event to begin.")
        self.members_label.setText("")
        self.timeline_label.setText("")
        self.generated_at_label.setText("")
        self.sent_at_label.setText("")
        self.notes_edit.setPlainText("")
        self.subject_edit.setPlainText("")
        self.body_edit.setPlainText("")

    def _filtered_events(self, events: list[Event]) -> list[Event]:
        choice = self.filter_combo.currentText()
        if choice == "All events":
            return events
        if choice == "All active events":
            return [event for event in events if event.status == "active"]
        if choice == "Sent or later":
            return [event for event in events if event.solicitation_status in {"sent", "responded", "closed"}]

        today = date.today()
        return [
            event
            for event in events
            if event.status == "active"
            and event.solicitation_status in {"not_started", "draft_ready"}
            and (
                (due_date := SolicitationService.estimated_solicitation_due_date(event, today=today)) is not None
                and due_date <= today
            )
        ]

    def _due_text(self, event: Event) -> str:
        due_date = SolicitationService.estimated_solicitation_due_date(event)
        if due_date is None:
            return "No calculated due date"
        today = date.today()
        if due_date < today:
            return f"Due since {due_date.isoformat()}"
        if due_date == today:
            return f"Due today ({due_date.isoformat()})"
        return f"Due {due_date.isoformat()}"

    def _status_combo_changed(self, value: str) -> None:
        if self.current_event is not None:
            self.current_event.solicitation_status = value
