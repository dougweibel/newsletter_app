from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
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
from src.models.member import Member
from src.services.newsletter_service import NewsletterService
from src.storage.event_repository import EventRepository
from src.storage.member_event_repository import MemberEventRepository


class NewsletterWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Generate Newsletter File")
        self.resize(1100, 740)

        self.event_repository = EventRepository()
        self.member_event_repository = MemberEventRepository()
        self.candidate_events: list[Event] = []
        self.members_by_event_id: dict[int, list[Member]] = {}

        root = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        root.addLayout(left_panel, 2)

        title = QLabel("Generate Newsletter File")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_panel.addWidget(title)

        explanation = QLabel(
            "Candidate events are ordered by newsletter likelihood: responded/closed first, then sent, then events that currently need solicitation attention."
        )
        explanation.setWordWrap(True)
        left_panel.addWidget(explanation)

        self.event_list = QListWidget()
        self.event_list.itemChanged.connect(self.update_preview)
        left_panel.addWidget(self.event_list)

        button_row = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Candidates")
        self.refresh_button.clicked.connect(self.refresh_candidates)
        button_row.addWidget(self.refresh_button)

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        button_row.addWidget(self.select_all_button)

        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all)
        button_row.addWidget(self.clear_all_button)
        left_panel.addLayout(button_row)

        self.selected_summary_label = QLabel("No events selected.")
        left_panel.addWidget(self.selected_summary_label)

        right_panel = QVBoxLayout()
        root.addLayout(right_panel, 3)

        preview_title = QLabel("Markdown Preview")
        preview_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_panel.addWidget(preview_title)

        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        right_panel.addWidget(self.preview_edit, 1)

        self.generate_button = QPushButton("Save Markdown File")
        self.generate_button.clicked.connect(self.save_markdown_file)
        right_panel.addWidget(self.generate_button)

        self.refresh_candidates()

    def refresh_candidates(self) -> None:
        selected_event_ids = set(self.selected_event_ids())
        self.event_list.blockSignals(True)
        self.event_list.clear()

        ranked_candidates = NewsletterService.rank_candidates(self.event_repository.list_events())
        self.candidate_events = [candidate.event for candidate in ranked_candidates]
        self.members_by_event_id = {
            candidate.event.id: self.member_event_repository.list_members_for_event(candidate.event.id)
            for candidate in ranked_candidates
            if candidate.event.id is not None
        }

        for candidate in ranked_candidates:
            item = QListWidgetItem(NewsletterService.event_summary_label(candidate))
            item.setData(Qt.UserRole, candidate.event.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            default_checked = candidate.priority_group <= 2
            if candidate.event.id in selected_event_ids:
                default_checked = True
            item.setCheckState(Qt.Checked if default_checked else Qt.Unchecked)
            self.event_list.addItem(item)

        self.event_list.blockSignals(False)
        self.update_preview()

    def selected_event_ids(self) -> list[int]:
        selected: list[int] = []
        for index in range(self.event_list.count()):
            item = self.event_list.item(index)
            event_id = item.data(Qt.UserRole)
            if event_id is not None and item.checkState() == Qt.Checked:
                selected.append(int(event_id))
        return selected

    def selected_events(self) -> list[Event]:
        selected_ids = set(self.selected_event_ids())
        return [event for event in self.candidate_events if event.id in selected_ids]

    def update_preview(self) -> None:
        selected_events = self.selected_events()
        markdown = NewsletterService.build_markdown(
            selected_events,
            self.members_by_event_id,
            today=date.today(),
        )
        self.preview_edit.setPlainText(markdown)
        count = len(selected_events)
        self.selected_summary_label.setText(f"{count} event{'s' if count != 1 else ''} selected.")

    def select_all(self) -> None:
        self._set_all_check_states(Qt.Checked)

    def clear_all(self) -> None:
        self._set_all_check_states(Qt.Unchecked)

    def _set_all_check_states(self, state: Qt.CheckState) -> None:
        self.event_list.blockSignals(True)
        for index in range(self.event_list.count()):
            self.event_list.item(index).setCheckState(state)
        self.event_list.blockSignals(False)
        self.update_preview()

    def save_markdown_file(self) -> None:
        selected_events = self.selected_events()
        if not selected_events:
            QMessageBox.warning(self, "No Events Selected", "Please select at least one event to include.")
            return

        default_name = f"newsletter_draft_{date.today().isoformat()}.md"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Newsletter Markdown File",
            str(Path.home() / default_name),
            "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)",
        )
        if not path:
            return

        markdown = NewsletterService.build_markdown(
            selected_events,
            self.members_by_event_id,
            today=date.today(),
        )
        try:
            Path(path).write_text(markdown, encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, "Save Failed", f"Could not save file:\n{exc}")
            return

        QMessageBox.information(self, "Saved", f"Newsletter markdown file saved to:\n{path}")
