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

This is how people really use Claude Code: one good prompt, then you check the evidence.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents. Some criteria already state the answer; others you work out. If the sheet has a worked example, check you get the same numbers. To look things up, run the app (`uv run uvicorn app.main:app --reload`) and use /docs, for example `GET /shows` to see the seeded shows and prices. In step 3, you'll compare Claude's tests against this answer key.
2. **One good prompt.** For example: "Read tasks/lab1a-category-filter.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after."
3. **Check the evidence.** Did the tests fail before the change? Does each test match your answer key, not just what Claude assumed?
4. **Try it yourself.** In a second terminal, start the app with `uv run uvicorn app.main:app --reload`, then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. Ctrl+C stops the app. Step by step, with screenshots: **Check it in your browser** below.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude: "Review this diff against tasks/lab1a-category-filter.md." Then decide which of its findings actually matter.

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
