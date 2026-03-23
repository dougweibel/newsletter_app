from dataclasses import dataclass
from datetime import date, datetime
from calendar import monthrange

from src.models.event import Event
from src.models.member import Member


@dataclass
class SolicitationDraft:
    subject: str
    body: str


class SolicitationService:
    @staticmethod
    def build_subject(event: Event) -> str:
        return f"Newsletter information request: {event.title}"

    @staticmethod
    def build_body(event: Event, members: list[Member]) -> str:
        greeting = SolicitationService._greeting(members)
        timeline_line = SolicitationService._timeline_line(event)
        detail_lines = SolicitationService._event_detail_lines(event)

        sections = [
            greeting,
            "",
            (
                f"We are gathering newsletter information for {event.title}. "
                f"{timeline_line}"
            ),
            "",
            "Current event details on file:",
            *detail_lines,
            "",
            "Please reply with any updates we should include, such as:",
            "- date and time confirmation",
            "- location updates",
            "- registration or contact details",
            "- short descriptive copy suitable for the newsletter",
            "- any other items members should know",
            "",
            "Thank you,",
            "Newsletter Team",
        ]
        return "\n".join(sections)

    @staticmethod
    def recommended_status_after_generate() -> str:
        return "draft_ready"

    @staticmethod
    def _greeting(members: list[Member]) -> str:
        if not members:
            return "Hello,"

        first_names = [member.first_name.strip() for member in members if member.first_name.strip()]
        if not first_names:
            return "Hello,"
        if len(first_names) == 1:
            return f"Hello {first_names[0]},"
        if len(first_names) == 2:
            return f"Hello {first_names[0]} and {first_names[1]},"
        return f"Hello {', '.join(first_names[:-1])}, and {first_names[-1]},"


    @staticmethod
    def _event_detail_lines(event: Event) -> list[str]:
        values = [
            ("Description", event.description),
            ("Date", event.one_time_date or event.recurrence_start_date),
            ("Time", event.time_text),
            ("Location", event.location),
            ("Contact", event.contact_info),
            ("Other", event.other_info),
        ]
        detail_lines = [f"- {label}: {value}" for label, value in values if value]
        return detail_lines or ["- No event details are currently stored."]

    @staticmethod
    def _timeline_line(event: Event) -> str:
        due_date = SolicitationService.estimated_solicitation_due_date(event)
        if due_date is None:
            return "This event does not yet have enough date information to calculate a solicitation window."
        return f"A good target for sending the solicitation is around {due_date.isoformat()}."

    @staticmethod
    def estimated_solicitation_due_date(event: Event) -> date | None:
        anchor = SolicitationService._event_anchor_date(event)
        if anchor is None:
            return None
        return SolicitationService._subtract_months(anchor, event.publicity_lead_months)

    @staticmethod
    def _event_anchor_date(event: Event) -> date | None:
        for value in (event.one_time_date, event.recurrence_start_date):
            if value:
                try:
                    return date.fromisoformat(value)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _subtract_months(value: date, months: int) -> date:
        month_index = value.month - 1 - months
        year = value.year + month_index // 12
        month = month_index % 12 + 1
        day = min(value.day, monthrange(year, month)[1])
        return date(year, month, day)

    @staticmethod
    def now_timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M")
