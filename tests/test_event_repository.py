from src.models.event import Event
from src.storage.database import get_connection, initialize_database
from src.storage.event_repository import EventRepository



def clear_events() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM member_events")
        conn.execute("DELETE FROM events")
        conn.commit()



def test_create_and_list_one_time_event() -> None:
    initialize_database()
    clear_events()

    repo = EventRepository()
    repo.create_event(
        Event(
            id=None,
            title="Board Meeting",
            description="Quarterly planning meeting",
            event_kind="one_time",
            one_time_date="2026-04-15",
            time_text="6:00 PM",
            location="Library",
            contact_info="president@example.com",
            publicity_lead_months=1,
        )
    )

    events = repo.list_events()

    assert len(events) == 1
    assert events[0].title == "Board Meeting"
    assert events[0].event_kind == "one_time"
    assert events[0].one_time_date == "2026-04-15"
    assert events[0].location == "Library"
    assert events[0].solicitation_status == "not_started"



def test_create_and_get_recurring_event() -> None:
    initialize_database()
    clear_events()

    repo = EventRepository()
    event_id = repo.create_event(
        Event(
            id=None,
            title="Monthly Potluck",
            description="Bring a dish to share",
            event_kind="recurring",
            time_text="5:30 PM",
            location="Clubhouse",
            publicity_lead_months=2,
            recurrence_frequency="monthly",
            recurrence_interval=1,
            recurrence_start_date="2026-01-01",
            recurrence_day_of_month=10,
            seasonal_start_month=1,
            seasonal_end_month=12,
        )
    )

    event = repo.get_event(event_id)

    assert event is not None
    assert event.title == "Monthly Potluck"
    assert event.event_kind == "recurring"
    assert event.recurrence_frequency == "monthly"
    assert event.recurrence_day_of_month == 10
    assert event.seasonal_start_month == 1
    assert event.seasonal_end_month == 12



def test_update_event() -> None:
    initialize_database()
    clear_events()

    repo = EventRepository()
    event_id = repo.create_event(
        Event(
            id=None,
            title="Garden Tour",
            event_kind="one_time",
            one_time_date="2026-06-01",
            status="active",
        )
    )

    repo.update_event(
        Event(
            id=event_id,
            title="Annual Garden Tour",
            description="Self-guided tour across town",
            event_kind="recurring",
            time_text="10:00 AM",
            location="Multiple homes",
            contact_info="garden@example.com",
            other_info="Tickets required",
            publicity_lead_months=3,
            status="cancelled",
            recurrence_frequency="yearly",
            recurrence_interval=1,
            recurrence_start_date="2026-06-01",
            recurrence_end_date="2028-06-01",
            recurrence_day_of_month=1,
            seasonal_start_month=6,
            seasonal_end_month=6,
            solicitation_status="draft_ready",
            solicitation_last_generated_at="2026-03-22 10:00",
            solicitation_last_sent_at="2026-03-23 11:00",
            solicitation_notes="Waiting on updated copy.",
        )
    )

    updated = repo.get_event(event_id)

    assert updated is not None
    assert updated.title == "Annual Garden Tour"
    assert updated.event_kind == "recurring"
    assert updated.status == "cancelled"
    assert updated.recurrence_frequency == "yearly"
    assert updated.location == "Multiple homes"
    assert updated.other_info == "Tickets required"
    assert updated.solicitation_status == "draft_ready"
    assert updated.solicitation_last_generated_at == "2026-03-22 10:00"
    assert updated.solicitation_last_sent_at == "2026-03-23 11:00"
    assert updated.solicitation_notes == "Waiting on updated copy."



def test_delete_event() -> None:
    initialize_database()
    clear_events()

    repo = EventRepository()
    event_id = repo.create_event(
        Event(
            id=None,
            title="Cleanup Day",
            event_kind="one_time",
            one_time_date="2026-05-03",
        )
    )

    repo.delete_event(event_id)

    events = repo.list_events()
    assert len(events) == 0
