from src.models.event import Event
from src.storage.database import get_connection


class EventRepository:
    def list_events(self) -> list[Event]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    event_kind,
                    one_time_date,
                    time_text,
                    location,
                    contact_info,
                    other_info,
                    publicity_lead_months,
                    status,
                    recurrence_frequency,
                    recurrence_interval,
                    recurrence_start_date,
                    recurrence_end_date,
                    recurrence_day_of_week,
                    recurrence_day_of_month,
                    seasonal_start_month,
                    seasonal_end_month,
                    solicitation_status,
                    solicitation_last_generated_at,
                    solicitation_last_sent_at,
                    solicitation_notes,
                    solicitation_subject,
                    solicitation_body
                FROM events
                ORDER BY title COLLATE NOCASE, id
                """
            ).fetchall()

        return [self._row_to_event(row) for row in rows]

    def get_event(self, event_id: int) -> Event | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    event_kind,
                    one_time_date,
                    time_text,
                    location,
                    contact_info,
                    other_info,
                    publicity_lead_months,
                    status,
                    recurrence_frequency,
                    recurrence_interval,
                    recurrence_start_date,
                    recurrence_end_date,
                    recurrence_day_of_week,
                    recurrence_day_of_month,
                    seasonal_start_month,
                    seasonal_end_month,
                    solicitation_status,
                    solicitation_last_generated_at,
                    solicitation_last_sent_at,
                    solicitation_notes,
                    solicitation_subject,
                    solicitation_body
                FROM events
                WHERE id = ?
                """,
                (event_id,),
            ).fetchone()

        if row is None:
            return None
        return self._row_to_event(row)

    def create_event(self, event: Event) -> int:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO events (
                    title,
                    description,
                    event_kind,
                    one_time_date,
                    time_text,
                    location,
                    contact_info,
                    other_info,
                    publicity_lead_months,
                    status,
                    recurrence_frequency,
                    recurrence_interval,
                    recurrence_start_date,
                    recurrence_end_date,
                    recurrence_day_of_week,
                    recurrence_day_of_month,
                    seasonal_start_month,
                    seasonal_end_month,
                    solicitation_status,
                    solicitation_last_generated_at,
                    solicitation_last_sent_at,
                    solicitation_notes,
                    solicitation_subject,
                    solicitation_body
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._event_values(event),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def update_event(self, event: Event) -> None:
        if event.id is None:
            raise ValueError("Event id is required for update.")

        with get_connection() as conn:
            conn.execute(
                """
                UPDATE events
                SET
                    title = ?,
                    description = ?,
                    event_kind = ?,
                    one_time_date = ?,
                    time_text = ?,
                    location = ?,
                    contact_info = ?,
                    other_info = ?,
                    publicity_lead_months = ?,
                    status = ?,
                    recurrence_frequency = ?,
                    recurrence_interval = ?,
                    recurrence_start_date = ?,
                    recurrence_end_date = ?,
                    recurrence_day_of_week = ?,
                    recurrence_day_of_month = ?,
                    seasonal_start_month = ?,
                    seasonal_end_month = ?,
                    solicitation_status = ?,
                    solicitation_last_generated_at = ?,
                    solicitation_last_sent_at = ?,
                    solicitation_notes = ?,
                    solicitation_subject = ?,
                    solicitation_body = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*self._event_values(event), event.id),
            )
            conn.commit()

    def delete_event(self, event_id: int) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                DELETE FROM events
                WHERE id = ?
                """,
                (event_id,),
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
            solicitation_subject=row["solicitation_subject"] or "",
            solicitation_body=row["solicitation_body"] or "",
        )

    @staticmethod
    def _event_values(event: Event) -> tuple:
        return (
            event.title,
            event.description,
            event.event_kind,
            EventRepository._clean_str(event.one_time_date),
            EventRepository._clean_str(event.time_text),
            EventRepository._clean_str(event.location),
            EventRepository._clean_str(event.contact_info),
            EventRepository._clean_str(event.other_info),
            event.publicity_lead_months,
            event.status,
            EventRepository._clean_str(event.recurrence_frequency),
            event.recurrence_interval,
            EventRepository._clean_str(event.recurrence_start_date),
            EventRepository._clean_str(event.recurrence_end_date),
            event.recurrence_day_of_week,
            event.recurrence_day_of_month,
            event.seasonal_start_month,
            event.seasonal_end_month,
            event.solicitation_status,
            EventRepository._clean_str(event.solicitation_last_generated_at),
            EventRepository._clean_str(event.solicitation_last_sent_at),
            EventRepository._clean_str(event.solicitation_notes),
            EventRepository._clean_str(event.solicitation_subject),
            EventRepository._clean_str(event.solicitation_body),
        )

    @staticmethod
    def _clean_str(value: str) -> str | None:
        return value.strip() or None
