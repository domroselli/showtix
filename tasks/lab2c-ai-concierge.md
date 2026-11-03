# Lab 2c: AI concierge

**Tier:** Advanced · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 starts with Claude interviewing you about the open decisions; then you write your answer key yourself.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

**Feature request:** "`POST /concierge` answers questions like *comedy tonight, 4 people, under $100 each* by calling Claude with tools over the app's own search, availability and quote functions. It recommends only real shows with live prices."

## Starting branch

```sh
git branch --show-current               # should be your Lab 1 branch, not main
git add -A && git commit -m "lab 1"     # save your Lab 1 work
git switch main
uv run python -m app.seed                # reset the local database
uv run python -m app.llm                 # your API key works: prints OK
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

Write the tests first and check them yourself, then let Claude make them pass. Each step has a prompt you can copy. Start with `/clear` so Claude begins fresh.

1. **Settle the decisions, then write your answer key.** Have Claude interview you about **Decisions to make**:

   > Read tasks/lab2c-ai-concierge.md and the relevant code. Interview me about the "Decisions to make", one question at a time. For each, give me 2-3 options and your recommendation. Don't write any code or tests. When we've covered every decision, update "Your criteria" in the sheet and change nothing else: one numbered, testable criterion per decision, with exact status codes and messages; under each, a "Why:" line with the reason we chose it; and a short "Not doing" list for what we deferred. Then show me the section so I can check it.

   You choose; Claude only offers options. ⏱ About 10 minutes: if a decision drags on, pick the simplest option and put the other on the "Not doing" list. Then, without Claude: Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 2, you'll compare Claude's tests against this answer key.
2. **Tests first.** Ask Claude:

   > Read tasks/lab2c-ai-concierge.md and the relevant code. Write a failing test for each acceptance criterion except the eval, using `fake_claude`. Then write the eval cases to tests/evals/concierge.json (cases only; don't call the API). Don't change anything in app/. Run the tests and show me which ones fail.

   Compare each test, and each eval case, with your answer key. The eval cases are the model's answer key, so they must be right too. If one is wrong, tell Claude what it should be and why:

   > The test for criterion 4 expects ___, but it should be ___ because ___. Fix that test.

   Check especially:
   - **One test's fake client recommends a made-up show id**, and the response leaves it out (criterion 1).
   - **Every decision in "Your criteria" has a test.**

   When you're satisfied with the tests, commit them:

   ```sh
   git add -A && git commit -m "lab2c: tests"
   ```

3. **Clear, then implement.** Type `/clear`, then ask:

   > Make the new tests from my last commit pass (see git show HEAD). Don't change any test. Read tasks/lab2c-ai-concierge.md for context. Run the full suite and show me the output. Then write tests/evals/run_concierge.py, which runs those eval cases with the shared runner (see the README). Don't run it.

   This is a bigger feature, so build it in slices (one tool first, then the loop, then the final recommendation). Add to the prompt: "Start with the tests for the first slice only. Stop when they pass." Commit each slice when you're satisfied with it, then ask for the next.

4. **Check the evidence.**
   - Run `uv run pytest` yourself. Is everything green?
   - Run `git diff HEAD --stat -- tests/`. It should print nothing, which means Claude didn't change your tests.
   - Run the eval twice against the real API: `uv run python -m tests.evals.run_concierge --repeat 2`. A score that changes between runs is normal. Read each failing case before changing anything.
   - Try it yourself. In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. To stop the app, click in that terminal and press **Ctrl+C** (on a Mac too: Control, not Command).
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Your tests are already committed, so this shows only the code Claude wrote. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude:

   > Use a subagent to review this branch's changes (git diff main) against tasks/lab2c-ai-concierge.md. It hasn't seen our conversation. Check every acceptance criterion, and don't report style. For each finding, give:
   > - a label: MUST FIX (a criterion isn't met, or a bug), OUT OF SCOPE (real, but not in the criteria, or already there before this branch), UNSURE, or OPTIONAL
   > - which criterion it's about
   > - evidence: the file and line, or an input that gives the wrong result
   >
   > Don't change any files or the database; if you need to experiment, do it in a test. Just show me the findings.

   **Why "don't report style"?** A reviewer asked to find problems always finds something. If you fix every finding, you end up with extra layers of code and tests for cases that can't happen. You want bugs and unmet criteria, not someone else's taste.

   The labels are the reviewer's opinion; you decide. Check the evidence for each MUST FIX and OUT OF SCOPE yourself (a reviewer can wave off a real bug as out of scope), ask for a failing test on anything UNSURE, and skip OPTIONAL. If an OUT OF SCOPE finding holds up, write it down and move on: fixing it is a new feature, not this one. Then fix the real ones test-first:

   > Findings 1 and 3 are real; ignore the rest. For each, write a failing test that shows the problem, then fix it. Run the full suite and show me the output.

   Then repeat step 4.
7. **Commit** when you're satisfied with the change:

   ```sh
   git add -A && git commit -m "lab2c: AI concierge"
   ```

## Done means

- [ ] Every decision you made is written down as a criterion with a test
- [ ] The tests you committed in step 2 weren't changed to make them pass
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
