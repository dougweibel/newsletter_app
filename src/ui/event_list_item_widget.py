from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EventListItemWidget(QWidget):
    def __init__(self, event_record, associated_member_names: list[str] | None = None) -> None:
        super().__init__()

        associated_member_names = associated_member_names or []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        header = QLabel(self._format_header(event_record))
        header.setStyleSheet("font-size: 14px; font-weight: 600; color: #000000;")
        header.setWordWrap(True)
        layout.addWidget(header)

        if associated_member_names:
            members_preview = self._join_preview(associated_member_names)
            members_label = QLabel()
            members_label.setText(
                f'<span style="color: #1c7ed6; font-weight: 600;">Members:</span> '
                f'<span style="color: #000000;">{members_preview}</span>'
            )
            members_label.setWordWrap(True)
            layout.addWidget(members_label)

        details_parts: list[str] = []
        if event_record.description:
            details_parts.append(event_record.description.strip())
        elif event_record.other_info:
            details_parts.append(event_record.other_info.strip())

        if details_parts:
            details_preview = details_parts[0]
            if len(details_preview) > 100:
                details_preview = details_preview[:97] + "..."
            details_label = QLabel()
            details_label.setText(
                f'<span style="color: #2f9e44; font-weight: 600;">Details:</span> '
                f'<span style="color: #000000;">{details_preview}</span>'
            )
            details_label.setWordWrap(True)
            layout.addWidget(details_label)

    @staticmethod
    def _format_header(event_record) -> str:
        parts = [event_record.title]
        if event_record.event_kind == "one_time" and event_record.one_time_date:
            parts.append(f"({event_record.one_time_date})")
        elif event_record.event_kind == "recurring":
            parts.append(f"[{event_record.recurrence_frequency or 'recurring'}]")
        if event_record.location:
            parts.append(f"- {event_record.location}")
        return " ".join(parts)

    @staticmethod
    def _join_preview(values: list[str], limit: int = 4) -> str:
        if len(values) <= limit:
            return ", ".join(values)
        remaining = len(values) - limit
        return f"{', '.join(values[:limit])}, +{remaining} more"
