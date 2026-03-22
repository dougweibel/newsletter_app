from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTextEdit,
)

from src.models.event import Event


class EventDialog(QDialog):
    def __init__(self, parent=None, event: Event | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Event" if event is None else "Edit Event")
        self.resize(520, 680)

        self.original_event = event

        self.title_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.event_kind_combo = QComboBox()
        self.event_kind_combo.addItems(["one_time", "recurring"])

        self.one_time_date_edit = self._build_date_edit()
        self.time_text_edit = QLineEdit()
        self.location_edit = QLineEdit()
        self.contact_info_edit = QLineEdit()
        self.other_info_edit = QTextEdit()

        self.publicity_lead_months_spin = QSpinBox()
        self.publicity_lead_months_spin.setRange(0, 24)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "cancelled"])

        self.recurrence_frequency_combo = QComboBox()
        self.recurrence_frequency_combo.addItems(["", "weekly", "monthly", "yearly"])

        self.recurrence_interval_spin = QSpinBox()
        self.recurrence_interval_spin.setRange(1, 365)
        self.recurrence_interval_spin.setValue(1)

        self.recurrence_start_date_edit = self._build_date_edit()
        self.has_recurrence_end_date_checkbox = QCheckBox("Has end date")
        self.recurrence_end_date_edit = self._build_date_edit()

        self.recurrence_day_of_week_spin = QSpinBox()
        self.recurrence_day_of_week_spin.setRange(0, 7)
        self.recurrence_day_of_week_spin.setSpecialValueText("")

        self.recurrence_day_of_month_spin = QSpinBox()
        self.recurrence_day_of_month_spin.setRange(0, 31)
        self.recurrence_day_of_month_spin.setSpecialValueText("")

        self.seasonal_start_month_spin = QSpinBox()
        self.seasonal_start_month_spin.setRange(0, 12)
        self.seasonal_start_month_spin.setSpecialValueText("")

        self.seasonal_end_month_spin = QSpinBox()
        self.seasonal_end_month_spin.setRange(0, 12)
        self.seasonal_end_month_spin.setSpecialValueText("")

        layout = QFormLayout(self)
        layout.addRow("Title", self.title_edit)
        layout.addRow("Description", self.description_edit)
        layout.addRow("Event Kind", self.event_kind_combo)
        layout.addRow("One-Time Date", self.one_time_date_edit)
        layout.addRow("Time", self.time_text_edit)
        layout.addRow("Location", self.location_edit)
        layout.addRow("Contact Info", self.contact_info_edit)
        layout.addRow("Other Info", self.other_info_edit)
        layout.addRow("Publicity Lead Months", self.publicity_lead_months_spin)
        layout.addRow("Status", self.status_combo)
        layout.addRow("Recurrence Frequency", self.recurrence_frequency_combo)
        layout.addRow("Recurrence Interval", self.recurrence_interval_spin)
        layout.addRow("Recurrence Start Date", self.recurrence_start_date_edit)
        layout.addRow("Recurrence End Date", self.has_recurrence_end_date_checkbox)
        layout.addRow("End Date Value", self.recurrence_end_date_edit)
        layout.addRow("Recurrence Day of Week", self.recurrence_day_of_week_spin)
        layout.addRow("Recurrence Day of Month", self.recurrence_day_of_month_spin)
        layout.addRow("Seasonal Start Month", self.seasonal_start_month_spin)
        layout.addRow("Seasonal End Month", self.seasonal_end_month_spin)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

        self.event_kind_combo.currentTextChanged.connect(self._update_enabled_states)
        self.has_recurrence_end_date_checkbox.toggled.connect(self._update_enabled_states)

        if event is not None:
            self._load_event(event)

        self._update_enabled_states()

    def _build_date_edit(self) -> QDateEdit:
        widget = QDateEdit()
        widget.setCalendarPopup(True)
        widget.setDisplayFormat("yyyy-MM-dd")
        widget.setDate(QDate.currentDate())
        return widget

    def _set_date_if_valid(self, widget: QDateEdit, value: str) -> None:
        if not value:
            return
        parsed = QDate.fromString(value, Qt.ISODate)
        if parsed.isValid():
            widget.setDate(parsed)

    def _update_enabled_states(self) -> None:
        is_one_time = self.event_kind_combo.currentText() == "one_time"
        is_recurring = not is_one_time
        has_end_date = self.has_recurrence_end_date_checkbox.isChecked()

        self.one_time_date_edit.setEnabled(is_one_time)

        self.recurrence_frequency_combo.setEnabled(is_recurring)
        self.recurrence_interval_spin.setEnabled(is_recurring)
        self.recurrence_start_date_edit.setEnabled(is_recurring)
        self.has_recurrence_end_date_checkbox.setEnabled(is_recurring)
        self.recurrence_end_date_edit.setEnabled(is_recurring and has_end_date)
        self.recurrence_day_of_week_spin.setEnabled(is_recurring)
        self.recurrence_day_of_month_spin.setEnabled(is_recurring)
        self.seasonal_start_month_spin.setEnabled(is_recurring)
        self.seasonal_end_month_spin.setEnabled(is_recurring)

    def _load_event(self, event: Event) -> None:
        self.title_edit.setText(event.title)
        self.description_edit.setPlainText(event.description)
        self.event_kind_combo.setCurrentText(event.event_kind)
        self._set_date_if_valid(self.one_time_date_edit, event.one_time_date)
        self.time_text_edit.setText(event.time_text)
        self.location_edit.setText(event.location)
        self.contact_info_edit.setText(event.contact_info)
        self.other_info_edit.setPlainText(event.other_info)
        self.publicity_lead_months_spin.setValue(event.publicity_lead_months)
        self.status_combo.setCurrentText(event.status)
        self.recurrence_frequency_combo.setCurrentText(event.recurrence_frequency)
        self.recurrence_interval_spin.setValue(event.recurrence_interval or 1)
        self._set_date_if_valid(self.recurrence_start_date_edit, event.recurrence_start_date)

        has_end_date = bool(event.recurrence_end_date)
        self.has_recurrence_end_date_checkbox.setChecked(has_end_date)
        self._set_date_if_valid(self.recurrence_end_date_edit, event.recurrence_end_date)

        self.recurrence_day_of_week_spin.setValue(event.recurrence_day_of_week or 0)
        self.recurrence_day_of_month_spin.setValue(event.recurrence_day_of_month or 0)
        self.seasonal_start_month_spin.setValue(event.seasonal_start_month or 0)
        self.seasonal_end_month_spin.setValue(event.seasonal_end_month or 0)

    def validate_and_accept(self) -> None:
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Title is required.")
            return

        event_kind = self.event_kind_combo.currentText()
        recurrence_frequency = self.recurrence_frequency_combo.currentText().strip()

        if event_kind == "recurring" and not recurrence_frequency:
            QMessageBox.warning(self, "Validation Error", "Recurring events require a recurrence frequency.")
            return

        self.accept()

    def get_event_data(self) -> Event:
        event_id = None if self.original_event is None else self.original_event.id
        event_kind = self.event_kind_combo.currentText()
        recurrence_frequency = self.recurrence_frequency_combo.currentText().strip()

        is_one_time = event_kind == "one_time"
        has_end_date = self.has_recurrence_end_date_checkbox.isChecked()

        recurrence_interval = self.recurrence_interval_spin.value() if not is_one_time else None
        recurrence_day_of_week = self.recurrence_day_of_week_spin.value() or None
        recurrence_day_of_month = self.recurrence_day_of_month_spin.value() or None
        seasonal_start_month = self.seasonal_start_month_spin.value() or None
        seasonal_end_month = self.seasonal_end_month_spin.value() or None

        return Event(
            id=event_id,
            title=self.title_edit.text().strip(),
            description=self.description_edit.toPlainText().strip(),
            event_kind=event_kind,
            one_time_date=self.one_time_date_edit.date().toString(Qt.ISODate) if is_one_time else "",
            time_text=self.time_text_edit.text().strip(),
            location=self.location_edit.text().strip(),
            contact_info=self.contact_info_edit.text().strip(),
            other_info=self.other_info_edit.toPlainText().strip(),
            publicity_lead_months=self.publicity_lead_months_spin.value(),
            status=self.status_combo.currentText(),
            recurrence_frequency=recurrence_frequency if not is_one_time else "",
            recurrence_interval=recurrence_interval,
            recurrence_start_date=self.recurrence_start_date_edit.date().toString(Qt.ISODate) if not is_one_time else "",
            recurrence_end_date=(
                self.recurrence_end_date_edit.date().toString(Qt.ISODate)
                if (not is_one_time and has_end_date)
                else ""
            ),
            recurrence_day_of_week=recurrence_day_of_week if not is_one_time else None,
            recurrence_day_of_month=recurrence_day_of_month if not is_one_time else None,
            seasonal_start_month=seasonal_start_month if not is_one_time else None,
            seasonal_end_month=seasonal_end_month if not is_one_time else None,
        )
