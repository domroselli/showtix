"""Seat availability per tier.

Seats sold = sum of order line qty on orders that aren't cancelled.
Nothing stores a running count, so cancelling an order releases its seats.
"""

import sqlite3

from app.errors import Conflict, NotFound
from app.models import Availability, TierAvailability


def tiers_for_performance(conn: sqlite3.Connection, performance_id: int) -> list[TierAvailability]:
    rows = conn.execute(
        """
        SELECT t.id, t.name, t.price_cents, t.seats_total,
               COALESCE(SUM(CASE WHEN o.status != 'cancelled' THEN l.qty END), 0) AS seats_sold
        FROM price_tiers t
        LEFT JOIN order_lines l ON l.tier_id = t.id
        LEFT JOIN orders o ON o.id = l.order_id
        WHERE t.performance_id = ?
        GROUP BY t.id
        ORDER BY t.price_cents
        """,
        (performance_id,),
    ).fetchall()
    return [
        TierAvailability(
            tier_id=r["id"],
            name=r["name"],
            price_cents=r["price_cents"],
            seats_total=r["seats_total"],
            seats_sold=r["seats_sold"],
            seats_left=r["seats_total"] - r["seats_sold"],
        )
        for r in rows
    ]


def availability(conn: sqlite3.Connection, performance_id: int) -> Availability:
    perf = conn.execute(
        "SELECT id, starts_at FROM performances WHERE id = ?", (performance_id,)
    ).fetchone()
    if perf is None:
        raise NotFound(f"Performance {performance_id} not found")
    return Availability(
        performance_id=perf["id"],
        starts_at=perf["starts_at"],
        tiers=tiers_for_performance(conn, performance_id),
    )


def check_seats(tier: TierAvailability, qty: int) -> None:
    """Raise Conflict if buying `qty` seats would oversell the tier."""
    if qty > tier.seats_left:
        raise Conflict(f"Only {tier.seats_left} {tier.name} seats left; requested {qty}")
