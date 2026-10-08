import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "helpdesk.db"
QUERIES_DIR = ROOT / "sql" / "queries"


def question_of(sql_text):
    """Return the text after '-- Question:' in the file's header comment."""
    for line in sql_text.splitlines():
        if line.startswith("-- Question:"):
            return line.removeprefix("-- Question:").strip()
    return "(no question written)"


def format_table(columns, rows):
    """Format query results as an aligned text table."""
    cells = [[str(value) for value in row] for row in rows]
    widths = [max([len(col)] + [len(row[i]) for row in cells]) for i, col in enumerate(columns)]
    header = "  ".join(col.ljust(width) for col, width in zip(columns, widths))
    divider = "  ".join("-" * width for width in widths)
    body = ["  ".join(cell.ljust(width) for cell, width in zip(row, widths)) for row in cells]
    return "\n".join([header, divider, *body])


def run_query(conn, path):
    sql_text = path.read_text(encoding="utf-8")
    cursor = conn.execute(sql_text)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    print(f"\n{path.stem}: {question_of(sql_text)}")
    print(format_table(columns, rows))


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    for path in sorted(QUERIES_DIR.glob("*.sql")):
        run_query(conn, path)
    conn.close()
