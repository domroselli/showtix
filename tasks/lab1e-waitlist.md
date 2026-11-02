# Lab 1e: Waitlist

**Tier:** Breakthrough · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

**Feature request:** "When a tier is sold out, let customers join a waitlist for it. When an order is cancelled, the freed seats go to the waitlist first-in-first-out, and partial quantities are allowed."

## Starting branch

```sh
git switch main
git switch -c lab1e-waitlist
uv run pytest          # green before you change anything
```

## Background

- Seats are never stored as a count: seats sold = sum of order line qty on orders that aren't cancelled (`app/inventory.py`). Cancelling an order frees its seats automatically.
- There's no waitlist table yet. The schema is in `app/db.py`.
- Seats are freed in exactly one place: `orders.cancel_order()`.
- The UI already marks a sold-out tier "Sold out" on the performance page; a join form could sit there.
- In tests, make any tier small inside `with conn:`: `with conn: conn.execute("UPDATE price_tiers SET seats_total = 3 WHERE id = ?", (tier_id,))`. Without `with conn:`, the change leaves a transaction open and the next order fails. Then buy 3 seats in one order to sell it out, add two waitlist entries for 2 each, and cancel that order to free exactly 3.

## Acceptance criteria

Two criteria are given. **Write the rest with Claude's help** before you write tests.

1. Joining the waitlist for a tier that still has seats is rejected with 409. The customer should buy instead.
2. When 3 seats are freed and the first two people in line want 2 seats each, the first gets 2 and the second gets 1, in the order they joined.

### Decisions to make

Decide these with Claude, then turn each decision into a criterion:

- What does "gets the seats" mean: a paid order created for them, or something else? At what price, with which fees?
- After a partial fill, does the person keep waiting for the rest?
- What does joining return, and how does a customer check their place or status? API only, or the UI too?
- Can the same email join twice? Does the 8-ticket limit apply to a waitlist entry?
- What if the freed seats are more than everyone in line wants?

50 minutes is tight. For each question, pick the simplest answer that works and note what you'd do with more time.

### Your criteria

3. _..._
4. _..._
5. _..._

## The working loop

This is how people really use Claude Code: one good prompt, then you check the evidence.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 3, you'll compare Claude's tests against this answer key.
2. **One good prompt.** For example: "Read tasks/lab1e-waitlist.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after."
   This is a bigger feature: settle your criteria first, then start in plan mode and review the plan before Claude writes code.
3. **Check the evidence.** Did the tests fail before the change? Does each test match your answer key, not just what Claude assumed?
4. **Try it yourself.** In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. Ctrl+C stops the app.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude: "Review this diff against tasks/lab1e-waitlist.md." Then decide which of its findings actually matter.

## Done means

- [ ] Every decision you made is written down as a criterion with a test
- [ ] First-in-first-out and the partial fill are tested with exact seat counts
- [ ] Any order created for a waitlisted customer has a price that matches a quote for the same seats
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] All money math is in `app/pricing.py`, in integer cents; no floats
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc2381f890caecd57cd909dc). Open one level at a time.
