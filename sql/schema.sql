CREATE TABLE IF NOT EXISTS agents (
    agent_id INTEGER PRIMARY KEY,
    name     TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id        INTEGER PRIMARY KEY,
    created_at       TEXT NOT NULL,
    category_id      INTEGER NOT NULL REFERENCES categories (category_id),
    priority         TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status           TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved')),
    agent_id         INTEGER NOT NULL REFERENCES agents (agent_id),
    resolution_hours REAL
);
