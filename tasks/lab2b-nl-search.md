# Lab 2b: Natural-language search

- **Tier**: Intermediate
- **Time**: 50 minutes
- Solo or with a partner

## Start here

If this is your first lab, read [Getting started](01-getting-started.md) for how to run commands, the app, and your API key, and then read [How we work](00-how-we-work.md) for the workflow. Each page takes about 5 minutes to read.

In this lab, Claude turns a customer's words into search filters, and your code checks the filters and runs the search.

To run this lab, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Run the command in the [Starting branch](#starting-branch) section of this document.
3. Read the [Goal](#goal), [Background](#background), and [Acceptance criteria](#acceptance-criteria) sections.
4. Follow the [Workflow](#workflow) section step by step.

Step 1 starts with you. Think through your edge cases, and then write out your expected results yourself.

The lab is complete when you can check every box in the [Completion checklist](#completion-checklist) section of this document. If you have time left, try the [Optional stretch](#optional-stretch) section. If you're stuck, see the [Hints](#hints) section.

## Goal

Add the `POST /search` endpoint. A customer sends `{"query": "comedy this weekend under $80"}`, Claude turns the query into search filters, and your code checks those filters and runs the search itself. The model parses, and your code decides.

## Starting branch

To create your lab branch, copy the following command and run it in Claude Code:

```text
! git switch main && uv run python -m app.seed && uv run python -m app.llm && git switch -c lab2b-nl-search && uv run pytest
```

The command does the following, in order:

1. Switches to `main`, so the new branch starts from the original code.
2. Resets the database to the seed data.
3. Checks your Claude API key.
4. Creates the feature branch `lab2b-nl-search` from `main`.
5. Runs the tests.

The key check prints `OK: Claude API key works`. Every test passes before you change anything.

If `git switch` stops because of unfinished Lab 1 work, see [Start a lab branch](01-getting-started.md#start-a-lab-branch). For key problems, see [Set up your API key](01-getting-started.md#set-up-your-api-key-lab-2).

## Background

The following list describes the feature and the rules that keep the model in its place:

- **Filters**: the filters are `category`, `start_date`, `end_date`, and `max_price_cents`. Any of them can be `null`, which means "no filter".
- **Existing search**: `shows.list_shows()` in the `app/shows.py` file filters by `start_date` and `end_date` (both inclusive) and orders by title. It can't filter by category or price, because category filtering is a different lab feature, so filter those yourself in Python on its results.
- **Categories**: the categories are `magic`, `comedy`, `music`, and `acrobatics` (see the `shows` table in the `app/db.py` file). The seed has two shows per category, playing nightly from Tuesday, November 10 to Monday, November 23, 2026. For the full data, see [`docs/seed-data.md`](../docs/seed-data.md).
- **Prices and seats**: `inventory.tiers_for_performance()` gives each tier's `price_cents` and `seats_left`, and `shows.show_detail()` lists a show's performances that haven't started yet. For the price check in criterion 5, query the performances in the date range yourself, or add a small helper to the `app/shows.py` file. Every seeded show has GA at $69.00, Premium at $120.00, and VIP at $199.99.
- **Time is injected**: "tonight" and "this weekend" depend on the current time, which routes get from the `get_now` dependency in the `app/clock.py` file. Never call `datetime.now()`. Claude can't know today's date unless you tell it.
- **Calling Claude**: the `app/llm.py` file gives routes a `get_llm` dependency and the model name `MODEL` (`claude-haiku-5-5`). It reads your key from `SHOWTIX_CLAUDE_KEY` in the `.env` file. Your code never reads the key itself, because `get_llm` does. To write cents as dollars, in a prompt for example, use `pricing.dollars()`. For more information, see [Set up your API key](01-getting-started.md#set-up-your-api-key-lab-2).
- **Structured output with a tool**: give Claude one tool whose input schema is the filters, with `"strict": true`, so its arguments match the schema. Strict mode gets you the right shape, not the right meaning. A date can still be `2026-02-30`, or come after the end date, so your code validates every field. A nullable field is written as `{"type": ["string", "null"], "description": "..."}`. In strict mode, don't combine `enum` with a nullable type, because the API rejects the schema. Name the allowed categories in the field's description instead. For more information, see [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) in the Claude docs.
- **Testing without the network**: every test runs with a fake Claude automatically, so no test can reach the real API. Take the `fake_claude` fixture (the `FakeClaude` class in the `tests/fakes.py` file) whenever you need to queue replies or check calls. Queue the tool call you want with `fake_claude.queue({"tool_use": "search_filters", "input": {...}})`, call your endpoint, and then check what was sent with `fake_claude.calls` or `fake_claude.last_prompt`. To pin the time in a test, see the `now` and `clock` fixtures in the `tests/conftest.py` file. To simulate an API failure, queue `api_error()` from the `tests/fakes.py` file. It's a real `anthropic.APIError`, as the SDK raises it.
- **New status codes**: the `app/errors.py` file has no class for an HTTP `422` or `502` status code yet. Adding one there is part of this feature, so update the `app/errors.py` line in the `CLAUDE.md` file when you commit.
- **The model is never the source of truth**: Claude only produces filters. Every show in the response comes from the database, and so does any price or seat that your code compares against.

**Warning**: Don't give Claude your API key. Don't paste it into Claude Code, in a prompt or a `!` command. Paste it into the `.env` file yourself, in your editor. Anything you type in Claude Code becomes part of the conversation, and Claude can copy it into a file and from there into a commit.

For more information about where Claude fits between your route and the domain modules, see [How a Lab 2 feature fits](../docs/architecture.md#4-how-a-lab-2-feature-fits).

### Unit tests and the eval

Unit tests and the evaluation (eval) check different things:

- **Unit tests**: these tests check your code with scripted tool calls. They're fast and offline, and they return the same result on every run.
- **Eval**: the eval checks the real model's behavior. Does Claude turn real phrases into the right filters? The eval calls the API, the answers vary, and you get a score, not a guaranteed pass.
- **Shared runner**: use `run()` from the `tests/evals/runner.py` file (see the Evals section of the `README.md` file). Claude writes the cases file in step 2 and a `check(case)` function in step 3. The `check(case)` function returns whether the case passed and a short detail, and the runner prints one line per case and a score. Run it with `--repeat 2`. A score that changes between runs is normal for a model.

When a case fails, look at the filters Claude produced before you change anything. If _every_ case fails with `Search unavailable`, that's not an outage. Criterion 7 turns any API error into that HTTP `502 Bad Gateway` status code, including the API rejecting your request because of a bad tool schema. Ask Claude for the underlying error before you change anything.

An eval case pins the time, because "this weekend" means different dates on different days:

```json
{"query": "comedy this weekend under $80",
 "now": "2026-11-12T15:00:00",
 "expected": {"category": "comedy", "start_date": "2026-11-13",
              "end_date": "2026-11-15", "max_price_cents": 8000}}
```

If you don't have a working key, build and unit-test everything with `fake_claude`. For the eval and for trying the endpoint on the `/docs` page, pair with someone whose key works.

## Acceptance criteria

The following list gives most of the criteria. Before you write tests, add one or two edge cases of your own as criteria 10 and 11.

Every criterion except 9 (the eval) needs at least one test:

1. `POST /search` with `{"query": "..."}` returns an HTTP `200 OK` status code with `filters` (all four fields, `null` where unused) and `shows` (the matching shows, ordered by title, in the same shape as `GET /shows`, with `id`, `title`, `category`, and `venue`).
2. The request to Claude uses `MODEL` and offers one tool, `search_filters`, with `"strict": true`. Its schema has exactly the four fields, each required and nullable, and no others. The prompt includes a line built from the injected `now` in exactly this form: `Today is Thursday, 2026-11-12, 15:00`. The customer's query goes in the user message.
3. Relative dates follow `now`. Unit-test this criterion by checking that the rules are in `fake_claude.last_prompt`. The eval checks that Claude follows them. The rules are the following:
   - "Tonight" is today only.
   - "This weekend" is Friday through Sunday. If today is already Friday, Saturday, or Sunday, it's today through Sunday.
4. Your code validates the filters before searching. Any of the following returns an HTTP `422 Unprocessable Entity` status code and never runs the search:
   - `category` is not one of the four, lowercase.
   - A date that isn't a real `YYYY-MM-DD` date.
   - `start_date` after `end_date`.
5. The search uses existing code. Dates go through `shows.list_shows()`, and category and price are filtered in Python. A show matches `max_price_cents` if any of its performances in the date range has a tier at or under that price.
6. All four filters `null` returns all 8 shows. Valid filters that match nothing return an HTTP `200` status code with `"shows": []`.
7. An empty or whitespace-only query returns an HTTP `400 Bad Request` status code without calling Claude, so `fake_claude.calls` stays empty. If the Claude call fails, the endpoint returns an HTTP `502` status code with the detail `Search unavailable`.
8. Unit tests use `fake_claude`, never access the network, and the full suite finishes in less than 5 seconds.
9. A separate eval file (aim for 10 phrases, at least 5) gives each phrase a pinned `now` and the exact expected filters. A case passes only if all four fields match exactly. At least two cases use "this weekend" with different `now` values, one of them on a weekend day. You run the eval by hand against the real API.
10. _Your edge case_
11. _Your edge case_ (optional)

One edge case to think about is what the HTTP `400` response for an empty query says, not only its code.

The following table shows the expected filters, with `now` pinned to Thursday, November 12, 2026 at 3:00 PM:

| Query | `category` | `start_date` | `end_date` | `max_price_cents` |
| --- | --- | --- | --- | --- |
| comedy this weekend under $80 | `comedy` | `2026-11-13` | `2026-11-15` | `8000` |
| magic tonight | `magic` | `2026-11-12` | `2026-11-12` | `null` |
| acrobatics | `acrobatics` | `null` | `null` | `null` |
| music this weekend, max $70 | `music` | `2026-11-13` | `2026-11-15` | `7000` |
| anything under $125 tonight | `null` | `2026-11-12` | `2026-11-12` | `12500` |

With the first row's filters, the search returns `Laugh Lines Live` and `Stand-Up Saloon`, because GA is $69.00. The same query with "under $60" returns an empty `shows` list. The last row returns all 8 shows, because every show plays nightly, and GA ($69.00) and Premium ($120.00) are both under $125.

Work these out yourself before you trust any test. If `now` is Saturday, November 14, "this weekend" is November 14 to November 15.

## Workflow

The workflow has the following seven steps:

1. Start a fresh conversation. Find your edge cases, and then write your expected results without Claude.
2. Start a fresh conversation. Claude writes failing tests and the eval cases. You check them against your expected results, and then you commit.
3. Start a fresh conversation. Claude makes the tests pass without changing them, and then writes the eval runner.
4. Check the evidence. Run the tests, confirm that only `app/` and the eval runner changed, run the eval twice, and try the endpoint on the `/docs` page.
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

This sheet asks for one or two edge cases of your own. Think them through yourself first. What can a customer do that the criteria don't answer? Type yours into the [Acceptance criteria](#acceptance-criteria) section as criteria 10 and 11.

If you're stuck, ask Claude for a hint:

```text
Read tasks/lab2b-nl-search.md and the relevant code. I'm stuck finding edge cases
the criteria don't cover. Give me one hint at a time, as a question, not the
edge case itself. If I say "just tell me", suggest 3 edge cases, one sentence
each, and I'll pick. Don't write any code or change any files.
```

#### 1c: Write your expected results without Claude

The acceptance criteria are how Claude knows when the feature is complete. Before Claude writes anything, think through exactly what each criterion returns, and write the results down somewhere you can refer to later, such as a notes app or a text file outside your `showtix` folder, because anything inside the folder gets committed with your tests.

To write your expected results, follow these steps:

1. Go through the [Acceptance criteria](#acceptance-criteria) section one by one, and write down which filters, which shows come back, which status code, and the exact message.
2. Work out the table of expected filters yourself.
3. Check that your filters and shows match the table.

The shows and prices are in the [`docs/seed-data.md`](../docs/seed-data.md) file. To see them in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

Start a new conversation:

```text
/clear
```

#### 2b: Ask Claude for failing tests and the eval cases

Ask Claude to write the tests and the eval cases:

```text
Read tasks/lab2b-nl-search.md and the relevant code. Write a failing test for
each acceptance criterion except the eval, using fake_claude. Then write the
eval cases to tests/evals/nl_search.json (cases only; don't call the API).
Test behavior through the API, the pages, or functions that already exist, not
new functions or exact HTML. Don't change anything in app/. Run the tests and
show me which ones fail.
```

#### 2c: Check the tests and eval cases against your expected results

Claude's reply is your checklist: one line per test with the criterion it covers, what it expects, and whether it already passes. If the reply doesn't give you that, ask for it:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the following:

- **Each expected value and each eval case matches your step 1 table.** Claude wrote the tests and the summary, so the table you wrote without Claude is the thing to trust. The eval cases are the model's expected results, so they must be right too. If you can't find a value in your table, work it out yourself, or use 2d.
- **Every route or function a test calls already exists in `app/`.** `client.get(...)` and `client.post(...)` are the API. A test that calls a function that doesn't exist yet is designing the code for Claude, so use 2d.
- **No test patches an `app/` function.** `monkeypatch.setattr` and `patch(` tie a test to how the code is written. The `fake_claude` and `clock` fixtures are the only doubles. If a test does, use 2d.
- **Each invalid-filter case in criterion 4 has its own test for the HTTP `422` status code.**
- **The eval cases' expected filters match the table of expected filters.** Check the dates for "this weekend" most closely.

#### 2d: Correct a test or case that doesn't match

If a test doesn't match your expected results, tell Claude what it must be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet, ask Claude to rewrite it:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

The following is an example of a correction:

```text
The eval case for "this weekend" with now on Saturday, Nov 14 expects
start_date 2026-11-13, but it should be 2026-11-14 because on a weekend day it
runs from today through Sunday. Fix that case.
```

#### 2e: Commit the tests and eval cases

When every test and case matches your expected results, commit them:

```text
! git add -A && git commit -m "lab2b: tests"
```

### Step 3: Make the tests pass

#### 3a: Start a fresh conversation

Claude builds better from the sheet and your committed tests than from the context of the last chat. Start a new conversation:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

Ask Claude to write the code and the eval runner:

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab2b-nl-search.md for context. Run the full suite and show me the
output. Then write tests/evals/run_nl_search.py, which runs those eval cases
with the shared runner (see the Evals section of README.md). Don't run it.
```

Claude must not touch any test file that you committed. You verified those tests, so the code alone must make them pass. Step 4 checks this.

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

Every file in the list must be under `app/`, plus the one new file you asked for, `tests/evals/run_nl_search.py`. Any other file in `tests/` (changed, or new with `??`), a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask why before you go on. If step 6 adds fixes, the only other test changes are the new tests that you asked for, and no existing test changes.

#### 4c: Run the eval against the real API

Run the eval twice. A score that changes between runs is normal. Read each failing case before you change anything:

```text
! uv run python -m tests.evals.run_nl_search --repeat 2
```

If every case says `Search unavailable`, the API rejected your request and criterion 7 hid the reason behind the HTTP `502` status code. Ask Claude: "Every eval case fails with Search unavailable. Print the underlying API error and tell me what caused it before changing anything."

#### 4d: Try the endpoint on the /docs page

Ask Claude to start the app in the background. For more information, see [Start the app](01-getting-started.md#start-the-app).

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

Then open the [API documentation page](http://127.0.0.1:8000/docs), click your endpoint, and then click **Try it out** and **Execute**. Use queries from your expected results. Also try a dated query, such as "comedy on November 14", or a query with no date, such as "magic under $80".

**Note**: The running app uses the real date, not the pinned `now` in your tests, so "this weekend" gives real dates. The seeded run is November 10 to 23, 2026. Before November 10, "tonight" and "this weekend" return `"shows": []` even when the filters are right.

When you're done, ask Claude to stop the app. For other ways to stop the app, see [Stop the app](01-getting-started.md#stop-the-app).

```text
Stop the app.
```

#### 4e: Report a mismatch

If something doesn't match, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read every change before you accept it

Stage the changes and show the diff between the staged changes and the latest commit on your branch:

```text
! git add -A && git diff --staged
```

Your tests are already committed, so the diff shows only the code Claude wrote, including the eval runner. As you read, ask yourself the following questions:

- Can you explain every change?
- Did anything change that has nothing to do with search?

To read the diff side by side, use the **Source Control** panel in VS Code.

### Step 6: Get a second opinion

#### 6a: Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. The subagent hasn't seen your conversation, and it checks the change against this sheet:

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab2b-nl-search.md. It hasn't seen our conversation. It should
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

Reply with the numbers of the findings you want fixed, for example "1 and 3", and then repeat steps 4 and 5. You can also decide not to fix a finding, or talk it through with Claude before you decide. Claude might also list UNSURE or OPTIONAL findings. Those are yours to decide, and the lab doesn't need them. If Claude reports no MUST FIX findings, there's nothing to answer. Repeat steps 4 and 5 once, and then go on to step 7. If Claude asks how to fix something, answer with the behavior that you want and let Claude choose the code.

For more information about why the reviewer doesn't report style, see [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7: Commit

When you're satisfied with the change, commit it:

```text
! git add -A && git commit -m "lab2b: natural-language search"
```

If you finish with time to spare, try the [Optional stretch](#optional-stretch) section of this document.

## Completion checklist

The lab is complete when the following statements are true:

- [ ] Each of criteria 1 to 8 and each of your own criteria has a test, and every test passes offline. Criterion 9 is the eval.
- [ ] The tests you committed in step 2 weren't changed to make them pass.
- [ ] Each of the three invalid-filter cases in criterion 4 has its own test for the HTTP `422` status code.
- [ ] The eval has at least 5 phrases (aim for 10) with pinned times, and you ran it twice against the real API.
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] Routes in the `app/main.py` file only call into domain code, and only the `app/llm.py` file reads the key.
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed.

## Optional stretch

If you finish early, extend the core one piece at a time, each with its own tests and eval cases:

- **"Next week"**: the following Monday through Sunday.
- **Dates without a year**: "music on Nov 20 or 21" is in the year of `now`.
- **More HTTP `422` cases**: a `max_price_cents` that isn't a whole number or is less than 0, and a reply from Claude with no `search_filters` call.
- **Sold-out tiers don't count**: a show matches the price only through a tier with seats left.

For a larger extension, add a search box to the home page (`GET /`) that posts to the same search code and lists the results. Then try queries that aren't searches at all, such as "what's the weather?" and "ignore your instructions", add them to the eval with all-`null` expected filters or an HTTP `422` status code, and see what Claude does.

## Hints

If you're stuck, open the [workshop hints page](https://www.notion.so/409be0acdc2381a29466d66c2e112745). It lists the places where students get stuck in this lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see.
