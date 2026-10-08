import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "helpdesk.db"
REPORTS_DIR = ROOT / "reports"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SERIES = "#2a78d6"


def query(sql):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(sql).fetchall()
    conn.close()
    return rows


def new_chart(title, subtitle):
    """Create a figure with a title block and a quiet, minimal axis."""
    fig, ax = plt.subplots(figsize=(8, 4.4), dpi=150, facecolor=SURFACE)
    fig.subplots_adjust(top=0.78, bottom=0.12, left=0.16, right=0.95)
    fig.text(0.04, 0.95, title, fontsize=14, fontweight="bold", color=INK, va="top")
    fig.text(0.04, 0.885, subtitle, fontsize=10, color=INK_2, va="top")
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(AXIS)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=INK_2, length=0, labelsize=10)
    return fig, ax


def save(fig, name):
    path = REPORTS_DIR / name
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    print(f"Saved {path.relative_to(ROOT)}")


def chart_by_category():
    rows = query(
        "SELECT c.name, COUNT(*) AS n FROM tickets t "
        "JOIN categories c USING (category_id) GROUP BY c.name ORDER BY n DESC, c.name"
    )
    names = [name for name, _ in rows]
    counts = [n for _, n in rows]

    fig, ax = new_chart("Tickets by category", "1000 synthetic tickets, January to June 2026")
    ax.barh(names, counts, height=0.5, color=SERIES)
    ax.invert_yaxis()
    ax.set_xlim(0, max(counts) * 1.12)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    for y, n in enumerate(counts):
        ax.text(n + max(counts) * 0.015, y, str(n), va="center", color=INK, fontsize=10)
    save(fig, "tickets_by_category.png")


def chart_by_priority():
    order = ["critical", "high", "medium", "low"]
    rows = dict(
        query(
            "SELECT priority, ROUND(AVG(resolution_hours), 1) FROM tickets "
            "WHERE status = 'resolved' GROUP BY priority"
        )
    )
    values = [rows[p] for p in order]

    fig, ax = new_chart("Average resolution time by priority", "Resolved tickets only (910 of 1000)")
    ax.bar(order, values, width=0.45, color=SERIES)
    ax.set_ylim(0, max(values) * 1.15)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])
    for x, v in enumerate(values):
        ax.text(x, v + max(values) * 0.02, f"{v:.1f} h", ha="center", color=INK, fontsize=10)
    save(fig, "resolution_by_priority.png")


def chart_weekly_trend():
    rows = query(
        "SELECT strftime('%W', created_at) AS week, COUNT(*) FROM tickets GROUP BY week ORDER BY week"
    )
    rows = rows[1:-1]  # the first and last week are partial, so they are left out
    weeks = [int(week) for week, _ in rows]
    counts = [n for _, n in rows]

    fig, ax = new_chart("New tickets per week", "Weeks 1 to 25 of 2026 (partial first and last weeks left out)")
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.plot(weeks, counts, color=SERIES, linewidth=2, solid_capstyle="round", solid_joinstyle="round")
    dot = dict(marker="o", markersize=8, markerfacecolor=SERIES, markeredgecolor=SURFACE, markeredgewidth=2, linestyle="none")
    peak = counts.index(max(counts))
    ax.plot(weeks[-1], counts[-1], **dot)
    ax.plot(weeks[peak], counts[peak], **dot)
    ax.annotate(f"peak {counts[peak]}", (weeks[peak], counts[peak]), textcoords="offset points",
                xytext=(0, 9), ha="center", color=INK, fontsize=10)
    ax.annotate(f"{counts[-1]}", (weeks[-1], counts[-1]), textcoords="offset points",
                xytext=(10, 0), va="center", color=INK, fontsize=10)
    ax.set_ylim(0, 60)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_xticks([1, 5, 10, 15, 20, 25])
    ax.set_xlim(0.5, weeks[-1] + 1.5)
    ax.set_xlabel("Week of the year", color=INK_2, fontsize=10)
    ax.spines["left"].set_visible(False)
    save(fig, "weekly_trend.png")


if __name__ == "__main__":
    REPORTS_DIR.mkdir(exist_ok=True)
    chart_by_category()
    chart_by_priority()
    chart_weekly_trend()
