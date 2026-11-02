"""Tests that check how separately-tested rules combine."""

NIGHT = "2026-11-12"
SHOW = "Laugh Lines Live"


def cart(performance_id, items, promo_code=None):
    body = {"email": "fan@example.com", "performance_id": performance_id, "items": items}
    if promo_code:
        body["promo_code"] = promo_code
    return body


def test_promo_order_is_taxed_after_the_discount(client, performance_id, tier_id):
    body = cart(
        performance_id(SHOW, NIGHT),
        [{"tier_id": tier_id(SHOW, NIGHT, "Premium"), "qty": 2}],
        "LOCALS10",
    )
    for resp in (client.post("/orders/quote", json=body), client.post("/orders", json=body)):
        priced = resp.json()
        assert priced["subtotal_cents"] == 24000
        assert priced["discount_cents"] == 2400
        assert priced["fees_cents"] == 1500
        assert priced["tax_cents"] == 1944
        assert priced["total_cents"] == 25044


def test_fixed_promo_order_is_taxed_after_the_discount(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), [{"tier_id": tier_id(SHOW, NIGHT, "GA"), "qty": 1}], "WELCOME5")
    q = client.post("/orders/quote", json=body).json()
    assert q["tax_cents"] == 576  # 9% of 6400
    assert q["total_cents"] == 6400 + 750 + 576


def test_stored_order_matches_its_quote(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), [{"tier_id": tier_id(SHOW, NIGHT, "GA"), "qty": 1}], "LOCALS10")
    q = client.post("/orders/quote", json=body).json()
    order = client.post("/orders", json=body).json()
    assert q["tax_cents"] == 559  # 9% of 6210 = 558.9, rounded half up
    assert order["tax_cents"] == q["tax_cents"]
    assert order["total_cents"] == q["total_cents"]


def test_stored_no_promo_order_matches_its_quote(client, performance_id, tier_id):
    body = cart(performance_id(SHOW, NIGHT), [{"tier_id": tier_id(SHOW, NIGHT, "Premium"), "qty": 5}])
    q = client.post("/orders/quote", json=body).json()
    order = client.post("/orders", json=body).json()
    assert q["tax_cents"] == 5400  # 9% of 60000
    assert order["tax_cents"] == q["tax_cents"]
    assert order["total_cents"] == 69150  # 60000 + 3750 + 5400


def test_ticket_limit_counts_every_line(client, performance_id, tier_id):
    body = cart(
        performance_id(SHOW, NIGHT),
        [
            {"tier_id": tier_id(SHOW, NIGHT, "GA"), "qty": 5},
            {"tier_id": tier_id(SHOW, NIGHT, "VIP"), "qty": 5},
        ],
    )
    resp = client.post("/orders", json=body)
    assert resp.status_code == 422
    assert "at most 8 tickets" in resp.text


def test_end_date_includes_evening_shows_on_that_day(client):
    resp = client.get("/shows?start_date=2026-11-15&end_date=2026-11-15")
    assert len(resp.json()) == 8


def test_end_date_on_the_first_night_includes_evening_shows(client):
    resp = client.get("/shows?end_date=2026-11-10")
    assert len(resp.json()) == 8
