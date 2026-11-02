NIGHT = "2026-11-12"
SHOW = "Laugh Lines Live"


def cart(performance_id, tier_id, qty, promo_code=None, email="fan@example.com"):
    body = {
        "email": email,
        "performance_id": performance_id,
        "items": [{"tier_id": tier_id, "qty": qty}],
    }
    if promo_code:
        body["promo_code"] = promo_code
    return body


def order_count(conn):
    return conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]


def promo_uses(conn, code):
    return conn.execute("SELECT uses FROM promo_codes WHERE code = ?", (code,)).fetchone()[0]


# --- quotes ---


def test_quote_breaks_down_the_price(client, performance_id, tier_id):
    premium = tier_id(SHOW, NIGHT, "Premium")
    resp = client.post("/orders/quote", json=cart(performance_id(SHOW, NIGHT), premium, 2))
    assert resp.status_code == 200
    q = resp.json()
    assert q["lines"] == [
        {"tier_id": premium, "tier_name": "Premium", "qty": 2,
         "unit_price_cents": 12000, "line_total_cents": 24000}
    ]
    assert q["subtotal_cents"] == 24000
    assert q["discount_cents"] == 0
    assert q["fees_cents"] == 1500
    assert q["tax_cents"] == 2160
    assert q["total_cents"] == 27660
    assert q["pricing_lines"] == [
        {"label": "Subtotal", "amount_cents": 24000},
        {"label": "Discount", "amount_cents": 0},
        {"label": "Service fees", "amount_cents": 1500},
        {"label": "Tax", "amount_cents": 2160},
        {"label": "Total", "amount_cents": 27660},
    ]


def test_quote_writes_nothing(client, conn, performance_id, tier_id):
    client.post(
        "/orders/quote",
        json=cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 2, "LOCALS10"),
    )
    assert order_count(conn) == 3  # only the seeded orders
    assert promo_uses(conn, "LOCALS10") == 0


def test_repeated_tier_lines_are_merged(client, performance_id, tier_id):
    ga = tier_id(SHOW, NIGHT, "GA")
    body = cart(performance_id(SHOW, NIGHT), ga, 1)
    body["items"].append({"tier_id": ga, "qty": 2})
    q = client.post("/orders/quote", json=body).json()
    assert [(l["tier_id"], l["qty"]) for l in q["lines"]] == [(ga, 3)]
    assert q["subtotal_cents"] == 20700


# --- promos (discount line only) ---


def test_percent_promo_discounts_the_quote(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "Premium"), 2, "LOCALS10")
    q = client.post("/orders/quote", json=body).json()
    assert q["promo_code"] == "LOCALS10"
    assert q["discount_cents"] == 2400
    assert q["pricing_lines"][1] == {"label": "Discount (LOCALS10)", "amount_cents": -2400}


def test_fixed_promo_discounts_the_quote(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 1, "WELCOME5")
    assert client.post("/orders/quote", json=body).json()["discount_cents"] == 500


def test_promo_codes_ignore_case_and_spaces(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 1, " welcome5 ")
    q = client.post("/orders/quote", json=body).json()
    assert q["promo_code"] == "WELCOME5"
    assert q["discount_cents"] == 500


def test_expired_promo_is_rejected(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 1, "SPRING24")
    resp = client.post("/orders/quote", json=body)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Promo code SPRING24 expired on 2024-05-31"


def test_unknown_promo_is_rejected(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 1, "FREESHOW")
    resp = client.post("/orders/quote", json=body)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Promo code FREESHOW does not exist"


def test_creating_an_order_counts_a_promo_use(client, conn, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 1, "WELCOME5")
    assert client.post("/orders", json=body).status_code == 201
    assert promo_uses(conn, "WELCOME5") == 1


def test_order_records_its_promo_code(client, conn, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 1, " welcome5 ")
    order = client.post("/orders", json=body).json()
    assert order["promo_code"] == "WELCOME5"
    stored = conn.execute("SELECT promo_code FROM orders WHERE id = ?", (order["id"],)).fetchone()
    assert stored["promo_code"] == "WELCOME5"


def test_cancelled_order_keeps_its_promo_code(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 1, "LOCALS10")
    order = client.post("/orders", json=body).json()
    assert client.post(f"/orders/{order['id']}/cancel").json()["promo_code"] == "LOCALS10"


# --- orders ---


def test_create_order_stores_a_paid_order(client, performance_id, tier_id):
    perf = performance_id(SHOW, NIGHT)
    premium = tier_id(SHOW, NIGHT, "Premium")
    resp = client.post("/orders", json=cart(perf, premium, 3))
    assert resp.status_code == 201
    order = resp.json()
    assert order["status"] == "paid"
    assert order["promo_code"] is None
    assert order["email"] == "fan@example.com"
    assert order["performance_id"] == perf
    assert order["created_at"] == "2026-11-01T12:00:00"
    assert order["lines"] == [
        {"tier_id": premium, "tier_name": "Premium", "qty": 3,
         "unit_price_cents": 12000, "line_total_cents": 36000}
    ]
    assert order["subtotal_cents"] == 36000
    assert order["discount_cents"] == 0
    assert order["fees_cents"] == 2250
    assert order["tax_cents"] == 3240
    assert order["total_cents"] == 41490
    assert order["pricing_lines"] == [
        {"label": "Subtotal", "amount_cents": 36000},
        {"label": "Discount", "amount_cents": 0},
        {"label": "Service fees", "amount_cents": 2250},
        {"label": "Tax", "amount_cents": 3240},
        {"label": "Total", "amount_cents": 41490},
    ]


def test_order_keeps_the_price_paid_after_a_price_change(client, conn, performance_id, tier_id):
    ga = tier_id(SHOW, NIGHT, "GA")
    order = client.post("/orders", json=cart(performance_id(SHOW, NIGHT), ga, 1)).json()
    with conn:
        conn.execute("UPDATE price_tiers SET price_cents = 9900 WHERE id = ?", (ga,))
    cancelled = client.post(f"/orders/{order['id']}/cancel").json()
    assert cancelled["lines"][0]["unit_price_cents"] == 6900
    assert cancelled["subtotal_cents"] == 6900
    assert cancelled["pricing_lines"][0] == {"label": "Subtotal", "amount_cents": 6900}


def test_eight_tickets_is_allowed(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 8)
    assert client.post("/orders", json=body).status_code == 201


def test_nine_tickets_is_rejected(client, conn, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 9)
    resp = client.post("/orders", json=body)
    assert resp.status_code == 422
    assert "at most 8 tickets" in resp.text
    assert order_count(conn) == 3


def test_zero_tickets_is_rejected(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 0)
    assert client.post("/orders", json=body).status_code == 422


def test_tier_must_belong_to_the_performance(client, performance_id, tier_id):
    other_night = tier_id(SHOW, "2026-11-13", "GA")
    resp = client.post("/orders", json=cart(performance_id(SHOW, NIGHT), other_night, 1))
    assert resp.status_code == 400
    assert "is not sold for performance" in resp.json()["detail"]


def test_unknown_performance_is_404(client, tier_id):
    assert client.post("/orders", json=cart(99999, tier_id(SHOW, NIGHT, "GA"), 1)).status_code == 404


# --- cancel ---


def test_cancel_marks_the_order_cancelled(client, performance_id, tier_id):
    order = client.post("/orders", json=cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 2)).json()
    resp = client.post(f"/orders/{order['id']}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


def test_cancelling_twice_is_rejected(client, performance_id, tier_id):
    order = client.post("/orders", json=cart(performance_id(SHOW, NIGHT), tier_id(SHOW, NIGHT, "GA"), 2)).json()
    client.post(f"/orders/{order['id']}/cancel")
    resp = client.post(f"/orders/{order['id']}/cancel")
    assert resp.status_code == 409
    assert resp.json()["detail"] == f"Order {order['id']} is already cancelled"


def test_cancel_unknown_order_is_404(client):
    assert client.post("/orders/99999/cancel").status_code == 404
