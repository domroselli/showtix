# Lab 1a: Category filter

**Tier:** Starter · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

Let customers list shows by category: `GET /shows?category=comedy`.

## Starting branch

```sh
git switch main
git switch -c lab1a-category-filter
uv run pytest          # green before you change anything
```

## Background

- `GET /shows` already takes `start_date` and `end_date`. The route is in `app/main.py`; the query is built in `shows.list_shows()` in `app/shows.py`.
- Every show has one of four categories: `magic`, `comedy`, `music`, `acrobatics` (see the `shows` table in `app/db.py`).
- The seed data has exactly 2 shows per category, and every show plays nightly from Nov 10 to Nov 23, 2026.
- Domain code reports bad input by raising `BadRequest` from `app/errors.py`, which becomes a 400.

## Acceptance criteria

The full criteria are given. Write one test for each.

1. `GET /shows?category=comedy` returns exactly `Laugh Lines Live` and `Stand-Up Saloon`, ordered by title.
2. Each of the four categories returns exactly its 2 shows.
3. Matching ignores case: `?category=Comedy` returns the same 2 shows as `?category=comedy`.
4. Without `category`, `GET /shows` returns all 8 shows, as before.
5. Category combines with dates: `?category=music&start_date=2026-11-20` returns both music shows; `?category=music&start_date=2026-11-24` returns `[]`.
6. An unknown category returns 400 with the detail `Unknown category 'opera'. Choose one of: acrobatics, comedy, magic, music`.
7. `category` shows up as an optional query parameter in /docs (test it through `client.get("/openapi.json")`).

## The working loop

Write the tests first and check them yourself, then let Claude make them pass. Each step has a prompt you can copy. Start with `/clear` so Claude begins fresh.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 2, you'll compare Claude's tests against this answer key.
2. **Tests first.** Ask Claude:

   > Read tasks/lab1a-category-filter.md and the relevant code. Write a failing test for each acceptance criterion. Don't change anything in app/. Run the tests and show me which ones fail.

   Compare each test with your answer key. If one is wrong, tell Claude what it should be and why:

   > The test for criterion 4 expects ___, but it should be ___ because ___. Fix that test.

   Check especially:
   - **Criterion 4 already passes**, before you build anything: without `category`, `GET /shows` already returns all 8 shows. That's expected; the test guards behavior your change must not break.
   - **Criterion 6's test checks the exact message**, not just the 400.

   When you're satisfied with the tests, commit them:

   ```sh
   git add -A && git commit -m "lab1a: tests"
   ```

3. **Clear, then implement.** Type `/clear`, then ask:

   > Make the new tests from my last commit pass (see git show HEAD). Don't change any test. Read tasks/lab1a-category-filter.md for context. Run the full suite and show me the output.

4. **Check the evidence.**
   - Run `uv run pytest` yourself. Is everything green?
   - Run `git diff HEAD --stat -- tests/`. It should print nothing, which means Claude didn't change your tests.
   - Try it yourself: follow **Check it in your browser** below.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Your tests are already committed, so this shows only the code Claude wrote. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude:

   > Use a subagent to review this branch's changes (git diff main) against tasks/lab1a-category-filter.md. It hasn't seen our conversation. Check every acceptance criterion, and don't report style. For each finding, give:
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
   git add -A && git commit -m "lab1a: category filter"
   ```

## Check it in your browser

Use this for step 4 of the loop. Compare every row with your answer key.

### 1. Start the app

Open a second terminal, go to your `showtix` folder, and run:

```sh
uv run uvicorn app.main:app --reload
```

Wait for `Application startup complete`. Leave this terminal running; keep working with Claude in the first one.

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

   ![Click GET /shows in the /docs page](img/lab1a-docs-1-find-endpoint.png)

2. **Criterion 7:** under **Parameters**, `category` is listed next to `start_date` and `end_date`, with no `* required` marker. Click **Try it out**.

   ![The category parameter and the Try it out button](img/lab1a-docs-2-try-it-out.png)

3. Type `opera` in the **category** box and click **Execute**.

   ![category set to opera, then Execute](img/lab1a-docs-3-fill-and-execute.png)

4. **Criterion 6:** scroll down to **Server response**. The code is **400**, and the response body's detail is exactly `Unknown category 'opera'. Choose one of: acrobatics, comedy, magic, music`.

   ![Code 400 with the unknown-category message](img/lab1a-docs-4-response-400.png)

5. Change `opera` to `comedy` and click **Execute** again. The code is **200**, with `Laugh Lines Live` and `Stand-Up Saloon`. The **Request URL** box shows the same link you opened in part 2.

   ![Code 200 with the two comedy shows](img/lab1a-docs-5-response-200.png)

**Something doesn't match?** Don't fix it by hand. Tell Claude which criterion failed and what you saw.

### 4. Stop the app

Click in the terminal where the app is running and press **Ctrl+C** (on a Mac too: Control, not Command). You'll see `Shutting down`. If you later get "address already in use," the app is still running in another terminal: find it and press Ctrl+C there.

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
