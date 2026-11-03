# Lab 1e: Waitlist

**Tier:** Breakthrough · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 starts with Claude interviewing you about the open decisions; then you write your answer key yourself.
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
- What does the 409 in criterion 1 say? The criterion gives only the code.

50 minutes is tight. For each question, pick the simplest answer that works and note what you'd do with more time.

### Your criteria

3. _..._
4. _..._
5. _..._

## The working loop

Write the tests first and check them yourself, then let Claude make them pass. Each step has a prompt you can copy. Start with `/clear` so Claude begins fresh.

1. **Settle the decisions, then write your answer key.** Have Claude interview you about **Decisions to make**:

   > Read tasks/lab1e-waitlist.md and the relevant code. Interview me about the "Decisions to make", one question at a time. For each, give me 2-3 options and your recommendation. Don't write any code or tests. When we've covered every decision, update "Your criteria" in the sheet and change nothing else: one numbered, testable criterion per decision, with exact status codes and messages; under each, a "Why:" line with the reason we chose it; and a short "Not doing" list for what we deferred. Then show me the section so I can check it.

   You choose; Claude only offers options. ⏱ About 10 minutes: if a decision drags on, pick the simplest option and put the other on the "Not doing" list. Then, without Claude: Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 2, you'll compare Claude's tests against this answer key.
2. **Tests first.** Ask Claude:

   > Read tasks/lab1e-waitlist.md and the relevant code. Write a failing test for each acceptance criterion. Don't change anything in app/. Run the tests and show me which ones fail.

   Compare each test with your answer key. If one is wrong, tell Claude what it should be and why:

   > The test for criterion 4 expects ___, but it should be ___ because ___. Fix that test.

   Check especially:
   - **First-in-first-out and the partial fill are tested with exact seat counts.**
   - **Every decision in "Your criteria" has a test.**

   When you're satisfied with the tests, commit them:

   ```sh
   git add -A && git commit -m "lab1e: tests"
   ```

3. **Clear, then implement.** Type `/clear`, then ask:

   > Make the new tests from my last commit pass (see git show HEAD). Don't change any test. Read tasks/lab1e-waitlist.md for context. Run the full suite and show me the output.

   This is a bigger feature, so build it in slices (joining the waitlist first, then giving freed seats to the line). Add to the prompt: "Start with the tests for the first slice only. Stop when they pass." Commit each slice when you're satisfied with it, then ask for the next.

4. **Check the evidence.**
   - Run `uv run pytest` yourself. Is everything green?
   - Run `git diff HEAD --stat -- tests/`. It should print nothing, which means Claude didn't change your tests.
   - Try it yourself. In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. To stop the app, click in that terminal and press **Ctrl+C** (on a Mac too: Control, not Command).
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Your tests are already committed, so this shows only the code Claude wrote. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude:

   > Use a subagent to review this branch's changes (git diff main) against tasks/lab1e-waitlist.md. It hasn't seen our conversation. Check every acceptance criterion, and don't report style. For each finding, give:
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
   git add -A && git commit -m "lab1e: waitlist"
   ```

## Done means

- [ ] Every decision you made is written down as a criterion with a test
- [ ] The tests you committed in step 2 weren't changed to make them pass
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
