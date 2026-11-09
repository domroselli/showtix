# Lab 1d: Promo usage limits

- **Tier**: Intermediate
- **Time**: 50 minutes
- Solo or with a partner

## Start here

If this is your first lab, read [Getting started](01-getting-started.md) for how to run commands and the app, and then read [How we work](00-how-we-work.md) for the workflow. Together, they take about 5 minutes.

In this lab, you finish a half-built rule that spans ordering and cancelling, with the full workflow.

To run this lab, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Run the command in the [Starting branch](#starting-branch) section of this document.
3. Read the [Goal](#goal), [Background](#background), and [Acceptance criteria](#acceptance-criteria) sections.
4. Follow the [Workflow](#workflow) section step by step.

Step 1 starts with you: think through your edge cases, and then write out your expected results yourself.

You're done when you can check every box in the [Completion checklist](#completion-checklist) section of this document. If you get stuck, see the [Hints](#hints) section.

## Goal

Finish promo usage limits: enforce `max_uses`, and give a use back when an order is cancelled.

## Starting branch

To start the lab, enter the following command in Claude Code:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1d-promo-limits && uv run pytest
```

The command does the following, in order:

1. Switches to the `main` branch, so the new branch starts from the original code.
2. Resets the database to the seed data.
3. Creates the `lab1d-promo-limits` feature branch from `main`.
4. Runs the tests.

Every test passes before you change anything. If the command fails, see [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

The following list describes the code that this feature touches:

- **Promo table**: the `promo_codes` table has a `max_uses` column (null means unlimited) and a `uses` column. The base app is half-built on purpose: `promos.record_use()` adds a use when an order is created, but nothing reads `max_uses`, and cancelling never gives a use back. Orders store the `promo_code` they used, or null when none.
- **Validation and cancelling**: validation lives in `promos.find_valid_promo()`, and cancelling is `orders.cancel_order()`. Cancelling an already-cancelled order raises `Conflict`, which returns an HTTP `409 Conflict` status code with the detail `Order 4 is already cancelled` (for order 4). A quote returns an HTTP `200 OK` status code, and a created order returns `201 Created`. Promo errors already appear inline on the web UI's quote page, so a new error message appears there without a template change.
- **Seeded limits**: the seeded limits are large (LOCALS10: 500, WELCOME5: 1000). In tests, set a small limit inside a `with conn:` block, for example `with conn: conn.execute("UPDATE promo_codes SET max_uses = 1 WHERE code = 'WELCOME5'")`. Without the `with conn:` block, the change leaves a transaction open, and the next order fails.

For an illustration of how orders and cancels flow, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).

## Acceptance criteria

The following list gives most of the criteria. Before you write tests, add one or two edge cases of your own as criteria 7 and 8. Every criterion needs at least one test.

1. A code whose `uses` has reached `max_uses` is rejected with an HTTP `400 Bad Request` status code and the detail `Promo code WELCOME5 has been fully used`, on both quotes and orders.
2. A code one use short of its limit still works, and that order takes the last use (`uses == max_uses` afterwards).
3. Cancelling a paid order that used a promo gives the use back (`uses` goes down by 1).
4. Cancelling an already-cancelled order is rejected with an HTTP `409 Conflict` status code and never gives the use back twice.
5. Cancelling an order without a promo changes no promo's `uses`.
6. A code with `max_uses` null is never rejected for usage.
7. _Your edge case_
8. _Your edge case_ (optional)

Edge cases to think about include the following: whether a quote uses up anything, what a freed use means for a code that was fully used, promo codes typed in lowercase, and what the `409` response in criterion 4 says, not only its status code.

Tests for criteria 2, 5, and 6 pass before you change anything, and the test for criterion 4 might too, depending on how you write it. That's expected: these tests guard behavior that your change must not break.

## Workflow

### About the workflow

There are many ways to work with a coding agent.

Engineers are experimenting to find what works for them. The models change so fast that a practice that works well can be discarded within months, or within a week. You'll probably arrive at your own workflow eventually, if you don't have one already. This lab introduces one way to build good software reliably with a coding agent like Claude.

The main takeaway is that there is no single correct way:

- Some practices help.
- Some practices hurt.
- Some practices seem to work in certain situations with certain models.

The workflow in this lab is based on general software engineering principles that have been around for decades, combined with guidance from Anthropic and others.

We encourage you to use what works for you and share your results.

**Note**: People who work with Claude or another coding agent often align on an idea first, have the agent write that idea into a spec, and create work items such as user stories or issues for the agent to work on, all _before_ steps 2 to 7. Because this is a lab with limited time, it focuses on the coding and review parts of the flow. We recommend that you get experience with the spec and work-item parts on your own time.

### Workflow overview

The workflow has the following seven steps:

1. Start a fresh conversation. Find your edge cases, and then write your expected results without Claude.
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, and then you commit them.
3. Start a fresh conversation. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm that only files under `app/` changed, and try the feature in the browser.
5. Review the diff.
6. A subagent, a separate Claude that starts with no memory of this conversation, reviews the change. For each real bug, Claude writes a failing test and fixes it, and then you repeat steps 4 and 5.
7. Commit.

For more information about why each step matters, see [How we work](00-how-we-work.md).

### Step 1: Align on what done means

#### 1a: Start a fresh conversation

Start a new conversation:

```text
/clear
```

#### 1b: Find your edge cases

This sheet asks for one or two edge cases of your own.

Think them through yourself first: what can a customer do that the criteria don't answer? Type yours into the [Acceptance criteria](#acceptance-criteria) section as criteria 7 and 8.

If you get stuck, ask Claude for a hint:

```text
Read tasks/lab1d-promo-limits.md and the relevant code. I'm stuck finding edge cases
the criteria don't cover. Give me one hint at a time, as a question, not the
edge case itself. If I say "just tell me", suggest 3 edge cases, one sentence
each, and I'll pick. Don't write any code or change any files.
```

#### 1c: Review the acceptance criteria without Claude

The acceptance criteria are how Claude knows when the feature is complete. Before Claude writes anything, think through exactly what each criterion returns, and write your answers down where you can find them later, such as in a notes app or a text file outside your `showtix` folder. Anything inside the folder gets committed with your tests.

Go through the [Acceptance criteria](#acceptance-criteria) section one criterion at a time, and write down the status code, the exact message, and the value of `uses` after each action.

The seeded promo codes and their limits are in [Seed data](../docs/seed-data.md). No page or endpoint shows `uses`, so work it out from the seed table and the criteria. To see the other values in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

Start a new conversation:

```text
/clear
```

#### 2b: Ask Claude for failing tests

Ask Claude to write a failing test for each criterion:

```text
Read tasks/lab1d-promo-limits.md and the relevant code. Write a failing test
for each acceptance criterion. Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

#### 2c: Check the tests against your expected results

Claude's reply is your checklist: one line per test with the criterion it covers, what it expects, and whether it passes before your change. If the reply doesn't give you that, ask for it:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the following:

- **Values**: each expected value matches your step 1 notes. Claude wrote the tests and the summary, so the notes you wrote without Claude are the thing to trust. If a value isn't in your notes, work it out yourself or use 2d.
- **Routes and functions**: every route or function that a test calls already exists in the `app/` directory. The `client.get(...)` and `client.post(...)` calls are the API. A test that calls a function that doesn't exist yet designs the code for Claude. Use 2d.
- **Tests that already pass**: tests for criteria 2, 5, and 6, and maybe 4, pass before you build anything. That's expected. They guard behavior that your change must not break.
- **Database reads**: each test reads `uses` from the database after the action, not only the status code.

#### 2d: Correct a test that doesn't match

If a test doesn't match your expected results, tell Claude what it must be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet, ask for a rewrite:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

The following is an example of a correction:

```text
The test for criterion 1 expects the detail "Promo code WELCOME5 is used up",
but it should be "Promo code WELCOME5 has been fully used" because that's the
exact message in the criterion. Fix that test.
```

#### 2e: Commit the tests

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1d: tests"
```

### Step 3: Make the tests pass

#### 3a: Clear the conversation

Claude builds from the sheet and your committed tests, not from the context of the last chat. Start a new conversation:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

Ask Claude to write the code:

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab1d-promo-limits.md for context. Run the full suite and show me
the output.
```

Claude must not touch any test file. You verified the tests, so the code alone must make them pass. Step 4 checks that.

### Step 4: Check the evidence

Don't take Claude's word for it. Check for yourself.

#### 4a: Run the tests

Run the full suite:

```text
! uv run pytest
```

The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`.

#### 4b: Check that Claude changed only app code

List the files that changed since the last commit:

```text
! git status --short
```

Every file in the list must be under `app/`. A file in `tests/` (changed, or new with `??`), a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask why before you go on. If step 6 adds fixes, the only test changes are the new tests that you asked for, and no existing test changes.

#### 4c: Check the feature in your browser

To start the app in the background, ask Claude:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

For more information, see [Start the app](01-getting-started.md#start-the-app).

Then open the [API documentation page](http://127.0.0.1:8000/docs) and click your endpoint, **Try it out**, and then **Execute**. To use the web UI instead, open http://127.0.0.1:8000/ in your browser, as described in [Use the web UI](01-getting-started.md#use-the-web-ui). Use values from your expected results.

You can't reach a limit by hand with the seed data. The seeded limits are 500 and 1,000 uses, and no page or endpoint shows `uses`, so your tests are the check for criteria 1 to 3. By hand, confirm that a promo quote, a promo order, and a cancel still work.

To see the `400` response yourself, lower one limit first. The app reads the database on every request, so it doesn't need a restart:

```text
! uv run python -c "import sqlite3; c = sqlite3.connect('showtix.db'); c.execute(\"UPDATE promo_codes SET max_uses = uses + 1 WHERE code = 'WELCOME5'\"); c.commit()"
```

After that command, one more `WELCOME5` order works, and the next quote or order with it is rejected. When you're done, reset the database with `uv run python -m app.seed`.

When you're done, stop the app:

```text
Stop the app.
```

#### 4d: Report a mismatch

If something doesn't match, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read every change before you accept it

Stage the changes and show the diff between the staged changes and the latest commit on your branch:

```text
! git add -A && git diff --staged
```

Your tests are already committed, so the diff shows only the code that Claude wrote. Ask yourself the following questions:

- Can you explain every change?
- Did anything change that has nothing to do with promo limits?

To read the diff side by side, use the **Source Control** panel in VS Code.

### Step 6: Get a second opinion

#### 6a: Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. The subagent hasn't seen your conversation, and it checks the change against this sheet:

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

Claude shows the MUST FIX findings and asks which ones to fix. The labels are the reviewer's opinion, so check the evidence yourself before you answer.

#### 6b: Answer with the numbers to fix

Reply with the numbers of the findings to fix, for example "1 and 3", and then repeat steps 4 and 5. You can also decide not to fix a finding, or talk it through with Claude before you decide. Claude might also list UNSURE or OPTIONAL findings. Those are yours to decide, and the lab doesn't need them. If Claude reports no MUST FIX findings, there's nothing to answer. Repeat steps 4 and 5 once, and then go on to step 7. If Claude asks how to fix something, answer with the behavior that you want and let Claude choose the code.

For more information about why the reviewer doesn't report style, see [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7: Commit

When you're satisfied with the change, commit it:

```text
! git add -A && git commit -m "lab1d: promo usage limits"
```

## Completion checklist

The lab is complete when the following statements are true:

- [ ] Each given criterion and each of your own edge cases has a passing test.
- [ ] The tests that you committed in step 2 weren't changed to make them pass.
- [ ] Tests check `uses` by reading the database after each action, not only by status codes.
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty".
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] The limit check lives in `promos.py` and `orders.py`, not in a route.
- [ ] You tried the feature by hand in the web UI or on the `/docs` page with values you worked out yourself: a promo quote, an order, and a cancel, and the limit itself only if you lowered `max_uses`.
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed.

## Hints

If you're stuck, open the [workshop hints page](https://www.notion.so/409be0acdc23818fa556ef1e8373e69c). It lists the places where students get stuck in this lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see.
