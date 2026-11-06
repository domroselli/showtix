# Lab 1f: Expiring seat holds

**Tier:** Advanced · **Time:** 50 minutes · Solo or with a partner

## Start here

A feature you design yourself: you settle the open decisions with Claude, then build it slice by slice.

1. New here? Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).
2. Run the command under [Starting branch](#starting-branch), then read [Goal](#goal), [Background](#background), [Acceptance criteria](#acceptance-criteria) and [Decisions to make](#decisions-to-make).
3. Follow [The workflow](#the-workflow) step by step. Step 1 starts with Claude explaining the code you'll change, then interviewing you about the open decisions; then you write your expected results yourself.

You're done when every box under [Done means](#done-means) is checked. Extra time? Pull an item off your Not doing list (step 7). Stuck? See [Hints](#hints).

## Goal

**Feature request:** "A quote holds the quoted seats for 10 minutes so nobody else can buy them. Expired holds release automatically. Time is injected so tests never sleep."

**What "time is injected" means:** the code takes the current time as an input (`now`) instead of reading the clock itself, so a test can jump the clock forward 10 minutes instantly instead of waiting.

## Starting branch

Create this lab's branch from `main`, reset the database, and check that the tests pass:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1f-seat-holds && uv run pytest
```

Every test should pass before you change anything. Trouble? See [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

Where the code you'll change lives:

- **Seats left = seats total - seats sold** on orders that aren't cancelled (`inventory.tiers_for_performance()`). Holds would be a third term. The UI's quote form (`POST /performances/{id}/quote`) and its "Place order" button go through the same `orders.quote()` and `orders.create_order()`, so they're affected too.
- **Time is already injected:** routes take `now` from the `get_now` dependency in `app/clock.py`, and `tests/conftest.py` overrides it. Each test starts at a fixed time, which `@pytest.mark.parametrize("now", [datetime(...)])` can change. To move time within a test (criterion 2), the test asks for the `clock` fixture and sets `clock.now = datetime(...)` between requests.
- **Today a quote "writes nothing",** and `tests/test_orders.py::test_quote_writes_nothing` checks that no orders are created and no promo uses are recorded. This feature changes what a quote does on purpose; decide what that test should still promise.

The nearly sold out tier (Gravity Optional VIP on Nov 14, 2 seats left) is a handy test target. Changing the schema? If you add a table or column in `app/db.py`, [reset the database](01-getting-started.md#reset-the-database) afterwards, or the UI will break even while tests pass. For a picture of how quotes and orders work, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).

## Acceptance criteria

Two criteria are given. Criteria 3 and on come from your decisions (see [Decisions to make](#decisions-to-make) below): **write them with Claude's help** before you write tests.

1. After a quote for the last 2 VIP seats, a second customer's quote or order for 1 of those seats is rejected with 409 while the hold is active.
2. 10 minutes after the quote, those seats can be bought again. The test moves the injected clock; it never sleeps.
3. _..._
4. _..._
5. _..._

### Decisions to make

Decide these with Claude, then turn each decision into a criterion. Use the explore and interview prompts in [step 1 of The workflow](#1-align-explore-settle-the-decisions-then-write-your-expected-results) below:

- Exactly when does a hold expire: at 10:00, or after it? Test both sides of the boundary.
- How does the customer who holds the seats use them? (A hold id returned by the quote and passed to `POST /orders`, and carried by the UI's "Place order" form?)
- Does placing the order use up the hold? Does a second quote from the same customer replace the first hold, including a re-quote from the page's quote form? (Without that, re-quoting the last seats on the page gets a 409 from your own hold.)
- How do held seats show up in `/performances/{id}/availability` and on the performance page?
- `create_order()` prices through `quote()`. Should creating an order also create a hold? If not, how do you separate pricing from holding?

50 minutes is tight. For each question, pick the simplest answer that works and note what you'd do with more time.

## The workflow

Explore the code and settle the decisions with Claude, write your expected results, then have Claude write the tests, check them yourself, and let Claude build it slice by slice.

- Steps that use Claude have a prompt to copy; commands start with `!`.
- Why each step matters: [How we work](00-how-we-work.md).
- Start with a fresh conversation:

  ```text
  /clear
  ```

### 1. Align: explore, settle the decisions, then write your expected results

Get oriented in the code you'll change, decide with Claude, then write down what "done" means without Claude.

First, have Claude explain the code:

```text
Read tasks/lab1f-seat-holds.md. Before we decide anything, explain how quotes
and orders work today: which functions run in what order, where seats are
counted, how the current time reaches the code, and every route and page form
that leads there. Plain words, file names included, short enough to read in 2
minutes. Don't change anything.
```

Then have Claude interview you about [Decisions to make](#decisions-to-make):

```text
Read tasks/lab1f-seat-holds.md and the relevant code. Interview me about the
"Decisions to make", one question at a time. For each, give me 2-3 options and
your recommendation. If a question depends on how the code works, explain that
part in plain words first. Don't write any code or tests. When we've covered
every decision, imagine this shipped and a customer hit a problem: list what
they could still run into that our decisions don't cover, and ask me which
ones to make criteria. Then replace the placeholder criteria (3 onward) in
Acceptance criteria: one numbered, testable criterion per decision, describing
behavior rather than which functions to create, with exact status codes and
messages; under each, a "Why:" line with the reason we chose it; right after
them, a short "Not doing" list for what we deferred, including problems I
didn't make criteria; and last, a "Slices" list: the order to build it in, as
vertical slices (each one a piece of behavior that works end to end, small
enough to review in a few minutes), with the criteria each slice covers. Then
replace the Decisions to make list with one line: "Decided: see criteria 3
onward, each with its Why. Deferred items are under Not doing." Change nothing
else in the sheet. Show me what you changed so I can check it.
```

**Short on time?** Add this to the end of the prompt:

```text
Keep the scope small enough to build and test in about 20 minutes; anything
bigger goes on the Not doing list.
```

You choose; Claude only offers options. ⏱ About 15 minutes for exploring and the interview together: if a decision drags on, pick the simplest option and put the other on the "Not doing" list.

Then, without Claude, write your expected results:

- Go through [Acceptance criteria](#acceptance-criteria) one by one, including the ones you just added: which status code, the exact message, the exact seat counts and cents, and the exact times on each side of the 10-minute boundary.
- Look up anything you need in [`docs/seed-data.md`](../docs/seed-data.md): every show, night, price, seat count, promo code and seeded order, plus how a price is built.
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

You'll compare Claude's tests against these expected results in step 2.

### 2. Tests first

Have Claude write failing tests, then check them against your expected results.

```text
Read tasks/lab1f-seat-holds.md and the relevant code. Write a failing test for
each acceptance criterion, including the ones you added from your decisions
(not the "Not doing" list). Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

Check especially:

- **Tests check behavior through the API or the page**, not functions that don't exist yet. A test that calls a new function is designing the code for Claude.
- **Criterion 2's test moves the injected clock; it never sleeps.** Expiry is tested on both sides of the 10-minute boundary.
- **`test_quote_writes_nothing` says what you decided a quote may now write** (see [Background](#background)).
- **Every criterion you added from your decisions has a test.**

If a test doesn't match your expected results, tell Claude what it should be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1f: tests"
```

### 3. Clear, then implement, one slice at a time

Clear the conversation, so Claude builds from the sheet and your committed tests, not the chat:

```text
/clear
```

Then ask:

```text
Make the new tests from my last commit pass (see git show HEAD), one slice at
a time, in the order of the Slices list in the sheet. Don't change any test.
If you change anything the tests don't need, tell me what and why. Read
tasks/lab1f-seat-holds.md for context. After each slice, run the full suite,
show me the output, and stop so I can review and commit it.
```

After each slice:

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

Tests for later slices still fail until their slice is built; that's expected. Why slices? See [step 3 of How we work](00-how-we-work.md#3-clear-then-implement).

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

- Check that no slice commit changed your tests. This lists the commits on this branch that touched them, and should show only your "lab1f: tests" commit:

  ```text
  ! git log --oneline --stat main..HEAD -- tests/ conftest.py pyproject.toml
  ```

- Try it yourself. Start the app ([more on starting the app](01-getting-started.md#start-the-app)):

  ```text
  Start the app in the background with uv run uvicorn app.main:app --reload,
  and tell me when it's ready.
  ```

  Then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or [the UI](01-getting-started.md#use-the-web-ui) at http://127.0.0.1:8000/. Use values from your expected results: check that a second customer's quote for held seats gets a 409.

  Don't sit and wait for a hold to expire: the running app uses the real clock, and your tests already check expiry. Want to see one expire anyway? Quote the last 2 VIP seats (Gravity Optional, Nov 14) now, then do steps 5 and 6. When you're done, quote them again as a different customer, in /docs or another browser window: the hold has expired, so it works.

  Test "a second customer" from /docs or another browser window, not by re-quoting in the same window. If your page's quote form doesn't carry the hold, re-quoting the last seats there gets a 409 from your own hold.

  When you're done, stop the app:

  ```text
  Stop the app.
  ```

Something doesn't match? Tell Claude which criterion failed and what you saw.

### 5. Review the diff

You read each slice as it went in. Now read the whole feature together, before you accept it:

```text
! git diff main -- app/
```

- Can you explain every change?
- Was anything touched that has nothing to do with seat holds?
- Prefer side by side? Use VS Code's **Source Control** panel.

This shows everything Claude changed in `app/` on this branch; your tests are in their own commit.

### 6. Get a second opinion

A reviewer that hasn't seen your conversation checks the change against this sheet.

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1f-seat-holds.md. It hasn't seen our conversation. It should check
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
! git add -A && git commit -m "lab1f: seat holds"
```

**Finished with time to spare?** Pull an item off your Not doing list and run it through the workflow, starting at step 2.

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
