# Lab 1b: Itemized receipt

**Tier:** Starter · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

Add `GET /orders/{id}/receipt`: every pricing line of a stored order, matching its stored totals to the cent.

## Starting branch

```sh
git switch main
git switch -c lab1b-itemized-receipt
uv run pytest          # green before you change anything
```

## Background

- An order stores its money when it's created: `subtotal_cents`, `discount_cents`, `fees_cents`, `tax_cents`, `total_cents`, plus `promo_code` (null when no promo was used).
- Each order line stores `unit_price_cents`, the price paid at purchase time. Tier prices can change later; receipts must not.
- `orders.get_order()` in `app/orders.py` already loads an order with its ticket `lines` and its `pricing_lines` (Subtotal, Discount, Service fees, Tax, Total), rebuilt from the stored totals. `shows.show_for_performance()` gives the show title and the venue name (`.venue`), and `inventory.availability(conn, performance_id).starts_at` gives the start time.
- `GET /orders/{id}` is the UI's confirmation page (HTML, in `app/web.py`). The receipt is a new JSON endpoint next to it.

## Acceptance criteria

The full criteria are given. Write one test for each.

1. `GET /orders/{id}/receipt` returns 200 with `order_id`, `status`, `email`, `show_title`, `venue_name`, `starts_at`, `promo_code` and `lines`. `starts_at` uses the same format `GET /shows/{id}` returns.
2. `lines` is a list of `{"label": str, "amount_cents": int}` in this order: one line per tier bought, labelled like `2 × Premium` (the × sign, U+00D7, not the letter x); then `Subtotal`, `Discount`, `Service fees`, `Tax`, `Total`.
3. The discount line is negative. Its label names the promo when one was used (`Discount (LOCALS10)`); with no promo, it's `Discount` with amount 0.
4. Every amount comes from the stored order, not from recalculating. 2 Premium with LOCALS10 gives: `2 × Premium` 24000, `Subtotal` 24000, `Discount (LOCALS10)` -2400, `Service fees` 1500, `Tax` 1944, `Total` 25044.
5. The tier lines add up to `Subtotal`, and `Subtotal + Discount + Service fees + Tax` equals `Total`.
6. If the tier's price changes after the order, the receipt still shows the price paid.
7. A cancelled order still has a receipt, with `status` `cancelled`.
8. An unknown order id returns 404.

## The working loop

This is how people really use Claude Code: one good prompt, then you check the evidence.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 3, you'll compare Claude's tests against this answer key.
2. **One good prompt.** For example: "Read tasks/lab1b-itemized-receipt.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after."
3. **Check the evidence.** Did the tests fail before the change? Does each test match your answer key, not just what Claude assumed?
4. **Try it yourself.** In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. Ctrl+C stops the app.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude: "Review this diff against tasks/lab1b-itemized-receipt.md." Then decide which of its findings actually matter.

## Done means

- [ ] A test for each of the 8 criteria, all passing
- [ ] The receipt never recalculates a price; it only reads stored values
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] All money math is in `app/pricing.py`, in integer cents; no floats
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Optional stretch

Finished early? Add a "View receipt" link to the order confirmation page that opens `/orders/{id}/receipt`. Add a test that the confirmation page contains the link.

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc23810383b1dd968c3eeccc). Open one level at a time.
