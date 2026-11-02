# ShowTix

A small ticketing backend for fictional Las Vegas shows.

## Setup

Requires [uv](https://docs.astral.sh/uv/). uv installs Python 3.12 if you don't have it.

```sh
uv sync
uv run pytest                              # run the tests
uv run uvicorn app.main:app --reload       # start the app
```

Open http://127.0.0.1:8000/ for the web UI: pick a show and night, choose tickets, get a quote, and place an order. It runs fully offline (no JavaScript, no external assets).

Open http://127.0.0.1:8000/docs to browse and try every API endpoint. The database (`showtix.db`) is created and seeded on first start. Run `uv run python -m app.seed` to reset it.

## API key (Lab 2)

Some Lab 2 features call the Claude API. They read the key from `SHOWTIX_CLAUDE_KEY` in a `.env` file at the repo root, never from `ANTHROPIC_API_KEY`, so Claude Code keeps using your own sign-in.

```sh
cp .env.example .env
# then edit .env: SHOWTIX_CLAUDE_KEY=sk-ant-...
```

`.env` is gitignored; never commit it. Without a key, those features return 503 with "Claude API key not configured: set SHOWTIX_CLAUDE_KEY in .env". Everything else works without one, and the tests never need it: they use a fake client and stay offline.

Check your key with one tiny call:

```sh
uv run python -m app.llm
```

It prints `OK: Claude API key works`, or one line saying what to fix: missing key, key rejected (401), no credits or billing, rate limited or overloaded, or no network. It exits non-zero on failure.

## Evals (Lab 2)

Unit tests use a fake client; evals check the real model against the API and give a score, not a guaranteed pass. Every test gets the fake automatically, and pytest never collects `tests/evals/`.

A feature's eval is a JSON list of cases plus a script that hands them to the shared runner:

```python
# tests/evals/run_support_reply.py
from tests.evals.runner import run

def check(case) -> tuple[bool, str]:
    ...  # call your feature with the real client from app/llm.py
    return passed, "what Claude produced"

if __name__ == "__main__":
    run("tests/evals/support_reply.json", check)
```

Run it with `uv run python -m tests.evals.run_support_reply`, and add `--repeat 3` to run every case three times. It prints one line per case and a total score, such as `Score: 8/10`.

## Endpoints

| Method | Path | Does |
| --- | --- | --- |
| GET | /shows | List shows; optional `start_date` and `end_date` (YYYY-MM-DD) |
| GET | /shows/{id} | Show detail with upcoming performances |
| GET | /performances/{id}/availability | Seats left per tier |
| POST | /orders/quote | Price breakdown for a cart and optional promo; writes nothing |
| POST | /orders | Create a paid order and take the seats |
| POST | /orders/{id}/cancel | Cancel an order and release its seats |

Example quote body:

```json
{"performance_id": 1, "items": [{"tier_id": 2, "qty": 2}], "promo_code": "LOCALS10"}
```

## Web pages

| Path | Shows |
| --- | --- |
| / | Every show with its category, venue and upcoming performances |
| /performances/{id} | Tiers, prices, seats left and a quote form |
| /orders/{id} | Confirmation for a placed order |

## Seed data

- 8 shows (magic, comedy, music, acrobatics) at 3 venues
- One performance per show every night, Nov 10 to Nov 23, 2026
- Three tiers per performance: GA $69, Premium $120, VIP $199.99
- Promo codes: `LOCALS10` (10% off), `WELCOME5` ($5 off), `SPRING24` (expired)
- Gravity Optional's VIP tier on Nov 14 has only 2 seats left

## Glossary

- **Show:** a production, like a magic act or a comedy night. Runs at one venue.
- **Performance:** one night of a show, with a start time in local Vegas time.
- **Tier:** a price level for a performance's seats: GA (general admission), Premium or VIP. Each tier has a fixed number of seats.
- **Quote:** the price breakdown for a cart, before buying. Nothing is saved.
- **Order:** a purchase of tickets for one performance. Paid when created; can be cancelled.
- **Promo code:** a discount on the ticket subtotal, either a percent (`LOCALS10`) or a fixed amount (`WELCOME5`). Promos have a valid date range.
- **Service fee:** $7.50 per ticket, added after any discount. Never discounted, never taxed.
- **Tax:** a simplified 9% workshop rate on the discounted ticket subtotal.
- **Cents:** every amount in the API is an integer number of cents. `25044` means $250.44.
