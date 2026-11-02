# Lab 1f: Expiring seat holds

**Tier:** Advanced · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

**Feature request:** "A quote holds the quoted seats for 10 minutes so nobody else can buy them. Expired holds release automatically. Time is injected so tests never sleep."

## Starting branch

```sh
git switch main
git switch -c lab1f-seat-holds
uv run pytest          # green before you change anything
```

## Background

- Seats left = seats total - seats sold on orders that aren't cancelled (`inventory.tiers_for_performance()`). Holds would be a third term.
- Time is already injected: routes take `now` from the `get_now` dependency in `app/clock.py`, and `tests/conftest.py` overrides it. A test can set its own time with `@pytest.mark.parametrize("now", [datetime(...)])`. That sets one fixed time per test. Criterion 2 needs time to move within a test, so you'll need a different approach.
- Today a quote "writes nothing", and `tests/test_orders.py::test_quote_writes_nothing` checks that no orders are created and no promo uses are recorded. This feature changes what a quote does on purpose; decide what that test should still promise.
- The UI's quote form (`POST /performances/{id}/quote`) and its "Place order" button go through the same `orders.quote()` and `orders.create_order()`, so they're affected too.
- The nearly sold out tier (Gravity Optional VIP on Nov 14, 2 seats left) is a handy test target.

## Acceptance criteria

Two criteria are given. **Write the rest with Claude's help** before you write tests.

1. After a quote for the last 2 VIP seats, a second customer's quote or order for 1 of those seats is rejected with 409 while the hold is active.
2. 10 minutes after the quote, those seats can be bought again. The test moves the injected clock; it never sleeps.

### Decisions to make

Decide these with Claude, then turn each decision into a criterion:

- Exactly when does a hold expire: at 10:00, or after it? Test both sides of the boundary.
- How does the customer who holds the seats use them? (A hold id returned by the quote and passed to `POST /orders`, and carried by the UI's "Place order" form?)
- Does placing the order use up the hold? Does a second quote from the same customer replace the first hold?
- How do held seats show up in `/performances/{id}/availability` and on the performance page?
- `create_order()` prices through `quote()`. Should creating an order also create a hold? If not, how do you separate pricing from holding?

50 minutes is tight. For each question, pick the simplest answer that works and note what you'd do with more time.

### Your criteria

3. _..._
4. _..._
5. _..._

## The working loop

This is how people really use Claude Code: one good prompt, then you check the evidence.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 3, you'll compare Claude's tests against this answer key.
2. **One good prompt.** For example: "Read tasks/lab1f-seat-holds.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after."
   This is a bigger feature: settle your criteria first, then start in plan mode and review the plan before Claude writes code.
3. **Check the evidence.** Did the tests fail before the change? Does each test match your answer key, not just what Claude assumed?
4. **Try it yourself.** In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. Ctrl+C stops the app.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude: "Review this diff against tasks/lab1f-seat-holds.md." Then decide which of its findings actually matter.

## Done means

- [ ] Every decision you made is written down as a criterion with a test
- [ ] Expiry is tested on both sides of the 10-minute boundary, with no `sleep`
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] All money math is in `app/pricing.py`, in integer cents; no floats
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc23815daf3ee26438afec9d). Open one level at a time.
