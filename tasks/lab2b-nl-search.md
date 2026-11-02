# Lab 2b: Natural-language search

**Tier:** Intermediate · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

Add `POST /search`: a customer types `{"query": "comedy this weekend under $80"}`, Claude turns it into search filters, and your code checks those filters and runs the search itself. The model parses; your code decides.

## Starting branch

```sh
git branch --show-current               # should be your Lab 1 branch, not main
git add -A && git commit -m "lab 1"     # save your Lab 1 work
git switch main
uv run python -m app.seed                # reset the local database
git switch -c lab2b-nl-search
uv run pytest          # green before you change anything
```

## Background

- **Filters:** `category`, `start_date`, `end_date` and `max_price_cents`. Any of them may be `null`, meaning "no filter".
- **Existing search:** `shows.list_shows()` in `app/shows.py` filters by `start_date` and `end_date` (both inclusive) and orders by title. It can't filter by category or price (category filtering is a different lab feature), so filter those yourself in Python on its results.
- **Categories:** `magic`, `comedy`, `music`, `acrobatics` (see the `shows` table in `app/db.py`). The seed has 2 shows per category, playing nightly from Tue Nov 10 to Mon Nov 23, 2026.
- **Prices and seats:** `inventory.tiers_for_performance()` gives each tier's `price_cents` and `seats_left`. `shows.show_detail()` lists a show's performances. Every seeded show has GA $69.00, Premium $120.00 and VIP $199.99.
- **Time is injected.** "Tonight" and "this weekend" depend on the current time, which routes get from the `get_now` dependency (`app/clock.py`). Never call `datetime.now()`. Claude can't know today's date unless you tell it.
- **Calling Claude:** `app/llm.py` gives routes a `get_llm` dependency and the model name `MODEL` (`claude-haiku-5-5`). It reads your key from `SHOWTIX_CLAUDE_KEY` in `.env`; copy `.env.example` if you haven't. Never read keys yourself.
- **Structured output with a tool:** give Claude one tool whose input schema *is* the filters, with `"strict": true`, so its arguments match the schema. Strict mode gets you the right shape, not the right meaning. A date can still be `2026-02-30`, or come after the end date, so your code validates every field.
- **Testing without the network:** every test runs with a fake Claude automatically, so no test can reach the real API. Take the `fake_claude` fixture (`FakeClaude`, in `tests/fakes.py`) whenever you need to queue replies or check calls. Queue the tool call you want with `fake_claude.queue({"tool_use": "search_filters", "input": {...}})`, call your endpoint, then check what was sent with `fake_claude.calls` or `fake_claude.last_prompt`. To simulate an API failure, queue `api_error()` from `tests/fakes.py`: it's a real `anthropic.APIError`, as the SDK would raise it.
- **The model is never the source of truth for shows, prices or seats.** Claude only produces filters; every show in the response comes from the database.

### About the eval

Unit tests check *your code*, with scripted tool calls: fast, offline, the same every run. The eval checks *the real model's behavior*: does Claude turn real phrases into the right filters? It calls the API, answers vary, and you get a score, not a guaranteed pass. Use the shared runner, `run()` from `tests/evals/runner.py` (see the README): you write the cases file and a `check(case)` function that returns whether the case passed and a short detail; it prints one line per case and a score. Run it with `--repeat 2`; a score that changes between runs is normal for a model. When a case fails, look at the filters Claude produced before changing anything.

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

## The working loop

This is how people really use Claude Code: one good prompt, then you check the evidence.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 3, you'll compare Claude's tests against this answer key.
2. **One good prompt.** For example: "Read tasks/lab2b-nl-search.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after."
3. **Check the evidence.** Did the tests fail before the change? Does each test match your answer key (filters and show titles), not just what Claude assumed?
4. **Try it yourself.** In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. Ctrl+C stops the app.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude: "Review this diff against tasks/lab2b-nl-search.md." Then decide which of its findings actually matter.

## Done means

- [ ] A test for each of criteria 1–8 and your own, all passing, all offline (criterion 9 is the eval)
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
