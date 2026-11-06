"""Fictional venues, shows, performances, tiers and promos.

Rebuild the local database from scratch: uv run python -m app.seed
"""

import sqlite3
from datetime import date, datetime, time, timedelta

from app import db, orders
from app.models import CartItem, OrderRequest

FIRST_NIGHT = date(2026, 11, 10)
NIGHTS = 14  # Nov 10 through Nov 23, 2026

VENUES = [
    # name, capacity
    ("Desert Bloom Theater", 900),
    ("Neon Mesa Showroom", 600),
    ("Silver Coyote Hall", 1200),
]

SHOWS = [
    # title, category, venue index, curtain time
    ("The Vanishing Ace", "magic", 0, time(19, 0)),
    ("Smoke & Sleight", "magic", 1, time(21, 30)),
    ("Laugh Lines Live", "comedy", 1, time(20, 0)),
    ("Stand-Up Saloon", "comedy", 0, time(21, 30)),
    ("Neon Nights Revue", "music", 2, time(20, 0)),
    ("Desert Strings", "music", 0, time(19, 30)),
    ("Skyline Circus", "acrobatics", 2, time(19, 0)),
    ("Gravity Optional", "acrobatics", 2, time(20, 0)),
]

# name, price, share of venue capacity
TIERS = [
    ("GA", 6900, 0.60),
    ("Premium", 12000, 0.30),
    ("VIP", 19999, 0.10),
]

PROMOS = [
    # code, kind, value, valid_from, valid_to, max_uses
    ("LOCALS10", "percent", 10, "2026-01-01", "2027-12-31", 500),
    ("WELCOME5", "fixed", 500, "2026-01-01", "2027-12-31", 1000),
    ("SPRING24", "percent", 20, "2024-03-01", "2024-05-31", 200),
]

# One tier left nearly sold out: a small VIP box with 2 of 14 seats left.
NEARLY_SOLD_OUT = ("Gravity Optional", date(2026, 11, 14), "VIP")
NEARLY_SOLD_OUT_SEATS = 14
NEARLY_SOLD_OUT_ORDERS = [4, 4, 4]

SEEDED_AT = datetime(2026, 10, 28, 12, 0)


def seed(conn: sqlite3.Connection) -> None:
    with conn:
        conn.executemany("INSERT INTO venues (name, capacity) VALUES (?, ?)", VENUES)
        venue_ids = [r["id"] for r in conn.execute("SELECT id FROM venues ORDER BY id")]
        conn.executemany(
            "INSERT INTO promo_codes (code, kind, value, valid_from, valid_to, max_uses) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            PROMOS,
        )

        for title, category, venue_index, curtain in SHOWS:
            capacity = VENUES[venue_index][1]
            show_id = conn.execute(
                "INSERT INTO shows (title, category, venue_id) VALUES (?, ?, ?)",
                (title, category, venue_ids[venue_index]),
            ).lastrowid
            for night in range(NIGHTS):
                day = FIRST_NIGHT + timedelta(days=night)
                perf_id = conn.execute(
                    "INSERT INTO performances (show_id, starts_at) VALUES (?, ?)",
                    (show_id, datetime.combine(day, curtain).isoformat()),
                ).lastrowid
                for name, price, share in TIERS:
                    seats = int(capacity * share)
                    if (title, day, name) == NEARLY_SOLD_OUT:
                        seats = NEARLY_SOLD_OUT_SEATS
                    conn.execute(
                        "INSERT INTO price_tiers (performance_id, name, price_cents, seats_total) "
                        "VALUES (?, ?, ?, ?)",
                        (perf_id, name, price, seats),
                    )

    title, day, tier_name = NEARLY_SOLD_OUT
    tier = conn.execute(
        """
        SELECT t.id, t.performance_id FROM price_tiers t
        JOIN performances p ON p.id = t.performance_id
        JOIN shows s ON s.id = p.show_id
        WHERE s.title = ? AND date(p.starts_at) = ? AND t.name = ?
        """,
        (title, day.isoformat(), tier_name),
    ).fetchone()
    for i, qty in enumerate(NEARLY_SOLD_OUT_ORDERS, start=1):
        orders.create_order(
            conn,
            OrderRequest(
                email=f"group{i}@example.com",
                performance_id=tier["performance_id"],
                items=[CartItem(tier_id=tier["id"], qty=qty)],
            ),
            SEEDED_AT,
        )


def reset_db() -> None:
    db.DB_PATH.unlink(missing_ok=True)
    conn = db.connect()
    try:
        db.create_schema(conn)
        seed(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    reset_db()
    print(f"Seeded {db.DB_PATH}")
