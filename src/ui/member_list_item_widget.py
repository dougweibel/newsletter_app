from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.models.member import Member


class MemberListItemWidget(QWidget):
    def __init__(
        self,
        member: Member,
        associated_event_titles: list[str] | None = None,
    ) -> None:
        super().__init__()

        associated_event_titles = associated_event_titles or []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        title_label = QLabel(f"{member.full_name}  <{member.email}>")
        title_label.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #000000;"
        )
        layout.addWidget(title_label)

        if associated_event_titles:
            events_preview = self._join_preview(associated_event_titles)
            events_label = QLabel()
            events_label.setText(
                f'<span style="color: #1c7ed6; font-weight: 600;">Events:</span> '
                f'<span style="color: #000000;">{events_preview}</span>'
            )
            events_label.setWordWrap(True)
            layout.addWidget(events_label)

        notes_preview = (member.notes or "").strip()
        if len(notes_preview) > 80:
            notes_preview = notes_preview[:77] + "..."

        if notes_preview:
            notes_label = QLabel()
            notes_label.setText(
                f'<span style="color: #2f9e44; font-weight: 600;">Notes:</span> '
                f'<span style="color: #000000;">{notes_preview}</span>'
            )
            notes_label.setWordWrap(True)
            layout.addWidget(notes_label)

    @staticmethod
    def _join_preview(values: list[str], limit: int = 3) -> str:
        if len(values) <= limit:
            return ", ".join(values)
        remaining = len(values) - limit
        return f"{', '.join(values[:limit])}, +{remaining} more"
