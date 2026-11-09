# Lab 1f: Expiring seat holds

- **Tier**: Advanced
- **Time**: 60 minutes
- Solo or with a partner

## Start here

If this is your first lab, read [Getting started](01-getting-started.md) for how to run commands and the app, and then read [How we work](00-how-we-work.md) for the workflow. Both take about 5 minutes.

In this lab, you design the feature yourself. You settle the open decisions with Claude, and then you build the feature slice by slice. A slice is one small piece of behavior that works end to end, such as "a quote holds the seats", not a layer such as "all the database code".

To run this lab, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Run the command in the [Starting branch](#starting-branch) section of this document.
3. Read the [Goal](#goal), [Background](#background), [Acceptance criteria](#acceptance-criteria), and [Decisions to make](#decisions-to-make) sections.
4. Follow the [Workflow](#workflow) section step by step.

Step 1 starts with Claude. Claude explains the code that you'll change, and then proposes an answer to each open decision for you to correct. After that, you write out your expected results yourself.

You're done when you can check every box in the [Completion checklist](#completion-checklist) section of this document.

If you have extra time, pull an item off your Not doing list in step 7. If you're stuck, see the [Hints](#hints) section of this document.

## Goal

The feature request reads as follows: "A quote holds the quoted seats for 10 minutes so nobody else can buy them. Expired holds release automatically. Time is injected so tests never sleep."

"Time is injected" means that the code takes the current time as an input (`now`) instead of reading the clock itself. A test can then move the clock forward 10 minutes instantly instead of waiting.

## Starting branch

To start the lab, enter the following command in Claude Code:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1f-seat-holds && uv run pytest
```

The command resets the database, creates the `lab1f-seat-holds` branch from `main`, and runs the tests, which all pass before you change anything.

If the command stops with an error or a test fails, see [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

The following list describes the code that this feature touches:

- **Seats left**: seats left equals seats total minus seats sold on orders that aren't cancelled, in `inventory.tiers_for_performance()`. Holds become a third term. The UI's quote form (`POST /performances/{id}/quote`) and its **Place order** button go through the same `orders.quote()` and `orders.create_order()` functions, so the feature affects them too.
- **Time is already injected**: routes take `now` from the `get_now` dependency in the `app/clock.py` file, and the `tests/conftest.py` file overrides it. Each test starts at a fixed time, which `@pytest.mark.parametrize("now", [datetime(...)])` can change. To move time within a test (criterion 2), the test asks for the `clock` fixture and sets `clock.now = datetime(...)` between requests.
- **A quote writes nothing today**: the `tests/test_orders.py::test_quote_writes_nothing` test checks that a quote creates no orders and records no promo uses. This feature changes what a quote does on purpose, so decide what that test must still promise.

The nearly sold out tier, Gravity Optional VIP on Nov 14 with 2 seats left, is a convenient test target.

**Caution**: If you add a table or column in the `app/db.py` file, [reset the database](01-getting-started.md#reset-the-database) afterward. Otherwise the UI breaks even though the tests pass.

For an illustration of how quotes and orders work, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).

## Acceptance criteria

This sheet gives two criteria. Criteria 3 onward come from your decisions in the [Decisions to make](#decisions-to-make) section of this document. Write them with Claude's help before you write tests.

Every criterion needs at least one test.

1. After a quote for the last 2 VIP seats, a second customer's quote or order for 1 of those seats is rejected with an HTTP `409` status code while the hold is active.
2. 10 minutes after the quote, those seats can be bought again. The test moves the injected clock and never sleeps.
3. _..._
4. _..._
5. _..._

### Decisions to make

Decide the following questions with Claude, and then turn each decision into a criterion. Use the explore and proposal prompts in [Step 1: Decide what to build and what done means](#step-1-decide-what-to-build-and-what-done-means):

- Exactly when does a hold expire: at 10:00, or after it? Test both sides of the boundary.
- How does the customer who holds the seats use them? For example, the quote returns a hold ID that the customer passes to `POST /orders` and that the UI's **Place order** form carries.
- Does placing the order use up the hold? Does a second quote from the same customer replace the first hold, including a re-quote from the page's quote form? Without that, re-quoting the last seats on the page runs into your own hold. Also decide what the page shows the holder: if their own hold counts against the `seats_left` value, the tier reads "Sold out" and its quantity box is disabled, so they can't re-quote at all.
- How do held seats show up in the `/performances/{id}/availability` response and on the performance page?
- The `create_order()` function prices through `quote()`. Does creating an order also create a hold? If not, how do you separate pricing from holding?

The 60 minutes are tight. Claude proposes the simplest answer that works for each question. Change a pick only when you have a reason, and note what you'd do with more time.

## Workflow

### About the workflow

There's no single correct way to work with a coding agent, and the methods change as fast as the models do. This lab teaches one way to build software reliably with Claude, based on software engineering principles that have been around for decades and on the practices that Anthropic and others recommend. For the full argument and its sources, see the [sources behind the workflow](00-how-we-work.md#appendix-sources-behind-the-workflow).

**Note**: People who work with Claude or another coding agent often get alignment on an idea first, have the agent write the idea into a spec, and create work items such as user stories or issues for the agent to work on, all before steps 2 to 7. This lab has limited time, so it focuses on the coding and review parts of the flow. We recommend that you get experience with the earlier parts on your own time.

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

### Step 1: Decide what to build and what done means

#### 1a: Start a fresh conversation

Start a new conversation:

```text
/clear
```

#### 1b: Ask Claude to explain the code

To get oriented in the code that you'll change before you decide anything, ask Claude:

```text
Read tasks/lab1f-seat-holds.md. Before we decide anything, explain how quotes
and orders work today: which functions run in what order, where seats are
counted, how the current time reaches the code, and every route and page form
that leads there. Plain words, file names included, short enough to read in 2
minutes. Don't change anything.
```

#### 1c: Ask Claude to propose the decisions, and then correct it

This step covers the [Decisions to make](#decisions-to-make) section of this document. Claude proposes one answer per bullet in a single message, capped at 5 new criteria and 3 slices. You keep the picks that you agree with and change the rest, so you still choose, by exception. When you answer, Claude writes the criteria, a Not doing list, and a Slices list into this sheet. Reload the sheet in your editor to see them.

To get the proposal, ask Claude:

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

Reply with the picks to change, or with none. For example, to change one pick:

```text
Change 2 to the simplest option you listed. Keep the rest.
```

To accept the proposal as it is:

```text
Keep all your picks.
```

Spend about 15 minutes on exploring and the proposal together. If you disagree with a pick but can't settle it in that time, take Claude's pick and put yours on the Not doing list.

#### 1d: Review the acceptance criteria without Claude

The acceptance criteria are how Claude knows when the feature is complete. Think through exactly what each criterion returns before Claude writes anything, and write the results down somewhere that you can refer to later, such as a notes app or a text file outside your `showtix` folder. Anything inside the folder gets committed with your tests.

Go through the [Acceptance criteria](#acceptance-criteria) section one by one, including the criteria that you added. For each one, write down the status code, the exact message, the exact seat counts and cents, and the exact times on each side of the 10-minute boundary.

The following resources help you work out the values:

- Every show, night, price, seat count, promo code, and seeded order, plus how a price is built, is in the [`docs/seed-data.md`](../docs/seed-data.md) file.
- To see the values in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

Your decisions are saved in the sheet, so clearing the conversation doesn't lose them. Start a new conversation:

```text
/clear
```

#### 2b: Ask Claude for failing tests

To get the tests, ask Claude:

```text
Read tasks/lab1f-seat-holds.md and the relevant code. Write a failing test for
each acceptance criterion, including the ones you added from your decisions
(not the "Not doing" list). Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

Then check the tests against your expected results.

#### 2c: Check the tests that Claude created

Claude's reply is your checklist: one line per test with the criterion it covers, what it expects, and whether it passes today. If the reply doesn't give you that, ask:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the following:

- **Each expected value matches your step 1 table.** Claude wrote the tests and the summary, so the table that you wrote without Claude is the thing to trust. If you can't find a value there, work it out yourself, or use 2d.
- **Every route or function that a test calls already exists in `app/`.** Calls to `client.get(...)` and `client.post(...)` are the API. A test that calls a function that doesn't exist yet is designing the code for Claude. Use 2d.
- **Each assert line can run.** Before the route exists, every new test fails at its first request with an HTTP `404` status code, so an assert line further down never runs. Read the assert lines once against the objects they use, or ask Claude: "Which line of each test fails today, and would the assert lines run if the route existed?"
- **The test for criterion 2 moves the injected clock and never sleeps.** Expiry must be tested on both sides of the 10-minute boundary.
- **The `test_quote_writes_nothing` test says what you decided a quote can now write.** For more information, see the [Background](#background) section of this document.
- **Every criterion that you added from your decisions has a test.**

#### 2d: Correct a test that doesn't match your expected results

If a test doesn't match your expected results, tell Claude what the test must expect and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet, tell Claude:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

The following example corrects a status code:

```text
The test for criterion 1 expects a 400 for the second customer's quote, but
it should be 409 because the seats are held. Fix that test.
```

#### 2e: Commit the tests

When every test matches your expected results, commit the tests:

```text
! git add -A && git commit -m "lab1f: tests"
```

### Step 3: Make the tests pass, one slice at a time

#### 3a: Start a fresh conversation

Claude builds from the sheet and your committed tests, not from the context of the last chat. Start a new conversation:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

To get the implementation, ask Claude:

```text
Make the new tests from my last commit pass (see git show HEAD), one slice at
a time, in the order of the Slices list in the sheet. Don't change any test.
If you change anything the tests don't need, tell me what and why. Read
tasks/lab1f-seat-holds.md for context. After each slice, run the full suite,
show me the output, and stop so I can review and commit it.
```

Claude must not touch any test file. You verified the tests already, so the code alone must make them pass. Step 4 checks that.

#### 3c: Review and commit each slice

After each slice, follow these steps:

1. Read the slice's diff:

   ```text
   ! git diff
   ```

2. Check that Claude changed only app code. Every file that this command lists must be under `app/`:

   ```text
   ! git status --short
   ```

3. Commit the slice:

   ```text
   ! git add -A && git commit -m "lab1f: <slice name>"
   ```

4. Tell Claude "Next slice."

Tests for later slices still fail until their slice is built. The reverse happens too: a later slice's tests might already pass because an earlier slice covered them. Then Claude has nothing to change and the `git commit` command reports "nothing to commit", so move on. For more information about why the lab uses slices, see [step 3 of How we work](00-how-we-work.md#3-make-the-tests-pass).

### Step 4: Check the evidence

Claude's summary isn't evidence. Check the results yourself.

#### 4a: Run the tests

Run the tests yourself. The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`:

```text
! uv run pytest
```

#### 4b: Check that Claude changed only app code

You committed each slice, so this command shows only what changed since your last commit, and it might list nothing. Any file that it lists must be under `app/`:

```text
! git status --short
```

A file in `tests/` (changed, or new with `??`), a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask Claude why before you go on. If step 6 adds fixes, the only test changes are the new tests that you asked for, and no existing test changes.

#### 4c: Check that no slice commit changed your tests

List the commits on this branch that touched your tests. The output shows only your "lab1f: tests" commit:

```text
! git log --oneline --stat main..HEAD -- tests/ conftest.py pyproject.toml
```

If a committed test turns out to be wrong, because it can't run or your expected results were wrong, have Claude fix only that test and commit it on its own with a message that says why. Expect that commit in this list too. A test that changed so that it passes is the problem. A test that changed for a reason you can state isn't.

#### 4d: Check the feature in your browser

If a slice added a table or column in the `app/db.py` file, reset the database first by entering `! uv run python -m app.seed` in Claude Code. Then ask Claude to start the app in the background. For more information, see [Start the app](01-getting-started.md#start-the-app).

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

To try the quote endpoint, follow these steps:

1. Open the [API documentation page](http://127.0.0.1:8000/docs).
2. Click **POST /orders/quote**, and then click **Try it out**.
3. Enter values from your expected results, and then click **Execute**.

Or use [the web UI](01-getting-started.md#use-the-web-ui) at http://127.0.0.1:8000/ instead.

Test "a second customer" from the `/docs` page or another browser window, not by re-quoting in the same window. On the `/docs` page, a second customer's quote for held seats gets an HTTP `409` status code. On the web page, the same request shows the "Only 0 VIP seats left" message, and the page itself returns an HTTP `400` status code, because the page routes render every domain error as a `400` page. If your page's quote form doesn't carry the hold, re-quoting the last seats there shows that message from your own hold.

Don't wait for a hold to expire. The running app uses the real clock, and your tests already check expiry. To watch one expire anyway, quote the last 2 VIP seats (Gravity Optional, Nov 14) now, and then do steps 5 and 6. When you're done, quote the seats again as a different customer, in the `/docs` page or another browser window. The hold has expired, so the quote works.

When you're done, stop the app. If you're watching a hold expire, stop it after step 6:

```text
Stop the app.
```

#### 4e: Report a mismatch

If something doesn't match, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read the whole feature before you accept it

You read each slice as it went in. The following command shows everything that Claude changed in `app/` on this branch:

```text
! git diff main -- app/
```

Your tests are in their own commit, so the diff shows only the code that Claude wrote. As you read, answer the following questions:

- Can you explain every change?
- Did anything change that has nothing to do with seat holds?

If the change makes a line in the `CLAUDE.md`, `README.md`, or `docs/architecture.md` file wrong, note it. On a real project, you update that line in the same branch. In this lab, leave it.

To read the diff side by side, use the **Source Control** panel in VS Code.

### Step 6: Get a second opinion

#### 6a: Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. The subagent hasn't seen your conversation, and it checks the change against this sheet:

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

#### 6b: Answer with the numbers that you want fixed

Reply with the numbers of the findings to fix, for example "1 and 3", and then repeat steps 4 and 5. You can also decide not to fix a finding, or discuss it with Claude before you decide. Claude might also list UNSURE or OPTIONAL findings. Those are yours to decide, and the lab doesn't need them. If Claude reports no MUST FIX findings, there's nothing to answer. Repeat steps 4 and 5 once, and then go on to step 7. If Claude asks how to fix something, answer with the behavior that you want and let Claude choose the code.

For more information about why the prompt says "not report style", see [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7: Commit

When you're satisfied with the change, commit it. If you didn't fix anything in step 6, your slices are already committed and there's nothing left to commit:

```text
! git add -A && git commit -m "lab1f: seat holds"
```

### Optional: Use the time that you have left

If you finish early, pull an item off your Not doing list and run it through the workflow, starting at step 2.

## Completion checklist

The lab is complete when the following statements are true:

- [ ] Every decision that you made is written down as a criterion with a test.
- [ ] The tests that you committed in step 2 weren't changed to make them pass.
- [ ] Expiry is tested on both sides of the 10-minute boundary, with no `sleep`.
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty".
- [ ] The `uv run pytest` command passes and still finishes in less than 5 seconds.
- [ ] All money math is in the `app/pricing.py` file, in integer cents, with no floats.
- [ ] Routes in `main.py` and `web.py` only call into domain modules.
- [ ] You tried the feature by hand in the UI or the `/docs` page with values that you worked out yourself.
- [ ] You can explain every line of the `git diff main` output, and nothing unrelated changed.

## Hints

If you're stuck, open the [workshop hints page](https://www.notion.so/409be0acdc23815daf3ee26438afec9d). It lists the places where students get stuck in this lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see.
