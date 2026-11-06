# Lab 1d: Promo usage limits

**Tier:** Intermediate · **Time:** 50 minutes · Solo or with a partner

## Start here

Finish a half-built rule that spans ordering and cancelling, built with the full workflow.

1. New here? Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).
2. Run the command under [Starting branch](#starting-branch), then read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow) step by step. Step 1 starts with you thinking through edge cases; then you write your expected results yourself.

You're done when every box under [Done means](#done-means) is checked. Stuck? See [Hints](#hints).

## Goal

Finish promo usage limits: enforce `max_uses`, and give a use back when an order is cancelled.

## Starting branch

Create this lab's branch from `main`, reset the database, and check that the tests pass:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1d-promo-limits && uv run pytest
```

Every test should pass before you change anything. Trouble? See [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

Where the promo code you'll change lives:

- **`promo_codes` has `max_uses` (null means unlimited) and `uses`.** The base app is deliberately half-built: `promos.record_use()` adds a use when an order is created, but nothing reads `max_uses`, and cancelling never gives a use back. Orders store the `promo_code` they used (null when none).
- **Validation lives in `promos.find_valid_promo()`; cancelling is `orders.cancel_order()`.** Cancelling an already-cancelled order raises `Conflict` (409). Promo errors already show inline on the UI's quote page, so a new error message appears there for free.
- **Seeded limits are large** (LOCALS10: 500, WELCOME5: 1000). In tests, set a small limit inside `with conn:`: `with conn: conn.execute("UPDATE promo_codes SET max_uses = 1 WHERE code = 'WELCOME5'")`. Without `with conn:`, the change leaves a transaction open and the next order fails.

For a picture of how orders and cancels flow, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).

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

## The workflow

Settle what "done" means, then have Claude write the tests, check them yourself, and let Claude make them pass.

- Steps that use Claude have a prompt to copy; commands start with `!`.
- Why each step matters: [How we work](00-how-we-work.md).
- Start with a fresh conversation:

  ```text
  /clear
  ```

### 1. Align: find your edge cases, then write your expected results

This sheet asks for one or two edge cases of your own. Think them through yourself first: what could a customer do that the criteria don't answer? Type yours into the sheet's edge-case lines.

Stuck? Ask Claude for a hint:

```text
Read tasks/lab1d-promo-limits.md and the relevant code. I'm stuck finding edge cases
the criteria don't cover. Give me one hint at a time, as a question, not the
edge case itself. If I say "just tell me", suggest 3 edge cases, one sentence
each, and I'll pick. Don't write any code or change any files.
```

Then, without Claude, write down exactly what each criterion should return:

- Go through [Acceptance criteria](#acceptance-criteria) one by one: which status code, the exact message, and what `uses` should be after each action.
- Look up the seeded promo codes and their limits in [`docs/seed-data.md`](../docs/seed-data.md).
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

You'll compare Claude's tests against these expected results in step 2.

### 2. Tests first

Have Claude write failing tests, then check them against your expected results.

```text
Read tasks/lab1d-promo-limits.md and the relevant code. Write a failing test
for each acceptance criterion. Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

Check especially:

- **Tests check behavior through the API or the page**, not functions that don't exist yet. A test that calls a new function is designing the code for Claude.
- **Some tests already pass**, as the sheet says (criteria 2, 5 and 6, maybe 4). They guard behavior your change must not break.
- **Each test reads `uses` from the database** after the action, not just the status code.

If a test doesn't match your expected results, tell Claude what it should be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1d: tests"
```

### 3. Clear, then implement

Clear the conversation, so Claude builds from the sheet and your committed tests, not the chat:

```text
/clear
```

Then ask:

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab1d-promo-limits.md for context. Run the full suite and show me
the output.
```

Claude shouldn't touch any test file. Step 4 checks that.

### 4. Check the evidence

Don't take Claude's word for it; check for yourself.

- Run the tests. The last line should say only `passed`, with no `skipped`, `deselected` or `xfailed`:

  ```text
  ! uv run pytest
  ```

- Check that Claude only changed app code. Every file this lists should be under `app/`:

  ```text
  ! git status --short
  ```

  A file in `tests/` (changed, or new with `??`), a `conftest.py`, or `pyproject.toml` means Claude touched your tests or how they run: ask why before going on. After step 6's fixes, the only test changes should be the new tests you asked for.

- Try it yourself. Ask Claude to start the app in the background ([more on starting the app](01-getting-started.md#start-the-app)):

  ```text
  Start the app in the background with uv run uvicorn app.main:app --reload,
  and tell me when it's ready.
  ```

  Then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or [the UI](01-getting-started.md#use-the-web-ui) at http://127.0.0.1:8000/. Use values from your expected results. When you're done, stop it:

  ```text
  Stop the app.
  ```

Something doesn't match? Tell Claude which criterion failed and what you saw.

### 5. Review the diff

Read every change Claude made before you accept it.

```text
! git add -A && git diff --staged
```

- Can you explain every change?
- Was anything touched that has nothing to do with promo limits?
- Prefer side by side? Use VS Code's **Source Control** panel.

Your tests are already committed, so this shows only the code Claude wrote.

### 6. Get a second opinion

A reviewer that hasn't seen your conversation checks the change against this sheet.

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1d-promo-limits.md. It hasn't seen our conversation. It should check
every acceptance criterion, not report style, and not change any files or the
database. Show me its findings as a numbered list, each with:
- a label: MUST FIX (a criterion isn't met, or a bug), OUT OF SCOPE (real, but
  not in the criteria, or already there before this branch), UNSURE, or
  OPTIONAL
- which criterion it's about
- evidence: the file and line, or an input that gives the wrong result

Then ask me which ones to fix. For each one I pick, write a failing test that
shows the problem, then fix it. Run the full suite and show me the output.
```

Claude shows the findings and asks which to fix. The labels are the reviewer's opinion; decide for yourself before you answer:

- **MUST FIX** and **OUT OF SCOPE:** check the evidence yourself. A reviewer can wave off a real bug as out of scope.
- **UNSURE:** answer "prove it with a failing test first." **OPTIONAL:** usually skip.
- **OUT OF SCOPE** that holds up: write it down and move on. Fixing it is a new feature, not this one.

Answer with the numbers you want fixed, for example "1 and 3".

Then repeat step 4. Why "don't report style"? See [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### 7. Commit

Commit when you're satisfied with the change:

```text
! git add -A && git commit -m "lab1d: promo usage limits"
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
