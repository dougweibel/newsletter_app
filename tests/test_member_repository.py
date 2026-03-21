from src.models.member import Member
from src.storage.database import initialize_database, get_connection
from src.storage.member_repository import MemberRepository


def clear_members() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM member_events")
        conn.execute("DELETE FROM members")
        conn.commit()


def test_create_and_list_members() -> None:
    initialize_database()
    clear_members()

    repo = MemberRepository()
    repo.create_member(Member(id=None, first_name="Jane", last_name="Smith", email="jane@example.com"))

    members = repo.list_members()

    assert len(members) == 1
    assert members[0].first_name == "Jane"
    assert members[0].last_name == "Smith"
    assert members[0].email == "jane@example.com"


def test_update_member() -> None:
    initialize_database()
    clear_members()

    repo = MemberRepository()
    member_id = repo.create_member(
        Member(id=None, first_name="Jane", last_name="Smith", email="jane@example.com", notes="Old notes")
    )

    repo.update_member(
        Member(
            id=member_id,
            first_name="Jane",
            last_name="Doe",
            email="janedoe@example.com",
            notes="Updated notes",
        )
    )

    updated = repo.get_member(member_id)

    assert updated is not None
    assert updated.first_name == "Jane"
    assert updated.last_name == "Doe"
    assert updated.email == "janedoe@example.com"
    assert updated.notes == "Updated notes"


def test_delete_member() -> None:
    initialize_database()
    clear_members()

    repo = MemberRepository()
    member_id = repo.create_member(
        Member(id=None, first_name="Jane", last_name="Smith", email="jane@example.com")
    )

    repo.delete_member(member_id)

    members = repo.list_members()
    assert len(members) == 0