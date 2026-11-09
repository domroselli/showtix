# Lab 1c: Group discount

- **Tier:** Intermediate
- **Time:** 50 minutes
- Solo or with a partner

## Start here

**New here?** Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).

**This lab:** a new pricing rule that has to fit the existing pricing order, built with the full workflow.

1. Run the command under [Starting branch](#starting-branch).
2. Read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow) step by step.

**Step 1 starts with you:** think through your edge cases, then write out (or think about) your expected results yourself.

**You're done when you can check every box under [Checklist: What Done Means](#checklist-what-done-means).**

**Stuck?** See [Hints](#hints).

## Goal

#### Reward groups: 6 or more tickets in one tier get 15% off that tier.

## Starting branch

Copy the command below and run in Claude Code

```text
! git switch main && uv run python -m app.seed && git switch -c lab1c-group-discount && uv run pytest
```

Here's what it does:

1. Switches to `main`, so the new branch starts from the original code
2. Resets the database to the seed data
3. Creates new feature branch `lab1c-group-discount` from `main`
4. Runs the tests

Every test should pass before you change anything.

**Trouble?** See [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

Here is the relevant background about the feature you'll be building:

- **Pricing happens in `pricing.price_order()`** in `app/pricing.py`, in a fixed order (see CLAUDE.md): subtotal, discount, service fee, tax, total. `orders.quote()` merges cart items by tier, so each `pricing.Line` it passes in is one tier.
- **A promo discount is computed by `pricing.discount()`.** Quotes and orders carry a single `discount_cents` today. `pricing.pricing_lines()` turns a breakdown into the ordered lines (Subtotal, Discount, Service fees, Tax, Total) that quotes and orders return as `pricing_lines`. The UI's quote and confirmation pages loop over that list, so a line you add there shows up in the UI with no template changes.
- **Quotes (`Quote`) and stored orders (`Order`, `orders` table) must show the same numbers.** Tests use an in-memory database, but the running app uses a local SQLite file. If you change the schema, [reset the database](01-getting-started.md#reset-the-database), or the UI will break even while tests pass.
- **Docs:** `CLAUDE.md`, module docstrings and code comments describe the rule this sheet changes. Update them in step 3 with the code, not in step 2. Leave `docs/` alone: it describes `main`, which every lab starts from.

**For an illustration of the pricing order, see [How a price is built](../docs/architecture.md#3-how-a-price-is-built).**

## Acceptance criteria

In this lab, most criteria are given below. **Add one or two edge cases of your own as criteria 8 and 9** before you write tests.

**Every criterion needs at least one test.**

1. 6 or more tickets in the same tier get 15% off that tier's subtotal (rounded half up to the cent).
2. 5 tickets get no discount; exactly 6 do.
3. If a promo code also applies, the customer gets whichever discount is larger. They never stack.
4. The quote breakdown shows the group discount as its own line: its own field, `group_discount_cents`, and its own entry in `pricing_lines` (labelled exactly `Group discount (15%)`, negative, right after `Subtotal`, and only when it's non-zero). The discount that loses is reported as 0, and the existing `Discount` line stays.
5. All amounts stay in integer cents; tax follows the existing pricing order (9% of the subtotal after the discount that won).
6. The stored order matches the quote, including the group discount line.
7. If the group discount beats a promo, the promo isn't applied: the order doesn't record the promo code, and the promo's use count doesn't go up.
8. _Your edge case_
9. _Your edge case_ (optional)

**Edge cases to think about:** ties (no seeded promo can tie, so a test needs its own promo), the 8-ticket limit, a fixed promo, which discount the breakdown reports when one loses.

**Worked examples (cents, dollars in parentheses):**

| Cart | Subtotal | Discount that wins | Fees | Tax | Total |
| --- | --- | --- | --- | --- | --- |
| 6 GA, no promo | 41400 ($414.00) | group 6210 ($62.10) | 4500 ($45.00) | 3167 ($31.67) | 42857 ($428.57) |
| 6 GA + LOCALS10 | 41400 ($414.00) | group 6210 ($62.10); promo would be 4140 ($41.40) | 4500 ($45.00) | 3167 ($31.67) | 42857 ($428.57) |
| 6 GA + 2 VIP + LOCALS10 | 81398 ($813.98) | promo 8140 ($81.40); group would be 6210 ($62.10) | 6000 ($60.00) | 6593 ($65.93) | 85851 ($858.51) |
| 7 VIP, no promo | 139993 ($1,399.93) | group 20999 ($209.99) | 5250 ($52.50) | 10709 ($107.09) | 134953 ($1,349.53) |

## The workflow

#### Introduction

There are many workflows out there.

Engineers are still experimenting and finding what works for them. The models are changing and improving so rapidly that what works great today may get discarded 3 months from now (or, next week). You'll probably come up with your own workflow eventually (or maybe you already have one). All we're doing here is introducing you to one way you can build good software reliably with a coding agent like Claude.  

The main takeaway is this: there is no "correct" way right now.

- There are things you should do.
- There are things you shouldn't do. 
- There are things that seem to work in certain situations with the models we have right now.

The workflow in this lab is based on general software engineering principles that have been around for decades, combined with best practices given by Anthropic (and others).

We encourage you to use what works for you and share your results.

**<ins>One thing to note:</ins>** Often people who work with Claude (or Codex, etc...) first get alignment on an idea, have Claude put that into a spec, and create work items (user stories, issues, etc...) for Claude to work on *before* steps 2-7. Since this is a lab and we have limited time, we're focusing on the coding and review aspects of the flow. But we highly recommend you get experience with this on your own time.

#### Workflow Overview

1. Start a fresh conversation. Find your edge cases, then write your expected results (without Claude).
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, then commit.
3. Start a fresh conversation. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm only app/ changed, try it in the browser.
5. Review the diff.
6. A subagent reviews the change. For each real bug, Claude writes a failing test and fixes it, then you repeat steps 4 and 5.
7. Commit.

Why each step matters: [How we work](00-how-we-work.md).

### Step 1. Alignment on what "done" means

#### 1a. Start with a fresh conversation

```text
/clear
```

#### 1b. Find your edge cases

This sheet asks for one or two edge cases of your own.

Think them through yourself first: what could a customer do that the criteria don't answer? Type yours into [Acceptance criteria](#acceptance-criteria), as criteria 8 and 9.

**Stuck?** Ask Claude for a hint:

```text
Read tasks/lab1c-group-discount.md and the relevant code. I'm stuck finding edge cases
the criteria don't cover. Give me one hint at a time, as a question, not the
edge case itself. If I say "just tell me", suggest 3 edge cases, one sentence
each, and I'll pick. Don't write any code or change any files.
```

#### 1c. Review the acceptance criteria (without Claude)

This is how Claude knows when the feature is complete. Think through exactly what each criterion should return before Claude writes anything.  
Make a note of this somewhere to refer to later (like notes, notepad, or an empty text file. Whatever works for you).

**Go through [Acceptance criteria](#acceptance-criteria) one by one:** which status code, the exact message, the exact cents.

**Check you get the same numbers as the worked examples.**

**Note:**

- Prices, fees, tax rules and promo codes are in [`docs/seed-data.md`](../docs/seed-data.md) for your convenience.
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2. Implement tests first

#### 2a. Start with a fresh conversation

```text
/clear
```

#### 2b. Have Claude write failing tests. Check them against your expected results

```text
Read tasks/lab1c-group-discount.md and the relevant code. Write a failing test
for each acceptance criterion. Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't overwrite
app constants or internals to create a scenario (the fake_claude and clock
fixtures are fine). If a wrong implementation can't be told apart through real
behavior, tell me so I can check for it in the diff.

Then check the impact of any rule this sheet changes. Search the existing
tests and app/ for anywhere the old rule is asserted or calculated, including
helper functions. For each one, ask: if someone used this to get the answer
the rule governs, would the new rule make today's answer wrong?
- Yes, and a test covers it: update the test to the new rule.
- Yes, and no test covers it: add a failing test.
- No: leave it.
- Unsure: leave it alone and say why in the report.

Where the sheet leaves a detail open, pick the simplest answer that fits it,
build the tests on that, and list each pick in one line at the end of the
report. Don't ask me questions. Report each one in plain English for someone
who doesn't know this code: what it does, the old answer, the new answer, what
you did. Don't change anything in app/. Run the tests and show me which ones
fail.
```

#### 2c. Manually check the tests Claude just created

Claude may write more tests than you expect. Check these first, then the rest as time allows:

- **Compare each test with your expected results from step 1.**
- **Tests must check behavior through the API or the page**, **<ins>not functions that don't exist yet</ins>**.   
A test that calls a new function is designing the code for Claude.
- **Tests must not overwrite app values to set up a situation the sheet doesn't describe.** The `fake_claude` and `clock` fixtures are fine.
- **Read Claude's impact report, even if you don't know the code.** Each new answer should match the rule this sheet changes, each updated test should fail right now, and every existing test that changed should be in the report. Reject any that isn't. If the sheet changes no rule, no existing test should change. Read its list of picks too: each should fit the sheet; if one doesn't, say so in 2d.
- **The four worked examples are tests**, with every line asserted in exact cents.
- **Your own edge cases have tests too.**

#### 2d. If a test doesn't match your expected results, tell Claude what it should be and why

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

**Example:**

```text
The test for criterion 4 expects the label "Group discount", but it should be
"Group discount (15%)" because the label has to match exactly. Fix that test.
```

#### 2e. Commit the test code

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1c: tests"
```

### Step 3. Make the tests pass (write the code)

#### 3a. Clear the conversation

To get good results, Claude should build from the "spec" and your committed tests (not all the context from that chat):

```text
/clear
```

#### 3b. Ask Claude to make the tests pass

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If an existing test conflicts with the sheet or blocks the right
design, stop and tell me why. If you change anything the tests don't need,
tell me what and why. Read tasks/lab1c-group-discount.md for context. Run the
full suite and show me the output.
```

Claude shouldn't touch any test file.

We don't want to rewrite tests we've already verified to make them pass. The code alone should do that. Step 4 checks it.

### Step 4. Check the evidence

Don't take Claude's word for it; check for yourself.

#### 4a. Run the tests

The last line should say only `passed`, with no `skipped`, `deselected` or `xfailed`:

```text
! uv run pytest
```

#### 4b. Check that Claude only changed app code

This shows the files that have changed since the last commit.  
Every file this lists should be under `app/` (or be `CLAUDE.md`, if Claude updated the rule text with the code):

```text
! git status --short
```

A file in `tests/` (changed, or new with `??`), a `conftest.py`, or `pyproject.toml` means Claude touched your tests or how they run: ask why before going on. If there are any fixes in step 6, the only test changes should be the new tests you asked for. Nothing existing should be modified.

#### 4c. Visual tests in the browser

**First, reset the database.** Storing the group discount on orders needs a new column, but the app's `showtix.db` file was created before that column existed, so placing or viewing an order would fail.

The tests still pass because each one builds a fresh in-memory database. Resetting rebuilds the file with the new column and puts back the starting data. In production you'd run a migration to keep real data, but this is local practice data, so a reset is fine:

```text
! uv run python -m app.seed
```

**Then start the app.** Ask Claude to start it in the background ([more on starting the app](01-getting-started.md#start-the-app)):

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

**Then check the worked examples in the UI:**

1. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and click a date under **Laugh Lines Live**.
2. In the **Qty** column, enter the tickets for one worked example, such as `6` for **GA**. If it has a promo, type it in **Promo code**. Click **Get quote** and compare every line with your expected results.
3. Go back to the date page and repeat for the other worked examples.
4. For one of them, enter any email and click **Place order**. The page you land on should show the same lines.

Prefer the API? Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (click your endpoint, **Try it out**, **Execute**).

When you're done, stop the app:

```text
Stop the app.
```

#### 4d. Something doesn't match?

Tell Claude which criterion failed and what you saw.

### Step 5. Review the diff

#### 5a. Read every change Claude made before you accept it

These commands stage the changes and then show the diff between these staged changes and the latest commit on your branch.

```text
! git add -A && git diff --staged
```

- Can you explain every change?
- Was anything touched that has nothing to do with the group discount?
- Prefer side by side? Use VS Code's **Source Control** panel.

Your tests are already committed, so this shows only the code Claude wrote.

### Step 6. Get a second opinion

#### 6a. Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. It hasn't seen your conversation, and it checks the change against this sheet.

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1c-group-discount.md. It hasn't seen our conversation. It should
check every acceptance criterion, not report style, and not change any files
or the database. It should also look for anything that still uses or expects
an old rule this sheet changes. Show me its findings as a numbered list, each
with:
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

Claude shows the MUST FIX findings and asks which to fix. The labels are the reviewer's opinion, so check the evidence yourself before you answer.

#### 6b. Answer with the numbers you want fixed

For example "1 and 3". Then repeat steps 4 and 5.   
Or you can decide you don't want to fix it, or you want to have a chat with Claude about it before you decide.

Why "don't report style"? See [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7. Commit

Commit when you're satisfied with the change:

```text
! git add -A && git commit -m "lab1c: group discount"
```

## Checklist: What Done Means

- [ ] A test for each given criterion and for your own edge cases, all passing
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] The four worked examples are tests, with every line asserted in exact cents
- [ ] The quote, the stored order and the UI agree on every line
- [ ] The group discount appears on the UI's quote and confirmation pages with no template changes
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] All money math is in `app/pricing.py`, in integer cents; no floats
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in the UI or /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc238156b855d22a8fe01f48). Open one level at a time.
