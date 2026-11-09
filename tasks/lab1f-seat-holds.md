# Lab 1f: Expiring seat holds

- **Tier:** Advanced
- **Time:** 50 minutes
- Solo or with a partner

## Start here

**New here?** Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).

**This lab:** a feature you design yourself. You settle the open decisions with Claude, then build it slice by slice.

**A slice** is one small piece of behavior that works end to end, such as "a quote holds the seats", not a layer such as "all the database code".

1. Run the command under [Starting branch](#starting-branch).
2. Read [Goal](#goal), [Background](#background), [Acceptance criteria](#acceptance-criteria) and [Decisions to make](#decisions-to-make).
3. Follow [The workflow](#the-workflow) step by step.

**Step 1 starts with Claude:** it explains the code you'll change, then proposes an answer to each open decision for you to correct. Then you write out (or think about) your expected results yourself.

**You're done when you can check every box under [Checklist: What Done Means](#checklist-what-done-means).**

**Extra time?** Pull an item off your Not doing list (step 7). Stuck? See [Hints](#hints).

## Goal

#### Feature request: "A quote holds the quoted seats for 10 minutes so nobody else can buy them. Expired holds release automatically. Time is injected so tests never sleep."

**What "time is injected" means:** the code takes the current time as an input (`now`) instead of reading the clock itself, so a test can jump the clock forward 10 minutes instantly instead of waiting.

## Starting branch

Copy the command below and run in Claude Code

```text
! git switch main && uv run python -m app.seed && git switch -c lab1f-seat-holds && uv run pytest
```

Here's what it does:

1. Switches to `main`, so the new branch starts from the original code
2. Resets the database to the seed data
3. Creates new feature branch `lab1f-seat-holds` from `main`
4. Runs the tests

Every test should pass before you change anything.

**Trouble?** See [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

Here is the relevant background about the feature you'll be building:

- **Seats left = seats total - seats sold** on orders that aren't cancelled (`inventory.tiers_for_performance()`). Holds would be a third term. The UI's quote form (`POST /performances/{id}/quote`) and its "Place order" button go through the same `orders.quote()` and `orders.create_order()`, so they're affected too.
- **Time is already injected:** routes take `now` from the `get_now` dependency in `app/clock.py`, and `tests/conftest.py` overrides it. Each test starts at a fixed time, which `@pytest.mark.parametrize("now", [datetime(...)])` can change. To move time within a test (criterion 2), the test asks for the `clock` fixture and sets `clock.now = datetime(...)` between requests.
- **Today a quote "writes nothing",** and `tests/test_orders.py::test_quote_writes_nothing` checks that no orders are created and no promo uses are recorded. This feature changes what a quote does on purpose; decide what that test should still promise.

**A handy test target:** the nearly sold out tier (Gravity Optional VIP on Nov 14, 2 seats left).

**Changing the schema?** If you add a table or column in `app/db.py`, [reset the database](01-getting-started.md#reset-the-database) afterwards, or the UI will break even while tests pass.

**For an illustration of how quotes and orders work, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).**

## Acceptance criteria

In this lab, two criteria are given below. Criteria 3 and on come from your decisions (see [Decisions to make](#decisions-to-make) below): **write them with Claude's help** before you write tests.

**Every criterion needs at least one test.**

1. After a quote for the last 2 VIP seats, a second customer's quote or order for 1 of those seats is rejected with 409 while the hold is active.
2. 10 minutes after the quote, those seats can be bought again. The test moves the injected clock; it never sleeps.
3. _..._
4. _..._
5. _..._

### Decisions to make

Decide these with Claude, then turn each decision into a criterion. Use the explore and proposal prompts in [step 1 of The workflow](#step-1-decide-what-to-build-and-what-done-means) below:

- Exactly when does a hold expire: at 10:00, or after it? Test both sides of the boundary.
- How does the customer who holds the seats use them? (A hold id returned by the quote and passed to `POST /orders`, and carried by the UI's "Place order" form?)
- Does placing the order use up the hold? Does a second quote from the same customer replace the first hold, including a re-quote from the page's quote form? (Without that, re-quoting the last seats on the page gets a 409 from your own hold. Also decide what the page shows the holder: if their own hold counts against `seats_left`, the tier reads "Sold out" and its quantity box is disabled, so they can't re-quote at all.)
- How do held seats show up in `/performances/{id}/availability` and on the performance page?
- `create_order()` prices through `quote()`. Should creating an order also create a hold? If not, how do you separate pricing from holding?

50 minutes is tight. Claude proposes the simplest answer that works for each; change a pick only when you have a reason, and note what you'd do with more time.

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

1. Start a fresh conversation. Claude explains the code and proposes the decisions; you correct them. Then you write your expected results (without Claude).
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, then commit.
3. Start a fresh conversation. Claude makes the tests pass without changing them, one slice at a time. You review and commit each slice.
4. Check the evidence: run the tests, confirm your tests didn't change, try it in the browser.
5. Review the whole diff.
6. A subagent reviews the change. For each real bug, Claude writes a failing test and fixes it, then you repeat steps 4 and 5.
7. Commit.

Why each step matters: [How we work](00-how-we-work.md).

### Step 1. Decide what to build and what "done" means

#### 1a. Start with a fresh conversation

```text
/clear
```

#### 1b. Have Claude explain the code

Get oriented in the code you'll change before you decide anything.

```text
Read tasks/lab1f-seat-holds.md. Before we decide anything, explain how quotes
and orders work today: which functions run in what order, where seats are
counted, how the current time reaches the code, and every route and page form
that leads there. Plain words, file names included, short enough to read in 2
minutes. Don't change anything.
```

#### 1c. Have Claude propose the decisions, then correct it

This covers [Decisions to make](#decisions-to-make). Claude proposes one answer per bullet in a single message, capped at 5 new criteria and 3 slices; you keep the picks you agree with and change the rest. You still choose, by exception.

```text
Read tasks/lab1f-seat-holds.md and the relevant code. Work through the
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

**Reply with your changes**, or none. For example:

```text
Change 2 to the simplest option you listed. Keep the rest.
```

```text
Keep all your picks.
```

**⏱ About 15 minutes for exploring and the proposal together.** Disagree with a pick but can't settle it quickly? Take Claude's pick and put yours on the "Not doing" list.

#### 1d. Review the acceptance criteria (without Claude)

This is how Claude knows when the feature is complete. Think through exactly what each criterion should return before Claude writes anything.  
Make a note of this somewhere to refer to later (like notes, notepad, or an empty text file. Whatever works for you).

**Go through [Acceptance criteria](#acceptance-criteria) one by one, including the ones you just added:** which status code, the exact message, the exact seat counts and cents, and the exact times on each side of the 10-minute boundary.

**Note:**

- Every show, night, price, seat count, promo code and seeded order, plus how a price is built, is in [`docs/seed-data.md`](../docs/seed-data.md) for your convenience.
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2. Implement tests first

#### 2a. Start with a fresh conversation

Your decisions are saved in the sheet, so clearing doesn't lose them.

```text
/clear
```

#### 2b. Have Claude write failing tests. Check them against your expected results

```text
Read tasks/lab1f-seat-holds.md and the relevant code. Write a failing test for
each acceptance criterion, including the ones you added from your decisions
(not the "Not doing" list). Test behavior through the API, the pages, or
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
- **Criterion 2's test must move the injected clock; it never sleeps.** Expiry must be tested on both sides of the 10-minute boundary.
- **`test_quote_writes_nothing` must say what you decided a quote may now write** (see [Background](#background)).
- **Every criterion you added from your decisions must have a test.**

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
The test for criterion 1 expects a 400 for the second customer's quote, but
it should be 409 because the seats are held. Fix that test.
```

#### 2e. Commit the test code

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1f: tests"
```

### Step 3. Make the tests pass, one slice at a time (write the code)

#### 3a. Clear the conversation

To get good results, Claude should build from the "spec" and your committed tests (not all the context from that chat):

```text
/clear
```

#### 3b. Ask Claude to make the tests pass

```text
Make the new tests from my last commit pass (see git show HEAD), one slice at
a time, in the order of the Slices list in the sheet. Don't change any test.
If you change anything the tests don't need, tell me what and why. Read
tasks/lab1f-seat-holds.md for context. After each slice, run the full suite,
show me the output, and stop so I can review and commit it.
```

Claude shouldn't touch any test file.

We don't want to rewrite tests we've already verified to make them pass. The code alone should do that. Step 4 checks it.

#### 3c. After each slice, review and commit it

- Read its diff:

  ```text
  ! git diff
  ```

- Check that Claude only changed app code. Every file this lists should be under `app/`:

  ```text
  ! git status --short
  ```

- Commit the slice, then tell Claude "Next slice.":

  ```text
  ! git add -A && git commit -m "lab1f: <slice name>"
  ```

Tests for later slices still fail until their slice is built; that's expected. The other way round happens too: a later slice's tests may already pass because an earlier slice covered them. Then Claude has nothing to change and `git commit` says "nothing to commit"; that's fine, move on. Why slices? See [step 3 of How we work](00-how-we-work.md#3-clear-then-implement).

### Step 4. Check the evidence

Don't take Claude's word for it; check for yourself.

#### 4a. Run the tests

The last line should say only `passed`, with no `skipped`, `deselected` or `xfailed`:

```text
! uv run pytest
```

#### 4b. Check that Claude only changed app code

You committed each slice, so this shows only what's changed since your last commit. It may list nothing.  
Any file it lists should be under `app/`:

```text
! git status --short
```

A file in `tests/` (changed, or new with `??`), a `conftest.py`, or `pyproject.toml` means Claude touched your tests or how they run: ask why before going on. If there are any fixes in step 6, the only test changes should be the new tests you asked for. Nothing existing should be modified.

#### 4c. Check that no slice commit changed your tests

This lists the commits on this branch that touched your tests. It should show only your "lab1f: tests" commit:

```text
! git log --oneline --stat main..HEAD -- tests/ conftest.py pyproject.toml
```

#### 4d. Visual tests in the browser

Ask Claude to start the app in the background ([more on starting the app](01-getting-started.md#start-the-app)):

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (click your endpoint, **Try it out**, **Execute**) or [the UI](01-getting-started.md#use-the-web-ui) at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Use values from your expected results: check that a second customer's quote for held seats gets a 409.

**Test "a second customer" from /docs or another browser window**, not by re-quoting in the same window. If your page's quote form doesn't carry the hold, re-quoting the last seats there gets a 409 from your own hold.

**Don't sit and wait for a hold to expire.** The running app uses the real clock, and your tests already check expiry.

Want to see one expire anyway? Quote the last 2 VIP seats (Gravity Optional, Nov 14) now, then do steps 5 and 6. When you're done, quote them again as a different customer, in /docs or another browser window: the hold has expired, so it works.

When you're done, stop the app (after step 6, if you're watching a hold expire):

```text
Stop the app.
```

#### 4e. Something doesn't match?

Tell Claude which criterion failed and what you saw.

### Step 5. Review the diff

#### 5a. Read the whole feature together before you accept it

You read each slice as it went in. This shows everything Claude changed in `app/` on this branch:

```text
! git diff main -- app/
```

- Can you explain every change?
- Was anything touched that has nothing to do with seat holds?
- Prefer side by side? Use VS Code's **Source Control** panel.

Your tests are in their own commit, so this shows only the code Claude wrote.

### Step 6. Get a second opinion

#### 6a. Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. It hasn't seen your conversation, and it checks the change against this sheet.

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1f-seat-holds.md. It hasn't seen our conversation. It should
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

Commit when you're satisfied with the change. If you didn't fix anything in step 6, your slices are already committed and there's nothing left to commit.

```text
! git add -A && git commit -m "lab1f: seat holds"
```

### Finished with time to spare?

Pull an item off your Not doing list and run it through the workflow, starting at step 2.

## Checklist: What Done Means

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
