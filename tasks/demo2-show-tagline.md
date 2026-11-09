# Demo 2: Show tagline

- **Tier:** Instructor demo (before Lab 2)
- **Time:** 10 minutes
- Watch along; every Lab 2 sheet relies on the three things shown here

## Start here

**This is the sheet the instructor follows on screen.** It has the same shape as every Lab 2 sheet. The feature is already built on the instructor's `demo` branch, so the demo doesn't run steps 1 to 3 from scratch: it shows the finished feature, builds one test live, and runs the eval. Nothing here is on the Lab 2 menu.

1. Run the command under [Starting branch](#starting-branch).
2. Read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow).

**Three things to take into Lab 2:** the key seam (`get_llm`), a `fake_claude` test, and an eval score you read before touching anything.

## Goal

#### Add `POST /shows/{id}/tagline`: Claude writes a one-line tagline for a show from its real facts, through a strict tool, and your code checks what came back.

## Starting branch

The feature lives on the instructor's `demo` branch (not in the public repo). The instructor runs:

```text
! git switch demo && uv run python -m app.seed && uv run python -m app.llm && uv run pytest
```

Here's what it does:

1. Switches to `demo`, which is `main` plus the tagline feature
2. Resets the database to the seed data
3. Checks the Claude API key
4. Runs the tests

The key check should print `OK: Claude API key works`, and every test should pass. In your lab, the starting command is the same shape with `git switch -c lab2…` in it.

## Background

Here is the relevant background about the feature, including the rules every Lab 2 sheet shares:

- **The key seam:** `app/llm.py` gives routes a `get_llm` dependency and the model name `MODEL` (`claude-haiku-5-5`). It reads `SHOWTIX_CLAUDE_KEY` from `.env` and never falls back to `ANTHROPIC_API_KEY`. Every Claude call goes through `get_llm()`; tests swap it for a fake. That one seam is why Lab 2 tests run offline in half a second.
- **Never give Claude your API key.** It goes in `.env`, in your editor. It's never opened on a projector.
- **The feature:** `app/tagline.py` has a one-line `SYSTEM` prompt (facts only, under 80 characters, no quotation marks), `facts()` built from the show in the database, and `TAGLINE_TOOL`, a strict tool `save_tagline` with `tagline` and a `mood` enum. Strict mode guarantees the shape of the reply, not the content, so the code still checks the tagline is one line and the mood is on the list.
- **Two patterns, one feature:** the first demo commit asks for free text and parses it (Lab 2a's pattern); the second sends the same facts through the strict tool (Lab 2b's pattern). Lab 2c adds a tool loop where Claude calls your functions.
- **Testing without the network:** every test takes the `fake_claude` fixture (`FakeClaude`, in `tests/fakes.py`). Queue what Claude will say, call your route, assert on two things: what your app returned and what your app sent. The fake can queue a thinking block before a tool call, which the real model sometimes sends, and `api_error()`, `connection_error()` or `timeout_error()` for failures.
- **The strict-mode trap:** an `enum` on a nullable field gets a 400 from the API, which your app shows as a 502. Lab 2b's sheet warns about it.
- **The model is never the source of truth.** Here that means the code validates the tagline and mood; in Lab 2 it means prices and seats.

**For an illustration of where Claude fits between your route and the domain modules, see [How a Lab 2 feature fits](../docs/architecture.md#4-how-a-lab-2-feature-fits).**

### About the eval

- **Unit tests check *your code*,** with scripted replies: fast, offline, the same every run.
- **The eval checks *the real model's behavior*:** `tests/evals/tagline.json` has 3 shows with the moods that fit them; `tests/evals/run_tagline.py` calls the API and scores each tagline (one line, under 80 characters, no quotes or prices, mood fits).
- **`--repeat 2`,** the same flag as your sheets. A score that changes between runs is normal. pytest never collects `tests/evals/`: unit tests stay offline and fast, evals cost money and run on purpose.

## Acceptance criteria

These are already built and tested on `demo`. Criteria 1 to 6 each have a test in `tests/test_tagline.py`; criterion 7 is the eval.

1. `POST /shows/{id}/tagline` returns 200 with `show_id`, `tagline` and `mood`, read from the `save_tagline` tool call. Surrounding whitespace is trimmed.
2. The request to Claude uses `MODEL`, offers exactly one tool, `save_tagline`, with `"strict": true`, forces it with `tool_choice`, puts the instructions in the system prompt, and sends the show's facts (title, category, venue, upcoming performances) in the user message.
3. An unknown show id returns 404 without calling Claude (`fake_claude.calls` stays empty).
4. If the Claude call fails, the endpoint returns 502 with the detail `Tagline writer unavailable`.
5. A reply with no tool call, an empty or multi-line tagline, or a mood not on the list also returns 502 with the same detail.
6. Unit tests use `fake_claude`, never touch the network, and the full suite stays under 5 seconds.
7. The eval's 3 cases pass when the tagline is one line under 80 characters with no quotation marks or prices, and the mood fits the show.

**Built live in the demo:** a test that the route still works when the real model puts a thinking block before the tool call (criterion 1, with a reply shape the fake can produce).

## The workflow

#### Workflow Overview

Steps 1 to 3 are done before the demo (they're the same seven steps as Lab 1). On stage:

1. The key seam: `app/llm.py`, one sentence.
2. What the feature looks like: `app/tagline.py`, two calls in /docs, the plain-call diff.
3. Built live: one `fake_claude` test (the shape of step 2 on every Lab 2 sheet).
4. Check the evidence: the test file, then the eval twice.
5. Hand off: same seven steps as Lab 1, plus Claude writes an eval runner in step 3 and step 4 runs it twice.

Why each step matters: [How we work](00-how-we-work.md).

### Step 1. The key seam

Open `app/llm.py`. `KEY_VAR = "SHOWTIX_CLAUDE_KEY"`, and the comment that it never falls back to `ANTHROPIC_API_KEY`. Every call goes through `get_llm()`; tests swap it for a fake.

### Step 2. What the feature looks like

Open `app/tagline.py`: `SYSTEM`, `facts()`, `TAGLINE_TOOL` with `"strict": True`, the `enum` for mood, `required`, `additionalProperties: False`, reading `call.input`, 502 on anything unusable.

Then two calls in /docs: follow [Check it in your browser](#check-it-in-your-browser) below. Different text, same shape.

Pattern 1 is the same feature without the tool. Show it as a diff between the two demo commits rather than a live switch:

```text
! git log --oneline -3
```

```text
! git diff <plain-call commit> <strict-tool commit> -- app/tagline.py
```

### Step 3. Built live: the `fake_claude` test

#### 3a. Start with a fresh conversation

```text
/clear
```

#### 3b. Have Claude add one test

```text
Read tasks/demo2-show-tagline.md, tests/test_tagline.py and tests/fakes.py. Add
one test: the real model sometimes puts a thinking block before the tool call.
Queue a reply on fake_claude with a thinking block and then the save_tagline
tool call, using the fake's {"thinking": ..., "tool_use": ..., "input": {...}}
shape, POST /shows/{id}/tagline, and assert the response is 200 with that
tagline and mood. Also assert the request sent exactly one strict tool and that
the show's facts are in the user message. Don't change app/. Run the file.
```

Every Lab 2 test looks like this. Queue what Claude will say, call your route, assert on what your app returned and what your app sent.

It passes first time, and that's fine: the code reads only `tool_use` blocks, so this is a regression guard. In Lab 2c you send Claude's reply back in a loop; forgetting the thinking block there breaks the call. The fake can reproduce it; the real API can't, cheaply.

### Step 4. Check the evidence

#### 4a. Run the test file

```text
! uv run pytest tests/test_tagline.py -q
```

Under a second, all passed.

#### 4b. Run the eval against the real API

```text
! uv run python -m tests.evals.run_tagline --repeat 2
```

One line per case, `PASS (2/2) …` or `FAIL (1/2) … (80 characters)`, then a score out of 6.

**Read the failing line before touching anything.** Is the model wrong, or is the eval wrong? A tagline at exactly 80 characters on an under-80 rule is the model clipping the edge: fix the prompt, not the eval. A 6/6 tells you little on its own; your sheet says run it twice and read any miss.

### Step 5. Hand off

Same seven steps as Lab 1, plus two things: Claude writes an eval runner in step 3, and step 4 runs it twice. Every Lab 2 sheet ends with an eval score. Bring yours to the share-out.

## Check it in your browser

Use this for step 2 of the demo.

### 1. Start the app

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

### 2. Call the endpoint twice in /docs (criterion 1)

1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and click **POST /shows/{show_id}/tagline**, then **Try it out**.
2. Enter `1` for `show_id` (The Vanishing Ace after a fresh seed) and click **Execute**. Read the tagline and mood out loud.
3. Click **Execute** again. Different text, same shape: `show_id`, `tagline`, `mood`.

### 3. Stop the app

```text
Stop the app.
```

## Checklist: What Done Means

- [ ] A test for each of criteria 1–6, all passing, all offline
- [ ] The live test queues a thinking block before the tool call and passes
- [ ] The request offers exactly one strict tool and sends the show's facts in the user message
- [ ] API failure and unusable replies both give 502 `Tagline writer unavailable`
- [ ] The eval has run twice for real, and you read every miss before changing anything
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] The key is only ever read by `app/llm.py`, and it was never on screen
