import csv
import logging
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "tickets.csv"
DB_PATH = ROOT / "data" / "helpdesk.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("load_data")


def clean_ticket(row):
    """Return a cleaned copy of one CSV row and a list of the fixes applied."""
    cleaned = dict(row)
    fixes = []

    category = row["category"].strip().lower()
    if not category:
        category = "unknown"
        fixes.append("missing category -> unknown")
    elif category != row["category"]:
        fixes.append("category normalised")
    cleaned["category"] = category

    agent = row["agent"].strip().title()
    if agent != row["agent"]:
        fixes.append("agent normalised")
    cleaned["agent"] = agent

    priority = row["priority"].strip().lower()
    if priority != row["priority"]:
        fixes.append("priority normalised")
    cleaned["priority"] = priority

    return cleaned, fixes


def read_and_clean(path):
    """Read the CSV, drop duplicate ticket ids and clean every remaining row."""
    seen_ids = set()
    tickets = []
    stats = {"read": 0, "duplicates": 0, "fixed": 0}

    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stats["read"] += 1

            if row["ticket_id"] in seen_ids:
                stats["duplicates"] += 1
                log.info("Dropped duplicate ticket_id=%s", row["ticket_id"])
                continue
            seen_ids.add(row["ticket_id"])

            cleaned, fixes = clean_ticket(row)
            if fixes:
                stats["fixed"] += 1
                log.info("Fixed ticket_id=%s: %s", row["ticket_id"], "; ".join(fixes))
            tickets.append(cleaned)

    return tickets, stats


def load_into_db(tickets, db_path):
    """Rebuild the SQLite database from scratch and insert the cleaned tickets."""
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    for name in sorted({t["category"] for t in tickets}):
        conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    for name in sorted({t["agent"] for t in tickets}):
        conn.execute("INSERT INTO agents (name) VALUES (?)", (name,))

    category_ids = dict(conn.execute("SELECT name, category_id FROM categories"))
    agent_ids = dict(conn.execute("SELECT name, agent_id FROM agents"))

    rows = [
        (
            int(t["ticket_id"]),
            t["created_at"],
            category_ids[t["category"]],
            t["priority"],
            t["status"],
            agent_ids[t["agent"]],
            float(t["resolution_hours"]) if t["resolution_hours"] else None,
        )
        for t in tickets
    ]
    conn.executemany(
        "INSERT INTO tickets (ticket_id, created_at, category_id, priority, status, agent_id, resolution_hours)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    return len(rows)


if __name__ == "__main__":
    tickets, stats = read_and_clean(CSV_PATH)
    loaded = load_into_db(tickets, DB_PATH)
    log.info(
        "Read %d rows, dropped %d duplicates, fixed %d rows, loaded %d tickets into %s",
        stats["read"], stats["duplicates"], stats["fixed"], loaded, DB_PATH.name,
    )
