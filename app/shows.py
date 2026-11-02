"""Show listing and detail."""

import sqlite3
from datetime import date, datetime, time, timedelta

from app.errors import BadRequest, NotFound
from app.models import Performance, ShowDetail, ShowSummary

SHOW_COLUMNS = """
    SELECT s.id, s.title, s.category, v.name AS venue
    FROM shows s JOIN venues v ON v.id = s.venue_id
"""


def list_shows(
    conn: sqlite3.Connection, start_date: date | None = None, end_date: date | None = None
) -> list[ShowSummary]:
    """Shows with at least one performance between start_date and end_date, both inclusive."""
    if start_date and end_date and start_date > end_date:
        raise BadRequest("start_date must be on or before end_date")

    conditions, params = [], []
    if start_date:
        conditions.append("p.starts_at >= ?")
        params.append(datetime.combine(start_date, time.min).isoformat())
    if end_date:
        # Everything before midnight at the start of the next day, so evening shows count.
        conditions.append("p.starts_at < ?")
        params.append(datetime.combine(end_date + timedelta(days=1), time.min).isoformat())

    sql = SHOW_COLUMNS
    if conditions:
        sql += f"""
            WHERE EXISTS (
                SELECT 1 FROM performances p
                WHERE p.show_id = s.id AND {" AND ".join(conditions)}
            )
        """
    sql += " ORDER BY s.title"
    return [ShowSummary(**dict(r)) for r in conn.execute(sql, params)]


def show_for_performance(conn: sqlite3.Connection, performance_id: int) -> ShowSummary:
    row = conn.execute(
        SHOW_COLUMNS + " JOIN performances p ON p.show_id = s.id WHERE p.id = ?", (performance_id,)
    ).fetchone()
    if row is None:
        raise NotFound(f"Performance {performance_id} not found")
    return ShowSummary(**dict(row))


def show_detail(conn: sqlite3.Connection, show_id: int, now: datetime) -> ShowDetail:
    """A show with its performances that haven't started yet."""
    row = conn.execute(SHOW_COLUMNS + " WHERE s.id = ?", (show_id,)).fetchone()
    if row is None:
        raise NotFound(f"Show {show_id} not found")
    perfs = conn.execute(
        """
        SELECT id, starts_at FROM performances
        WHERE show_id = ? AND starts_at >= ?
        ORDER BY starts_at
        """,
        (show_id, now.isoformat()),
    ).fetchall()
    return ShowDetail(**dict(row), performances=[Performance(**dict(p)) for p in perfs])
