# Demo 1: Fee cap

- **Tier:** Instructor demo (before Lab 1)
- **Time:** 10 minutes
- Watch along; you'll do the same seven steps in Lab 1

## Start here

**This is the sheet the instructor follows on screen.** It has the same shape as every Lab 1 sheet, so when you open yours it won't be the first time you've seen it. Nothing here is on the Lab 1 menu, so it spoils nothing. The prompts are the same as yours, plus one sentence in step 2: this feature changes a rule that an existing test asserts, while your Lab 1 features add behavior, so your sheets don't need it.

1. Run the command under [Starting branch](#starting-branch).
2. Read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow) step by step.

**Step 1 is yours:** work out the expected results before you ask Claude anything. In the demo they're on a slide.

**You're done when you can check every box under [Checklist: What Done Means](#checklist-what-done-means).**

## Goal

#### Cap service fees at 3000 cents ($30.00) per order. Below the cap, fees stay 750 ($7.50) per ticket.

## Starting branch

Copy the command below and run in Claude Code

```text
! git switch main && uv run python -m app.seed && git switch -c demo1-fee-cap && uv run pytest
```

Here's what it does:

1. Switches to `main`, so the new branch starts from the original code
2. Resets the database to the seed data
3. Creates new feature branch `demo1-fee-cap` from `main`
4. Runs the tests

Every test should pass before you change anything.

## Background

Here is the relevant background about the feature you'll be building:

- All money math lives in `app/pricing.py`. `service_fees(ticket_count)` returns `ticket_count × 750`; `price_order()` assembles subtotal, discount, fees, tax and total in the order `CLAUDE.md` describes.
- GA is 6900 ($69.00) a ticket. Tax is 9% of the discounted ticket subtotal only, never of fees (all of it is in [`docs/seed-data.md`](../docs/seed-data.md)).
- Two traps to watch for: capping the total instead of the fees, and putting the cap anywhere but `pricing.py`.
- Today the fee is 750 ($7.50) per ticket with no limit; this sheet changes that rule. Stored orders are never re-priced, so orders already placed keep what was charged with no new code or test.
- **Docs:** `CLAUDE.md`, module docstrings and code comments describe the rule this sheet changes. Update them in step 3 with the code, not in step 2. Leave `docs/` alone: it describes `main`, which every lab starts from.

**For an illustration of where pricing sits, see [`docs/architecture.md`](../docs/architecture.md).**

## Acceptance criteria

In this demo, the full criteria are given below.

**Every criterion needs at least one test.**

1. Service fees on an order are `min(750 × tickets, 3000)` cents. The cap is on the order's fee total, not on a ticket count.
2. `POST /orders/quote` for 3 GA returns fees 2250 ($22.50), tax 1863 ($18.63), total 24813 ($248.13). Unchanged from today.
3. `POST /orders/quote` for 4 GA returns fees 3000 ($30.00), tax 2484 ($24.84), total 33084 ($330.84). Exactly at the cap, unchanged from today.
4. `POST /orders/quote` for 8 GA returns fees 3000 ($30.00), tax 4968 ($49.68), total 63168 ($631.68). Today it returns fees 6000 ($60.00) and total 66168 ($661.68).
5. Tax does not move: it is still 9% of the discounted ticket subtotal, never of fees.

**Worked examples (cents, dollars in parentheses):**

| Order | Subtotal | Fees today | Fees with cap | Tax | Total with cap |
| --- | --- | --- | --- | --- | --- |
| 3 GA | 20700 ($207.00) | 2250 ($22.50) | 2250 ($22.50), under cap | 1863 ($18.63) | 24813 ($248.13), unchanged |
| 4 GA | 27600 ($276.00) | 3000 ($30.00) | 3000 ($30.00), exactly at cap | 2484 ($24.84) | 33084 ($330.84), unchanged |
| 8 GA | 55200 ($552.00) | 6000 ($60.00) | 3000 ($30.00), capped | 4968 ($49.68) | 63168 ($631.68), was 66168 ($661.68) |
| 5 Premium | 60000 ($600.00) | 3750 ($37.50) | 3000 ($30.00) | 5400 ($54.00) | 68400 ($684.00), was 69150 ($691.50) |

## The workflow

#### Workflow Overview

1. Write your expected results (no Claude yet).
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, then commit.
3. Start a fresh conversation. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm only app/ changed, try it in /docs.
5. Review the diff.
6. A subagent reviews the change. (Named in the demo, not run: it takes two or three minutes.)
7. Commit.

Why each step matters: [How we work](00-how-we-work.md).

### Step 1. Alignment on what "done" means (no Claude yet)

#### 1a. Review the acceptance criteria

Think through exactly what each criterion should return before Claude writes anything. In the demo, the worked-examples table is on a slide; in your lab, you write it down yourself.

**Two things to notice:**

- Tax does not move. Only the fees line changes. "Cap the fees" is easy to misread as "cap the total".
- A rule change can leave old tests behind. You don't need to know which ones: step 2 has Claude find and update them, and you check its old and new answers against this table.

### Step 2. Implement tests first

#### 2a. Start with a fresh conversation

```text
/clear
```

#### 2b. Have Claude write failing tests. Check them against your expected results

```text
Read tasks/demo1-fee-cap.md and the relevant code. Write a failing test for
each acceptance criterion. Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML, and don't change
app values to set up a scenario. Also update any existing test that still
asserts the old rule, including tests of helper functions, and tell me which
ones. Where the sheet leaves a detail open, pick the simplest answer. Don't
change anything in app/. Run the tests and show me which ones fail.
```

#### 2c. Manually check the tests Claude just created

Claude's reply is your checklist: one line per test with the criterion it covers, what it expects and whether it passes today. If the reply doesn't give you that, ask:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check:

- **Each expected value matches the worked examples.** Exact cents: 2250, 3000, 3000 for fees; 1863, 2484, 4968 for tax; 24813, 33084, 63168 for totals; 68400 for 5 Premium. For a case Claude invented (a promo order, a mixed-tier order), work it out: discounted subtotal, fees `min(750 × tickets, 3000)`, tax 9% of the discounted subtotal, total.
- **Every route or function a test calls already exists in `app/`.** `client.get(...)` and `client.post(...)` are the API. A test that calls a function that doesn't exist yet is designing the code for Claude: use 2d.
- **Claude names the existing tests it updated.** Expect two: the fee helper (8 tickets, 6000 to 3000) and the 5 Premium total (69150 to 68400). Claude may ask whether the cap must live inside `service_fees()`: yes, anyone who calls that helper should get the real fee.
- **Criteria 2 and 3 already pass before you build anything.** That's expected; they guard behavior your change <ins>must not</ins> break. Criterion 4 and both updated tests must fail.
- **If every test passes, a test is wrong.**

#### 2d. If a test doesn't match your expected results, tell Claude what it should be and why

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

#### 2e. Commit the test code

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "demo1: fee cap tests"
```

Committed tests are tamper-evident. If Claude loosens one later, the diff shows it.

### Step 3. Make the tests pass (write the code)

#### 3a. Clear the conversation

```text
/clear
```

#### 3b. Ask Claude to make the tests pass

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/demo1-fee-cap.md for context. Run the full suite and show me the
output.
```

Claude shouldn't touch any test file.

**Watch for:**

- Cap applied to the total, or to fees plus tax: wrong. See [When Claude gets something wrong](00-how-we-work.md#when-claude-gets-something-wrong); its example is this exact feature.
- A cap added in `price_order()` with `service_fees()` left uncapped: wrong, and the updated helper test catches it. The function that computes the fee must give the real fee.
- Money math anywhere but `pricing.py`, or a float anywhere: wrong, `CLAUDE.md` rules.
- A ticket-count threshold (`if tickets >= 4`): wrong. The 4 is a consequence of 750 × 4 = 3000, not a rule. Change the fee and it moves; `min()` doesn't care.

Claude usually ends by asking whether to update `CLAUDE.md`, the README and the docs, which still describe the uncapped fee. The answer is:

```text
Yes: update CLAUDE.md, README.md, the pricing.py docstring and any comment
that states the old fee. Leave docs/ alone.
```

`CLAUDE.md` is where the rule lives for every future session, so it moves with the code. `docs/` describes `main` and stays as it is on a lab branch.

### Step 4. Check the evidence

Don't take Claude's word for it; check for yourself.

#### 4a. Run the tests

The last line should say only `passed`, with no `skipped`, `deselected` or `xfailed`:

```text
! uv run pytest
```

#### 4b. Check that Claude only changed app code

Every file this lists should be under `app/` (or be `CLAUDE.md`, if Claude updated the rule text with the code):

```text
! git status --short
```

A file in `tests/` here means Claude touched your tests after you committed them: ask why.

#### 4c. Try it in /docs

Follow [Check it in your browser](#check-it-in-your-browser) below.

#### 4d. Something doesn't match?

Tell Claude which criterion failed and what you saw.

### Step 5. Review the diff

#### 5a. Read every change Claude made before you accept it

```text
! git add -A && git diff --staged
```

Expect: one constant, `min()` inside `service_fees()`, the pricing-order docstring updated, plus the rule text in `CLAUDE.md` and `README.md`. Nothing else.

- Can you explain every change?
- Was anything touched that has nothing to do with fees?

### Step 6. Get a second opinion

In the demo this step is named, not run. In your lab you run it; it takes two or three minutes.

A reviewer subagent that hasn't seen the conversation checks the branch against this sheet and labels each finding MUST FIX, OUT OF SCOPE, UNSURE or OPTIONAL. You pick which to fix; Claude writes a failing test for each first. The prompt is on every Lab 1 sheet, and the labs mark this step optional when you're short on time.

### Step 7. Commit

```text
! git add -A && git commit -m "demo1: cap service fees at 30 dollars per order"
```

Those are the seven steps on every Lab 1 sheet. Decide what right is, get tests you can read, let Claude code against them, check the evidence yourself, read the diff, commit.

## Check it in your browser

Use this for step 4c of the workflow.

### 1. Start the app

Ask Claude to start the app in the background ([more on starting the app](01-getting-started.md#start-the-app)):

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

### 2. Quote 8 GA tickets in /docs (criterion 4)

1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and click **POST /orders/quote**, then **Try it out**.
2. Replace the request body with this (after a fresh seed, performance 1 is The Vanishing Ace on Nov 10 and tier 1 is its GA):

   ```json
   {"performance_id": 1, "items": [{"tier_id": 1, "qty": 8}]}
   ```

3. Click **Execute**. In the response, `fees_cents` is 3000 ($30.00) and `total_cents` is 63168 ($631.68). Match them to the worked examples.

### 3. Stop the app

```text
Stop the app.
```

## Checklist: What Done Means

- [ ] A test for each of the 5 criteria, all passing
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] The existing tests that changed are the ones Claude named in step 2, with old and new answers that match the rule change
- [ ] Every test asserts exact cents, not "smaller than before"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] The cap lives in `pricing.py`, inside the function that computes the fee, and tax is unchanged
- [ ] You tried 8 GA in /docs and read 3000 and 63168 off the response
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed
