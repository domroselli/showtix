# Lab 1a: Category filter

**Tier:** Starter · **Time:** 50 minutes · Solo or with a partner

## Start here

Your first lab: a small filter, built with the full workflow.

1. New here? Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).
2. Run the command under [Starting branch](#starting-branch), then read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow) step by step. Step 1 is yours: write your answer key before you ask Claude anything.

You're done when every box under [Done means](#done-means) is checked. Extra time? Try the [Optional stretch](#optional-stretch). Stuck? See [Hints](#hints).

## Goal

Let customers list shows by category: `GET /shows?category=comedy`.

## Starting branch

Create this lab's branch from `main`, reset the database, and check that the tests pass:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1a-category-filter && uv run pytest
```

Every test should pass before you change anything. Trouble? See [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

Where the code you'll change lives:

- `GET /shows` already takes `start_date` and `end_date`. The route is in `app/main.py`; the query is built in `shows.list_shows()` in `app/shows.py`.
- Every show has one of four categories, `magic`, `comedy`, `music` or `acrobatics`, and the seed data has exactly 2 of each. Every show plays nightly from Nov 10 to Nov 23, 2026 (all of it is in [`docs/seed-data.md`](../docs/seed-data.md)).
- Domain code reports bad input by raising `BadRequest` from `app/errors.py`, which becomes a 400.

For a picture of how a request flows through these files, see [`docs/architecture.md`](../docs/architecture.md).

## Acceptance criteria

The full criteria are given. Write one test for each.

1. `GET /shows?category=comedy` returns exactly `Laugh Lines Live` and `Stand-Up Saloon`, ordered by title.
2. Each of the four categories returns exactly its 2 shows.
3. Matching ignores case: `?category=Comedy` returns the same 2 shows as `?category=comedy`.
4. Without `category`, `GET /shows` returns all 8 shows, as before.
5. Category combines with dates: `?category=music&start_date=2026-11-20` returns both music shows; `?category=music&start_date=2026-11-24` returns `[]`.
6. An unknown category returns 400 with the detail `Unknown category 'opera'. Choose one of: acrobatics, comedy, magic, music`.
7. `category` shows up as an optional query parameter in /docs (test it through `client.get("/openapi.json")`).

## The workflow

Settle what "done" means, then have Claude write the tests, check them yourself, and let Claude make them pass.

- Steps that use Claude have a prompt to copy; commands start with `!`.
- Why each step matters: [How we work](00-how-we-work.md).
- Start with a fresh conversation:

  ```text
  /clear
  ```

### 1. Align: write your answer key (no Claude yet)

Write down exactly what each criterion should return before Claude writes anything.

- Go through [Acceptance criteria](#acceptance-criteria) one by one: which shows come back, in what order, which status code, the exact message.
- Look up anything you need in [`docs/seed-data.md`](../docs/seed-data.md). For example, which 2 shows are in each category.
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

You'll compare Claude's tests against this answer key in step 2.

### 2. Tests first

Have Claude write failing tests, then check them against your answer key.

```text
Read tasks/lab1a-category-filter.md and the relevant code. Write a failing
test for each acceptance criterion. Test behavior through the API, the pages,
or functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

Check especially:

- **Tests check behavior through the API or the page**, not functions that don't exist yet. A test that calls a new function is designing the code for Claude.
- **Criterion 4 already passes** before you build anything: without `category`, `GET /shows` already returns all 8 shows. That's expected; the test guards behavior your change must not break.
- **Criterion 6's test checks the exact message**, not just the 400.

If a test doesn't match your answer key, tell Claude what it should be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

When every test matches your answer key, commit them:

```text
! git add -A && git commit -m "lab1a: tests"
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
Read tasks/lab1a-category-filter.md for context. Run the full suite and show
me the output.
```

Claude shouldn't touch any test file. Step 4 checks that.

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

- Try it yourself: follow [Check it in your browser](#check-it-in-your-browser) below.

Something doesn't match? Tell Claude which criterion failed and what you saw.

### 5. Review the diff

Read every change Claude made before you accept it.

```text
! git add -A && git diff --staged
```

- Can you explain every change?
- Was anything touched that has nothing to do with categories?
- Prefer side by side? Use VS Code's **Source Control** panel.

Your tests are already committed, so this shows only the code Claude wrote.

### 6. Get a second opinion

A reviewer that hasn't seen your conversation checks the change against this sheet.

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1a-category-filter.md. It hasn't seen our conversation. It should
check every acceptance criterion, not report style, and not change any files
or the database. Show me its findings as a numbered list, each with:
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
! git add -A && git commit -m "lab1a: category filter"
```

Finished with time to spare? Try the [Optional stretch](#optional-stretch) below.

## Check it in your browser

Use this for step 4 of the workflow. Compare every result with your answer key.

### 1. Start the app

Ask Claude to start the app in the background ([more on starting the app](01-getting-started.md#start-the-app)):

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

Wait until Claude says it's ready, then keep working in the same conversation.

### 2. Open each link (criteria 1–5)

Paste each link into your browser. In Chrome or Edge, tick **Pretty-print** to make the result easier to read.

| Criterion | Open | You should see |
| --- | --- | --- |
| 1 | http://127.0.0.1:8000/shows?category=comedy | Exactly 2 shows: `Laugh Lines Live`, then `Stand-Up Saloon` |
| 2 | http://127.0.0.1:8000/shows?category=magic | `Smoke & Sleight`, then `The Vanishing Ace` |
| 2 | http://127.0.0.1:8000/shows?category=music | `Desert Strings`, then `Neon Nights Revue` |
| 2 | http://127.0.0.1:8000/shows?category=acrobatics | `Gravity Optional`, then `Skyline Circus` |
| 3 | http://127.0.0.1:8000/shows?category=Comedy | The same 2 shows as criterion 1 |
| 4 | http://127.0.0.1:8000/shows | All 8 shows |
| 5 | http://127.0.0.1:8000/shows?category=music&start_date=2026-11-20 | `Desert Strings`, then `Neon Nights Revue` |
| 5 | http://127.0.0.1:8000/shows?category=music&start_date=2026-11-24 | `[]` (nothing plays after Nov 23) |

**Tip:** open the criterion 1 link *before* you build the feature. You'll get all 8 shows, because the app silently ignores parameters it doesn't know. That's why your tests have to fail first.

### 3. Check the error and the parameter in /docs (criteria 6–7)

A browser link shows the error message but not the status code, so use /docs for these two.

1. Open http://127.0.0.1:8000/docs and click **GET /shows**.

   <img src="img/lab1a-docs-1-find-endpoint.png" alt="Click GET /shows in the /docs page" width="600">

2. **Criterion 7:** under **Parameters**, `category` is listed next to `start_date` and `end_date`, with no `* required` marker. Click **Try it out**.

   <img src="img/lab1a-docs-2-try-it-out.png" alt="The category parameter and the Try it out button" width="600">

3. Type `opera` in the **category** box and click **Execute**.

   <img src="img/lab1a-docs-3-fill-and-execute.png" alt="category set to opera, then Execute" width="600">

4. **Criterion 6:** scroll down to **Server response**. The code is **400**, and the response body's detail is exactly `Unknown category 'opera'. Choose one of: acrobatics, comedy, magic, music`.

   <img src="img/lab1a-docs-4-response-400.png" alt="Code 400 with the unknown-category message" width="600">

5. Change `opera` to `comedy` and click **Execute** again. The code is **200**, with `Laugh Lines Live` and `Stand-Up Saloon`. The **Request URL** box shows the same link you opened in part 2.

   <img src="img/lab1a-docs-5-response-200.png" alt="Code 200 with the two comedy shows" width="600">

**Something doesn't match?** Don't fix it by hand. Tell Claude which criterion failed and what you saw.

### 4. Stop the app

When you're done checking:

```text
Stop the app.
```

Other ways to stop it, and what "address already in use" means: [Stop the app](01-getting-started.md#stop-the-app).

## Done means

- [ ] A test for each of the 7 criteria, all passing
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] Existing `tests/test_shows.py` tests pass unchanged
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Optional stretch

Finished early? Add a category dropdown to the home page (`GET /`) that filters the show list. The template only renders a form and the results; the filtering still happens in `shows.list_shows()`. Add a test that `GET /?category=comedy` lists only the two comedy shows.

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc2381a19172d05d8bc0cb5c). Open one level at a time.
