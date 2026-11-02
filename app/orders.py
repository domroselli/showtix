"""Quote -> order -> cancel. Money math is delegated to pricing.py."""

import sqlite3
from collections import Counter
from datetime import datetime

from app import inventory, pricing, promos
from app.errors import BadRequest, Conflict, NotFound
from app.models import Order, OrderRequest, PricingLine, Quote, QuoteLine, QuoteRequest


def quote(conn: sqlite3.Connection, req: QuoteRequest, now: datetime) -> Quote:
    """Price a cart without writing anything."""
    if conn.execute(
        "SELECT 1 FROM performances WHERE id = ?", (req.performance_id,)
    ).fetchone() is None:
        raise NotFound(f"Performance {req.performance_id} not found")

    # Merge repeated tiers so availability is checked against the full quantity.
    qty_by_tier = Counter()
    for item in req.items:
        qty_by_tier[item.tier_id] += item.qty

    tiers = {t.tier_id: t for t in inventory.tiers_for_performance(conn, req.performance_id)}
    lines = []
    for tier_id, qty in qty_by_tier.items():
        tier = tiers.get(tier_id)
        if tier is None:
            raise BadRequest(f"Tier {tier_id} is not sold for performance {req.performance_id}")
        inventory.check_seats(tier, qty)
        lines.append(
            QuoteLine(
                tier_id=tier_id,
                tier_name=tier.name,
                qty=qty,
                unit_price_cents=tier.price_cents,
                line_total_cents=pricing.line_total(qty, tier.price_cents),
            )
        )

    promo = promos.find_valid_promo(conn, req.promo_code, now) if req.promo_code else None
    breakdown = pricing.price_order(
        [pricing.Line(qty=l.qty, unit_price_cents=l.unit_price_cents) for l in lines], promo
    )
    promo_code = promo.code if promo else None
    return Quote(
        performance_id=req.performance_id,
        promo_code=promo_code,
        lines=lines,
        pricing_lines=_pricing_lines(breakdown, promo_code),
        subtotal_cents=breakdown.subtotal_cents,
        discount_cents=breakdown.discount_cents,
        fees_cents=breakdown.fees_cents,
        tax_cents=breakdown.tax_cents,
        total_cents=breakdown.total_cents,
    )


def create_order(conn: sqlite3.Connection, req: OrderRequest, now: datetime) -> Order:
    """Create a paid order at the quoted price and take the seats."""
    # Lock the database so two buyers can't both take the last seats.
    conn.execute("BEGIN IMMEDIATE")
    try:
        q = quote(conn, req, now)
        cur = conn.execute(
            """
            INSERT INTO orders (email, performance_id, status, promo_code, subtotal_cents,
                                discount_cents, fees_cents, tax_cents, total_cents, created_at)
            VALUES (?, ?, 'paid', ?, ?, ?, ?, ?, ?, ?)
            """,
            (req.email, q.performance_id, q.promo_code, q.subtotal_cents, q.discount_cents,
             q.fees_cents, q.tax_cents, q.total_cents, now.isoformat()),
        )
        order_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO order_lines (order_id, tier_id, qty, unit_price_cents) VALUES (?, ?, ?, ?)",
            [(order_id, l.tier_id, l.qty, l.unit_price_cents) for l in q.lines],
        )
        if q.promo_code:
            promos.record_use(conn, q.promo_code)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return get_order(conn, order_id)


def cancel_order(conn: sqlite3.Connection, order_id: int) -> Order:
    """Cancel an order. Its seats are released because seat counts skip cancelled orders."""
    order = get_order(conn, order_id)
    if order.status == "cancelled":
        raise Conflict(f"Order {order_id} is already cancelled")
    with conn:
        conn.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
    return get_order(conn, order_id)


def get_order(conn: sqlite3.Connection, order_id: int) -> Order:
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise NotFound(f"Order {order_id} not found")
    lines = conn.execute(
        """
        SELECT l.tier_id, t.name AS tier_name, l.qty, l.unit_price_cents
        FROM order_lines l JOIN price_tiers t ON t.id = l.tier_id
        WHERE l.order_id = ?
        ORDER BY l.id
        """,
        (order_id,),
    ).fetchall()
    # Rebuilt from the stored totals, never re-priced.
    stored = pricing.PriceBreakdown(
        subtotal_cents=row["subtotal_cents"],
        discount_cents=row["discount_cents"],
        fees_cents=row["fees_cents"],
        tax_cents=row["tax_cents"],
        total_cents=row["total_cents"],
    )
    return Order(
        **dict(row),
        lines=[
            QuoteLine(**dict(l), line_total_cents=pricing.line_total(l["qty"], l["unit_price_cents"]))
            for l in lines
        ],
        pricing_lines=_pricing_lines(stored, row["promo_code"]),
    )


def _pricing_lines(breakdown: pricing.PriceBreakdown, promo_code: str | None) -> list[PricingLine]:
    return [
        PricingLine(label=line.label, amount_cents=line.amount_cents)
        for line in pricing.pricing_lines(breakdown, promo_code)
    ]
