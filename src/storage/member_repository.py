from src.models.member import Member
from src.storage.database import get_connection


class MemberRepository:
    def list_members(self) -> list[Member]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, first_name, last_name, email, notes
                FROM members
                ORDER BY last_name COLLATE NOCASE, first_name COLLATE NOCASE
                """
            ).fetchall()

        return [
            Member(
                id=row["id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                notes=row["notes"] or "",
            )
            for row in rows
        ]

    def get_member(self, member_id: int) -> Member | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT id, first_name, last_name, email, notes
                FROM members
                WHERE id = ?
                """,
                (member_id,),
            ).fetchone()

        if row is None:
            return None

        return Member(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            notes=row["notes"] or "",
        )

    def create_member(self, member: Member) -> int:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO members (first_name, last_name, email, notes)
                VALUES (?, ?, ?, ?)
                """,
                (member.first_name, member.last_name, member.email, member.notes),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def update_member(self, member: Member) -> None:
        if member.id is None:
            raise ValueError("Member id is required for update.")

        with get_connection() as conn:
            conn.execute(
                """
                UPDATE members
                SET first_name = ?, last_name = ?, email = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    member.first_name,
                    member.last_name,
                    member.email,
                    member.notes,
                    member.id,
                ),
            )
            conn.commit()

    def delete_member(self, member_id: int) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                DELETE FROM members
                WHERE id = ?
                """,
                (member_id,),
            )
            conn.commit()