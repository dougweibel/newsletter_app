from datetime import date

from src.models.event import Event
from src.models.member import Member
from src.services.solicitation_service import SolicitationService


def test_build_subject_and_body() -> None:
    event = Event(
        id=1,
        title="Spring Picnic",
        description="A casual outdoor picnic.",
        event_kind="one_time",
        one_time_date="2026-06-15",
        time_text="12:00 PM",
        location="Riverside Park",
        contact_info="picnic@example.com",
        publicity_lead_months=2,
    )
    members = [
        Member(id=1, first_name="Avery", last_name="Stone", email="avery@example.com"),
        Member(id=2, first_name="Blair", last_name="Hart", email="blair@example.com"),
    ]

    subject = SolicitationService.build_subject(event)
    body = SolicitationService.build_body(event, members)

    assert subject == "Newsletter information request: Spring Picnic"
    assert "Hello Avery and Blair," in body
    assert "We are gathering newsletter information for Spring Picnic." in body
    assert "Riverside Park" in body
    assert "2026-03-31" in body


def test_estimated_solicitation_due_date_for_one_time_event() -> None:
    event = Event(
        id=1,
        title="Workshop",
        event_kind="one_time",
        one_time_date="2026-09-10",
        publicity_lead_months=2,
    )

    due_date = SolicitationService.estimated_solicitation_due_date(event, today=date(2026, 1, 1))

    assert due_date is not None
    assert due_date.isoformat() == "2026-06-25"


def test_estimated_solicitation_due_date_for_recurring_event_uses_next_occurrence() -> None:
    event = Event(
        id=1,
        title="Board Meeting",
        event_kind="recurring",
        recurrence_frequency="monthly",
        recurrence_interval=1,
        recurrence_start_date="2026-01-10",
        recurrence_day_of_month=10,
        publicity_lead_months=1,
    )

    next_occurrence = SolicitationService.next_occurrence_date(event, today=date(2026, 3, 24))
    due_date = SolicitationService.estimated_solicitation_due_date(event, today=date(2026, 3, 24))

    assert next_occurrence is not None
    assert next_occurrence.isoformat() == "2026-04-10"
    assert due_date is not None
    assert due_date.isoformat() == "2026-02-23"


def test_estimated_solicitation_due_date_enforces_minimum_one_month() -> None:
    event = Event(
        id=1,
        title="Legacy Event",
        event_kind="one_time",
        one_time_date="2026-05-20",
        publicity_lead_months=0,
    )

    due_date = SolicitationService.estimated_solicitation_due_date(event, today=date(2026, 1, 1))

    assert due_date is not None
    assert due_date.isoformat() == "2026-04-05"
