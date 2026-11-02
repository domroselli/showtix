from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app import db, seed
from app.llm import get_llm
from app.main import app, get_db, get_now
from tests.fakes import FakeClaude

# Eval scripts call the real API and run by hand, never under pytest.
collect_ignore = ["evals"]

# Before the seeded run starts, so every performance is upcoming and every live promo is valid.
FIXED_NOW = datetime(2026, 11, 1, 12, 0)


@pytest.fixture
def conn():
    conn = db.connect(":memory:")
    db.create_schema(conn)
    seed.seed(conn)
    yield conn
    conn.close()


@pytest.fixture
def now():
    """Override with @pytest.mark.parametrize("now", [...]) or a local fixture to move the clock."""
    return FIXED_NOW


@pytest.fixture
def client(conn, now):
    app.dependency_overrides[get_db] = lambda: conn
    app.dependency_overrides[get_now] = lambda: now
    # Not used as a context manager, so the app's startup hook never touches showtix.db.
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _fake_llm():
    """Every test gets a fresh FakeClaude in place of the real client, so none can reach the API."""
    fake = FakeClaude()
    app.dependency_overrides[get_llm] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_llm, None)


@pytest.fixture
def fake_claude(_fake_llm):
    """The FakeClaude every route gets for this test. Queue replies before calling the route."""
    return _fake_llm


@pytest.fixture
def tier_id(conn):
    """Look up a seeded tier: tier_id("Laugh Lines Live", "2026-11-12", "GA")."""

    def lookup(title: str, day: str, tier_name: str) -> int:
        row = conn.execute(
            """
            SELECT t.id FROM price_tiers t
            JOIN performances p ON p.id = t.performance_id
            JOIN shows s ON s.id = p.show_id
            WHERE s.title = ? AND date(p.starts_at) = ? AND t.name = ?
            """,
            (title, day, tier_name),
        ).fetchone()
        return row["id"]

    return lookup


@pytest.fixture
def performance_id(conn):
    """Look up a seeded performance: performance_id("Laugh Lines Live", "2026-11-12")."""

    def lookup(title: str, day: str) -> int:
        row = conn.execute(
            """
            SELECT p.id FROM performances p JOIN shows s ON s.id = p.show_id
            WHERE s.title = ? AND date(p.starts_at) = ?
            """,
            (title, day),
        ).fetchone()
        return row["id"]

    return lookup
