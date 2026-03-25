from dataclasses import dataclass
from datetime import date, datetime, timedelta
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
        detail_lines = SolicitationService._event_detail_lines(event)

        sections = [
            greeting,
            "",
            f"We are gathering newsletter information for {event.title}.",
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
    def estimated_solicitation_due_date(event: Event, *, today: date | None = None) -> date | None:
        anchor = SolicitationService._event_anchor_date(event, today=today)
        if anchor is None:
            return None
        lead_months = max(1, event.publicity_lead_months)
        return SolicitationService._subtract_months(anchor, lead_months) - timedelta(days=15)

    @staticmethod
    def next_occurrence_date(event: Event, *, today: date | None = None) -> date | None:
        today = today or date.today()
        return SolicitationService._event_anchor_date(event, today=today)

    @staticmethod
    def _event_anchor_date(event: Event, *, today: date | None = None) -> date | None:
        today = today or date.today()

        if event.event_kind == "recurring":
            recurring_anchor = SolicitationService._next_recurring_occurrence(event, today=today)
            if recurring_anchor is not None:
                return recurring_anchor

        for value in (event.one_time_date, event.recurrence_start_date):
            if value:
                try:
                    return date.fromisoformat(value)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _next_recurring_occurrence(event: Event, *, today: date) -> date | None:
        start = SolicitationService._parse_iso_date(event.recurrence_start_date)
        if start is None:
            return None

        end = SolicitationService._parse_iso_date(event.recurrence_end_date)
        interval = max(1, event.recurrence_interval or 1)
        search_start = max(today + timedelta(days=1), start)
        frequency = (event.recurrence_frequency or "").strip()

        if frequency == "weekly":
            candidate = SolicitationService._next_weekly_occurrence(
                start=start,
                target=search_start,
                interval=interval,
                day_of_week=event.recurrence_day_of_week,
            )
        elif frequency == "monthly":
            candidate = SolicitationService._next_monthly_occurrence(
                start=start,
                target=search_start,
                interval=interval,
                day_of_month=event.recurrence_day_of_month,
            )
        elif frequency == "yearly":
            candidate = SolicitationService._next_yearly_occurrence(
                start=start,
                target=search_start,
                interval=interval,
                day_of_month=event.recurrence_day_of_month,
            )
        else:
            candidate = None

        if candidate is None:
            return None
        if end is not None and candidate > end:
            return None
        if not SolicitationService._matches_season(candidate, event.seasonal_start_month, event.seasonal_end_month):
            return SolicitationService._advance_until_in_season(event, candidate, today=today, end=end)
        return candidate

    @staticmethod
    def _advance_until_in_season(event: Event, candidate: date, *, today: date, end: date | None) -> date | None:
        for _ in range(60):
            if SolicitationService._matches_season(candidate, event.seasonal_start_month, event.seasonal_end_month):
                if end is not None and candidate > end:
                    return None
                return candidate
            candidate = SolicitationService._next_after_candidate(event, candidate)
            if candidate is None:
                return None
            if candidate <= today:
                candidate = today + timedelta(days=1)
            if end is not None and candidate > end:
                return None
        return None

    @staticmethod
    def _next_after_candidate(event: Event, candidate: date) -> date | None:
        frequency = (event.recurrence_frequency or "").strip()
        interval = max(1, event.recurrence_interval or 1)
        if frequency == "weekly":
            return candidate + timedelta(days=7 * interval)
        if frequency == "monthly":
            return SolicitationService._add_months(candidate, interval)
        if frequency == "yearly":
            return SolicitationService._add_months(candidate, interval * 12)
        return None

    @staticmethod
    def _next_weekly_occurrence(*, start: date, target: date, interval: int, day_of_week: int | None) -> date:
        weekday = SolicitationService._normalize_weekday(day_of_week, fallback=start.weekday())
        candidate = target + timedelta(days=(weekday - target.weekday()) % 7)
        if candidate < start:
            candidate = start + timedelta(days=(weekday - start.weekday()) % 7)
        weeks_since_start = (candidate - start).days // 7
        remainder = weeks_since_start % interval
        if remainder:
            candidate += timedelta(days=(interval - remainder) * 7)
        return candidate

    @staticmethod
    def _next_monthly_occurrence(*, start: date, target: date, interval: int, day_of_month: int | None) -> date:
        desired_day = day_of_month or start.day
        months_since_start = max(0, SolicitationService._month_delta(start, target))
        step_index = months_since_start // interval
        candidate = SolicitationService._monthly_candidate(start, step_index * interval, desired_day)
        while candidate < target:
            step_index += 1
            candidate = SolicitationService._monthly_candidate(start, step_index * interval, desired_day)
        return candidate

    @staticmethod
    def _next_yearly_occurrence(*, start: date, target: date, interval: int, day_of_month: int | None) -> date:
        desired_day = day_of_month or start.day
        month = start.month
        year = max(start.year, target.year)
        while True:
            candidate_year = start.year + ((max(0, year - start.year) + interval - 1) // interval) * interval
            candidate = date(
                candidate_year,
                month,
                min(desired_day, monthrange(candidate_year, month)[1]),
            )
            if candidate < start:
                year = start.year + interval
                continue
            if candidate < target:
                year = candidate.year + interval
                continue
            return candidate

    @staticmethod
    def _monthly_candidate(start: date, month_offset: int, desired_day: int) -> date:
        base = SolicitationService._add_months(date(start.year, start.month, 1), month_offset)
        last_day = monthrange(base.year, base.month)[1]
        return date(base.year, base.month, min(desired_day, last_day))

    @staticmethod
    def _month_delta(start: date, end: date) -> int:
        return (end.year - start.year) * 12 + (end.month - start.month)

    @staticmethod
    def _matches_season(candidate: date, start_month: int | None, end_month: int | None) -> bool:
        if not start_month or not end_month:
            return True
        if start_month <= end_month:
            return start_month <= candidate.month <= end_month
        return candidate.month >= start_month or candidate.month <= end_month

    @staticmethod
    def _normalize_weekday(value: int | None, *, fallback: int) -> int:
        if value is None:
            return fallback
        if 1 <= value <= 7:
            return (value - 1) % 7
        if 0 <= value <= 6:
            return value
        return fallback

    @staticmethod
    def _parse_iso_date(value: str) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _subtract_months(value: date, months: int) -> date:
        month_index = value.month - 1 - months
        year = value.year + month_index // 12
        month = month_index % 12 + 1
        day = min(value.day, monthrange(year, month)[1])
        return date(year, month, day)

    @staticmethod
    def _add_months(value: date, months: int) -> date:
        month_index = value.month - 1 + months
        year = value.year + month_index // 12
        month = month_index % 12 + 1
        day = min(value.day, monthrange(year, month)[1])
        return date(year, month, day)

    @staticmethod
    def now_timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M")
