PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    event_kind TEXT NOT NULL CHECK (event_kind IN ('one_time', 'recurring')),
    one_time_date TEXT,
    time_text TEXT,
    location TEXT,
    contact_info TEXT,
    other_info TEXT,
    publicity_lead_months INTEGER NOT NULL DEFAULT 0 CHECK (publicity_lead_months >= 0),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled')),
    recurrence_frequency TEXT CHECK (recurrence_frequency IN ('weekly', 'monthly', 'yearly')),
    recurrence_interval INTEGER,
    recurrence_start_date TEXT,
    recurrence_end_date TEXT,
    recurrence_day_of_week INTEGER,
    recurrence_day_of_month INTEGER,
    seasonal_start_month INTEGER CHECK (seasonal_start_month BETWEEN 1 AND 12),
    seasonal_end_month INTEGER CHECK (seasonal_end_month BETWEEN 1 AND 12),
    solicitation_status TEXT NOT NULL DEFAULT 'not_started' CHECK (
        solicitation_status IN ('not_started', 'draft_ready', 'sent', 'responded', 'closed')
    ),
    solicitation_last_generated_at TEXT,
    solicitation_last_sent_at TEXT,
    solicitation_notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS member_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE(member_id, event_id)
);
