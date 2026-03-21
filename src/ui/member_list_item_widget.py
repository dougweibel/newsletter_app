from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.models.member import Member


class MemberListItemWidget(QWidget):
    def __init__(self, member: Member) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        title_label = QLabel(f"{member.name}  <{member.email}>")
        title_label.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #ffffff;"
        )
        layout.addWidget(title_label)

        notes_preview = (member.notes or "").strip()
        if len(notes_preview) > 80:
            notes_preview = notes_preview[:77] + "..."

        if notes_preview:
            notes_label = QLabel()
            notes_label.setText(
                f'<span style="color: #2f9e44; font-weight: 600;">Notes:</span> '
                f'<span style="color: #ffffff;">{notes_preview}</span>'
            )
            notes_label.setWordWrap(True)
            layout.addWidget(notes_label)