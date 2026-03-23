from src.models.event import Event
from src.models.member import Member
from src.storage.database import get_connection


class MemberEventRepository:
    def list_member_ids_for_event(self, event_id: int) -> list[int]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT member_id
                FROM member_events
                WHERE event_id = ?
                ORDER BY member_id
                """,
                (event_id,),
            ).fetchall()

        return [int(row["member_id"]) for row in rows]

    def list_event_ids_for_member(self, member_id: int) -> list[int]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT event_id
                FROM member_events
                WHERE member_id = ?
                ORDER BY event_id
                """,
                (member_id,),
            ).fetchall()

        return [int(row["event_id"]) for row in rows]

    def list_members_for_event(self, event_id: int) -> list[Member]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT m.id, m.first_name, m.last_name, m.email, m.notes
                FROM members m
                INNER JOIN member_events me ON me.member_id = m.id
                WHERE me.event_id = ?
                ORDER BY m.last_name COLLATE NOCASE, m.first_name COLLATE NOCASE, m.id
                """,
                (event_id,),
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

    def list_events_for_member(self, member_id: int) -> list[Event]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    e.id,
                    e.title,
                    e.description,
                    e.event_kind,
                    e.one_time_date,
                    e.time_text,
                    e.location,
                    e.contact_info,
                    e.other_info,
                    e.publicity_lead_months,
                    e.status,
                    e.recurrence_frequency,
                    e.recurrence_interval,
                    e.recurrence_start_date,
                    e.recurrence_end_date,
                    e.recurrence_day_of_week,
                    e.recurrence_day_of_month,
                    e.seasonal_start_month,
                    e.seasonal_end_month,
                    e.solicitation_status,
                    e.solicitation_last_generated_at,
                    e.solicitation_last_sent_at,
                    e.solicitation_notes
                FROM events e
                INNER JOIN member_events me ON me.event_id = e.id
                WHERE me.member_id = ?
                ORDER BY e.title COLLATE NOCASE, e.id
                """,
                (member_id,),
            ).fetchall()

        return [self._row_to_event(row) for row in rows]

    def list_member_names_for_event(self, event_id: int) -> list[str]:
        return [member.full_name for member in self.list_members_for_event(event_id)]

    def list_event_titles_for_member(self, member_id: int) -> list[str]:
        return [event.title for event in self.list_events_for_member(member_id)]

    def replace_members_for_event(self, event_id: int, member_ids: list[int]) -> None:
        unique_member_ids = sorted(set(member_ids))

        with get_connection() as conn:
            conn.execute("DELETE FROM member_events WHERE event_id = ?", (event_id,))
            conn.executemany(
                "INSERT INTO member_events (member_id, event_id) VALUES (?, ?)",
                [(member_id, event_id) for member_id in unique_member_ids],
            )
            conn.commit()

    def replace_events_for_member(self, member_id: int, event_ids: list[int]) -> None:
        unique_event_ids = sorted(set(event_ids))

        with get_connection() as conn:
            conn.execute("DELETE FROM member_events WHERE member_id = ?", (member_id,))
            conn.executemany(
                "INSERT INTO member_events (member_id, event_id) VALUES (?, ?)",
                [(member_id, event_id) for event_id in unique_event_ids],
            )
            conn.commit()

    @staticmethod
    def _row_to_event(row) -> Event:
        return Event(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            event_kind=row["event_kind"],
            one_time_date=row["one_time_date"] or "",
            time_text=row["time_text"] or "",
            location=row["location"] or "",
            contact_info=row["contact_info"] or "",
            other_info=row["other_info"] or "",
            publicity_lead_months=row["publicity_lead_months"],
            status=row["status"],
            recurrence_frequency=row["recurrence_frequency"] or "",
            recurrence_interval=row["recurrence_interval"],
            recurrence_start_date=row["recurrence_start_date"] or "",
            recurrence_end_date=row["recurrence_end_date"] or "",
            recurrence_day_of_week=row["recurrence_day_of_week"],
            recurrence_day_of_month=row["recurrence_day_of_month"],
            seasonal_start_month=row["seasonal_start_month"],
            seasonal_end_month=row["seasonal_end_month"],
            solicitation_status=row["solicitation_status"] or "not_started",
            solicitation_last_generated_at=row["solicitation_last_generated_at"] or "",
            solicitation_last_sent_at=row["solicitation_last_sent_at"] or "",
            solicitation_notes=row["solicitation_notes"] or "",
        )
