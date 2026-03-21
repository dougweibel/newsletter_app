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
    repo.create_member(Member(id=None, name="Jane Smith", email="jane@example.com"))

    members = repo.list_members()

    assert len(members) == 1
    assert members[0].name == "Jane Smith"
    assert members[0].email == "jane@example.com"


def test_update_member() -> None:
    initialize_database()
    clear_members()

    repo = MemberRepository()
    member_id = repo.create_member(
        Member(id=None, name="Jane Smith", email="jane@example.com", notes="Old notes")
    )

    repo.update_member(
        Member(
            id=member_id,
            name="Jane Doe",
            email="janedoe@example.com",
            notes="Updated notes",
        )
    )

    updated = repo.get_member(member_id)

    assert updated is not None
    assert updated.name == "Jane Doe"
    assert updated.email == "janedoe@example.com"
    assert updated.notes == "Updated notes"


def test_delete_member() -> None:
    initialize_database()
    clear_members()

    repo = MemberRepository()
    member_id = repo.create_member(
        Member(id=None, name="Jane Smith", email="jane@example.com")
    )

    repo.delete_member(member_id)

    members = repo.list_members()
    assert len(members) == 0