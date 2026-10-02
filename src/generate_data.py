import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

CATEGORIES = ["account", "network", "printer", "software", "hardware"]
CATEGORY_WEIGHTS = [25, 20, 12, 30, 13]
PRIORITIES = ["low", "medium", "high", "critical"]
PRIORITY_WEIGHTS = [35, 40, 20, 5]
RESOLUTION_RANGE = {"critical": (0.5, 6), "high": (1, 12), "medium": (2, 30), "low": (4, 72)}
AGENT_SPEED = {"Anna K.": 0.8, "Piotr W.": 1.0, "Marta S.": 0.9, "Tomasz B.": 1.2, "Ola N.": 1.1}
WEEKDAY_WEIGHTS = [30, 20, 18, 16, 14, 1, 1]  # Monday ... Sunday
HOUR_WEIGHTS = [1, 1, 1, 1, 1, 1, 2, 5, 12, 14, 12, 10, 8, 10, 10, 8, 6, 3, 2, 1, 1, 1, 1, 1]

START = datetime(2026, 1, 1)
DAYS = [START + timedelta(days=i) for i in range(180)]
DAY_WEIGHTS = [WEEKDAY_WEIGHTS[d.weekday()] for d in DAYS]
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"


def random_created_at():
    day = random.choices(DAYS, weights=DAY_WEIGHTS)[0]
    hour = random.choices(range(24), weights=HOUR_WEIGHTS)[0]
    return day.replace(hour=hour, minute=random.randrange(60))


def make_ticket(ticket_id):
    priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0]
    agent = random.choice(list(AGENT_SPEED))
    status = random.choices(["resolved", "in_progress", "open"], weights=[90, 6, 4])[0]
    if status == "resolved":
        low, high = RESOLUTION_RANGE[priority]
        resolution_hours = round(random.uniform(low, high) * AGENT_SPEED[agent], 1)
    else:
        resolution_hours = ""
    return {
        "ticket_id": ticket_id,
        "created_at": random_created_at().isoformat(timespec="minutes"),
        "category": random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS)[0],
        "priority": priority,
        "status": status,
        "agent": agent,
        "resolution_hours": resolution_hours,
    }


def write_csv(tickets, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tickets[0].keys())
        writer.writeheader()
        writer.writerows(tickets)


if __name__ == "__main__":
    tickets = [make_ticket(i) for i in range(1, 1001)]
    write_csv(tickets, OUTPUT_PATH)
    print(f"Wrote {len(tickets)} tickets to {OUTPUT_PATH}")
