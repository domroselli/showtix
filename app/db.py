"""SQLite connection and schema."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "showtix.db"

SCHEMA = """
CREATE TABLE venues (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE shows (
    id       INTEGER PRIMARY KEY,
    title    TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('magic', 'comedy', 'music', 'acrobatics')),
    venue_id INTEGER NOT NULL REFERENCES venues(id)
);

-- starts_at is local Vegas time, stored as ISO text: 2026-11-10T20:00:00
CREATE TABLE performances (
    id        INTEGER PRIMARY KEY,
    show_id   INTEGER NOT NULL REFERENCES shows(id),
    starts_at TEXT NOT NULL
);

CREATE TABLE price_tiers (
    id             INTEGER PRIMARY KEY,
    performance_id INTEGER NOT NULL REFERENCES performances(id),
    name           TEXT NOT NULL,
    price_cents    INTEGER NOT NULL,
    seats_total    INTEGER NOT NULL
);

CREATE TABLE orders (
    id             INTEGER PRIMARY KEY,
    email          TEXT NOT NULL,
    performance_id INTEGER NOT NULL REFERENCES performances(id),
    status         TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'cancelled')),
    promo_code     TEXT REFERENCES promo_codes(code),
    subtotal_cents INTEGER NOT NULL,
    discount_cents INTEGER NOT NULL,
    fees_cents     INTEGER NOT NULL,
    tax_cents      INTEGER NOT NULL,
    total_cents    INTEGER NOT NULL,
    created_at     TEXT NOT NULL
);

CREATE TABLE order_lines (
    id               INTEGER PRIMARY KEY,
    order_id         INTEGER NOT NULL REFERENCES orders(id),
    tier_id          INTEGER NOT NULL REFERENCES price_tiers(id),
    qty              INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL
);

-- kind 'percent': value is whole percent (10 = 10% off)
-- kind 'fixed':   value is cents (500 = $5.00 off)
-- valid_from / valid_to are inclusive ISO dates
CREATE TABLE promo_codes (
    code       TEXT PRIMARY KEY,
    kind       TEXT NOT NULL CHECK (kind IN ('percent', 'fixed')),
    value      INTEGER NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to   TEXT NOT NULL,
    max_uses   INTEGER,
    uses       INTEGER NOT NULL DEFAULT 0
);
"""


def connect(path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def get_db():
    """FastAPI dependency: one connection per request."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
