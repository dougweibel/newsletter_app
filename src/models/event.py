from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    id: Optional[int]
    title: str
    description: str = ""
    event_kind: str = "one_time"
    one_time_date: str = ""
    time_text: str = ""
    location: str = ""
    contact_info: str = ""
    other_info: str = ""
    publicity_lead_months: int = 0
    status: str = "active"
    recurrence_frequency: str = ""
    recurrence_interval: Optional[int] = None
    recurrence_start_date: str = ""
    recurrence_end_date: str = ""
    recurrence_day_of_week: Optional[int] = None
    recurrence_day_of_month: Optional[int] = None
    seasonal_start_month: Optional[int] = None
    seasonal_end_month: Optional[int] = None
    solicitation_status: str = "not_started"
    solicitation_last_generated_at: str = ""
    solicitation_last_sent_at: str = ""
    solicitation_notes: str = ""
    solicitation_subject: str = ""
    solicitation_body: str = ""
