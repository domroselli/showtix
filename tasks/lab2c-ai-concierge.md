# Lab 2c: AI concierge

- **Tier**: Advanced
- **Time**: 70 minutes
- Solo or with a partner

## Start here

If this is your first lab, read [Getting started](01-getting-started.md) for how to run commands and the app, and then read [How we work](00-how-we-work.md) for the workflow. Both take about 5 minutes.

In this lab, you design an AI feature yourself. Claude calls tools over the app's own code. You settle the open decisions, and then you build the feature slice by slice. A slice is one small piece of behavior that works end to end, such as "the concierge recommends a real show", not a layer such as "all the database code".

To do this lab, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Run the command in the [Starting branch](#starting-branch) section of this document.
3. Read the [Goal](#goal), [Background](#background), [About the eval](#about-the-eval), [Acceptance criteria](#acceptance-criteria), and [Decisions to make](#decisions-to-make) sections.
4. Follow the [Workflow](#workflow) section step by step.

Step 1 starts with Claude. Claude explains the code that you'll change and then proposes an answer to each open decision for you to correct. After that, you write out your expected results yourself.

You're done when you can check every box in the [Completion checklist](#completion-checklist) section of this document.

If you have extra time, pull an item off your Not doing list in step 7. If you're stuck, see the [Hints](#hints) section.

## Goal

Add the `POST /concierge` endpoint. The endpoint answers questions such as "comedy tonight, 4 people, under $100 each" by calling Claude with tools over the app's own search, availability, and quote functions. It recommends only real shows with live prices.

## Starting branch

To create the lab branch, copy the following command and run it in Claude Code:

```text
! git switch main && uv run python -m app.seed && uv run python -m app.llm && git switch -c lab2c-ai-concierge && uv run pytest
```

The command switches to `main`, resets the database to the seed data, checks your Claude API key, creates the `lab2c-ai-concierge` branch, and runs the tests. The key check prints `OK: Claude API key works`, and every test passes before you change anything.

If `git switch` stops because of unfinished Lab 1 work, see [Start a lab branch](01-getting-started.md#start-a-lab-branch). For key problems, see [Set up your API key](01-getting-started.md#set-up-your-api-key-lab-2).

## Background

The following list describes the feature and the rules that it must follow:

- **Tools**: the tools that Claude calls must be thin wrappers over code that already exists: `shows.list_shows()`, `shows.show_detail()`, `inventory.availability()`, and `orders.quote()`. Don't add pricing or inventory logic. `ShowSummary` includes `category`, but `GET /shows` can't filter by it, because that filter is a different lab's feature. Your search tool can filter the list itself.
- **Time**: "tonight" means local Vegas time from the injected `now`, which routes get from the `get_now` dependency in the `app/clock.py` file. The seeded run is November 10 to November 23, 2026, so pin the clock inside that range.
- **Calling Claude**: the `app/llm.py` file gives routes the `get_llm` dependency and the model name `MODEL`, which is `claude-haiku-5-5`. Keep that model, because it costs less per call than the larger models, so your credits last. The file reads your key from `SHOWTIX_CLAUDE_KEY` in the `.env` file and never from `ANTHROPIC_API_KEY`, which keeps Claude Code on your subscription. For more information, see [Set up your API key](01-getting-started.md#set-up-your-api-key-lab-2). To write cents as dollars, for example in a prompt, use `pricing.dollars()`.
- **Offline tests**: every test runs with a fake Claude automatically, so no test can reach the real API. Take the `fake_claude` fixture (the `FakeClaude` class in the `tests/fakes.py` file) whenever you need to queue replies or check calls. Queue scripted replies with `fake_claude.queue(...)`: a string is a final text answer, and `{"tool_use": "name", "input": {...}}` is a tool call. Check what the app sent with `fake_claude.calls`. A separate eval file checks the recommended show IDs against the real API.
- **Tool loop**: the endpoint calls Claude with the tool definitions, runs each tool that Claude asks for, sends the results back as `tool_result` blocks, and calls Claude again, until Claude answers in text. The last Decisions bullet caps how many rounds the loop makes.
- **Thinking blocks**: a real reply can contain thinking blocks as well as `text` and `tool_use` blocks. In the tool loop, send Claude's reply back exactly as it came (`{"role": "assistant", "content": response.content}`) rather than rebuilding it from the text, and read the final answer only from blocks whose `type` is `text`.
  - **Test it**: code that assumes every block has `.text` crashes on the first real call. `fake_claude.queue({"thinking": "Let me check.", "tool_use": "name", "input": {...}})` puts a thinking block before the tool call. For a timeout, queue `timeout_error()` from the `tests/fakes.py` file.
- **Already decided**: the following points are settled, so the proposal round stays short. A budget such as "under $100 each" means the per-ticket total from `orders.quote()`, fees and tax included. The endpoint returns at most 3 recommendations, in the order that Claude gave them, and is API only, with no UI box. The eval is the `tests/evals/concierge.json` file, a list of cases with `question`, `now`, and `expected_show_ids`, run by the `tests/evals/run_concierge.py` file through the shared runner. For more information about the runner, see the Evals section of the `README.md` file.

**Warning**: Don't give Claude your API key. Don't paste it into Claude Code, in a prompt or in a `!` command. Anything that you type in Claude Code becomes part of the conversation, and Claude can copy it into a file and from there into a commit. Paste the key into the `.env` file yourself, in your editor.

For an illustration of how the pieces fit, see [How a Lab 2 feature fits](../docs/architecture.md#4-how-a-lab-2-feature-fits).

### About the eval

Unit tests and evals check different things:

- **Unit tests**: these tests check your code. The fake client returns scripted replies, so the tests are fast and offline, and they return the same result on every run.
- **Eval**: the eval checks the real model's behavior on realistic questions. It calls the API, the answers vary, and you get a score rather than a guaranteed pass.
- **Failing cases**: when a case fails, read what happened before you change anything: which tools Claude called, with what arguments, and what it got back. Then decide whether to fix the prompt, the tool, or your expected answer.

The eval file is a list of cases. Each case has a question, a pinned time, and the show IDs that you expect. For example:

```json
{"question": "comedy tonight, 4 people, under $100 each",
 "now": "2026-11-14T18:00:00",
 "expected_show_ids": [<the two comedy shows>]}
```

A case passes when the set of recommended show IDs equals `expected_show_ids`, so write cases with at most 3 right answers. Work out each expected answer yourself from the seed data. The eval encodes what you know is right. Write at least 5 cases, and aim for 10.

For the runner, use the shared `run()` function from the `tests/evals/runner.py` file, described in the Evals section of the `README.md` file. You write the cases file and a `check(case)` function that returns whether the case passed and a short detail. The runner prints one line per case and a score. Run it with the `--repeat 2` flag. A score that changes between runs is normal for a model.

If you don't have a working key, build and unit-test everything with `fake_claude`. For the eval and for trying the endpoint on the `/docs` page, pair with someone whose key works.

## Acceptance criteria

This lab gives you two criteria. Criteria 3 onward come from your decisions, which the [Decisions to make](#decisions-to-make) section of this document describes. Write them with Claude's help before you write tests.

Every criterion except the eval needs at least one test.

1. Every recommendation is real and live: its show, performance, and tier exist, there are enough seats for the party, and its price comes from `orders.quote()`. In a unit test whose fake client recommends a made-up show ID, the response leaves that show out.
2. Unit tests use a fake client, run offline, and keep the full suite under 5 seconds. A separate eval file (at least 5 cases, aim for 10) checks the recommended show IDs, and you run it by hand against the real API.
3. _..._
4. _..._
5. _..._

### Decisions to make

Decide the following points with Claude, and then turn each decision into a criterion. Use the explore and proposal prompts in the [Step 1: Decide what to build and what done means](#step-1-decide-what-to-build-and-what-done-means) section of this document:

- Request and response shape: what does `POST /concierge` take, and what does each recommendation contain?
- What does the endpoint return when nothing matches? What does it return when Claude's answer can't be used?
- What does a tool return to Claude when the app rejects the call, for example when the tier is sold out, the tier is wrong, or the party has more than 8 tickets?
- What does `POST /concierge` return when the Claude API fails or times out, and how many tool rounds does it try before it gives up?

Four decisions give you about four new criteria. The budget's meaning, the recommendation count and placement, and the eval file's shape are settled in the [Background](#background) section of this document.

The 70 minutes are tight. Take the pick with the least work unless you have a reason not to, and note what you'd do with more time.

## Workflow

The workflow has the following seven steps:

1. Start a fresh conversation. Claude explains the code and proposes the decisions, and you correct them. Then you write your expected results without Claude.
2. Start a fresh conversation. Claude writes failing tests and the eval cases. You check them against your expected results, and then you commit them.
3. Start a fresh conversation. Claude makes the tests pass without changing them, one slice at a time, and then writes the eval runner. You review and commit each slice.
4. Check the evidence: run the tests, confirm that your tests didn't change, run the eval twice, and try the feature in your browser.
5. Review the whole diff.
6. Optional: a subagent, a separate Claude that starts with no memory of this conversation, reviews the change. For each real bug, Claude writes a failing test and fixes it, and then you repeat steps 4 and 5.
7. Commit.

For more information about why each step matters, see [How we work](00-how-we-work.md).

### Step 1: Decide what to build and what done means

#### 1a: Start a fresh conversation

```text
/clear
```

#### 1b: Ask Claude to explain the code

To get oriented in the code that you'll change before you decide anything, ask Claude:

```text
Read tasks/lab2c-ai-concierge.md. Before we decide anything, explain how the
app's search, availability and quote functions work today: what each one takes
and returns, which of them a tool could call, and which routes and pages use
them today. Plain words, file names included, short enough to read in 2
minutes. Don't change anything.
```

#### 1c: Ask Claude to propose the decisions, and then correct it

This step covers the [Decisions to make](#decisions-to-make) section of this document. Claude proposes one answer per bullet in a single message, capped at 5 new criteria and 3 slices. You keep the picks that you agree with and change the rest, so you still choose, by exception.

To get the proposal, ask Claude:

```text
Read tasks/lab2c-ai-concierge.md and the relevant code. Work through the
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

Reply with the picks to change, or with none. For example:

```text
Change 2 to the simplest option you listed. Keep the rest.
```

```text
Keep all your picks.
```

Spend about 15 minutes on the exploration and the proposal together. If you disagree with a pick but can't settle it in that time, take Claude's pick and put yours on the Not doing list.

#### 1d: Review the acceptance criteria without Claude

The acceptance criteria are how Claude knows when the feature is complete. Before Claude writes anything, work out exactly what each criterion returns, and write the results down outside your `showtix` folder, because anything inside the folder gets committed with your tests.

Go through the [Acceptance criteria](#acceptance-criteria) section of this document one by one, including the criteria that you added. For each one, note the status code, the exact message, the exact cents, and the show IDs that each eval question gets.

**Note**: Every show, night, price, seat count, promo code, and seeded order, plus how a price is built, is in the [`docs/seed-data.md`](../docs/seed-data.md) file. To see the values in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

Your decisions are saved in the sheet, so clearing the conversation doesn't lose them.

```text
/clear
```

#### 2b: Ask Claude for failing tests and the eval cases

To get the tests and the eval cases, ask Claude:

```text
Read tasks/lab2c-ai-concierge.md and the relevant code. Write a failing test
for each acceptance criterion except the eval, including the ones you added
from your decisions (not the "Not doing" list), using fake_claude. Then write
the eval cases to tests/evals/concierge.json (cases only; don't call the API).
Test behavior through the API, the pages, or functions that already exist, not
new functions or exact HTML. Don't change anything in app/. Run the tests and
show me which ones fail.
```

#### 2c: Check the tests and eval cases yourself

Claude's reply is your checklist: one line per test with the criterion that it covers, what it expects, and whether it passes today. Expect 20 to 50 cases. A parametrized test is one test to review, however many cases it runs. If the reply doesn't give you that checklist, ask:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the following points:

- **Expected values**: each expected value, and each eval case, matches your step 1 table. Claude wrote the tests and the summary, so the table that you wrote without Claude is the thing to trust. The eval cases are the model's expected results, so they must be right too. If you can't find a value in your table, work it out yourself, or correct the test as described in [step 2d](#2d-correct-a-test-or-case-that-doesnt-match-your-expected-results).
- **Existing routes and functions**: every route or function that a test calls already exists in `app/`. A test that calls a function that doesn't exist yet designs the code for Claude. To fix it, see [step 2d](#2d-correct-a-test-or-case-that-doesnt-match-your-expected-results).
- **No patching**: no test uses `monkeypatch`, `setattr`, or `patch(` on `app/` constants or the environment. Tests use `fake_claude` and the fixtures in the `tests/conftest.py` file. If a test patches, see [step 2d](#2d-correct-a-test-or-case-that-doesnt-match-your-expected-results).
- **Assert lines that can run**: before the route exists, every new test fails at its first request with an HTTP `404` status code, so an assert line further down never runs. Read the assert lines once against the objects they use, or ask Claude: "Which line of each test fails today, and would the assert lines run if the route existed?"
- **Made-up show**: one test's fake client recommends a made-up show ID, and the response leaves it out (criterion 1).
- **Your criteria**: every criterion that you added from your decisions has a test.

#### 2d: Correct a test or case that doesn't match your expected results

If a test or case doesn't match, tell Claude what it must be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet, ask Claude to rewrite it:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

For example:

```text
The test for criterion 1 expects the made-up show id in the response, but it
should be left out because every recommendation must be a real show. Fix that
test.
```

#### 2e: Commit the tests and eval cases

When every test and case matches your expected results, commit them:

```text
! git add -A && git commit -m "lab2c: tests"
```

### Step 3: Make the tests pass, one slice at a time

#### 3a: Clear the conversation

Claude builds from the sheet and your committed tests, not from the context of the last chat, so clear the conversation:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

To implement the feature, ask Claude:

```text
Make the new tests from my last commit pass (see git show HEAD), one slice at
a time, in the order of the Slices list in the sheet. Don't change any test.
If you change anything the tests don't need, tell me what and why. Read
tasks/lab2c-ai-concierge.md for context. After each slice, run the full suite,
show me the output, and stop so I can review and commit it. When every slice
is done, write tests/evals/run_concierge.py, which runs those eval cases with
the shared runner (see the Evals section of README.md). Don't run it.
```

Claude must not touch any test file. You verified the tests, so the code alone makes them pass, and step 4 checks that.

#### 3c: Review and commit each slice

After each slice, follow these steps:

1. Read the slice's diff:

   ```text
   ! git diff
   ```

2. Check that Claude changed only app code. Every file that the command lists must be under `app/`. Claude writes the `tests/evals/run_concierge.py` file in the same turn as the last slice, so after the last slice the command also lists that one new test file:

   ```text
   ! git status --short
   ```

3. Commit the slice:

   ```text
   ! git add -A && git commit -m "lab2c: <slice name>"
   ```

4. Tell Claude "Next slice."

Tests for later slices fail until their slice is built. The reverse happens too: a later slice's tests might already pass because an earlier slice covered them. Then Claude has nothing to change, `git commit` reports nothing to commit, and you move on. For more information about slices, see [step 3 of How we work](00-how-we-work.md#3-make-the-tests-pass).

### Step 4: Check the evidence

Don't take Claude's word for it. Check for yourself.

#### 4a: Run the tests

The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`:

```text
! uv run pytest
```

#### 4b: Check that Claude changed only app code

You committed each slice, so this command shows only what changed since your last commit, and it might list nothing. Any file that it lists must be under `app/`:

```text
! git status --short
```

A file in `tests/`, whether changed or new with `??`, a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask why before you go on. If step 6 adds fixes, the only test changes are the new tests that you asked for, and no existing test changes.

#### 4c: Check that no slice commit changed your tests

This command lists the commits on this branch that touched your tests. It shows only your `lab2c: tests` commit and the commit that adds the `tests/evals/run_concierge.py` file, which is a new file and so has only `+` lines:

```text
! git log --oneline --stat main..HEAD -- tests/ conftest.py pyproject.toml
```

If a committed test turns out to be wrong, because it can't run or your expected results were wrong, have Claude fix only that test and commit it on its own with a message that says why. Expect that commit in this list too. A test that changed so that it passes is the problem. A test that changed for a reason you can state isn't.

#### 4d: Run the eval against the real API

Run the eval twice. A score that changes between runs is normal. Read each failing case before you change anything:

```text
! uv run python -m tests.evals.run_concierge --repeat 2
```

#### 4e: Test the endpoint in your browser

To start the app in the background, ask Claude:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

For more information, see [Start the app](01-getting-started.md#start-the-app).

Then open the [API documentation page](http://127.0.0.1:8000/docs), click your endpoint, click **Try it out**, and then click **Execute**. You can also use the [ticket shop](http://127.0.0.1:8000/). For more information, see [Use the web UI](01-getting-started.md#use-the-web-ui). Use values from your expected results.

**Caution**: The running app uses the real date, not the pinned `now` in your tests. The seeded run is November 10 to November 23, 2026. Before November 10, "tonight" and "this weekend" find nothing, even when your code is right. Ask about a date in the run, such as "comedy on November 14 for 2", or leave the date out, such as "magic under $80".

When you're done, stop the app:

```text
Stop the app.
```

#### 4f: Report a mismatch

If something doesn't match, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read the whole feature before you accept it

You read each slice as it went in. This command shows everything that Claude changed in `app/` on this branch:

```text
! git diff main -- app/
```

Your tests and eval are in `tests/`, so the command shows only the app code that Claude wrote. Ask yourself the following questions:

- Can you explain every change?
- Did anything change that has nothing to do with the concierge?

### Step 6: Get a second opinion

This step is optional in this lab. If you have less than 10 minutes left, skip to [Step 7: Commit](#step-7-commit) and commit what you have. Come back to the review if time allows.

#### 6a: Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. The subagent hasn't seen your conversation, and it checks the change against this sheet:

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab2c-ai-concierge.md. It hasn't seen our conversation. It should
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

For example, answer "1 and 3". Then repeat steps 4 and 5. You can also decide not to fix a finding, or talk it through with Claude before you decide. Claude might also list UNSURE or OPTIONAL findings. Those are yours to decide, and the lab doesn't need them. If Claude reports no MUST FIX findings, there's nothing to answer. Repeat steps 4 and 5 once, and then go on to step 7. If Claude asks how to fix something, answer with the behavior that you want and let Claude choose the code.

For more information about why the prompt says not to report style, see [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7: Commit

Commit when you're satisfied with the change. If you didn't fix anything in step 6, your slices are already committed and there's nothing left to commit.

```text
! git add -A && git commit -m "lab2c: AI concierge"
```

### Optional: Use the time that's left

Pull an item off your Not doing list and run it through the workflow, starting at step 2.

## Completion checklist

The lab is complete when the following statements are true:

- [ ] Every decision that you made is written down as a criterion with a test.
- [ ] The tests that you committed in step 2 weren't changed to make them pass.
- [ ] Unit tests never touch the network, and the fake client covers a tool call, a final answer, and a made-up show.
- [ ] The eval file has at least 5 cases (aim for 10), each with a question, a pinned time, and expected show IDs, and you ran it against the real API.
- [ ] The `.env` file is listed in `.gitignore`, and the key is read only from `SHOWTIX_CLAUDE_KEY`.
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty".
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] All money math is in the `app/pricing.py` file, in integer cents, with no floats.
- [ ] Routes in `main.py` only call into domain modules.
- [ ] You tried the feature by hand in the UI or on the `/docs` page with values that you worked out yourself.
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed.

## Hints

If you're stuck, open the [workshop hints page](https://www.notion.so/409be0acdc2381aebcc4eddaebc4ec9f). It lists the places where students get stuck in this lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see.
