# Lab 1d: Promo usage limits

**Tier:** Intermediate · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

Finish promo usage limits: enforce `max_uses`, and give a use back when an order is cancelled.

## Starting branch

```sh
git switch main
git switch -c lab1d-promo-limits
uv run pytest          # green before you change anything
```

## Background

- `promo_codes` has `max_uses` (null means unlimited) and `uses`.
- The base app is deliberately half-built: `promos.record_use()` adds a use when an order is created, but nothing reads `max_uses`, and cancelling never gives a use back.
- Orders store the `promo_code` they used (null when none).
- Validation lives in `promos.find_valid_promo()`; cancelling is `orders.cancel_order()`. Cancelling an already-cancelled order raises `Conflict` (409).
- Promo errors already show inline on the UI's quote page, so a new error message appears there for free.
- Seeded limits are large (LOCALS10: 500, WELCOME5: 1000). In tests, set a small limit inside `with conn:`: `with conn: conn.execute("UPDATE promo_codes SET max_uses = 1 WHERE code = 'WELCOME5'")`. Without `with conn:`, the change leaves a transaction open and the next order fails.

## Acceptance criteria

Most criteria are given. **Add one or two edge cases of your own** before you write tests.

1. A code whose `uses` has reached `max_uses` is rejected with 400 and the detail `Promo code WELCOME5 has been fully used`, on both quotes and orders.
2. A code one use short of its limit still works, and that order takes the last use (`uses == max_uses` afterwards).
3. Cancelling a paid order that used a promo gives the use back (`uses` goes down by 1).
4. Cancelling an already-cancelled order is rejected (409) and never gives the use back twice.
5. Cancelling an order without a promo changes no promo's `uses`.
6. A code with `max_uses` null is never rejected for usage.

Tests for criteria 2, 5 and 6 (and 4, depending on how you write it) pass before you change anything. That's expected: they guard behavior your change must not break.

Your edge cases:

7. _..._
8. _..._ (optional)

Think about: does a quote use up anything, what a freed use means for a code that was fully used, and promo codes typed in lowercase.

## The working loop

This is how people really use Claude Code: one good prompt, then you check the evidence.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 3, you'll compare Claude's tests against this answer key.
2. **One good prompt.** For example: "Read tasks/lab1d-promo-limits.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after."
3. **Check the evidence.** Did the tests fail before the change? Does each test match your answer key, not just what Claude assumed?
4. **Try it yourself.** In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. Ctrl+C stops the app.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude: "Review this diff against tasks/lab1d-promo-limits.md." Then decide which of its findings actually matter.

## Done means

- [ ] A test for each given criterion and for your own edge cases, all passing
- [ ] `uses` is checked by reading the database after each action, not just by status codes
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc23818fa556ef1e8373e69c). Open one level at a time.
