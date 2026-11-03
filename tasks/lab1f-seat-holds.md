# Lab 1f: Expiring seat holds

**Tier:** Advanced · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 starts with Claude interviewing you about the open decisions; then you write your answer key yourself.
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

Write the tests first and check them yourself, then let Claude make them pass. Each step has a prompt you can copy. Start with `/clear` so Claude begins fresh.

1. **Settle the decisions, then write your answer key.** Have Claude interview you about **Decisions to make**:

   > Read tasks/lab1f-seat-holds.md and the relevant code. Interview me about the "Decisions to make", one question at a time. For each, give me 2-3 options and your recommendation. Don't write any code or tests. When we've covered every decision, update "Your criteria" in the sheet and change nothing else: one numbered, testable criterion per decision, with exact status codes and messages; under each, a "Why:" line with the reason we chose it; and a short "Not doing" list for what we deferred. Then show me the section so I can check it.

   You choose; Claude only offers options. ⏱ About 10 minutes: if a decision drags on, pick the simplest option and put the other on the "Not doing" list. Then, without Claude: Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 2, you'll compare Claude's tests against this answer key.
2. **Tests first.** Ask Claude:

   > Read tasks/lab1f-seat-holds.md and the relevant code. Write a failing test for each acceptance criterion. Don't change anything in app/. Run the tests and show me which ones fail.

   Compare each test with your answer key. If one is wrong, tell Claude what it should be and why:

   > The test for criterion 4 expects ___, but it should be ___ because ___. Fix that test.

   Check especially:
   - **Criterion 2's test moves the injected clock; it never sleeps.** Expiry is tested on both sides of the 10-minute boundary.
   - **`test_quote_writes_nothing` says what you decided a quote may now write** (see Background).
   - **Every decision in "Your criteria" has a test.**

   When you're satisfied with the tests, commit them:

   ```sh
   git add -A && git commit -m "lab1f: tests"
   ```

3. **Clear, then implement.** Type `/clear`, then ask:

   > Make the new tests from my last commit pass (see git show HEAD). Don't change any test. Read tasks/lab1f-seat-holds.md for context. Run the full suite and show me the output.

   This is a bigger feature, so build it in slices (holding seats first, then expiry, then using the hold). Add to the prompt: "Start with the tests for the first slice only. Stop when they pass." Commit each slice when you're satisfied with it, then ask for the next.

4. **Check the evidence.**
   - Run `uv run pytest` yourself. Is everything green?
   - Run `git diff HEAD --stat -- tests/`. It should print nothing, which means Claude didn't change your tests.
   - Try it yourself. In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. To stop the app, click in that terminal and press **Ctrl+C** (on a Mac too: Control, not Command).
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Your tests are already committed, so this shows only the code Claude wrote. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude:

   > Use a subagent to review this branch's changes (git diff main) against tasks/lab1f-seat-holds.md. It hasn't seen our conversation. Check every acceptance criterion, and don't report style. For each finding, give:
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
   git add -A && git commit -m "lab1f: seat holds"
   ```

## Done means

- [ ] Every decision you made is written down as a criterion with a test
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] Expiry is tested on both sides of the 10-minute boundary, with no `sleep`
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] All money math is in `app/pricing.py`, in integer cents; no floats
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc23815daf3ee26438afec9d). Open one level at a time.
