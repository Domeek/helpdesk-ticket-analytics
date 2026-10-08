import csv
import sqlite3
from pathlib import Path

from load_data import clean_ticket, load_into_db, read_and_clean

ROOT = Path(__file__).resolve().parent.parent
SLA_QUERY = (ROOT / "sql" / "queries" / "03_sla_breaches.sql").read_text(encoding="utf-8")

FIELDS = ["ticket_id", "created_at", "category", "priority", "status", "agent", "resolution_hours"]


def make_row(**changes):
    row = {
        "ticket_id": "1",
        "created_at": "2026-01-05 09:00:00",
        "category": "network",
        "priority": "high",
        "status": "resolved",
        "agent": "Anna K.",
        "resolution_hours": "5.0",
    }
    row.update(changes)
    return row


def test_clean_ticket_fixes_case_and_spaces():
    row = make_row(category="  NETWORK ", priority="High", agent="  anna k. ")
    cleaned, fixes = clean_ticket(row)
    assert cleaned["category"] == "network"
    assert cleaned["priority"] == "high"
    assert cleaned["agent"] == "Anna K."
    assert len(fixes) == 3


def test_clean_ticket_missing_category_becomes_unknown():
    cleaned, fixes = clean_ticket(make_row(category=""))
    assert cleaned["category"] == "unknown"
    assert "missing category -> unknown" in fixes


def test_clean_ticket_leaves_clean_row_alone():
    row = make_row()
    cleaned, fixes = clean_ticket(row)
    assert cleaned == row
    assert fixes == []


def test_read_and_clean_drops_duplicate_ticket_ids(tmp_path):
    path = tmp_path / "tickets.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(make_row(ticket_id="1"))
        writer.writerow(make_row(ticket_id="2"))
        writer.writerow(make_row(ticket_id="1", category="printer"))  # duplicate of 1

    tickets, stats = read_and_clean(path)

    assert [t["ticket_id"] for t in tickets] == ["1", "2"]
    assert tickets[0]["category"] == "network"  # the first copy wins
    assert stats["read"] == 3
    assert stats["duplicates"] == 1


def test_sla_query_counts_breaches_on_tiny_database(tmp_path):
    db_path = tmp_path / "test.db"
    tickets = [
        make_row(ticket_id="1", priority="critical", resolution_hours="3.0"),  # inside 4 h
        make_row(ticket_id="2", priority="critical", resolution_hours="5.0"),  # breached
        make_row(ticket_id="3", priority="low", resolution_hours="50.0"),      # breached (48 h)
        make_row(ticket_id="4", priority="low", status="open", resolution_hours=""),  # ignored
    ]
    load_into_db(tickets, db_path)

    conn = sqlite3.connect(db_path)
    result = {row[0]: row[1:] for row in conn.execute(SLA_QUERY)}
    conn.close()

    # priority: (sla_hours, resolved_tickets, breached, breached_pct)
    assert result["critical"] == (4, 2, 1, 50.0)
    assert result["low"] == (48, 1, 1, 100.0)
