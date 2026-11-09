# Lab 1c: Group discount

- **Tier**: Intermediate
- **Time**: 50 minutes
- **Format**: solo or with a partner

## Start here

If you're new to the labs, read [Getting started](01-getting-started.md) for how to run commands and the app, and then [How we work](00-how-we-work.md) for the workflow. Each page takes about 5 minutes to read.

In this lab, you add a pricing rule that must fit the existing pricing order, and you build it with the full workflow.

To do this lab, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Run the command in the [Starting branch](#starting-branch) section of this document.
3. Read the [Goal](#goal), [Background](#background), and [Acceptance criteria](#acceptance-criteria) sections.
4. Follow the [Workflow](#workflow) section step by step.

Step 1 starts with you. Think through your edge cases, and then write out your expected results yourself.

The lab is done when every statement in the [Completion checklist](#completion-checklist) section of this document is true. If you're stuck, see the [Hints](#hints) section.

## Goal

Reward groups. When a customer buys 6 or more tickets in one tier, that tier gets 15% off.

## Starting branch

To start the lab, enter the following command in Claude Code:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1c-group-discount && uv run pytest
```

The command does the following, in order:

1. Switches to the `main` branch, so that the new branch starts from the original code.
2. Resets the database to the seed data.
3. Creates the `lab1c-group-discount` feature branch from `main`.
4. Runs the tests.

Every test passes before you change anything. If the command fails, see [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

The following list describes the code that this feature touches:

- **Pricing**: the `price_order` function in the `app/pricing.py` file builds a price in a fixed order (see the `CLAUDE.md` file): subtotal, discount, service fee, tax, total. The `orders.quote` function merges cart items by tier, so each `pricing.Line` that it passes in is one tier.
- **Promo discount**: the `pricing.discount` function computes a promo discount. Quotes and orders carry a single `discount_cents` today. The `pricing.pricing_lines` function turns a breakdown into the ordered lines (Subtotal, Discount, Service fees, Tax, Total) that quotes and orders return as `pricing_lines`. The web UI's quote and confirmation pages loop over that list, so a line that you add there appears in the UI with no template changes.
- **Quotes and stored orders**: quotes (`Quote`) and stored orders (`Order`, the `orders` table) must show the same numbers. Tests use an in-memory database, but the running app uses a local SQLite file. If you change the schema, [reset the database](01-getting-started.md#reset-the-database), or the web UI breaks even though the tests pass.
- **The `CLAUDE.md` file and the `docs/` folder**: leave them as they are. They still describe a promo-only discount after this change, and that's fine, because they describe the `main` branch and every lab starts from `main`.

For an illustration of the pricing order, see [How a price is built](../docs/architecture.md#3-how-a-price-is-built).

## Acceptance criteria

This lab gives most of the criteria. Before you write tests, add one or two edge cases of your own as criteria 8 and 9.

Every criterion needs at least one test.

1. 6 or more tickets in the same tier get 15% off that tier's subtotal, rounded half up to the cent.
2. 5 tickets get no discount, and exactly 6 do.
3. If a promo code also applies, the customer gets whichever discount is larger. The two discounts never stack.
4. The quote breakdown shows the group discount as its own line: its own field, `group_discount_cents`, and its own entry in `pricing_lines`, labeled exactly `Group discount (15%)`, negative, right after `Subtotal`, and only when it's non-zero.
5. All amounts stay in integer cents, and tax follows the existing pricing order: 9% of the subtotal after the discount that won.
6. The stored order matches the quote, including the group discount line.
7. If the group discount beats a promo, the promo isn't applied: the order doesn't record the promo code, and the promo's use count doesn't go up. The use count is the `uses` column of the `promo_codes` table. No endpoint shows it, so a test reads it from the database.
8. _Your edge case_
9. _Your edge case_ (optional)

Edge cases to think about include ties, the 8-ticket limit, a fixed promo, and which discount the breakdown reports when one loses. No seeded promo can tie, so a tie test needs its own promo, inserted through the `conn` fixture in the `tests/conftest.py` file. When one discount loses, decide what the breakdown shows for it, which makes a good criterion 8 or 9, or accept the existing `Discount` line at $0.00.

The following table shows worked examples, in cents with dollars in parentheses:

| Cart | Subtotal | Discount that wins | Fees | Tax | Total |
| --- | --- | --- | --- | --- | --- |
| 6 GA, no promo | 41400 ($414.00) | group 6210 ($62.10) | 4500 ($45.00) | 3167 ($31.67) | 42857 ($428.57) |
| 6 GA + LOCALS10 | 41400 ($414.00) | group 6210 ($62.10); promo would be 4140 ($41.40) | 4500 ($45.00) | 3167 ($31.67) | 42857 ($428.57) |
| 6 GA + 2 VIP + LOCALS10 | 81398 ($813.98) | promo 8140 ($81.40); group would be 6210 ($62.10) | 6000 ($60.00) | 6593 ($65.93) | 85851 ($858.51) |
| 7 VIP, no promo | 139993 ($1,399.93) | group 20999 ($209.99) | 5250 ($52.50) | 10709 ($107.09) | 134953 ($1,349.53) |

## Workflow

### About the workflow

There are many workflows. Engineers experiment to find what works for them, and the models change fast enough that a practice can stop working within months. You'll probably settle on your own workflow eventually, if you don't have one already. This lab introduces one way to build good software reliably with a coding agent like Claude.

The main takeaway is that there's no single correct way:

- There are practices that help.
- There are practices that hurt.
- There are practices that work in some situations with some models.

The workflow in this lab combines software engineering principles that are decades old with practices that Anthropic and others recommend. Use what works for you, and share your results.

**Note**: People who work with Claude or another coding agent often align on an idea first, have Claude write it into a spec, and create work items such as user stories or issues before steps 2 to 7. This lab has limited time, so it focuses on the coding and review parts of the flow. We recommend that you get experience with the spec step on your own time.

### Workflow overview

The workflow has the following seven steps, and each of steps 1 to 3 starts with a fresh conversation:

1. Find your edge cases, and then write your expected results without Claude.
2. Claude writes failing tests. You check them against your expected results, and then you commit them.
3. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm that only the `app/` folder changed, and try the feature in the web UI.
5. Review the diff.
6. A subagent, a separate Claude that starts with no memory of this conversation, reviews the change. For each real bug, Claude writes a failing test and fixes it, and then you repeat steps 4 and 5.
7. Commit.

For more information about why each step matters, see [How we work](00-how-we-work.md).

### Step 1: Align on what done means

#### 1a: Start a fresh conversation

Start a fresh conversation:

```text
/clear
```

#### 1b: Find your edge cases

This sheet asks for one or two edge cases of your own. Think them through yourself first: what can a customer do that the criteria don't answer? Type your edge cases into the [Acceptance criteria](#acceptance-criteria) section as criteria 8 and 9.

If you're stuck, ask Claude for a hint:

```text
Read tasks/lab1c-group-discount.md and the relevant code. I'm stuck finding edge cases
the criteria don't cover. Give me one hint at a time, as a question, not the
edge case itself. If I say "just tell me", suggest 3 edge cases, one sentence
each, and I'll pick. Don't write any code or change any files.
```

#### 1c: Review the acceptance criteria without Claude

The acceptance criteria are how Claude knows when the feature is complete. Before Claude writes anything, think through exactly what each criterion returns, and write your answers where you can refer to them later, such as a notes app or a text file outside your `showtix` folder, because anything inside the folder gets committed with your tests.

For each criterion in the [Acceptance criteria](#acceptance-criteria) section, write down the exact cents, and the status code and message where a criterion has one. Check that you get the same numbers as the worked examples.

**Note**: Prices, fees, tax rules, and promo codes are in the [`docs/seed-data.md`](../docs/seed-data.md) file. To see the values in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

Start a fresh conversation:

```text
/clear
```

#### 2b: Ask Claude for failing tests

Ask Claude to write a failing test for each criterion:

```text
Read tasks/lab1c-group-discount.md and the relevant code. Write a failing test
for each acceptance criterion. Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

Then check the tests against your expected results, as described in the next step.

#### 2c: Check the tests yourself

Claude's reply is your checklist: one line per test with the criterion it covers, what it expects, and whether it passes today. If the reply doesn't give you that, ask for a table:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the tests. Claude might write more tests than you expect. Check the following items first, and then the rest as time allows:

- **Each expected value matches your step 1 table.** Claude wrote the tests and the summary, so the table that you wrote without Claude is the thing to trust. If you can't find a value there, work it out yourself, or use 2d.
- **Every route or function that a test calls already exists in the `app/` folder.** Calls to the `client.get(...)` and `client.post(...)` methods are the API. A test that calls a function that doesn't exist yet is designing the code for Claude. Use 2d.
- **The four worked examples are tests.** Every line is asserted in exact cents.
- **Your own edge cases have tests too.**

#### 2d: Correct a test that doesn't match

If a test doesn't match your expected results, tell Claude the right value and the reason:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet, ask for a rewrite:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

For example:

```text
The test for criterion 4 expects the label "Group discount", but it should be
"Group discount (15%)" because the label has to match exactly. Fix that test.
```

#### 2e: Commit the tests

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1c: tests"
```

### Step 3: Make the tests pass

#### 3a: Clear the conversation

Claude builds better from the sheet and your committed tests than from the context of the test-writing chat. Start a fresh conversation:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

Ask Claude to write the code:

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab1c-group-discount.md for context. Run the full suite and show me
the output.
```

Claude must not touch any test file. You verified the tests, so the code alone must make them pass, and step 4 checks that.

### Step 4: Check the evidence

Don't take Claude's word for it. Check for yourself.

#### 4a: Run the tests

Run the tests. The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`:

```text
! uv run pytest
```

#### 4b: Check that Claude changed only app code

List the files that changed since the last commit:

```text
! git status --short
```

Every listed file must be under the `app/` folder. A file in the `tests/` folder (changed, or new with `??`), a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask Claude why before you go on. If step 6 adds fixes, the only test changes are the new tests that you asked for, and no existing test changes.

#### 4c: Check the feature in your browser

First, reset the database. Storing the group discount on orders needs a new column, but the app's `showtix.db` file was created before that column existed, so placing or viewing an order fails until you reset.

The tests still pass because each one builds a fresh in-memory database. The reset rebuilds the file with the new column and restores the starting data. In production, you'd run a migration to keep real data, but this is local practice data, so a reset is fine.

Reset the database:

```text
! uv run python -m app.seed
```

Then ask Claude to start the app in the background:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

For more information, see [Start the app](01-getting-started.md#start-the-app).

To check the worked examples in the web UI, follow these steps:

1. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/), and then click a date under **Laugh Lines Live**.
2. In the **Qty** column, enter the tickets for one worked example, such as `6` for **GA**. If the example has a promo, type it in **Promo code**.
3. Click **Get quote**.
4. Compare every line with your expected results.
5. Go back to the date page, and repeat for the other worked examples.
6. For one example, enter any email and click **Place order**. The order page shows the same lines.

To use the API instead, follow these steps:

1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), and then click your endpoint.
2. Click **Try it out**.
3. Enter the values for one worked example, and then click **Execute**.
4. Compare the response with your expected results.

When you're done, stop the app:

```text
Stop the app.
```

#### 4d: Report a mismatch

If something doesn't match, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read every change

Before you accept the changes, read every one. The following command stages the changes and shows the diff between the staged changes and the latest commit on your branch:

```text
! git add -A && git diff --staged
```

Your tests are already committed, so the diff shows only the code that Claude wrote. As you read, ask the following questions:

- Can you explain every change?
- Did anything change that has nothing to do with the group discount?

To see the diff side by side, use the **Source Control** panel in VS Code.

### Step 6: Get a second opinion

#### 6a: Create a code reviewer

Ask Claude to create a reviewer subagent. The subagent hasn't seen your conversation, and it checks the change against this sheet:

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1c-group-discount.md. It hasn't seen our conversation. It should
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

#### 6b: Answer with the numbers to fix

Reply with the numbers of the findings to fix, for example "1 and 3", and then repeat steps 4 and 5. You can also decide not to fix a finding, or discuss it with Claude before you decide. Claude might also list UNSURE or OPTIONAL findings. Those are yours to decide, and the lab doesn't need them. If Claude reports no MUST FIX findings, there's nothing to answer. Repeat steps 4 and 5 once, and then go on to step 7. If Claude asks how to fix something, answer with the behavior that you want and let Claude choose the code.

For more information about why the prompt says not to report style, see [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7: Commit

When you're satisfied with the change, commit it:

```text
! git add -A && git commit -m "lab1c: group discount"
```

## Completion checklist

The lab is complete when the following statements are true:

- [ ] A test exists for each given criterion and for your own edge cases, and all of the tests pass.
- [ ] The tests that you committed in step 2 weren't changed to make them pass.
- [ ] The four worked examples are tests, with every line asserted in exact cents.
- [ ] The quote, the stored order, and the web UI agree on every line.
- [ ] The group discount appears on the web UI's quote and confirmation pages with no template changes.
- [ ] Every test asserts exact values, with exact cents for money, not "smaller" or "not empty".
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] All money math is in the `app/pricing.py` file, in integer cents, with no floats.
- [ ] Routes in the `main.py` and `web.py` files only call into domain modules.
- [ ] You tried the feature by hand in the web UI or the `/docs` page with values that you worked out yourself.
- [ ] You can explain every line of the `git diff main` output, and nothing unrelated changed.

## Hints

If you're stuck, open the [workshop hints page](https://www.notion.so/409be0acdc238156b855d22a8fe01f48). It lists the places where students get stuck in this lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see.
