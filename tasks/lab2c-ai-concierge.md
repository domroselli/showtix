# Lab 2c: AI concierge

**Tier:** Advanced · **Time:** 50 minutes · Solo or with a partner

## Start here

An AI feature you design yourself: Claude calls tools over the app's own code, and you settle the open decisions, then build it slice by slice.

1. New here? Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).
2. Run the command under [Starting branch](#starting-branch), then read [Goal](#goal), [Background](#background), [About the eval](#about-the-eval), [Acceptance criteria](#acceptance-criteria) and [Decisions to make](#decisions-to-make).
3. Follow [The workflow](#the-workflow) step by step. Step 1 starts with Claude explaining the code you'll change, then interviewing you about the open decisions; then you write your answer key yourself.

You're done when every box under [Done means](#done-means) is checked. Extra time? Pull an item off your Not doing list (step 7). Stuck? See [Hints](#hints).

## Goal

**Feature request:** "`POST /concierge` answers questions like *comedy tonight, 4 people, under $100 each* by calling Claude with tools over the app's own search, availability and quote functions. It recommends only real shows with live prices."

## Starting branch

Create this lab's branch from `main`, reset the database, check your API key, and run the tests:

```text
! git switch main && uv run python -m app.seed && uv run python -m app.llm && git switch -c lab2c-ai-concierge && uv run pytest
```

The key check should print `OK: Claude API key works`, and every test should pass. If `git switch` stops because of unfinished Lab 1 work, see [Start a lab branch](01-getting-started.md#start-a-lab-branch). Key trouble? See [Set up your API key](01-getting-started.md#set-up-your-api-key-lab-2).

## Background

Where the code your tools will call lives:

- **The tools Claude calls should be thin wrappers over code that already exists:** `shows.list_shows()` / `shows.show_detail()`, `inventory.availability()` and `orders.quote()`. No new pricing or inventory logic. `ShowSummary` includes `category`, but `GET /shows` can't filter by it (that's a different lab feature); your search tool can filter the list itself.
- **"Tonight" means local Vegas time** from the injected `now` (`get_now` in `app/clock.py`). The seeded run is Nov 10 to Nov 23, 2026, so pin the clock inside that range.
- **Calling Claude:** `app/llm.py` gives routes a `get_llm` dependency and the model name `MODEL` (`claude-haiku-5-5`: fast and cheap, so your credits last). It reads your key from `SHOWTIX_CLAUDE_KEY` in `.env` ([Set up your API key](01-getting-started.md#set-up-your-api-key-lab-2)), never `ANTHROPIC_API_KEY`, which keeps Claude Code on your subscription. To write cents as dollars, in a prompt for example, use `pricing.dollars()`.
- **Never give Claude your API key.** Don't paste it into Claude Code, in a prompt or a `!` command. Paste it into `.env` yourself, in your editor: anything you type in Claude Code becomes part of the conversation, and Claude can copy it into a file and from there into a commit.
- **Testing without the network:** every test runs with a fake Claude automatically, so no test can reach the real API. Take the `fake_claude` fixture (`FakeClaude`, in `tests/fakes.py`) whenever you need to queue replies or check calls. Queue scripted replies with `fake_claude.queue(...)`: a string is a final text answer, `{"tool_use": "name", "input": {...}}` is a tool call. Check what was sent with `fake_claude.calls`. A separate eval file checks the recommended show ids against the real API.

For a picture of how the pieces fit, see [How a Lab 2 feature fits](../docs/architecture.md#4-how-a-lab-2-feature-fits).

### About the eval

Unit tests and evals check different things:

- **Unit tests check *your code*:** the fake client returns scripted replies, so they're fast, offline and give the same result every run.
- **The eval checks *the real model's behavior*** on realistic questions. It calls the API, the answers vary, and you get a score, not a guaranteed pass.
- **When a case fails, read what happened before changing anything:** which tools Claude called, with what arguments, and what it got back. Then decide whether to fix the prompt, the tool, or your expected answer.

**The eval file** is a list of cases, each with a question, a pinned time, and the show ids you expect. For example:

```json
{"question": "comedy tonight, 4 people, under $100 each",
 "now": "2026-11-14T18:00:00",
 "expected_show_ids": [<the two comedy shows>]}
```

Work out each expected answer yourself from the seed data. That's the point: the eval encodes what *you* know is right. Aim for 10 cases; 5 is fine if you're short on time.

**The runner:** use the shared runner, `run()` from `tests/evals/runner.py` (see the README). You write the cases file and a `check(case)` function that returns whether the case passed and a short detail; it prints one line per case and a score. Run it with `--repeat 2`; a score that changes between runs is normal for a model.

**No working key?** Build and unit-test everything with `fake_claude`; for the eval and trying it in /docs, pair with someone whose key works.

## Acceptance criteria

Two criteria are given. Criteria 3 and on come from your decisions (see [Decisions to make](#decisions-to-make) below): **write them with Claude's help** before you write tests.

1. Every recommendation is real and live: its show, performance and tier exist, there are enough seats for the party, and its price comes from `orders.quote()`. A unit test whose fake client recommends a made-up show id gets no recommendation for it.
2. Unit tests use a fake client, run offline, and keep the full suite under 5 seconds. A separate eval file (aim for 10 questions, at least 5) checks the recommended show ids, and you run it by hand against the real API.
3. _..._
4. _..._
5. _..._

### Decisions to make

Decide these with Claude, then turn each decision into a criterion. Use the explore and interview prompts in [step 1 of The workflow](#1-align-explore-settle-the-decisions-then-write-your-answer-key) below:

- Request and response shape: what does `POST /concierge` take, and what does each recommendation contain?
- Does "under $100 each" mean the tier price, or the price per person including fees and tax?
- What does the endpoint return when nothing matches? When Claude's answer can't be used?
- What does a tool return to Claude when the app rejects the call (sold out, wrong tier, more than 8 tickets)?
- What does `POST /concierge` return when the Claude API fails or times out, and how many tool rounds before it gives up?
- How many recommendations, in what order? API only, or a box on the UI's home page too?
- What does the eval file look like (question, pinned time, expected show ids), and how do you run it?

50 minutes is tight. For each question, pick the simplest answer that works and note what you'd do with more time.

## The workflow

Explore the code and settle the decisions with Claude, write your answer key, then have Claude write the tests, check them yourself, and let Claude build it slice by slice.

- Steps that use Claude have a prompt to copy; commands start with `!`.
- Why each step matters: [How we work](00-how-we-work.md).
- Start with a fresh conversation:

  ```text
  /clear
  ```

### 1. Align: explore, settle the decisions, then write your answer key

Get oriented in the code you'll change, decide with Claude, then write down what "done" means without Claude.

First, have Claude explain the code:

```text
Read tasks/lab2c-ai-concierge.md. Before we decide anything, explain how the
app's search, availability and quote functions work today: what each one takes
and returns, which of them a tool could call, and which routes and pages use
them today. Plain words, file names included, short enough to read in 2
minutes. Don't change anything.
```

Then have Claude interview you about [Decisions to make](#decisions-to-make):

```text
Read tasks/lab2c-ai-concierge.md and the relevant code. Interview me about the
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

Then, without Claude, write your answer key:

- Go through [Acceptance criteria](#acceptance-criteria) one by one, including the ones you just added: which status code, the exact message, the exact cents, and which show ids each eval question should get.
- Look up anything you need in [`docs/seed-data.md`](../docs/seed-data.md): every show, night, price, seat count, promo code and seeded order, plus how a price is built.
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

You'll compare Claude's tests against this answer key in step 2.

### 2. Tests first

Have Claude write failing tests and the eval cases, then check them against your answer key.

```text
Read tasks/lab2c-ai-concierge.md and the relevant code. Write a failing test
for each acceptance criterion except the eval, including the ones you added
from your decisions (not the "Not doing" list), using fake_claude. Then write
the eval cases to tests/evals/concierge.json (cases only; don't call the API).
Test behavior through the API, the pages, or functions that already exist, not
new functions or exact HTML. Don't change anything in app/. Run the tests and
show me which ones fail.
```

Compare each test, and each eval case, with your answer key. The eval cases are the model's answer key, so they must be right too. Check especially:

- **Tests check behavior through the API or the page**, not functions that don't exist yet. A test that calls a new function is designing the code for Claude.
- **One test's fake client recommends a made-up show id**, and the response leaves it out (criterion 1).
- **Every criterion you added from your decisions has a test.**

If a test doesn't match your answer key, tell Claude what it should be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

When every test and eval case matches your answer key, commit them:

```text
! git add -A && git commit -m "lab2c: tests"
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
tasks/lab2c-ai-concierge.md for context. After each slice, run the full suite,
show me the output, and stop so I can review and commit it. When every slice
is done, write tests/evals/run_concierge.py, which runs those eval cases with
the shared runner (see the README). Don't run it.
```

After each slice:

- Read its diff:

  ```text
  ! git diff
  ```

- Check that Claude only changed app code. Every file this lists should be under `app/`. After the last slice, `tests/evals/run_concierge.py` is the one expected new test file:

  ```text
  ! git status --short
  ```

- Commit the slice, then tell Claude "Next slice.":

  ```text
  ! git add -A && git commit -m "lab2c: <slice name>"
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

- Check that no slice commit changed your tests. This lists the commits on this branch that touched them, and should show only your "lab2c: tests" commit and the one that adds `tests/evals/run_concierge.py` (a new file, so only `+` lines):

  ```text
  ! git log --oneline --stat main..HEAD -- tests/ conftest.py pyproject.toml
  ```

- Run the eval twice against the real API. A score that changes between runs is normal. Read each failing case before changing anything:

  ```text
  ! uv run python -m tests.evals.run_concierge --repeat 2
  ```

- Try it yourself. Start the app ([more on starting the app](01-getting-started.md#start-the-app)):

  ```text
  Start the app in the background with uv run uvicorn app.main:app --reload,
  and tell me when it's ready.
  ```

  Then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/, and use values from your answer key. When you're done, stop it:

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
- Was anything touched that has nothing to do with the concierge?
- Prefer side by side? Use VS Code's **Source Control** panel.

This shows everything Claude changed in `app/` on this branch; your tests and eval are in `tests/`.

### 6. Get a second opinion

A reviewer that hasn't seen your conversation checks the change against this sheet.

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab2c-ai-concierge.md. It hasn't seen our conversation. It should check
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
! git add -A && git commit -m "lab2c: AI concierge"
```

**Finished with time to spare?** Pull an item off your Not doing list and run it through the workflow, starting at step 2.

## Done means

- [ ] Every decision you made is written down as a criterion with a test
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] Unit tests never touch the network; the fake client covers a tool call, a final answer, and a made-up show
- [ ] The eval file has at least 5 questions (aim for 10), each with a pinned time and expected show ids, and you've run it for real
- [ ] `.env` is gitignored, and the key is only ever read from `SHOWTIX_CLAUDE_KEY`
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] All money math is in `app/pricing.py`, in integer cents; no floats
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc2381aebcc4eddaebc4ec9f). Open one level at a time.
