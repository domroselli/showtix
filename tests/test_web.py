import re

from app.web import dollars

NIGHT = "2026-11-12"
SHOW = "Laugh Lines Live"


def total_on_page(html: str) -> str:
    return re.search(r'id="total">([^<]+)<', html).group(1)


def test_dollars_formats_cents():
    assert dollars(0) == "$0.00"
    assert dollars(5) == "$0.05"
    assert dollars(25044) == "$250.44"
    assert dollars(123456789) == "$1,234,567.89"
    assert dollars(-2400) == "−$24.00"


def test_home_page_lists_shows_and_performances(client, performance_id):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Laugh Lines Live" in resp.text
    assert "Comedy · Neon Mesa Showroom" in resp.text
    assert f'href="/performances/{performance_id(SHOW, NIGHT)}"' in resp.text
    assert "Thu Nov 12, 8:00 PM" in resp.text


def test_performance_page_shows_tiers(client, performance_id):
    resp = client.get(f"/performances/{performance_id(SHOW, NIGHT)}")
    assert resp.status_code == 200
    for text in ("GA", "$69.00", "Premium", "$120.00", "VIP", "$199.99", ">360<", "Get quote"):
        assert text in resp.text


def test_sold_out_tier_cannot_be_chosen(client, performance_id, tier_id):
    perf = performance_id("Gravity Optional", "2026-11-14")
    client.post(f"/performances/{perf}/orders", data={
        f"qty_{tier_id('Gravity Optional', '2026-11-14', 'VIP')}": "2", "email": "fan@example.com",
    })
    resp = client.get(f"/performances/{perf}")
    assert "Sold out" in resp.text


def test_quote_page_total_matches_the_api(client, performance_id, tier_id):
    perf = performance_id(SHOW, NIGHT)
    ga, premium = tier_id(SHOW, NIGHT, "GA"), tier_id(SHOW, NIGHT, "Premium")
    api = client.post("/orders/quote", json={
        "performance_id": perf,
        "items": [{"tier_id": ga, "qty": 1}, {"tier_id": premium, "qty": 2}],
        "promo_code": "LOCALS10",
    }).json()

    resp = client.post(f"/performances/{perf}/quote", data={
        f"qty_{ga}": "1", f"qty_{premium}": "2", "promo_code": "LOCALS10",
    })
    assert resp.status_code == 200
    assert total_on_page(resp.text) == dollars(api["total_cents"])
    for line in api["pricing_lines"]:
        assert f"<td>{line['label']}</td>" in resp.text
        assert dollars(line["amount_cents"]) in resp.text
    assert "Place order" in resp.text


def test_expired_promo_error_shows_inline(client, performance_id, tier_id):
    perf = performance_id(SHOW, NIGHT)
    resp = client.post(f"/performances/{perf}/quote", data={
        f"qty_{tier_id(SHOW, NIGHT, 'GA')}": "1", "promo_code": "SPRING24",
    })
    assert resp.status_code == 400
    assert "Promo code SPRING24 expired on 2024-05-31" in resp.text
    assert 'value="SPRING24"' in resp.text  # form keeps what was typed


def test_ticket_limit_error_shows_inline(client, performance_id, tier_id):
    perf = performance_id(SHOW, NIGHT)
    resp = client.post(f"/performances/{perf}/quote", data={f"qty_{tier_id(SHOW, NIGHT, 'GA')}": "9"})
    assert resp.status_code == 400
    assert "An order can have at most 8 tickets; this one has 9" in resp.text


def test_sold_out_error_shows_inline(client, performance_id, tier_id):
    perf = performance_id("Gravity Optional", "2026-11-14")
    resp = client.post(f"/performances/{perf}/quote", data={
        f"qty_{tier_id('Gravity Optional', '2026-11-14', 'VIP')}": "3",
    })
    assert resp.status_code == 400
    assert "Only 2 VIP seats left; requested 3" in resp.text


def test_empty_cart_error_shows_inline(client, performance_id):
    resp = client.post(f"/performances/{performance_id(SHOW, NIGHT)}/quote", data={})
    assert resp.status_code == 400
    assert "Choose at least one ticket" in resp.text


def test_place_order_shows_the_stored_order(client, conn, performance_id, tier_id):
    perf = performance_id(SHOW, NIGHT)
    resp = client.post(
        f"/performances/{perf}/orders",
        data={f"qty_{tier_id(SHOW, NIGHT, 'VIP')}": "1", "email": "fan@example.com"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    order_url = resp.headers["location"]
    order_id = int(order_url.rsplit("/", 1)[1])

    page = client.get(order_url)
    assert page.status_code == 200
    assert f"Order {order_id}: paid" in page.text
    stored = conn.execute("SELECT total_cents FROM orders WHERE id = ?", (order_id,)).fetchone()
    assert total_on_page(page.text) == dollars(stored["total_cents"])
    for label in ("Subtotal", "Discount", "Service fees", "Tax", "Total"):
        assert f"<td>{label}</td>" in page.text


def test_place_order_needs_an_email(client, conn, performance_id, tier_id):
    resp = client.post(f"/performances/{performance_id(SHOW, NIGHT)}/orders", data={
        f"qty_{tier_id(SHOW, NIGHT, 'GA')}": "1", "email": "",
    })
    assert resp.status_code == 400
    assert "Enter a valid email address" in resp.text
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 3
