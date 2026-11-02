"""Promo code lookup and validation."""

import sqlite3
from datetime import datetime

from app.errors import BadRequest
from app.pricing import Promo


def normalize(code: str) -> str:
    return code.strip().upper()


def find_valid_promo(conn: sqlite3.Connection, code: str, now: datetime) -> Promo:
    """Return the promo for `code`, or raise BadRequest if it can't be used today."""
    code = normalize(code)
    row = conn.execute("SELECT * FROM promo_codes WHERE code = ?", (code,)).fetchone()
    if row is None:
        raise BadRequest(f"Promo code {code} does not exist")

    today = now.date().isoformat()
    if today < row["valid_from"]:
        raise BadRequest(f"Promo code {code} is not valid until {row['valid_from']}")
    if today > row["valid_to"]:
        raise BadRequest(f"Promo code {code} expired on {row['valid_to']}")

    return Promo(code=row["code"], kind=row["kind"], value=row["value"])


def record_use(conn: sqlite3.Connection, code: str) -> None:
    conn.execute("UPDATE promo_codes SET uses = uses + 1 WHERE code = ?", (normalize(code),))
