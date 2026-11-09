# Lab 1d: Promo usage limits

- **Tier:** Intermediate
- **Time:** 50 minutes
- Solo or with a partner

## Start here

**New here?** Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).

**This lab:** finish a half-built rule that spans ordering and cancelling, built with the full workflow.

1. Run the command under [Starting branch](#starting-branch).
2. Read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow) step by step.

**Step 1 starts with you:** think through your edge cases, then write out (or think about) your expected results yourself.

**You're done when you can check every box under [Checklist: What Done Means](#checklist-what-done-means).**

**Stuck?** See [Hints](#hints).

## Goal

#### Finish promo usage limits: enforce `max_uses`, and give a use back when an order is cancelled.

## Starting branch

Copy the command below and run in Claude Code

```text
! git switch main && uv run python -m app.seed && git switch -c lab1d-promo-limits && uv run pytest
```

Here's what it does:

1. Switches to `main`, so the new branch starts from the original code
2. Resets the database to the seed data
3. Creates new feature branch `lab1d-promo-limits` from `main`
4. Runs the tests

Every test should pass before you change anything.

**Trouble?** See [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

Here is the relevant background about the feature you'll be building:

- **`promo_codes` has `max_uses` (null means unlimited) and `uses`.** The base app is deliberately half-built: `promos.record_use()` adds a use when an order is created, but nothing reads `max_uses`, and cancelling never gives a use back. Orders store the `promo_code` they used (null when none).
- **Validation lives in `promos.find_valid_promo()`; cancelling is `orders.cancel_order()`.** Cancelling an already-cancelled order raises `Conflict` (409). Promo errors already show inline on the UI's quote page, so a new error message appears there for free.
- **Seeded limits are large** (LOCALS10: 500, WELCOME5: 1000). In tests, set a small limit inside `with conn:`: `with conn: conn.execute("UPDATE promo_codes SET max_uses = 1 WHERE code = 'WELCOME5'")`. Without `with conn:`, the change leaves a transaction open and the next order fails.

**For an illustration of how orders and cancels flow, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).**

## Acceptance criteria

In this lab, most criteria are given below. **Add one or two edge cases of your own as criteria 7 and 8** before you write tests.

**Every criterion needs at least one test.**

1. A code whose `uses` has reached `max_uses` is rejected with 400 and the detail `Promo code WELCOME5 has been fully used`, on both quotes and orders.
2. A code one use short of its limit still works, and that order takes the last use (`uses == max_uses` afterwards).
3. Cancelling a paid order that used a promo gives the use back (`uses` goes down by 1).
4. Cancelling an already-cancelled order is rejected (409) and never gives the use back twice.
5. Cancelling an order without a promo changes no promo's `uses`.
6. A code with `max_uses` null is never rejected for usage.
7. _Your edge case_
8. _Your edge case_ (optional)

**Edge cases to think about:** does a quote use up anything, what a freed use means for a code that was fully used, promo codes typed in lowercase, and what the 409 in criterion 4 says, not just its code.

Tests for criteria 2, 5 and 6 (and 4, depending on how you write it) pass before you change anything. **That's expected:** they guard behavior your change <ins>must not</ins> break.

## The workflow

#### Introduction

There are many workflows out there.

Engineers are still experimenting and finding what works for them. The models are changing and improving so rapidly that what works great today may get discarded 3 months from now (or, next week). You'll probably come up with your own workflow eventually (or maybe you already have one). All we're doing here is introducing you to one way you can build good software reliably with a coding agent like Claude.  

The main takeaway is this: there is no "correct" way right now.

- There are things you should do.
- There are things you shouldn't do. 
- There are things that seem to work in certain situations with the models we have right now.

The workflow in this lab is based on general software engineering principles that have been around for decades, combined with best practices given by Anthropic (and others).

We encourage you to use what works for you and share your results.

**<ins>One thing to note:</ins>** Often people who work with Claude (or Codex, etc...) first get alignment on an idea, have Claude put that into a spec, and create work items (user stories, issues, etc...) for Claude to work on *before* steps 2-7. Since this is a lab and we have limited time, we're focusing on the coding and review aspects of the flow. But we highly recommend you get experience with this on your own time.

#### Workflow Overview

1. Start a fresh conversation. Find your edge cases, then write your expected results (without Claude).
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, then commit.
3. Start a fresh conversation. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm only app/ changed, try it in the browser.
5. Review the diff.
6. A subagent reviews the change. For each real bug, Claude writes a failing test and fixes it, then you repeat steps 4 and 5.
7. Commit.

Why each step matters: [How we work](00-how-we-work.md).

### Step 1. Alignment on what "done" means

#### 1a. Start with a fresh conversation

```text
/clear
```

#### 1b. Find your edge cases

This sheet asks for one or two edge cases of your own.

Think them through yourself first: what could a customer do that the criteria don't answer? Type yours into [Acceptance criteria](#acceptance-criteria), as criteria 7 and 8.

**Stuck?** Ask Claude for a hint:

```text
Read tasks/lab1d-promo-limits.md and the relevant code. I'm stuck finding edge cases
the criteria don't cover. Give me one hint at a time, as a question, not the
edge case itself. If I say "just tell me", suggest 3 edge cases, one sentence
each, and I'll pick. Don't write any code or change any files.
```

#### 1c. Review the acceptance criteria (without Claude)

This is how Claude knows when the feature is complete. Think through exactly what each criterion should return before Claude writes anything.  
Make a note of this somewhere to refer to later (like notes, notepad, or an empty text file. Whatever works for you).

**Go through [Acceptance criteria](#acceptance-criteria) one by one:** which status code, the exact message, and what `uses` should be after each action.

**Note:**

- The seeded promo codes and their limits are in [`docs/seed-data.md`](../docs/seed-data.md) for your convenience.
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2. Implement tests first

#### 2a. Start with a fresh conversation

```text
/clear
```

#### 2b. Have Claude write failing tests. Check them against your expected results

```text
Read tasks/lab1d-promo-limits.md and the relevant code. Write a failing test
for each acceptance criterion. Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

#### 2c. Manually check the tests Claude just created

Claude's reply is your checklist: one line per test with the criterion it covers, what it expects and whether it passes today. If the reply doesn't give you that, ask:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check:

- **Each expected value matches your step 1 table.** Claude wrote the tests and the summary, so the table you wrote without Claude is the thing to trust. A value you can't find there: work it out yourself, or use 2d.
- **Every route or function a test calls already exists in `app/`.** `client.get(...)` and `client.post(...)` are the API. A test that calls a function that doesn't exist yet is designing the code for Claude: use 2d.
- **Some tests already pass before you build anything:** criteria 2, 5 and 6, and maybe 4.   
**That's expected**; they guard behavior your change <ins>must not</ins> break.
- **Each test must read `uses` from the database** after the action, not just check the status code.

#### 2d. If a test doesn't match your expected results, tell Claude what it should be and why

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

**Example:**

```text
The test for criterion 1 expects the detail "Promo code WELCOME5 is used up",
but it should be "Promo code WELCOME5 has been fully used" because that's the
exact message in the criterion. Fix that test.
```

#### 2e. Commit the test code

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1d: tests"
```

### Step 3. Make the tests pass (write the code)

#### 3a. Clear the conversation

To get good results, Claude should build from the "spec" and your committed tests (not all the context from that chat):

```text
/clear
```

#### 3b. Ask Claude to make the tests pass

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab1d-promo-limits.md for context. Run the full suite and show me
the output.
```

Claude shouldn't touch any test file.

We don't want to rewrite tests we've already verified to make them pass. The code alone should do that. Step 4 checks it.

### Step 4. Check the evidence

Don't take Claude's word for it; check for yourself.

#### 4a. Run the tests

The last line should say only `passed`, with no `skipped`, `deselected` or `xfailed`:

```text
! uv run pytest
```

#### 4b. Check that Claude only changed app code

This shows the files that have changed since the last commit.  
Every file this lists should be under `app/`:

```text
! git status --short
```

A file in `tests/` (changed, or new with `??`), a `conftest.py`, or `pyproject.toml` means Claude touched your tests or how they run: ask why before going on. If there are any fixes in step 6, the only test changes should be the new tests you asked for. Nothing existing should be modified.

#### 4c. Visual tests in the browser

Ask Claude to start the app in the background ([more on starting the app](01-getting-started.md#start-the-app)):

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (click your endpoint, **Try it out**, **Execute**) or [the UI](01-getting-started.md#use-the-web-ui) at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Use values from your expected results.

**You can't hit a limit by hand with the seed data:** the seeded limits are 500 and 1000 uses, and no page or endpoint shows `uses`. Your tests are the check for criteria 1 to 3. By hand, confirm that a promo quote, a promo order and a cancel still work. To see the 400 for yourself, lower one limit first (the app reads the database on every request, so no restart is needed):

```text
! uv run python -c "import sqlite3; c = sqlite3.connect('showtix.db'); c.execute(\"UPDATE promo_codes SET max_uses = uses + 1 WHERE code = 'WELCOME5'\"); c.commit()"
```

Now one more `WELCOME5` order works and the next quote or order with it is rejected. Reset with `uv run python -m app.seed` when you're done.

When you're done, stop the app:

```text
Stop the app.
```

#### 4d. Something doesn't match?

Tell Claude which criterion failed and what you saw.

### Step 5. Review the diff

#### 5a. Read every change Claude made before you accept it

These commands stage the changes and then show the diff between these staged changes and the latest commit on your branch.

```text
! git add -A && git diff --staged
```

- Can you explain every change?
- Was anything touched that has nothing to do with promo limits?
- Prefer side by side? Use VS Code's **Source Control** panel.

Your tests are already committed, so this shows only the code Claude wrote.

### Step 6. Get a second opinion

#### 6a. Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. It hasn't seen your conversation, and it checks the change against this sheet.

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1d-promo-limits.md. It hasn't seen our conversation. It should
check every acceptance criterion, not report style, and not change any files
or the database. Show me its findings as a numbered list, each with:
- a label: MUST FIX (a criterion isn't met, or a bug), OUT OF SCOPE (real, but
  not in the criteria, or already there before this branch), UNSURE, or
  OPTIONAL
- which criterion it's about
- evidence: the file and line, or an input that gives the wrong result

To keep it simple, after you categorize the findings only show MUST FIX. All
other findings you can ignore.

Then ask me which ones to fix. For each one I pick, write a failing test that
shows the problem, then fix it. Run the full suite and show me the output.
```

Claude shows the MUST FIX findings and asks which to fix. The labels are the reviewer's opinion, so check the evidence yourself before you answer.

#### 6b. Answer with the numbers you want fixed

For example "1 and 3". Then repeat steps 4 and 5.   
Or you can decide you don't want to fix it, or you want to have a chat with Claude about it before you decide.

Why "don't report style"? See [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7. Commit

Commit when you're satisfied with the change:

```text
! git add -A && git commit -m "lab1d: promo usage limits"
```

## Checklist: What Done Means

- [ ] A test for each given criterion and for your own edge cases, all passing
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] `uses` is checked by reading the database after each action, not just by status codes
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself (a promo quote, order and cancel; the limit itself only if you lowered `max_uses`)
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc23818fa556ef1e8373e69c). Open one level at a time.
