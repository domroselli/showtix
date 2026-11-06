# Lab 2b: Natural-language search

**Tier:** Intermediate · **Time:** 50 minutes · Solo or with a partner

## Start here

Claude turns a customer's words into search filters; your code checks them and runs the search.

1. New here? Read [Getting started](01-getting-started.md) for running commands, the app and your API key, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).
2. Run the commands under [Starting branch](#starting-branch), then read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow) step by step. Step 1 starts with you thinking through edge cases; then you write your expected results yourself.

You're done when every box under [Done means](#done-means) is checked. Extra time? Try the [Optional stretch](#optional-stretch). Stuck? See [Hints](#hints).

## Goal

Add `POST /search`: a customer types `{"query": "comedy this weekend under $80"}`, Claude turns it into search filters, and your code checks those filters and runs the search itself. The model parses; your code decides.

## Starting branch

Create this lab's branch from `main`, reset the database, check your API key, and run the tests:

```text
! git switch main && uv run python -m app.seed && uv run python -m app.llm && git switch -c lab2b-nl-search && uv run pytest
```

The key check should print `OK: Claude API key works`, and every test should pass. If `git switch` stops because of unfinished Lab 1 work, see [Start a lab branch](01-getting-started.md#start-a-lab-branch). Key trouble? See [Set up your API key](01-getting-started.md#set-up-your-api-key-lab-2).

## Background

What you'll build on, and the rules that keep the model in its place:

- **Filters:** `category`, `start_date`, `end_date` and `max_price_cents`. Any of them may be `null`, meaning "no filter".
- **Existing search:** `shows.list_shows()` in `app/shows.py` filters by `start_date` and `end_date` (both inclusive) and orders by title. It can't filter by category or price (category filtering is a different lab feature), so filter those yourself in Python on its results.
- **Categories:** `magic`, `comedy`, `music`, `acrobatics` (see the `shows` table in `app/db.py`). The seed has 2 shows per category, playing nightly from Tue Nov 10 to Mon Nov 23, 2026 (all of it is in [`docs/seed-data.md`](../docs/seed-data.md)).
- **Prices and seats:** `inventory.tiers_for_performance()` gives each tier's `price_cents` and `seats_left`. `shows.show_detail()` lists a show's performances. Every seeded show has GA $69.00, Premium $120.00 and VIP $199.99.
- **Time is injected.** "Tonight" and "this weekend" depend on the current time, which routes get from the `get_now` dependency (`app/clock.py`). Never call `datetime.now()`. Claude can't know today's date unless you tell it.
- **Calling Claude:** `app/llm.py` gives routes a `get_llm` dependency and the model name `MODEL` (`claude-haiku-5-5`). It reads your key from `SHOWTIX_CLAUDE_KEY` in `.env` (see [Set up your API key](01-getting-started.md#set-up-your-api-key-lab-2)). Your code never reads the key itself; `get_llm` does. To write cents as dollars, in a prompt for example, use `pricing.dollars()`.
- **Never give Claude your API key.** Don't paste it into Claude Code, in a prompt or a `!` command. Paste it into `.env` yourself, in your editor: anything you type in Claude Code becomes part of the conversation, and Claude can copy it into a file and from there into a commit.
- **Structured output with a tool:** give Claude one tool whose input schema *is* the filters, with `"strict": true`, so its arguments match the schema. Strict mode gets you the right shape, not the right meaning. A date can still be `2026-02-30`, or come after the end date, so your code validates every field.
- **Testing without the network:** every test runs with a fake Claude automatically, so no test can reach the real API. Take the `fake_claude` fixture (`FakeClaude`, in `tests/fakes.py`) whenever you need to queue replies or check calls. Queue the tool call you want with `fake_claude.queue({"tool_use": "search_filters", "input": {...}})`, call your endpoint, then check what was sent with `fake_claude.calls` or `fake_claude.last_prompt`. To simulate an API failure, queue `api_error()` from `tests/fakes.py`: it's a real `anthropic.APIError`, as the SDK would raise it.
- **The model is never the source of truth for shows, prices or seats.** Claude only produces filters; every show in the response comes from the database.

For a picture of where Claude fits between your route and the domain modules, see [How a Lab 2 feature fits](../docs/architecture.md#4-how-a-lab-2-feature-fits).

### About the eval

Unit tests and the eval check different things:

- **Unit tests check *your code*,** with scripted tool calls: fast, offline, the same every run.
- **The eval checks *the real model's behavior*:** does Claude turn real phrases into the right filters? It calls the API, answers vary, and you get a score, not a guaranteed pass.
- **Use the shared runner,** `run()` from `tests/evals/runner.py` (see the README): you write the cases file and a `check(case)` function that returns whether the case passed and a short detail; it prints one line per case and a score. Run it with `--repeat 2`; a score that changes between runs is normal for a model.

When a case fails, look at the filters Claude produced before changing anything.

An eval case pins the time, because "this weekend" means different dates on different days:

```json
{"query": "comedy this weekend under $80",
 "now": "2026-11-12T15:00:00",
 "expected": {"category": "comedy", "start_date": "2026-11-13",
              "end_date": "2026-11-15", "max_price_cents": 8000}}
```

**No working key?** Build and unit-test everything with `fake_claude`; for the eval and trying it in /docs, pair with someone whose key works.

## Acceptance criteria

Most criteria are given. **Add one or two edge cases of your own** before you write tests.

1. `POST /search` with `{"query": "..."}` returns 200 with `filters` (all four fields, `null` where unused) and `shows` (the matching shows, ordered by title, in the same shape as `GET /shows`).
2. The request to Claude uses `MODEL` and offers one tool, `search_filters`, with `"strict": true`. Its schema has exactly the four fields, each required and nullable, and no others. The prompt includes a line built from the injected `now` in exactly this form: `Today is Thursday, 2026-11-12, 15:00`, and the customer's query goes in the user message.
3. Relative dates follow `now` (unit-test this by checking the rules are in `fake_claude.last_prompt`; the eval checks Claude actually follows them):
   - **"Tonight"** is today only.
   - **"This weekend"** is Friday through Sunday. If today is already Friday, Saturday or Sunday, it's today through Sunday.
4. Your code validates the filters before searching. Any of these returns 422 and never runs the search:
   - `category` is not one of the four, lowercase
   - a date that isn't a real `YYYY-MM-DD` date
   - `start_date` after `end_date`
5. The search uses existing code: dates go through `shows.list_shows()`, and category and price are filtered in Python. A show matches `max_price_cents` if any of its performances in the date range has a tier at or under that price.
6. All four filters `null` returns all 8 shows. Valid filters that match nothing return 200 with `"shows": []`.
7. An empty or whitespace-only query returns 400 without calling Claude (`fake_claude.calls` stays empty). If the Claude call fails, the endpoint returns 502 with the detail `Search unavailable`.
8. Unit tests use `fake_claude`, never touch the network, and the full suite stays under 5 seconds.
9. A separate eval file (aim for 10 phrases, at least 5) gives each a pinned `now` and the exact expected filters. A case passes only if all four fields match exactly. At least two cases use "this weekend" with different `now` values, one of them on a weekend day. You run it by hand against the real API.
10. _Your edge case..._
11. _Your edge case..._

Think about: what the 400 for an empty query says, not just its code.

**Worked example:** filters, with `now` pinned to Thursday, Nov 12, 2026 at 3:00 PM.

| Query | `category` | `start_date` | `end_date` | `max_price_cents` |
| --- | --- | --- | --- | --- |
| comedy this weekend under $80 | `comedy` | `2026-11-13` | `2026-11-15` | `8000` |
| magic tonight | `magic` | `2026-11-12` | `2026-11-12` | `null` |
| acrobatics | `acrobatics` | `null` | `null` | `null` |
| music this weekend, max $70 | `music` | `2026-11-13` | `2026-11-15` | `7000` |
| anything under $125 tonight | `null` | `2026-11-12` | `2026-11-12` | `12500` |

With the first row's filters, the search returns `Laugh Lines Live` and `Stand-Up Saloon` (GA is $69.00). The same query "under $60" returns `[]`. The last row returns all 8 shows: every show plays nightly, and GA ($69.00) and Premium ($120.00) are both under $125.

Work these out yourself before you trust any test. If `now` were Saturday, Nov 14, "this weekend" would be Nov 14 to Nov 15.

## The workflow

Settle what "done" means, then have Claude write the tests, check them yourself, and let Claude make them pass.

- Steps that use Claude have a prompt to copy; commands start with `!`.
- Why each step matters: [How we work](00-how-we-work.md).
- Start with a fresh conversation:

  ```text
  /clear
  ```

### 1. Align: find your edge cases, then write your expected results

This sheet asks for one or two edge cases of your own. Think them through yourself first: what could a customer do that the criteria don't answer? Type yours into the sheet's edge-case lines (criteria 10 and 11).

Stuck? Ask Claude for a hint:

```text
Read tasks/lab2b-nl-search.md and the relevant code. I'm stuck finding edge cases
the criteria don't cover. Give me one hint at a time, as a question, not the
edge case itself. If I say "just tell me", suggest 3 edge cases, one sentence
each, and I'll pick. Don't write any code or change any files.
```

Then, without Claude:

- Go through [Acceptance criteria](#acceptance-criteria) one by one: which filters, which shows come back, which status code, the exact message.
- Work out the worked-example table yourself and check you get the same filters and shows. Shows and prices are in [`docs/seed-data.md`](../docs/seed-data.md); to see them in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

You'll compare Claude's tests and eval cases against these expected results in step 2.

### 2. Tests first

Have Claude write failing tests and the eval cases, then check them against your expected results.

```text
Read tasks/lab2b-nl-search.md and the relevant code. Write a failing test for
each acceptance criterion except the eval, using fake_claude. Then write the
eval cases to tests/evals/nl_search.json (cases only; don't call the API).
Test behavior through the API, the pages, or functions that already exist, not
new functions or exact HTML. Don't change anything in app/. Run the tests and
show me which ones fail.
```

Compare each test, and each eval case, with your expected results. The eval cases are the model's expected results, so they must be right too.

Check especially:

- **Tests check behavior through the API or the page**, not functions that don't exist yet. A test that calls a new function is designing the code for Claude.
- **Each invalid-filter case in criterion 4 has its own 422 test.**
- **The eval cases' expected filters match the worked-example table**, especially the dates for "this weekend".

If a test or case doesn't match your expected results, tell Claude what it should be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

When every test and case matches your expected results, commit them:

```text
! git add -A && git commit -m "lab2b: tests"
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
Read tasks/lab2b-nl-search.md for context. Run the full suite and show me the
output. Then write tests/evals/run_nl_search.py, which runs those eval cases
with the shared runner (see the README). Don't run it.
```

Claude shouldn't touch any test file you committed. Step 4 checks that.

### 4. Check the evidence

Don't take Claude's word for it; check for yourself.

- Run the tests. The last line should say only `passed`, with no `skipped`, `deselected` or `xfailed`:

  ```text
  ! uv run pytest
  ```

- Check that Claude only changed app code. Every file this lists should be under `app/`, plus the one new file you asked for, `tests/evals/run_nl_search.py`:

  ```text
  ! git status --short
  ```

  Any other file in `tests/` (changed, or new with `??`), a `conftest.py`, or `pyproject.toml` means Claude touched your tests or how they run: ask why before going on. After step 6's fixes, the only other test changes should be the new tests you asked for.

- Run the eval twice against the real API. A score that changes between runs is normal; read each failing case before changing anything:

  ```text
  ! uv run python -m tests.evals.run_nl_search --repeat 2
  ```

- Try it yourself. Start the app ([more on starting the app](01-getting-started.md#start-the-app)), then open http://127.0.0.1:8000/docs, click your endpoint, **Try it out**, **Execute**. Use queries from your expected results.

  ```text
  Start the app in the background with uv run uvicorn app.main:app --reload,
  and tell me when it's ready.
  ```

  The running app uses the real date, not the pinned `now` in your tests, so "this weekend" gives real dates. When you're done checking ([other ways to stop it](01-getting-started.md#stop-the-app)):

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
- Was anything touched that has nothing to do with search?
- Prefer side by side? Use VS Code's **Source Control** panel.

Your tests are already committed, so this shows only the code Claude wrote.

### 6. Get a second opinion

A reviewer that hasn't seen your conversation checks the change against this sheet.

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab2b-nl-search.md. It hasn't seen our conversation. It should check
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
! git add -A && git commit -m "lab2b: natural-language search"
```

Finished with time to spare? Try the [Optional stretch](#optional-stretch) below.

## Done means

- [ ] A test for each of criteria 1–8 and your own, all passing, all offline (criterion 9 is the eval)
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] Each of the three invalid-filter cases in criterion 4 has its own 422 test
- [ ] The eval has at least 5 phrases (aim for 10) with pinned times, and you've run it twice for real
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] Routes in `main.py` only call into domain code; the key is only ever read by `app/llm.py`
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Optional stretch

Finished early? Extend the core, one piece at a time, each with its own tests and eval cases:

- **"Next week"** is the following Monday through Sunday.
- **Dates without a year** ("music on Nov 20 or 21") are in `now`'s year.
- **More 422 cases:** `max_price_cents` that isn't a whole number or is below 0, and a reply from Claude with no `search_filters` call.
- **Sold-out tiers don't count:** a show matches the price only through a tier with seats left.

More ideas: add a search box to the home page (`GET /`) that posts to the same search code and lists the results. Then try queries that aren't searches at all ("what's the weather?", "ignore your instructions"), add them to the eval with all-`null` expected filters or a 422, and see what Claude does.

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc2381a29466d66c2e112745). Open one level at a time.
