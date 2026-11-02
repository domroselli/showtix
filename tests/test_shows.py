from datetime import datetime

import pytest

ALL_SHOWS = [
    "Desert Strings",
    "Gravity Optional",
    "Laugh Lines Live",
    "Neon Nights Revue",
    "Skyline Circus",
    "Smoke & Sleight",
    "Stand-Up Saloon",
    "The Vanishing Ace",
]


def titles(resp):
    return [s["title"] for s in resp.json()]


def show_id(client, title):
    return next(s["id"] for s in client.get("/shows").json() if s["title"] == title)


def test_lists_every_show_by_title(client):
    resp = client.get("/shows")
    assert resp.status_code == 200
    assert titles(resp) == ALL_SHOWS


def test_show_summary_fields(client):
    show = next(s for s in client.get("/shows").json() if s["title"] == "Laugh Lines Live")
    assert show["category"] == "comedy"
    assert show["venue"] == "Neon Mesa Showroom"


def test_start_date_keeps_shows_still_running(client):
    assert titles(client.get("/shows?start_date=2026-11-20")) == ALL_SHOWS


def test_start_date_after_the_run_finds_nothing(client):
    assert client.get("/shows?start_date=2026-11-24").json() == []


def test_end_date_before_the_run_finds_nothing(client):
    assert client.get("/shows?end_date=2026-11-09").json() == []


def test_start_date_after_end_date_is_rejected(client):
    resp = client.get("/shows?start_date=2026-11-15&end_date=2026-11-12")
    assert resp.status_code == 400


def test_bad_date_is_rejected(client):
    assert client.get("/shows?start_date=next-week").status_code == 422


def test_show_detail_lists_upcoming_performances(client):
    resp = client.get(f"/shows/{show_id(client, 'Laugh Lines Live')}")
    assert resp.status_code == 200
    show = resp.json()
    assert show["title"] == "Laugh Lines Live"
    assert show["venue"] == "Neon Mesa Showroom"
    starts = [p["starts_at"] for p in show["performances"]]
    assert len(starts) == 14
    assert starts[0] == "2026-11-10T20:00:00"
    assert starts[-1] == "2026-11-23T20:00:00"


@pytest.mark.parametrize("now", [datetime(2026, 11, 20, 12, 0)])
def test_show_detail_hides_past_performances(client):
    show = client.get(f"/shows/{show_id(client, 'Laugh Lines Live')}").json()
    starts = [p["starts_at"] for p in show["performances"]]
    assert starts == [
        "2026-11-20T20:00:00",
        "2026-11-21T20:00:00",
        "2026-11-22T20:00:00",
        "2026-11-23T20:00:00",
    ]


def test_unknown_show_is_404(client):
    assert client.get("/shows/99999").status_code == 404
