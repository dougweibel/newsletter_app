from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from src.models.event import Event
from src.models.member import Member
from src.services.solicitation_service import SolicitationService


@dataclass(frozen=True)
class NewsletterCandidate:
    event: Event
    priority_group: int
    next_date: date | None
    reason: str


class NewsletterService:
    @staticmethod
    def rank_candidates(events: Iterable[Event], *, today: date | None = None) -> list[NewsletterCandidate]:
        today = today or date.today()
        candidates: list[NewsletterCandidate] = []
        for event in events:
            if event.status != "active":
                continue
            group, reason = NewsletterService._priority_for_event(event, today=today)
            next_date = SolicitationService.next_occurrence_date(event, today=today)
            candidates.append(
                NewsletterCandidate(
                    event=event,
                    priority_group=group,
                    next_date=next_date,
                    reason=reason,
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.priority_group,
                candidate.next_date or date.max,
                candidate.event.title.casefold(),
                candidate.event.id or 0,
            ),
        )

    @staticmethod
    def build_markdown(
        selected_events: Iterable[Event],
        members_by_event_id: dict[int, list[Member]] | None = None,
        *,
        today: date | None = None,
    ) -> str:
        today = today or date.today()
        members_by_event_id = members_by_event_id or {}
        events = list(selected_events)

        lines = [
            f"# Newsletter Draft - {today.isoformat()}",
            "",
            f"Generated on {today.isoformat()}.",
        ]

        if not events:
            lines.extend(["", "No events were selected."])
            return "\n".join(lines).rstrip() + "\n"

        for event in events:
            lines.extend([
                "",
                f"## {event.title}",
                "",
            ])
            lines.extend(NewsletterService._event_markdown_lines(event, members_by_event_id.get(event.id or -1, [])))

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def event_summary_label(candidate: NewsletterCandidate, *, today: date | None = None) -> str:
        today = today or date.today()
        date_text = NewsletterService._display_date_text(candidate.event, today=today)
        status_text = candidate.event.solicitation_status.replace("_", " ").title()
        return f"{candidate.event.title} | {status_text} | {date_text} | {candidate.reason}"

    @staticmethod
    def _priority_for_event(event: Event, *, today: date) -> tuple[int, str]:
        if event.solicitation_status in {"responded", "closed"}:
            return 0, "response received"
        if event.solicitation_status == "sent":
            return 1, "sent and awaiting response"

        due_date = SolicitationService.estimated_solicitation_due_date(event, today=today)
        if event.solicitation_status in {"not_started", "draft_ready"} and due_date is not None and due_date <= today:
            return 2, "solicitation due now"

        if event.solicitation_status == "draft_ready":
            return 3, "draft ready"
        if event.solicitation_status == "not_started":
            return 4, "not yet solicited"
        return 5, "other active event"

    @staticmethod
    def _event_markdown_lines(event: Event, members: list[Member]) -> list[str]:
        lines: list[str] = []

        date_text = NewsletterService._event_date_line(event)
        if date_text:
            lines.append(f"- **Date:** {date_text}")
        if event.time_text:
            lines.append(f"- **Time:** {event.time_text}")
        if event.location:
            lines.append(f"- **Location:** {event.location}")
        if event.contact_info:
            lines.append(f"- **Contact:** {event.contact_info}")
        if members:
            names = ", ".join(member.full_name for member in members)
            lines.append(f"- **Associated Members:** {names}")

        if event.description:
            lines.extend(["", event.description])
        if event.other_info:
            lines.extend(["", "**Additional Information**", "", event.other_info])
        if not lines:
            lines.append("No details are currently stored for this event.")
        return lines

    @staticmethod
    def _display_date_text(event: Event, *, today: date) -> str:
        next_date = SolicitationService.next_occurrence_date(event, today=today)
        if next_date is not None:
            return next_date.isoformat()
        anchor = SolicitationService._event_anchor_date(event, today=today)
        if anchor is not None:
            return anchor.isoformat()
        return "No date"

    @staticmethod
    def _event_date_line(event: Event) -> str:
        if event.event_kind == "one_time":
            return event.one_time_date or "Date not set"

        parts: list[str] = ["Recurring"]
        if event.recurrence_frequency:
            phrase = event.recurrence_frequency.capitalize()
            if event.recurrence_interval and event.recurrence_interval > 1:
                phrase += f" every {event.recurrence_interval} intervals"
            parts.append(phrase)
        if event.recurrence_day_of_week:
            weekday_names = {
                1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Saturday",
                7: "Sunday",
            }
            parts.append(f"on {weekday_names.get(event.recurrence_day_of_week, str(event.recurrence_day_of_week))}")
        if event.recurrence_day_of_month:
            parts.append(f"on day {event.recurrence_day_of_month}")
        if event.recurrence_start_date:
            parts.append(f"starting {event.recurrence_start_date}")
        if event.recurrence_end_date:
            parts.append(f"through {event.recurrence_end_date}")
        if event.seasonal_start_month and event.seasonal_end_month:
            parts.append(
                f"season {NewsletterService._month_name(event.seasonal_start_month)} to {NewsletterService._month_name(event.seasonal_end_month)}"
            )
        return ", ".join(parts)

    @staticmethod
    def _month_name(month: int) -> str:
        names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }
        return names.get(month, str(month))
