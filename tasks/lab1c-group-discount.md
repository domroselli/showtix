# Lab 1c: Group discount

**Tier:** Intermediate · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

Reward groups: 6 or more tickets in one tier get 15% off that tier.

## Starting branch

```sh
git switch main
git switch -c lab1c-group-discount
uv run pytest          # green before you change anything
```

## Background

- Pricing happens in `pricing.price_order()` in `app/pricing.py`, in a fixed order (see CLAUDE.md): subtotal, discount, service fee, tax, total.
- `orders.quote()` merges cart items by tier, so each `pricing.Line` it passes in is one tier.
- A promo discount is computed by `pricing.discount()`. Quotes and orders carry a single `discount_cents` today.
- `pricing.pricing_lines()` turns a breakdown into the ordered lines (Subtotal, Discount, Service fees, Tax, Total) that quotes and orders return as `pricing_lines`. The UI's quote and confirmation pages loop over that list, so a line you add there shows up in the UI with no template changes.
- Quotes (`Quote`) and stored orders (`Order`, `orders` table) must show the same numbers.
- Tests use an in-memory database, but the running app uses a local SQLite file. If you change the schema, reset it with `uv run python -m app.seed`, or the UI will break even while tests pass.

## Acceptance criteria

Most criteria are given. **Add one or two edge cases of your own** before you write tests.

1. 6 or more tickets in the same tier get 15% off that tier's subtotal (rounded half up to the cent).
2. 5 tickets get no discount; exactly 6 do.
3. If a promo code also applies, the customer gets whichever discount is larger. They never stack.
4. The quote breakdown shows the group discount as its own line: its own field, and its own entry in `pricing_lines` (labelled exactly `Group discount (15%)`, negative, right after `Subtotal`, and only when it's non-zero).
5. All amounts stay in integer cents; tax follows the existing pricing order (9% of the subtotal after the discount that won).
6. The stored order matches the quote, including the group discount line.
7. If the group discount beats a promo, the promo isn't applied: the order doesn't record the promo code, and the promo's use count doesn't go up.

Worked examples (cents):

| Cart | Subtotal | Discount that wins | Fees | Tax | Total |
| --- | --- | --- | --- | --- | --- |
| 6 GA, no promo | 41400 | group 6210 | 4500 | 3167 | 42857 |
| 6 GA + LOCALS10 | 41400 | group 6210 (promo would be 4140) | 4500 | 3167 | 42857 |
| 6 GA + 2 VIP + LOCALS10 | 81398 | promo 8140 (group would be 6210) | 6000 | 6593 | 85851 |
| 7 VIP, no promo | 139993 | group 20999 | 5250 | 10709 | 134953 |

Your edge cases:

8. _..._
9. _..._ (optional)

Think about: ties, the 8-ticket limit, a fixed promo, which discount the breakdown reports when one loses.

## The working loop

This is how people really use Claude Code: one good prompt, then you check the evidence.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 3, you'll compare Claude's tests against this answer key.
2. **One good prompt.** For example: "Read tasks/lab1c-group-discount.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after."
3. **Check the evidence.** Did the tests fail before the change? Does each test match your answer key, not just what Claude assumed?
4. **Try it yourself.** In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. Ctrl+C stops the app.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude: "Review this diff against tasks/lab1c-group-discount.md." Then decide which of its findings actually matter.

## Done means

- [ ] A test for each given criterion and for your own edge cases, all passing
- [ ] The four worked examples are tests, with every line asserted in exact cents
- [ ] The quote, the stored order and the UI agree on every line
- [ ] The group discount appears on the UI's quote and confirmation pages with no template changes
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] All money math is in `app/pricing.py`, in integer cents; no floats
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc238156b855d22a8fe01f48). Open one level at a time.
