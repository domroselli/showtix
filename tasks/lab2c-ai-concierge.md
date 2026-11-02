# Lab 2c: AI concierge

**Tier:** Advanced · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

**Feature request:** "`POST /concierge` answers questions like *comedy tonight, 4 people, under $100 each* by calling Claude with tools over the app's own search, availability and quote functions. It recommends only real shows with live prices."

## Starting branch

```sh
git branch --show-current               # should be your Lab 1 branch, not main
git add -A && git commit -m "lab 1"     # save your Lab 1 work
git switch main
uv run python -m app.seed                # reset the local database
git switch -c lab2c-ai-concierge
uv run pytest          # green before you change anything
```

## Background

- The tools Claude calls should be thin wrappers over code that already exists: `shows.list_shows()` / `shows.show_detail()`, `inventory.availability()` and `orders.quote()`. No new pricing or inventory logic.
- `ShowSummary` includes `category`, but `GET /shows` can't filter by it (that's a different lab feature). Your search tool can filter the list itself.
- "Tonight" means local Vegas time from the injected `now` (`get_now` in `app/clock.py`). The seeded run is Nov 10 to Nov 23, 2026, so pin the clock inside that range.
- **Calling Claude:** `app/llm.py` gives routes a `get_llm` dependency and the model name `MODEL` (`claude-haiku-5-5`: fast and cheap, so your credits last). It reads your key from `SHOWTIX_CLAUDE_KEY` in `.env` (copy `.env.example`), never `ANTHROPIC_API_KEY`, which keeps Claude Code on your subscription.
- **Testing without the network:** every test runs with a fake Claude automatically, so no test can reach the real API. Take the `fake_claude` fixture (`FakeClaude`, in `tests/fakes.py`) whenever you need to queue replies or check calls. Queue scripted replies with `fake_claude.queue(...)`: a string is a final text answer, `{"tool_use": "name", "input": {...}}` is a tool call. Check what was sent with `fake_claude.calls`. A separate eval file checks the recommended show ids against the real API.

### About the eval

**Unit tests and evals check different things.** Unit tests check *your code*: the fake client returns scripted replies, so they're fast, offline and give the same result every run. The eval checks *the real model's behavior* on realistic questions. It calls the API, the answers vary, and you get a score, not a guaranteed pass.

**The eval file** is a list of cases, each with a question, a pinned time, and the show ids you expect. For example:

```json
{"question": "comedy tonight, 4 people, under $100 each",
 "now": "2026-11-14T18:00:00",
 "expected_show_ids": [<the two comedy shows>]}
```

Work out each expected answer yourself from the seed data. That's the point: the eval encodes what *you* know is right. Aim for 10 cases; 5 is fine if you're short on time.

**The runner:** Use the shared runner, `run()` from `tests/evals/runner.py` (see the README): you write the cases file and a `check(case)` function that returns whether the case passed and a short detail; it prints one line per case and a score. Run it with `--repeat 2`; a score that changes between runs is normal for a model.

**When a case fails, read what happened before changing anything:** which tools Claude called, with what arguments, and what it got back. Then decide whether to fix the prompt, the tool, or your expected answer.

**No working key?** Build and unit-test everything with `fake_claude`; for the eval and trying it in /docs, pair with someone whose key works.

## Acceptance criteria

Two criteria are given. **Write the rest with Claude's help** before you write tests.

1. Every recommendation is real and live: its show, performance and tier exist, there are enough seats for the party, and its price comes from `orders.quote()`. A unit test whose fake client recommends a made-up show id gets no recommendation for it.
2. Unit tests use a fake client, run offline, and keep the full suite under 5 seconds. A separate eval file (aim for 10 questions, at least 5) checks the recommended show ids, and you run it by hand against the real API.

### Decisions to make

Decide these with Claude, then turn each decision into a criterion:

- Request and response shape: what does `POST /concierge` take, and what does each recommendation contain?
- Does "under $100 each" mean the tier price, or the price per person including fees and tax?
- What does the endpoint return when nothing matches? When Claude's answer can't be used?
- How many recommendations, in what order? API only, or a box on the UI's home page too?
- What does the eval file look like (question, pinned time, expected show ids), and how do you run it?

50 minutes is tight. For each question, pick the simplest answer that works and note what you'd do with more time.

### Your criteria

3. _..._
4. _..._
5. _..._

## The working loop

This is how people really use Claude Code: one good prompt, then you check the evidence.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 3, you'll compare Claude's tests against this answer key.
2. **One good prompt.** For example: "Read tasks/lab2c-ai-concierge.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after."
   This is a bigger feature: settle your criteria first, then start in plan mode and review the plan before Claude writes code.
3. **Check the evidence.** Did the tests fail before the change? Does each test match your answer key, not just what Claude assumed?
4. **Try it yourself.** In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. Ctrl+C stops the app.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude: "Review this diff against tasks/lab2c-ai-concierge.md." Then decide which of its findings actually matter.

## Done means

- [ ] Every decision you made is written down as a criterion with a test
- [ ] Unit tests never touch the network; the fake client covers a tool call, a final `recommend` call and a made-up show
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
