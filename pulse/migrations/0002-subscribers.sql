-- Status-update subscribers (the <Form> showcase on /about).
-- pyxle-db applies this once at startup, tracked by checksum.
CREATE TABLE subscribers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email      TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
