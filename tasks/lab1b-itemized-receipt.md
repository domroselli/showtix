# Lab 1b: Itemized receipt

- **Tier**: Starter
- **Time**: 50 minutes
- **Format**: solo or with a partner

## Start here

If this is your first lab, read [Getting started](01-getting-started.md) for how to run commands and the app, and then read [How we work](00-how-we-work.md) for the workflow. Together they take about 5 minutes.

In this lab, you use the full workflow to build a small endpoint that reads stored money.

To run this lab, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Run the command in the [Starting branch](#starting-branch) section of this document.
3. Read the [Goal](#goal), [Background](#background), and [Acceptance criteria](#acceptance-criteria) sections.
4. Follow the [Workflow](#workflow) section step by step.

Step 1 is yours: write out, or think through, your expected results before you ask Claude anything.

You're done when you can check every box in the [Completion checklist](#completion-checklist) section of this document. If you have extra time, try the [Optional stretch](#optional-stretch). If you're stuck, see the [Hints](#hints) section.

## Goal

Add the `GET /orders/{id}/receipt` endpoint. The receipt returns every pricing line of a stored order, and the lines match the order's stored totals to the cent.

## Starting branch

To start the lab, enter the following command in Claude Code:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1b-itemized-receipt && uv run pytest
```

The command does the following, in order:

1. Switches to the `main` branch, so that the new branch starts from the original code.
2. Resets the database to the seed data.
3. Creates the `lab1b-itemized-receipt` feature branch from `main`.
4. Runs the tests.

Every test must pass before you change anything.

If the command fails, see [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

The following list describes the code that the feature builds on:

- **Stored money**: an order stores its money when it's created: `subtotal_cents`, `discount_cents`, `fees_cents`, `tax_cents`, `total_cents`, and `promo_code`, which is null when no promo was used. Each order line stores `unit_price_cents`, the price paid. Tier prices can change later. Receipts must not change.
- **Existing functions**: the `orders.get_order()` function in the `app/orders.py` file loads an order with its ticket `lines` and its `pricing_lines` (Subtotal, Discount, Service fees, Tax, Total), rebuilt from the stored totals. The `shows.show_for_performance()` function gives the show title and the venue name in its `.venue` attribute, and `inventory.availability(conn, performance_id).starts_at` gives the start time.
- **Confirmation page**: the `GET /orders/{id}` route is the UI's confirmation page, which is HTML in the `app/web.py` file. The receipt is a new JSON endpoint next to it.

For an illustration of how an order is created and stored, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).

## Acceptance criteria

This lab gives you the full criteria. Every criterion needs at least one test.

1. The `GET /orders/{id}/receipt` endpoint returns an HTTP `200 OK` status code and a JSON body with `order_id`, `status`, `email`, `show_title`, `venue_name`, `starts_at`, `promo_code`, and `lines`. `starts_at` uses the same format that `GET /shows/{id}` returns, for example `2026-11-10T19:00:00` for The Vanishing Ace on November 10.
2. The `lines` field is a list of `{"label": str, "amount_cents": int}` in this order: one line per tier bought, labeled like `2 × Premium` (the × sign, U+00D7, not the letter x), and then `Subtotal`, `Discount`, `Service fees`, `Tax`, and `Total`.
3. The discount line is negative. Its label names the promo when one was used (`Discount (LOCALS10)`). With no promo, the label is `Discount` with an amount of 0.
4. Every amount comes from the stored order, not from a recalculation. 2 Premium with LOCALS10 gives: `2 × Premium` 24000 ($240.00), `Subtotal` 24000 ($240.00), `Discount (LOCALS10)` -2400 (-$24.00), `Service fees` 1500 ($15.00), `Tax` 1944 ($19.44), `Total` 25044 ($250.44).
5. The tier lines add up to `Subtotal`, and `Subtotal + Discount + Service fees + Tax` equals `Total`.
6. If the tier's price changes after the order, the receipt still shows the price paid.
7. A cancelled order still has a receipt, with a `status` of `cancelled`.
8. An unknown order ID returns an HTTP `404 Not Found` status code with the detail `Order 99999 not found` (for ID 99999), which is the message that `orders.get_order()` already raises.

## Workflow

### About the workflow

There are many workflows for working with a coding agent.

Engineers are still experimenting and finding what works for them. The models change so fast that what works well can be discarded within months, or within weeks. You'll probably develop your own workflow, or you have one already. This lab introduces one way to build reliable software with a coding agent like Claude.

The main point is that there's no single correct way yet:

- Some practices help.
- Some practices hurt.
- Some practices work only in certain situations, or only with certain models.

The workflow in this lab combines software engineering principles that have been in use for decades with the practices that Anthropic and others recommend.

Use what works for you, and share your results.

**Note**: People who work with Claude or another coding agent often agree on an idea first, have the agent write that idea into a spec, and create work items such as user stories or issues for the agent to work on before steps 2 to 7. This lab has limited time, so it focuses on the coding and review parts of the flow. We recommend that you practice the spec and work-item parts on your own time.

### Workflow overview

The workflow has seven steps:

1. Write your expected results, without Claude.
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, and then you commit them.
3. Start a fresh conversation. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm that only `app/` changed, and try the feature in your browser.
5. Review the diff.
6. A subagent, a separate Claude that starts with no memory of this conversation, reviews the change. For each real bug, Claude writes a failing test and fixes it, and then you repeat steps 4 and 5.
7. Commit.

For more information about why each step matters, see [How we work](00-how-we-work.md).

### Step 1: Align on what done means, without Claude

#### 1a: Review the acceptance criteria

The acceptance criteria are how Claude knows when the feature is complete. Before Claude writes anything, work out exactly what each criterion returns, and write the results down somewhere that you can refer to later, such as a notes app or a text file outside your `showtix` folder. Anything inside the folder gets committed with your tests.

To write your expected results, follow these steps:

1. Go through the [Acceptance criteria](#acceptance-criteria) one by one, and write down the status code, the fields, the labels, and the exact cents for each.
2. Work out criterion 4's example yourself, and check that you get the same numbers.

Prices, fees, and tax rules are in the [seed data](../docs/seed-data.md) document. To see the values in the running app, see [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs). You can ask Claude to start the app. Claude doesn't write your expected values.

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

```text
/clear
```

#### 2b: Ask Claude for failing tests

Ask Claude to write a failing test for each criterion, and then check the tests against your expected results:

```text
Read tasks/lab1b-itemized-receipt.md and the relevant code. Write a failing
test for each acceptance criterion. Test behavior through the API, the pages,
or functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

#### 2c: Check the tests yourself

Claude's reply is your checklist: one line per test with the criterion that it covers, what it expects, and whether it passes today. If the reply doesn't give you that, ask for it:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the following:

- **Expected values**: each expected value matches your step 1 table. Claude wrote the tests and the summary, so the table that you wrote without Claude is the one to trust. If you can't find a value in your table, work it out yourself or use 2d.
- **Existing routes and functions**: every route or function that a test calls already exists in `app/`. The `client.get(...)` and `client.post(...)` calls are the API. A test that calls a function that doesn't exist yet designs the code for Claude. Use 2d.
- **Criterion 8**: the test must fail for the right reason. Before the route exists, every receipt request returns FastAPI's generic `{"detail":"Not Found"}`. A test that checks only the 404 passes already and proves nothing. A test that checks the exact detail fails until your route is in place.
- **Criterion 6**: the test must change the tier's price after it places the order, and then check that the receipt still shows the old price. A test that never changes the price proves nothing.
- **Criterion 4**: the test must change every stored total, so that the totals no longer match today's prices, fees, or tax and no longer add up. It then checks that the receipt shows them anyway. This stands in for an order placed under older rules. Criterion 6 can't do this job, because it changes only a tier price, so code that redoes the math from the price paid still passes.

#### 2d: Correct a test that doesn't match

If a test doesn't match your expected results, tell Claude what the test must expect and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet, ask for a rewrite:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

The following example corrects a label:

```text
The test for criterion 3 expects the no-promo line to be labelled "Discount
(none)", but it should be "Discount" with amount 0 because no promo was used.
Fix that test.
```

#### 2e: Commit the tests

When every test matches your expected results, commit the tests:

```text
! git add -A && git commit -m "lab1b: tests"
```

### Step 3: Make the tests pass

#### 3a: Clear the conversation

Claude builds from the sheet and your committed tests, not from the context of the test-writing chat:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab1b-itemized-receipt.md for context. Run the full suite and show
me the output.
```

Claude must not touch any test file. You already verified the tests, so the code alone makes them pass. Step 4 checks that.

### Step 4: Check the evidence

Don't take Claude's word for it. Check for yourself.

#### 4a: Run the tests

The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`:

```text
! uv run pytest
```

#### 4b: Check that only app code changed

List the files that changed since the last commit. Every file in the list must be under `app/`:

```text
! git status --short
```

A file in `tests/`, either changed or new with `??`, a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask why before you go on. If step 6 adds fixes, the only test changes are the new tests that you asked for, and no existing test changes.

#### 4c: Check the feature in your browser

Follow the [Check it in your browser](#check-it-in-your-browser) section of this document.

#### 4d: Report a mismatch

If something doesn't match, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read every change before you accept it

Stage the changes and show the diff between the staged changes and the last commit on your branch:

```text
! git add -A && git diff --staged
```

Your tests are already committed, so the diff shows only the code that Claude wrote. Your changes stay staged. That's expected, and step 7 commits them. As you read, ask yourself the following questions:

- Can you explain every change?
- Did anything change that has nothing to do with receipts?

To read the diff side by side, use the **Source Control** panel in VS Code.

### Step 6: Get a second opinion

#### 6a: Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. The subagent hasn't seen your conversation, and it checks the change against this sheet:

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1b-itemized-receipt.md. It hasn't seen our conversation. It should
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

Reply with the numbers of the findings that you want fixed, for example "1 and 3", and then repeat steps 4 and 5. You can also decide not to fix a finding, or discuss it with Claude before you decide. If Claude asks how to fix something, answer with the behavior that you want and let Claude choose the code. Claude might also list UNSURE or OPTIONAL findings. Those are yours to decide, and the lab doesn't need them.

If Claude reports no MUST FIX findings, there's nothing to answer. Repeat steps 4 and 5 once, and then go on to step 7.

For more information about why the prompt says "don't report style", see [Get a second opinion](00-how-we-work.md#6-get-a-second-opinion).

### Step 7: Commit

When you're satisfied with the change, commit it:

```text
! git add -A && git commit -m "lab1b: itemized receipt"
```

If you finish with time to spare, try the [Optional stretch](#optional-stretch) section of this document.

## Check it in your browser

Use this section during [4c: Check the feature in your browser](#4c-check-the-feature-in-your-browser).

You place a real order in the app, and then you look at its receipt. Compare what you see with your expected results.

### Start the app

Ask Claude to start the app in the background:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

Wait until Claude says that the app is ready, and then keep working in the same conversation. For more information, see [Start the app](01-getting-started.md#start-the-app).

### Place the worked-example order

To place the order from criterion 4, follow these steps:

1. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and click any date under any show.

   <img src="img/lab1b-1-pick-a-date.png" alt="Click any date under any show" width="450">

2. In the **Qty** column, enter `2` for **Premium**. In **Promo code**, type `LOCALS10`, and then click **Get quote**.

   <img src="img/lab1b-2-quote-form.png" alt="2 Premium, promo code LOCALS10, then Get quote" width="600">

3. Check the quote: Subtotal $240.00, Discount (LOCALS10) −$24.00, Service fees $15.00, Tax $19.44, Total $250.44.

   <img src="img/lab1b-3-quote-and-place-order.png" alt="The quote totals $250.44; enter an email, then Place order" width="600">

4. Enter any email, and then click **Place order**.
5. Write down your order number. The confirmation page's heading shows it, for example **Order 4: paid**. The seed data already has three orders, so your order isn't number 1.

   <img src="img/lab1b-4-confirmation.png" alt="The order number is in the heading" width="600">

### Open the receipt (criteria 1 to 5)

Open [http://127.0.0.1:8000/orders/4/receipt](http://127.0.0.1:8000/orders/4/receipt), with your order number in place of 4. In Chrome or Edge, select **Pretty-print** to make the result easier to read. Firefox formats the result on its own. In Safari, read the raw text or use the `/docs` page. The receipt then looks like the following image, with the show and time that match the date you picked:

<img src="img/lab1b-5-receipt.png" alt="The receipt for the worked-example order" width="450">

The following table lists what the receipt shows for each criterion.

| Criterion | What you see |
| --- | --- |
| 1 | `order_id`, `status` (`paid`), `email`, `show_title`, `venue_name`, `starts_at`, `promo_code` (`LOCALS10`), and `lines`. `starts_at` has the same format as in [http://127.0.0.1:8000/shows/1](http://127.0.0.1:8000/shows/1) |
| 2, 4 | `lines` in this order: `2 × Premium` 24000 ($240.00), `Subtotal` 24000 ($240.00), `Discount (LOCALS10)` -2400 (-$24.00), `Service fees` 1500 ($15.00), `Tax` 1944 ($19.44), `Total` 25044 ($250.44) |
| 3 | The discount is negative and names the promo. Place a second order with no promo code: its receipt shows `Discount` with an amount of 0 |
| 5 | 24000 = 24000, and 24000 − 2400 + 1500 + 1944 = 25044 ($250.44) |

Criterion 6, where the price changes after the order, needs a database change, so your test is the check. You don't need to try it by hand.

### Cancel the order (criterion 7)

To cancel the order and check its receipt, follow these steps:

1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and click **POST /orders/{order_id}/cancel**.
2. Click **Try it out**, enter your order number in **order_id**, and then click **Execute**.

   <img src="img/lab1b-6-cancel-execute.png" alt="Try it out on the cancel endpoint, with your order number" width="600">

3. Scroll down to **Server response**. The code is `200`.

   <img src="img/lab1b-7-cancel-200.png" alt="Code 200" width="600">

4. Reload your receipt. The `status` field is now `cancelled`, and every amount is unchanged.

   <img src="img/lab1b-8-receipt-cancelled.png" alt="The same receipt, now cancelled" width="450">

### Request an unknown order (criterion 8)

Open [http://127.0.0.1:8000/orders/99999/receipt](http://127.0.0.1:8000/orders/99999/receipt). The page shows the detail `Order 99999 not found`. If it shows `{"detail":"Not Found"}` instead, the receipt route doesn't exist. That's the 404 that you got before you built anything.

<img src="img/lab1b-9-unknown-order.png" alt="Order 99999 not found" width="600">

If something doesn't match, don't fix it by hand. Tell Claude which criterion failed and what you saw.

### Stop the app

When you're done checking, ask Claude to stop the app:

```text
Stop the app.
```

For other ways to stop the app, and what "address already in use" means, see [Stop the app](01-getting-started.md#stop-the-app).

Then go back to [4d: Report a mismatch](#4d-report-a-mismatch) and continue with [Step 5: Review the diff](#step-5-review-the-diff).

## Completion checklist

The lab is complete when the following statements are true:

- [ ] Each of the eight criteria has a test, and every test passes.
- [ ] The tests that you committed in step 2 weren't changed to make them pass.
- [ ] The receipt never recalculates a price. It only reads stored values.
- [ ] Every test asserts exact values, with exact cents for money, not "smaller" or "not empty".
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] All money math is in the `app/pricing.py` file, in integer cents, with no floats.
- [ ] Routes in the `main.py` file only call into domain modules.
- [ ] You tried the feature by hand in the browser, with values that you worked out yourself.
- [ ] You can explain every line of the `git diff main` output, and nothing unrelated changed.

## Optional stretch

If you finish early, pick one of the following extensions:

- **View receipt link**: add a "View receipt" link on the order confirmation page that opens the `/orders/{id}/receipt` endpoint. Add a test that checks that the confirmation page contains the link.
- **Tier name at purchase**: keep the tier's name at purchase time, not only its price. Without it, renaming a tier changes the name on old receipts. Write a failing test first. This change needs a new column on the `order_lines` table, so [reset the local database](01-getting-started.md#reset-the-database) afterwards:

  ```text
  ! uv run python -m app.seed
  ```

Either extension goes through the same workflow, starting at step 2.

## Hints

If you're stuck, open the [workshop hints page](https://www.notion.so/409be0acdc23810383b1dd968c3eeccc). It lists the places where students get stuck in this lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see.
