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
    assert "2026-04-15" in body


def test_estimated_solicitation_due_date_for_one_time_event() -> None:
    event = Event(
        id=1,
        title="Workshop",
        event_kind="one_time",
        one_time_date="2026-09-10",
        publicity_lead_months=2,
    )

    due_date = SolicitationService.estimated_solicitation_due_date(event)

    assert due_date is not None
    assert due_date.isoformat() == "2026-07-10"
