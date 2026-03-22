from src.models.event import Event
from src.models.member import Member
from src.storage.database import get_connection, initialize_database
from src.storage.event_repository import EventRepository
from src.storage.member_event_repository import MemberEventRepository
from src.storage.member_repository import MemberRepository


def clear_data() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM member_events")
        conn.execute("DELETE FROM events")
        conn.execute("DELETE FROM members")
        conn.commit()


def create_member(first_name: str, last_name: str, email: str) -> int:
    return MemberRepository().create_member(
        Member(id=None, first_name=first_name, last_name=last_name, email=email, notes="")
    )


def create_event(title: str, one_time_date: str) -> int:
    return EventRepository().create_event(
        Event(id=None, title=title, event_kind="one_time", one_time_date=one_time_date)
    )


def test_replace_members_for_event_and_list_members() -> None:
    initialize_database()
    clear_data()

    alice_id = create_member("Alice", "Able", "alice@example.com")
    bob_id = create_member("Bob", "Baker", "bob@example.com")
    event_id = create_event("Cleanup Day", "2026-05-03")

    repo = MemberEventRepository()
    repo.replace_members_for_event(event_id, [bob_id, alice_id, alice_id])

    member_ids = repo.list_member_ids_for_event(event_id)
    members = repo.list_members_for_event(event_id)

    assert member_ids == [alice_id, bob_id]
    assert [member.full_name for member in members] == ["Alice Able", "Bob Baker"]


def test_replace_events_for_member_and_list_events() -> None:
    initialize_database()
    clear_data()

    member_id = create_member("Carol", "Clark", "carol@example.com")
    potluck_id = create_event("Potluck", "2026-04-01")
    picnic_id = create_event("Picnic", "2026-06-15")

    repo = MemberEventRepository()
    repo.replace_events_for_member(member_id, [picnic_id, potluck_id, picnic_id])

    event_ids = repo.list_event_ids_for_member(member_id)
    events = repo.list_events_for_member(member_id)

    assert event_ids == [potluck_id, picnic_id]
    assert [event.title for event in events] == ["Picnic", "Potluck"]


def test_replace_clears_old_associations() -> None:
    initialize_database()
    clear_data()

    member_id = create_member("Dana", "Dover", "dana@example.com")
    event_a_id = create_event("Class A", "2026-02-10")
    event_b_id = create_event("Class B", "2026-02-11")

    repo = MemberEventRepository()
    repo.replace_events_for_member(member_id, [event_a_id, event_b_id])
    repo.replace_events_for_member(member_id, [event_b_id])

    assert repo.list_event_ids_for_member(member_id) == [event_b_id]


def test_summary_helpers_return_related_names() -> None:
    initialize_database()
    clear_data()

    member_id = create_member("Erin", "East", "erin@example.com")
    helper_id = create_member("Frank", "Field", "frank@example.com")
    event_id = create_event("River Cleanup", "2026-07-04")
    second_event_id = create_event("Harvest Dinner", "2026-09-12")

    repo = MemberEventRepository()
    repo.replace_members_for_event(event_id, [helper_id, member_id])
    repo.replace_events_for_member(member_id, [second_event_id, event_id])

    assert repo.list_member_names_for_event(event_id) == ["Erin East", "Frank Field"]
    assert repo.list_event_titles_for_member(member_id) == ["Harvest Dinner", "River Cleanup"]
