# Lab 1e: Waitlist

- **Tier**: Advanced
- **Time**: 60 minutes
- Solo or with a partner

## Start here

If this is your first lab, read [Getting started](01-getting-started.md) for how to run commands and the app, and then read [How we work](00-how-we-work.md) for the workflow. Each page takes about 5 minutes to read.

In this lab, you design the feature yourself. You settle the open decisions with Claude, and then you build the feature slice by slice. A slice is one small piece of behavior that works end to end, such as "customers can join the waitlist," not a layer such as "all the database code."

To run this lab, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Run the command in the [Starting branch](#starting-branch) section of this document.
3. Read the [Goal](#goal), [Background](#background), [Acceptance criteria](#acceptance-criteria), and [Decisions to make](#decisions-to-make) sections.
4. Follow the [Workflow](#workflow) section step by step.

Step 1 starts with Claude. Claude explains the code that you change, and then proposes an answer to each open decision for you to correct. After that, you write your expected results yourself.

You're done when you can check every box in the [Completion checklist](#completion-checklist) section of this document. If you have extra time, see the [Optional: Use the time you have left](#optional-use-the-time-you-have-left) section of this document. If you're stuck, see the [Hints](#hints) section.

## Goal

The feature request is the following: "When a tier is sold out, let customers join a waitlist for it. When an order is cancelled, the freed seats go to the waitlist first-in-first-out, and partial quantities are allowed."

## Starting branch

To start the lab, enter the following command in Claude Code, which switches to `main`, resets the database, creates the `lab1e-waitlist` branch, and runs the tests:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1e-waitlist && uv run pytest
```

Every test passes before you change anything. If the command fails, see [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

The following list describes the code that the feature touches and the rules that are already settled:

- **Seats are never stored as a count**: seats sold is the sum of order line quantities on orders that aren't cancelled, in the `app/inventory.py` file. Cancelling an order frees its seats automatically, and seats are freed in exactly one place, the `orders.cancel_order()` function.
- **There's no waitlist table yet**: the schema is in the `app/db.py` file. The UI marks a sold-out tier "Sold out" on the performance page, and a join form can go there.
- **In tests, make any tier small inside `with conn:`**: for example, `with conn: conn.execute("UPDATE price_tiers SET seats_total = 3 WHERE id = ?", (tier_id,))`. Without `with conn:`, the change leaves a transaction open and the next order fails. Then buy 3 seats in one order to sell the tier out, add two waitlist entries for 2 seats each, and cancel that order to free exactly 3 seats.
- **Already decided for you, so that the proposal round stays short**: a waitlist entry's `qty` is 1 to 8, like an order, and anything else gets the request model's HTTP `422` status code, the same way an order for 9 tickets does. Joining twice with the same email for the same tier is rejected with an HTTP `409` status code. Freed seats that nobody in line wants go back on general sale. Leaving the waitlist is not part of this lab and belongs on the Not doing list.

**Caution**: If you add a table or column in the `app/db.py` file, [reset the database](01-getting-started.md#reset-the-database) afterwards. Otherwise, the UI breaks even though the tests pass.

For an illustration of how orders and cancels work, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).

## Acceptance criteria

In this lab, two criteria are given. Criteria 3 and onward come from your decisions in the [Decisions to make](#decisions-to-make) section. Write them with Claude's help before you write tests.

Every criterion needs at least one test.

1. Joining the waitlist for a tier that still has seats is rejected with an HTTP `409` status code and the detail `This tier still has seats`. The customer buys instead.
2. When 3 seats are freed and the first two people in line want 2 seats each, the first gets 2 and the second gets 1, in the order they joined.
3. _..._
4. _..._
5. _..._

### Decisions to make

Decide the following questions with Claude, and then turn each decision into a criterion. Use the explore and proposal prompts in the [Step 1](#step-1-decide-what-to-build-and-what-done-means) section of this document:

- What does "gets the seats" mean: a paid order created for them, or something else? At what price, with which fees?
- After a partial fill, does the person keep waiting for the rest?
- What does joining return, and how does a customer check their place or status? API only, or the UI too?
- Can a regular buyer get freed seats while someone is waiting, or does the line get them first?

Four decisions give about four new criteria. The smaller questions, such as duplicate joins, the ticket limit, leftovers, and leaving the line, are settled in the [Background](#background) section.

The lab's 60 minutes are tight. Claude proposes the simplest answer that works for each question. Change a pick only when you have a reason, and note what you'd do with more time.

## Workflow

### About the workflow

There are many workflows for working with a coding agent, and no single correct one, because the models and the methods change fast. This lab introduces one way to build good software reliably with a coding agent such as Claude, based on software engineering principles that have been around for decades and on the recommended practices from Anthropic and others. For the full argument, see [How we work](00-how-we-work.md).

**Note**: Many teams align on an idea first, have the agent write a spec, and create work items for the agent before steps 2 to 7. This lab has limited time, so it focuses on the coding and review parts. We recommend that you get experience with the earlier parts on your own time.

### Workflow overview

The lab has the following seven steps:

1. Start a fresh conversation. Claude explains the code and proposes the decisions, and you correct them. Then you write your expected results without Claude.
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, and then you commit them.
3. Start a fresh conversation. Claude makes the tests pass without changing them, one slice at a time. You review and commit each slice.
4. Check the evidence: run the tests, confirm that your tests didn't change, and try the feature in the browser.
5. Review the whole diff.
6. A subagent, a separate Claude that starts with no memory of this conversation, reviews the change. For each real bug, Claude writes a failing test and fixes it, and then you repeat steps 4 and 5.
7. Commit.

For more information about why each step matters, see [How we work](00-how-we-work.md).

### Step 1: Decide what to build and what "done" means

#### 1a: Start a fresh conversation

Start a new conversation:

```text
/clear
```

#### 1b: Ask Claude to explain the code

To get oriented in the code that you change before you decide anything, ask Claude:

```text
Read tasks/lab1e-waitlist.md. Before we decide anything, explain how seats
work today: how seats left are counted, exactly what happens when an order is
cancelled, and every route and page form that leads there. Plain words, file
names included, short enough to read in 2 minutes. Don't change anything.
```

#### 1c: Ask Claude to propose the decisions, and then correct it

This step covers the [Decisions to make](#decisions-to-make) section. Claude proposes one answer per bullet in a single message, capped at 5 new criteria and 3 slices. You keep the picks that you agree with and change the rest, so you still choose, by exception.

To get the proposal, ask Claude:

```text
Read tasks/lab1e-waitlist.md and the relevant code. Work through the
"Decisions to make" for me in one message: for each bullet, your pick in one
line, why, and the alternative you rejected. If a pick depends on how the code
works, explain that part in plain words first. Then imagine this shipped and a
customer hit a problem: name the three most likely things our picks don't
cover and say which one, if any, you'd make a criterion. Don't write any code
or tests. End by asking me which picks to change. Once I've answered, replace
the placeholder criteria (3 onward) in Acceptance criteria with at most 5 new
criteria: one numbered, testable criterion each, describing behavior rather
than which functions to create, with exact status codes and messages; under
each, a "Why:" line with the reason we chose it; right after them, a short
"Not doing" list for everything we deferred, including problems we didn't make
criteria; and last, a "Slices" list of at most 3 vertical slices (each a piece
of behavior that works end to end, small enough to review in a few minutes),
in build order, with the criteria each covers. Then replace everything under
the Decisions to make heading (the intro sentence, the bullets and the
paragraph after them) with one line: "Decided: see criteria 3 onward, each
with its Why. Deferred items are under Not doing." Change nothing else in the
sheet. Show me what you changed so I can check it.
```

Reply with the picks to change, or with none. For example, to change one pick:

```text
Change 2 to the simplest option you listed. Keep the rest.
```

To accept the proposal as it is:

```text
Keep all your picks.
```

After you answer, Claude writes the criteria, the Not doing list, and the Slices into this sheet, so they survive `/clear`.

Spend about 15 minutes on exploring and the proposal together. If you disagree with a pick but can't settle it in that time, take Claude's pick and put yours on the Not doing list.

#### 1d: Review the acceptance criteria without Claude

The acceptance criteria are how Claude knows when the feature is complete. Before Claude writes anything, work out exactly what each criterion returns, and write the results down where you can find them later, such as a notes app or a text file outside your `showtix` folder, because anything inside the folder gets committed with your tests.

Go through the [Acceptance criteria](#acceptance-criteria) section one by one, including the criteria that you added: the status code, the exact message, the exact seat counts, and the exact cents. For criterion 2, the setup (which tier, which order, and `with conn:`) is in the third bullet of the [Background](#background) section.

**Note**: Every show, night, price, seat count, promo code, and seeded order, plus how a price is built, is in [Seed data](../docs/seed-data.md). To check a value in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

Your decisions are saved in the sheet, so clearing the conversation doesn't lose them:

```text
/clear
```

#### 2b: Ask Claude for failing tests

To get one failing test per criterion, ask Claude:

```text
Read tasks/lab1e-waitlist.md and the relevant code. Write a failing test for
each acceptance criterion, including the ones you added from your decisions
(not the "Not doing" list). Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

#### 2c: Check the tests against your expected results

Claude's reply is your checklist: one line per test with the criterion it covers, what it expects, and whether it passes today. If the reply doesn't give you that, ask:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the following points:

- **Each expected value matches your step 1 table.** Claude wrote the tests and the summary, so the table that you wrote without Claude is the thing to trust. If you can't find a value there, work it out yourself, or use 2d.
- **Every route or function that a test calls already exists in `app/`.** The `client.get(...)` and `client.post(...)` calls are the API. A test that calls a function that doesn't exist yet designs the code for Claude. Use 2d.
- **Each assert line can run.** Before the route exists, every new test fails at its first request with an HTTP `404` status code, so an assert line further down never runs. Read the assert lines once against the objects they use, or ask Claude: "Which line of each test fails today, and would the assert lines run if the route existed?"
- **First-in-first-out and the partial fill are tested with exact seat counts.**
- **Every criterion that you added from your decisions has a test.**

#### 2d: Correct a test that doesn't match your expected results

If a test expects the wrong value, tell Claude what the value is and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

The following example corrects a test for criterion 2:

```text
The test for criterion 2 expects the second person to get 2 seats, but it
should be 1 because only 3 seats were freed and the first person takes 2. Fix
that test.
```

#### 2e: Commit the tests

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1e: tests"
```

### Step 3: Make the tests pass, one slice at a time

#### 3a: Clear the conversation

Claude builds from the sheet and your committed tests, not from the earlier conversation, so clear it:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

To build the first slice, ask Claude:

```text
Make the new tests from my last commit pass (see git show HEAD), one slice at
a time, in the order of the Slices list in the sheet. Don't change any test.
If you change anything the tests don't need, tell me what and why. Read
tasks/lab1e-waitlist.md for context. After each slice, run the full suite,
show me the output, and stop so I can review and commit it.
```

Claude must not touch any test file. The tests that you verified are the target, and the code alone makes them pass. Step 4 checks this.

#### 3c: Review and commit each slice

After each slice, follow these steps:

1. Read the slice's diff:

   ```text
   ! git diff
   ```

2. Check that Claude changed only app code. Every file in this list must be under `app/`:

   ```text
   ! git status --short
   ```

3. Commit the slice:

   ```text
   ! git add -A && git commit -m "lab1e: <slice name>"
   ```

4. Tell Claude "Next slice."

Tests for later slices still fail until their slice is built. The reverse also happens: a later slice's tests might already pass because an earlier slice covered them. Then Claude has nothing to change and the `git commit` command reports "nothing to commit," so move on. For more information about why slices matter, see [step 3 of How we work](00-how-we-work.md#3-make-the-tests-pass).

### Step 4: Check the evidence

Don't take Claude's word for it. Check for yourself.

#### 4a: Run the tests

Run the full suite. The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`:

```text
! uv run pytest
```

#### 4b: Check that Claude changed only app code

You committed each slice, so this command lists only what changed since your last commit, which might be nothing. Every file in the list must be under `app/`:

```text
! git status --short
```

A file in `tests/`, whether changed or new with `??`, a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask why before you go on. If step 6 adds fixes, the only test changes are the new tests that you asked for, and no existing test changes.

#### 4c: Check that no slice commit changed your tests

This command lists the commits on this branch that touched your tests. It shows only your "lab1e: tests" commit:

```text
! git log --oneline --stat main..HEAD -- tests/ conftest.py pyproject.toml
```

If a committed test turns out to be wrong, because it can't run or your expected results were wrong, have Claude fix only that test and commit it on its own with a message that says why. Expect that commit in this list too. A test that changed so that it passes is the problem. A test that changed for a reason you can state isn't.

#### 4d: Check the feature in your browser

To start the app in the background, ask Claude:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

If your slices added a table or column, [reset the database](01-getting-started.md#reset-the-database) first. Otherwise, the pages fail while the tests pass.

Then open the [API documentation page](http://127.0.0.1:8000/docs), click your endpoint, click **Try it out**, and then click **Execute**. Or use the [web UI](01-getting-started.md#use-the-web-ui) at http://127.0.0.1:8000/. Use values from your expected results. For more information, see [Start the app](01-getting-started.md#start-the-app).

When you're done, stop the app:

```text
Stop the app.
```

#### 4e: Report a mismatch

If something doesn't match, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read the whole feature before you accept it

You read each slice as it went in. This command shows everything that Claude changed in `app/` on this branch:

```text
! git diff main -- app/
```

As you read, ask yourself the following questions:

- Can you explain every change?
- Was anything touched that has nothing to do with the waitlist?

To see the diff side by side, use the **Source Control** panel in VS Code. Your tests are in their own commit, so this diff shows only the code that Claude wrote.

### Step 6: Get a second opinion

This step is optional in this lab. If you have less than 10 minutes left, skip to [Step 7](#step-7-commit) and commit what you have. Come back to the review if time allows.

#### 6a: Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. The subagent hasn't seen your conversation, and it checks the change against this sheet:

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1e-waitlist.md. It hasn't seen our conversation. It should
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

#### 6b: Answer with the numbers to fix

Reply with the numbers of the findings to fix, for example "1 and 3," and then repeat steps 4 and 5. You can also decide not to fix a finding, or talk it through with Claude before you decide. If Claude reports no MUST FIX findings, there's nothing to answer. Repeat steps 4 and 5 once, and then go on to step 7. If Claude asks how to fix something, answer with the behavior that you want and let Claude choose the code. Claude might also list UNSURE or OPTIONAL findings. Those are yours to decide, and the lab doesn't need them.

For more information about why the prompt says "don't report style," see [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7: Commit

Commit when you're satisfied with the change. If you didn't fix anything in step 6, your slices are already committed and there's nothing left to commit:

```text
! git add -A && git commit -m "lab1e: waitlist"
```

### Optional: Use the time you have left

If you finish early, pull an item off your Not doing list and run it through the workflow, starting at step 2.

## Completion checklist

The lab is complete when the following statements are true:

- [ ] Every decision that you made is written down as a criterion with a test.
- [ ] The tests that you committed in step 2 weren't changed to make them pass.
- [ ] First-in-first-out and the partial fill are tested with exact seat counts.
- [ ] If your decision creates an order, any order created for a waitlisted customer has a price that matches a quote for the same seats.
- [ ] Every test asserts exact values, with exact cents for money, not "smaller" or "not empty."
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] All money math is in the `app/pricing.py` file, in integer cents, with no floats.
- [ ] Routes in the `main.py` and `web.py` files only call into domain modules.
- [ ] You tried the feature by hand in the UI or the `/docs` page with values that you worked out yourself.
- [ ] You can explain every line of the `git diff main` output, and nothing unrelated changed.

## Hints

If you're stuck, open the [workshop hints page](https://www.notion.so/409be0acdc2381f890caecd57cd909dc). It lists the places where students get stuck in this lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see.
