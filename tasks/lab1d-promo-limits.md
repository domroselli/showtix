# Lab 1d: Promo usage limits

**Tier:** Intermediate · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 starts with a quick brainstorm with Claude about edge cases; then you write your answer key yourself.
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

Think about: does a quote use up anything, what a freed use means for a code that was fully used, promo codes typed in lowercase, and what the 409 in criterion 4 says, not just its code.

## The working loop

Write the tests first and check them yourself, then let Claude make them pass. Each step has a prompt you can copy. Start with `/clear` so Claude begins fresh.

1. **Find your edge cases, then write your answer key.** This sheet asks for one or two edge cases of your own. Ask Claude for ideas, then choose:

   > Read tasks/lab1d-promo-limits.md and the relevant code. Suggest 3 edge cases the criteria don't cover, one sentence each. Don't write any code. I'll pick which ones to add.

   Add the ones you pick to the sheet's edge-case lines. Then, without Claude: Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 2, you'll compare Claude's tests against this answer key.
2. **Tests first.** Ask Claude:

   > Read tasks/lab1d-promo-limits.md and the relevant code. Write a failing test for each acceptance criterion. Don't change anything in app/. Run the tests and show me which ones fail.

   Compare each test with your answer key. If one is wrong, tell Claude what it should be and why:

   > The test for criterion 4 expects ___, but it should be ___ because ___. Fix that test.

   Check especially:
   - **Some tests already pass**, as the sheet says (criteria 2, 5 and 6, maybe 4). They guard behavior your change must not break.
   - **Each test reads `uses` from the database** after the action, not just the status code.

   When you're satisfied with the tests, commit them:

   ```sh
   git add -A && git commit -m "lab1d: tests"
   ```

3. **Clear, then implement.** Type `/clear`, then ask:

   > Make the new tests from my last commit pass (see git show HEAD). Don't change any test. Read tasks/lab1d-promo-limits.md for context. Run the full suite and show me the output.

4. **Check the evidence.**
   - Run `uv run pytest` yourself. Is everything green?
   - Run `git diff HEAD --stat -- tests/`. It should print nothing, which means Claude didn't change your tests.
   - Try it yourself. In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. To stop the app, click in that terminal and press **Ctrl+C** (on a Mac too: Control, not Command).
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Your tests are already committed, so this shows only the code Claude wrote. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude:

   > Use a subagent to review this branch's changes (git diff main) against tasks/lab1d-promo-limits.md. It hasn't seen our conversation. Check every acceptance criterion, and don't report style. For each finding, give:
   > - a label: MUST FIX (a criterion isn't met, or a bug), OUT OF SCOPE (real, but not in the criteria, or already there before this branch), UNSURE, or OPTIONAL
   > - which criterion it's about
   > - evidence: the file and line, or an input that gives the wrong result
   >
   > Don't change any files or the database; if you need to experiment, do it in a test. Just show me the findings.

   **Why "don't report style"?** A reviewer asked to find problems always finds something. If you fix every finding, you end up with extra layers of code and tests for cases that can't happen. You want bugs and unmet criteria, not someone else's taste.

   The labels are the reviewer's opinion; you decide. Check the evidence for each MUST FIX and OUT OF SCOPE yourself (a reviewer can wave off a real bug as out of scope), ask for a failing test on anything UNSURE, and skip OPTIONAL. If an OUT OF SCOPE finding holds up, write it down and move on: fixing it is a new feature, not this one. Then fix the real ones test-first:

   > Findings 1 and 3 are real; ignore the rest. For each, write a failing test that shows the problem, then fix it. Run the full suite and show me the output.

   Then repeat step 4.
7. **Commit** when you're satisfied with the change:

   ```sh
   git add -A && git commit -m "lab1d: promo usage limits"
   ```

## Done means

- [ ] A test for each given criterion and for your own edge cases, all passing
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] `uses` is checked by reading the database after each action, not just by status codes
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc23818fa556ef1e8373e69c). Open one level at a time.
