-- Pulse — initial schema.
-- pyxle-db applies this once at startup (checksum-tracked). Never edit an
-- applied migration; add a new NNNN-slug.sql instead. db.py seeds realistic
-- demo data on first boot.

CREATE TABLE services (
    id     INTEGER PRIMARY KEY,
    slug   TEXT    NOT NULL UNIQUE,
    name   TEXT    NOT NULL,
    region TEXT    NOT NULL,
    -- operational | degraded | partial | major | maintenance
    status TEXT    NOT NULL DEFAULT 'operational',
    sort   INTEGER NOT NULL DEFAULT 0
);

-- One row per service per day, for the 90-day uptime bars.
CREATE TABLE daily_status (
    service_id INTEGER NOT NULL REFERENCES services(id),
    day        TEXT    NOT NULL,          -- YYYY-MM-DD (UTC)
    status     TEXT    NOT NULL,
    uptime     REAL    NOT NULL,          -- 0..100
    PRIMARY KEY (service_id, day)
);

CREATE TABLE incidents (
    id          INTEGER PRIMARY KEY,
    slug        TEXT    NOT NULL UNIQUE,
    title       TEXT    NOT NULL,
    -- minor | major | critical | maintenance
    severity    TEXT    NOT NULL,
    -- investigating | identified | monitoring | resolved
    status      TEXT    NOT NULL,
    service_id  INTEGER REFERENCES services(id),
    summary     TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL,
    resolved_at TEXT
);

CREATE TABLE incident_updates (
    id          INTEGER PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id),
    status      TEXT    NOT NULL,         -- the incident status at this update
    body        TEXT    NOT NULL,
    author      TEXT    NOT NULL DEFAULT 'Pulse',
    created_at  TEXT    NOT NULL
);

CREATE INDEX idx_updates_incident   ON incident_updates(incident_id, created_at);
CREATE INDEX idx_incidents_status   ON incidents(status, created_at);
CREATE INDEX idx_daily_service_day  ON daily_status(service_id, day);
