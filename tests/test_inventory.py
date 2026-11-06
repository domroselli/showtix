NIGHT = "2026-11-12"
SHOW = "Laugh Lines Live"  # Neon Mesa Showroom, capacity 600


def buy(client, performance_id, tier_id, qty):
    return client.post(
        "/orders",
        json={
            "email": "fan@example.com",
            "performance_id": performance_id,
            "items": [{"tier_id": tier_id, "qty": qty}],
        },
    )


def seats(client, performance_id):
    body = client.get(f"/performances/{performance_id}/availability").json()
    return {t["name"]: t for t in body["tiers"]}


def test_availability_lists_every_tier(client, performance_id):
    tiers = seats(client, performance_id(SHOW, NIGHT))
    assert [(name, t["price_cents"], t["seats_total"], t["seats_left"]) for name, t in tiers.items()] == [
        ("GA", 6900, 360, 360),
        ("Premium", 12000, 180, 180),
        ("VIP", 19999, 60, 60),
    ]


def test_nearly_sold_out_tier_has_two_seats_left(client, performance_id):
    vip = seats(client, performance_id("Gravity Optional", "2026-11-14"))["VIP"]
    assert vip["seats_total"] == 14
    assert vip["seats_sold"] == 12
    assert vip["seats_left"] == 2


def test_buying_takes_seats(client, performance_id, tier_id):
    perf = performance_id(SHOW, NIGHT)
    assert buy(client, perf, tier_id(SHOW, NIGHT, "Premium"), 3).status_code == 201
    premium = seats(client, perf)["Premium"]
    assert premium["seats_sold"] == 3
    assert premium["seats_left"] == 177


def test_cancelling_releases_seats(client, performance_id, tier_id):
    perf = performance_id(SHOW, NIGHT)
    order = buy(client, perf, tier_id(SHOW, NIGHT, "GA"), 4).json()
    assert seats(client, perf)["GA"]["seats_left"] == 356

    client.post(f"/orders/{order['id']}/cancel")
    assert seats(client, perf)["GA"]["seats_left"] == 360


def test_cannot_oversell_a_tier(client, performance_id, tier_id):
    perf = performance_id("Gravity Optional", "2026-11-14")
    vip = tier_id("Gravity Optional", "2026-11-14", "VIP")

    resp = buy(client, perf, vip, 3)
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Only 2 VIP seats left; requested 3"
    assert seats(client, perf)["VIP"]["seats_left"] == 2


def test_can_buy_the_last_seats(client, performance_id, tier_id):
    perf = performance_id("Gravity Optional", "2026-11-14")
    assert buy(client, perf, tier_id("Gravity Optional", "2026-11-14", "VIP"), 2).status_code == 201
    assert seats(client, perf)["VIP"]["seats_left"] == 0


def test_unknown_performance_is_404(client):
    assert client.get("/performances/99999/availability").status_code == 404
