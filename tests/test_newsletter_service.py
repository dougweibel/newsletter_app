from datetime import date

from src.models.event import Event
from src.models.member import Member
from src.services.newsletter_service import NewsletterService


def test_rank_candidates_prioritizes_responded_then_sent_then_due_attention() -> None:
    responded = Event(id=1, title="Responded", one_time_date="2026-04-10", solicitation_status="responded")
    sent = Event(id=2, title="Sent", one_time_date="2026-04-09", solicitation_status="sent")
    due_attention = Event(
        id=3,
        title="Due Attention",
        one_time_date="2026-04-15",
        solicitation_status="not_started",
        publicity_lead_months=1,
    )
    not_due = Event(
        id=4,
        title="Not Due",
        one_time_date="2026-08-01",
        solicitation_status="not_started",
        publicity_lead_months=1,
    )

    ranked = NewsletterService.rank_candidates(
        [not_due, due_attention, sent, responded],
        today=date(2026, 3, 25),
    )

    assert [candidate.event.title for candidate in ranked] == [
        "Responded",
        "Sent",
        "Due Attention",
        "Not Due",
    ]


def test_rank_candidates_excludes_cancelled_events() -> None:
    active = Event(id=1, title="Active", one_time_date="2026-05-01", status="active")
    cancelled = Event(id=2, title="Cancelled", one_time_date="2026-05-01", status="cancelled")

    ranked = NewsletterService.rank_candidates([cancelled, active], today=date(2026, 3, 25))

    assert [candidate.event.title for candidate in ranked] == ["Active"]


def test_build_markdown_includes_selected_event_details_and_members() -> None:
    event = Event(
        id=10,
        title="Spring Picnic",
        description="Bring lunch and a chair.",
        event_kind="one_time",
        one_time_date="2026-05-01",
        time_text="12:00 PM",
        location="Riverside Park",
        contact_info="picnic@example.com",
        other_info="Guests are welcome.",
    )
    members = [
        Member(id=1, first_name="Avery", last_name="Stone", email="avery@example.com"),
        Member(id=2, first_name="Blair", last_name="Hart", email="blair@example.com"),
    ]

    markdown = NewsletterService.build_markdown(
        [event],
        {10: members},
        today=date(2026, 3, 25),
    )

    assert "# Newsletter Draft - 2026-03-25" in markdown
    assert "## Spring Picnic" in markdown
    assert "- **Date:** 2026-05-01" in markdown
    assert "- **Associated Members:** Avery Stone, Blair Hart" in markdown
    assert "Bring lunch and a chair." in markdown
    assert "Guests are welcome." in markdown
