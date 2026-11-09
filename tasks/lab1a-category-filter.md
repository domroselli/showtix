# Lab 1a: Category filter

- **Tier**: Starter
- **Time**: 50 minutes
- **Format**: solo or with a partner

## Start here

If this is your first lab, read [Getting started](01-getting-started.md) for how to run commands and the app, and then read [How we work](00-how-we-work.md) for the workflow. Each page takes about 5 minutes to read.

In this lab, you build a small filter with the full seven-step workflow.

To run this lab, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Run the command in the [Starting branch](#starting-branch) section of this document.
3. Read the [Goal](#goal), [Background](#background), and [Acceptance criteria](#acceptance-criteria) sections.
4. Follow the [Workflow](#workflow) section step by step.

Step 1 is yours: write out your expected results before you ask Claude anything.

You're done when you can check every box in the [Completion checklist](#completion-checklist) section of this document. If you have time left, try the [Optional stretch](#optional-stretch) section. If you're stuck, see the [Hints](#hints) section.

## Goal

Let customers list shows by category with the `GET /shows?category=comedy` request.

## Starting branch

To create your lab branch, enter the following command in Claude Code:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1a-category-filter && uv run pytest
```

The command does the following, in order:

1. Switches to the `main` branch, so the new branch starts from the original code.
2. Resets the database to the seed data.
3. Creates the `lab1a-category-filter` feature branch from `main`.
4. Runs the tests.

Every test passes before you change anything. If the command fails, see [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

The following list describes the code that this feature touches:

- The `GET /shows` endpoint already takes `start_date` and `end_date`. The route is in the `app/main.py` file, and the `shows.list_shows()` function in the `app/shows.py` file builds the query.
- Every show has one of four categories: `magic`, `comedy`, `music`, or `acrobatics`. The seed data has exactly 2 shows in each category, and every show plays nightly from November 10 to November 23, 2026. The `docs/seed-data.md` file lists all of the seed data.
- Domain code reports bad input by raising `BadRequest` from the `app/errors.py` file, which becomes an HTTP `400 Bad Request` status code.

For an illustration of the request flow through these files, see [Architecture](../docs/architecture.md).

## Acceptance criteria

This lab gives you the full list of criteria. Every criterion needs at least one test.

1. The `GET /shows?category=comedy` request returns exactly `Laugh Lines Live` and `Stand-Up Saloon`, ordered by title.
2. Each of the four categories returns exactly its 2 shows, ordered by title.
3. Matching ignores case: `?category=Comedy` returns the same 2 shows as `?category=comedy`.
4. Without `category`, the `GET /shows` request returns all 8 shows, as before.
5. Category combines with dates: `?category=music&start_date=2026-11-20` returns both music shows, and `?category=music&start_date=2026-11-24` returns `[]`.
6. An unknown category returns an HTTP `400` status code with the detail `Unknown category 'opera'. Choose one of: acrobatics, comedy, magic, music`.
7. The `category` parameter appears on the `/docs` page as an optional query parameter, that is, with no `* required` marker, next to `start_date` and `end_date`. Claude tests this through `client.get("/openapi.json")`.

## Workflow

### About the workflow

There are many workflows for working with a coding agent, and engineers are still finding out what works for them. The models change fast, so a method that works well can fall out of use within months or even weeks. You'll probably settle on your own workflow in time, if you don't have one already. This lab introduces one way to build good software reliably with a coding agent such as Claude.

The main point is that there's no single correct way:

- Some things are worth doing.
- Some things are worth avoiding.
- Some things work in certain situations with certain models.

The workflow in this lab combines software engineering principles that have held up for decades with the practices that Anthropic and others recommend. Use what works for you, and share your results.

**Note**: People who work with Claude or another coding agent often align on an idea first, have the agent write it into a spec, and then create work items such as user stories or issues for the agent to work on, all before steps 2 to 7. This lab has limited time, so it focuses on the coding and review parts of the flow. We recommend that you try the spec and work-item parts on your own time.

### Workflow overview

The workflow has the following seven steps:

1. Write your expected results, without Claude.
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, and then you commit them.
3. Start a fresh conversation. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm that only the `app/` directory changed, and try the feature in your browser.
5. Review the diff.
6. A subagent, a separate Claude that starts with no memory of this conversation, reviews the change. For each real bug, Claude writes a failing test and fixes it, and then you repeat steps 4 and 5.
7. Commit.

For more information about why each step matters, see [How we work](00-how-we-work.md).

### Step 1: Align on what done means

This step has no Claude in it.

#### 1a: Review the acceptance criteria

The acceptance criteria are how Claude knows when the feature is complete. Before Claude writes anything, work out exactly what each criterion returns, and write it down somewhere you can find again, such as a notes app or a text file outside your `showtix` folder, because anything inside the folder gets committed with your tests.

To build your expected results, go through the [Acceptance criteria](#acceptance-criteria) section one by one, and write down which shows come back, in what order, which status code, and the exact message.

The `docs/seed-data.md` file has all of the seed data, including which 2 shows are in each category. To see the data in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

To start a fresh conversation, enter the following command:

```text
/clear
```

#### 2b: Ask Claude for failing tests

To have Claude write a failing test for each criterion, enter the following prompt:

```text
Read tasks/lab1a-category-filter.md and the relevant code. Write a failing
test for each acceptance criterion. Test behavior through the API, the pages,
or functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

#### 2c: Check the tests against your expected results

Claude's reply is your checklist. It has one line per test, with the criterion the test covers, what the test expects, and whether the test passes today. If the reply doesn't give you that, ask for it:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the following points:

- **Each expected value matches your step 1 notes.** Claude wrote the tests and the summary, so the notes that you wrote without Claude are the thing to trust. If a value isn't in your notes, work it out yourself or use 2d.
- **Every route or function that a test calls already exists in `app/`.** The `client.get(...)` and `client.post(...)` calls are the API. A test that calls a function that doesn't exist yet designs the code for Claude. Use 2d.
- **Criterion 4 already passes before you build anything.** Without the `category` parameter, the `GET /shows` request already returns all 8 shows. That result is expected. The test guards behavior that your change must not break. Criterion 5's `start_date=2026-11-24` case also passes today, because the date filter alone already returns `[]`. The `2026-11-20` case is the one that fails.
- **Criterion 6's test checks the exact message.** The HTTP `400` status code alone isn't enough.

#### 2d: Correct a test that doesn't match

If a test doesn't match your expected results, tell Claude what the test must check and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet, ask Claude to rewrite the test:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

The following prompt is an example of a correction:

```text
The test for criterion 6 expects the error message to be "Unknown category
'opera'", but it should be "Unknown category 'opera'. Choose one of:
acrobatics, comedy, magic, music" because the error should list the available
categories. Fix that test.
```

#### 2e: Commit the tests

When every test matches your expected results, commit the tests:

```text
! git add -A && git commit -m "lab1a: tests"
```

### Step 3: Make the tests pass

#### 3a: Clear the conversation

Claude builds from the sheet and your committed tests, not from the conversation that produced them. To clear the conversation, enter the following command:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

To have Claude write the code, enter the following prompt:

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab1a-category-filter.md for context. Run the full suite and show
me the output.
```

Claude must not touch any test file. You verified the tests in step 2, so the code alone has to make them pass. Step 4 checks that.

### Step 4: Check the evidence

Don't take Claude's word for the result. Check it yourself.

#### 4a: Run the tests

To run the tests yourself, enter the following command:

```text
! uv run pytest
```

The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`.

#### 4b: Check that Claude changed only app code

To list the files that changed since the last commit, enter the following command:

```text
! git status --short
```

Every file in the list must be under the `app/` directory. A file in `tests/`, whether changed or new with `??`, a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask Claude why before you go on. If step 6 adds fixes, the only test changes are the new tests that you asked for, and no existing test changes.

#### 4c: Check the feature in your browser

To try the feature yourself, follow the [Check it in your browser](#check-it-in-your-browser) section of this document.

#### 4d: Report a mismatch

If something doesn't match your expected results, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read every change before you accept it

To stage the changes and show the diff between the staged changes and the latest commit on your branch, enter the following command:

```text
! git add -A && git diff --staged
```

Your tests are already committed, so the diff shows only the code that Claude wrote. As you read the diff, answer the following questions:

- Can you explain every change?
- Did anything change that has nothing to do with categories?

To read the diff side by side, use the **Source Control** panel in VS Code.

### Step 6: Get a second opinion

#### 6a: Create a code reviewer for your changes

A reviewer subagent hasn't seen your conversation, and it checks the change against this sheet. To create one, enter the following prompt:

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

To keep it simple, after you categorize the findings only show MUST FIX. All
other findings you can ignore.

Then ask me which ones to fix. For each one I pick, write a failing test that
shows the problem, then fix it. Run the full suite and show me the output.
```

Claude shows the MUST FIX findings and asks which ones to fix. The labels are the reviewer's opinion, so check the evidence yourself before you answer.

#### 6b: Answer with the numbers you want fixed

Reply with the numbers of the findings to fix, such as "1 and 3", and then repeat steps 4 and 5. You can also decide not to fix a finding, or discuss it with Claude before you decide. Claude might also list UNSURE or OPTIONAL findings. Those are yours to decide, and the lab doesn't need them. If Claude reports no MUST FIX findings, there's nothing to answer. Repeat steps 4 and 5 once, and then go on to step 7. If Claude asks how to fix something, answer with the behavior that you want and let Claude choose the code.

For more information about why the prompt says "not report style", see [Get a second opinion](00-how-we-work.md#6-get-a-second-opinion).

### Step 7: Commit

When you're satisfied with the change, commit it:

```text
! git add -A && git commit -m "lab1a: category filter"
```

If you finish with time to spare, try the [Optional stretch](#optional-stretch) section of this document.

## Check it in your browser

Use this section during [4c: Check the feature in your browser](#4c-check-the-feature-in-your-browser). Compare what you see with your expected results.

### Start the app

Ask Claude to start the app in the background:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

Wait until Claude says that the app is ready, and then keep working in the same conversation. For more information, see [Start the app](01-getting-started.md#start-the-app).

### Open each link for criteria 1 to 5

Open each link in the following table in your browser. In Chrome or Edge, select **Pretty-print** to make the result easier to read. Firefox formats the result on its own. In Safari, read the raw text or use the `/docs` page.

| Criterion | Open | Expected result |
| --- | --- | --- |
| 1 | [http://127.0.0.1:8000/shows?category=comedy](http://127.0.0.1:8000/shows?category=comedy) | Exactly 2 shows: `Laugh Lines Live`, then `Stand-Up Saloon` |
| 2 | [http://127.0.0.1:8000/shows?category=magic](http://127.0.0.1:8000/shows?category=magic) | `Smoke & Sleight`, then `The Vanishing Ace` |
| 2 | [http://127.0.0.1:8000/shows?category=music](http://127.0.0.1:8000/shows?category=music) | `Desert Strings`, then `Neon Nights Revue` |
| 2 | [http://127.0.0.1:8000/shows?category=acrobatics](http://127.0.0.1:8000/shows?category=acrobatics) | `Gravity Optional`, then `Skyline Circus` |
| 3 | [http://127.0.0.1:8000/shows?category=Comedy](http://127.0.0.1:8000/shows?category=Comedy) | The same 2 shows as criterion 1 |
| 4 | [http://127.0.0.1:8000/shows](http://127.0.0.1:8000/shows) | All 8 shows |
| 5 | [http://127.0.0.1:8000/shows?category=music&start_date=2026-11-20](http://127.0.0.1:8000/shows?category=music&start_date=2026-11-20) | `Desert Strings`, then `Neon Nights Revue` |
| 5 | [http://127.0.0.1:8000/shows?category=music&start_date=2026-11-24](http://127.0.0.1:8000/shows?category=music&start_date=2026-11-24) | `[]`, because nothing plays after November 23 |

**Note**: If you open the criterion 1 link before you build the feature, you get all 8 shows, because the app ignores parameters that it doesn't know. That's why your tests have to fail first.

### Check the error and the parameter on the `/docs` page for criteria 6 and 7

A browser link shows the error message but not the status code, so use the `/docs` page for these two criteria. To check them, follow these steps:

1. Open the [API documentation page](http://127.0.0.1:8000/docs), and then click **GET /shows**.

   <img src="img/lab1a-docs-1-find-endpoint.png" alt="Click GET /shows in the /docs page" width="600">

2. For criterion 7, confirm that under **Parameters**, `category` is listed next to `start_date` and `end_date` with no `* required` marker.

   <img src="img/lab1a-docs-2-try-it-out.png" alt="The category parameter and the Try it out button" width="600">

3. Click **Try it out**.

4. In the **category** box, enter `opera`, and then click **Execute**.

   <img src="img/lab1a-docs-3-fill-and-execute.png" alt="category set to opera, then Execute" width="600">

5. For criterion 6, scroll down to **Server response**. The code is **400**, and the detail in the response body is exactly `Unknown category 'opera'. Choose one of: acrobatics, comedy, magic, music`.

   <img src="img/lab1a-docs-4-response-400.png" alt="Code 400 with the unknown-category message" width="600">

6. Change `opera` to `comedy`, and then click **Execute** again. The code is **200**, with `Laugh Lines Live` and `Stand-Up Saloon`. The **Request URL** box shows the same link that you opened in the preceding table.

   <img src="img/lab1a-docs-5-response-200.png" alt="Code 200 with the two comedy shows" width="600">

If something doesn't match, don't fix it by hand. Tell Claude which criterion failed and what you saw.

### Stop the app

When you're done checking, ask Claude to stop the app:

```text
Stop the app.
```

For other ways to stop the app, and what an "address already in use" error means, see [Stop the app](01-getting-started.md#stop-the-app).

Then go back to [4d: Report a mismatch](#4d-report-a-mismatch) and continue with [Step 5: Review the diff](#step-5-review-the-diff).

## Completion checklist

The lab is complete when the following statements are true:

- [ ] Each of the 7 criteria has a test, and every test passes.
- [ ] The tests that you committed in step 2 weren't changed to make them pass.
- [ ] The existing tests in the `tests/test_shows.py` file pass unchanged.
- [ ] Every test asserts exact values, such as exact cents for money, not "smaller" or "not empty".
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] Routes in the `main.py` file only call into domain modules.
- [ ] You tried the feature by hand in the UI or on the `/docs` page with values that you worked out yourself.
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed.

## Optional stretch

If you finish early, add a category dropdown to the home page (`GET /`) that filters the show list. The template only renders a form and the results, and the filtering still happens in the `shows.list_shows()` function. Add a test that the `GET /?category=comedy` request lists only the two comedy shows.

## Hints

If you're stuck, open the [workshop hints page](https://www.notion.so/409be0acdc2381a19172d05d8bc0cb5c). It lists the places where students get stuck in this lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see.
