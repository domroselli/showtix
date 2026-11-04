# ShowTix

Ticketing backend for fictional Las Vegas shows. Python 3.12, FastAPI, SQLite, pytest, uv.

## Commands

- Run: `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/ (web UI) or http://127.0.0.1:8000/docs (API)
- Test: `uv run pytest` (the full suite must stay under 5 seconds)
- Reset the local database: `uv run python -m app.seed`
- Check the Claude API key: `uv run python -m app.llm` (one small real call; prints OK or what to fix)

## Where things live

- `app/main.py`: JSON API routes only. No business logic; call into the modules below.
- `app/web.py` and `app/templates/`: server-rendered pages. Routes only read forms, call `shows.py`, `orders.py` and `inventory.py`, and render templates.
- `app/pricing.py`: all money math. Nothing else adds, multiplies, discounts or taxes money.
- `app/orders.py`: quote, create, cancel. Orders are priced by calling `orders.quote()`, which calls `pricing.price_order()`.
- `app/inventory.py`: seats left per tier.
- `app/promos.py`: promo code lookup and validation.
- `app/shows.py`: show listing, date filters, show detail.
- `app/models.py`: Pydantic request and response models, including the per-order ticket limit.
- `app/db.py`: SQLite connection, schema and the `get_db` dependency. `app/seed.py`: fictional seed data.
- `app/errors.py`: `NotFound` (404), `BadRequest` (400), `Conflict` (409), `ServiceUnavailable` (503). Raise these from domain code; `main.py` turns them into responses.
- `app/clock.py`: current Vegas time. Routes get it through the `get_now` dependency.
- `app/llm.py`: the Claude API client (`get_llm` dependency) and `MODEL`. `tests/fakes.py`: `FakeClaude` for tests.

## Conventions

- **Money is integer cents.** Every price, discount, fee, tax and total is an `int` of cents with a `_cents` suffix. Never use floats for money, not even temporarily. Round with integer math (`pricing.percent_of`).
- **All pricing logic lives in `pricing.py`.** If a change touches money, it changes `pricing.py` and is called from there. Never copy a formula into another module.
- **The web layer holds no logic.** No business rules or money math in `web.py` or the templates. Templates show a price breakdown by looping over `pricing_lines` (built by `pricing.pricing_lines()`), never by naming totals. Cents become dollars only through `pricing.dollars()`: the `dollars` template filter on pages, and the same function anywhere else, such as amounts in a prompt to Claude. No JavaScript, no CDN links; pages must work offline.
- **One price, everywhere.** A stored order must match its quote to the cent, because both come from the same function.
- **Order lines capture the price at purchase time.** Don't recompute old orders from current tier prices.
- **Seats are derived, not stored.** Seats sold = sum of order line qty on orders that aren't cancelled.
- **Time is injected.** Never call `datetime.now()` in domain code; take a `now` argument. Tests pin the clock by overriding `get_now`; to move time within a test, use the `clock` fixture in `tests/conftest.py` (set `clock.now`). Don't add another clock override. Times are naive local Vegas time.
- **Test first.** Write a failing test, then make it pass. Tests run offline against an in-memory database (see `tests/conftest.py`).
- **Assert exact cents.** `assert q["total_cents"] == 25044`, never `assert total < before`.
- **All Claude API calls go through `app/llm.py`.** Tests use the `fake_claude` fixture and never touch the network.
- **Keep the app small.** Prefer editing an existing module over adding a new one. Exception: a Lab 2 Claude API feature gets its own small module (for example `app/support.py`), so the LLM code stays in one place.

## Pricing order

Apply these steps in this order:

1. **Subtotal:** Sum of qty × tier price.
2. **Discount:** Apply the promo to the subtotal. A percent promo can't exceed the subtotal; a fixed promo can't take it below zero.
3. **Service fee:** $7.50 per ticket. Never discounted.
4. **Tax:** 9% of the discounted subtotal only, not fees, rounded half up to the cent once. This is a simplified workshop rate, not real Nevada tax law.
5. **Total:** Discounted subtotal + fees + tax.

Limits: a maximum of 8 tickets per order, and no tier can be oversold. Expired promo codes are rejected with a clear error.
