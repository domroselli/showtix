# Lab 1b: Itemized receipt

- **Tier:** Starter
- **Time:** 50 minutes
- Solo or with a partner

## Start here

**New here?** Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).

**This lab:** a small new endpoint that reads stored money, built with the full workflow.

1. Run the command under [Starting branch](#starting-branch).
2. Read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow) step by step.

**Step 1 is yours:** write out (or think about) your expected results before you ask Claude anything.

**You're done when you can check every box under [Checklist: What Done Means](#checklist-what-done-means).**

**Extra time?** Try the [Optional stretch](#optional-stretch). Stuck? See [Hints](#hints).

## Goal

#### Add `GET /orders/{id}/receipt`: every pricing line of a stored order, matching its stored totals to the cent.

## Starting branch

Copy the command below and run in Claude Code

```text
! git switch main && uv run python -m app.seed && git switch -c lab1b-itemized-receipt && uv run pytest
```

Here's what it does:

1. Switches to `main`, so the new branch starts from the original code
2. Resets the database to the seed data
3. Creates new feature branch `lab1b-itemized-receipt` from `main`
4. Runs the tests

Every test should pass before you change anything.

**Trouble?** See [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

Here is the relevant background about the feature you'll be building:

- **An order stores its money when it's created:** `subtotal_cents`, `discount_cents`, `fees_cents`, `tax_cents`, `total_cents`, plus `promo_code` (null when no promo was used). Each order line stores `unit_price_cents`, the price paid. Tier prices can change later; receipts must not.
- **`orders.get_order()`** in `app/orders.py` already loads an order with its ticket `lines` and its `pricing_lines` (Subtotal, Discount, Service fees, Tax, Total), rebuilt from the stored totals. `shows.show_for_performance()` gives the show title and venue name (`.venue`), and `inventory.availability(conn, performance_id).starts_at` gives the start time.
- **`GET /orders/{id}`** is the UI's confirmation page (HTML, in `app/web.py`). The receipt is a new JSON endpoint next to it.

**For an illustration of how an order is created and stored, see [Quote, order, cancel](../docs/architecture.md#2-quote-order-cancel).**

## Acceptance criteria

In this lab, the full criteria are given below.

**Every criterion needs at least one test.**

1. `GET /orders/{id}/receipt` returns 200 with `order_id`, `status`, `email`, `show_title`, `venue_name`, `starts_at`, `promo_code` and `lines`. `starts_at` uses the same format `GET /shows/{id}` returns.
2. `lines` is a list of `{"label": str, "amount_cents": int}` in this order: one line per tier bought, labelled like `2 × Premium` (the × sign, U+00D7, not the letter x); then `Subtotal`, `Discount`, `Service fees`, `Tax`, `Total`.
3. The discount line is negative. Its label names the promo when one was used (`Discount (LOCALS10)`); with no promo, it's `Discount` with amount 0.
4. Every amount comes from the stored order, not from recalculating. 2 Premium with LOCALS10 gives: `2 × Premium` 24000, `Subtotal` 24000, `Discount (LOCALS10)` -2400, `Service fees` 1500, `Tax` 1944, `Total` 25044.
5. The tier lines add up to `Subtotal`, and `Subtotal + Discount + Service fees + Tax` equals `Total`.
6. If the tier's price changes after the order, the receipt still shows the price paid.
7. A cancelled order still has a receipt, with `status` `cancelled`.
8. An unknown order id returns 404 with the detail `Order 99999 not found` (for id 99999), the message `orders.get_order()` already raises.

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

1. Start a fresh conversation. Write your expected results (no Claude yet).
2. Start a fresh conversation. Claude writes failing tests. You check them against your expected results, then commit.
3. Start a fresh conversation. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm only app/ changed, try it in the browser.
5. Review the diff.
6. A subagent reviews the change. For each real bug, Claude writes a failing test and fixes it, then you repeat steps 4 and 5.
7. Commit.

Why each step matters: [How we work](00-how-we-work.md).

### Step 1. Alignment on what "done" means (no Claude yet)

#### 1a. Start with a fresh conversation

```text
/clear
```

#### 1b. Review the acceptance criteria

This is how Claude knows when the feature is complete. Think through exactly what each criterion should return before Claude writes anything.  
Make a note of this somewhere to refer to later (like notes, notepad, or an empty text file. Whatever works for you).

**Go through [Acceptance criteria](#acceptance-criteria) one by one:** which status code, which fields, which labels, the exact cents.

**Work out criterion 4's example yourself** and check you get the same numbers.

**Note:**

- Prices, fees and tax rules are in [`docs/seed-data.md`](../docs/seed-data.md) for your convenience.
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

### Step 2. Implement tests first

#### 2a. Start with a fresh conversation

```text
/clear
```

#### 2b. Have Claude write failing tests. Check them against your expected results

```text
Read tasks/lab1b-itemized-receipt.md and the relevant code. Write a failing
test for each acceptance criterion. Test behavior through the API, the pages,
or functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

#### 2c. Manually check the tests Claude just created

- **Compare each test with your expected results from step 1.**
- **Tests must check behavior through the API or the page**, **<ins>not functions that don't exist yet</ins>**.   
A test that calls a new function is designing the code for Claude.
- **Criterion 8 must fail for the right reason.** Before the route exists, every receipt request returns FastAPI's generic `{"detail":"Not Found"}`.   
A test that checks only the 404 would pass already and prove nothing. One that checks the exact detail fails until your route is in place.
- **Criterion 6's test changes the tier's price *after* placing the order**, then checks the receipt still shows the old price.   
A test that never changes the price proves nothing.
- **Criterion 4's test changes every stored total,** so they no longer match today's prices, fees or tax and no longer add up. It then checks the receipt shows them anyway.   
This stands in for an order placed under older rules. Criterion 6 can't do this job: it only changes a tier price, so code that redoes the math from the price paid still passes.

#### 2d. If a test doesn't match your expected results, tell Claude what it should be and why

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

**Example:**

```text
The test for criterion 3 expects the no-promo line to be labelled "Discount
(none)", but it should be "Discount" with amount 0 because no promo was used.
Fix that test.
```

#### 2e. Commit the test code

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "lab1b: tests"
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
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab1b-itemized-receipt.md for context. Run the full suite and show
me the output.
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
Every file this lists should be under `app/`:

```text
! git status --short
```

A file in `tests/` (changed, or new with `??`), a `conftest.py`, or `pyproject.toml` means Claude touched your tests or how they run: ask why before going on. If there are any fixes in step 6, the only test changes should be the new tests you asked for. Nothing existing should be modified.

#### 4c. Visual tests in the browser

Try it yourself: follow [Check it in your browser](#check-it-in-your-browser) below.

#### 4d. Something doesn't match?

Tell Claude which criterion failed and what you saw.

### Step 5. Review the diff

#### 5a. Read every change Claude made before you accept it

These commands stage the changes and then show the diff between these staged changes and the latest commit on your branch.

```text
! git add -A && git diff --staged
```

- Can you explain every change?
- Was anything touched that has nothing to do with receipts?
- Prefer side by side? Use VS Code's **Source Control** panel.

Your tests are already committed, so this shows only the code Claude wrote.

### Step 6. Get a second opinion

#### 6a. Create a code reviewer for your changes

Ask Claude to create a reviewer subagent. It hasn't seen your conversation, and it checks the change against this sheet.

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

Claude shows the MUST FIX findings and asks which to fix. The labels are the reviewer's opinion, so check the evidence yourself before you answer.

#### 6b. Answer with the numbers you want fixed

For example "1 and 3". Then repeat steps 4 and 5.   
Or you can decide you don't want to fix it, or you want to have a chat with Claude about it before you decide.

Why "don't report style"? See [step 6 of How we work](00-how-we-work.md#6-get-a-second-opinion).

### Step 7. Commit

Commit when you're satisfied with the change:

```text
! git add -A && git commit -m "lab1b: itemized receipt"
```

### Finished with time to spare?

Try the [Optional stretch](#optional-stretch) below.

## Check it in your browser

Use this for step 4c of the workflow.

You'll place a real order in the app, then look at its receipt. Compare what you see with your expected results.

### 1. Start the app

Ask Claude to start the app in the background ([more on starting the app](01-getting-started.md#start-the-app)):

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

Wait until Claude says it's ready, then keep working in the same conversation.

### 2. Place the worked-example order

1. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and click any date under any show.

   <img src="img/lab1b-1-pick-a-date.png" alt="Click any date under any show" width="450">

2. In the **Qty** column, enter `2` for **Premium**. Type `LOCALS10` in **Promo code** and click **Get quote**.

   <img src="img/lab1b-2-quote-form.png" alt="2 Premium, promo code LOCALS10, then Get quote" width="600">

3. Check the quote: Subtotal $240.00, Discount (LOCALS10) −$24.00, Service fees $15.00, Tax $19.44, Total $250.44. Enter any email and click **Place order**.

   <img src="img/lab1b-3-quote-and-place-order.png" alt="The quote totals $250.44; enter an email, then Place order" width="600">

4. The confirmation page's heading shows your order number, for example **Order 4: paid**. The seed data already has 3 orders, so yours won't be 1. Write it down.

   <img src="img/lab1b-4-confirmation.png" alt="The order number is in the heading" width="600">

### 3. Open the receipt (criteria 1–5)

Open [http://127.0.0.1:8000/orders/4/receipt](http://127.0.0.1:8000/orders/4/receipt), using your order number. In Chrome or Edge, tick **Pretty-print**; it then looks like this (the show and time depend on which date you picked):

<img src="img/lab1b-5-receipt.png" alt="The receipt for the worked-example order" width="450">

| Criterion | You should see |
| --- | --- |
| 1 | `order_id`, `status` (`paid`), `email`, `show_title`, `venue_name`, `starts_at`, `promo_code` (`LOCALS10`) and `lines`. `starts_at` has the same format as in [http://127.0.0.1:8000/shows/1](http://127.0.0.1:8000/shows/1) |
| 2, 4 | `lines` in this order: `2 × Premium` 24000, `Subtotal` 24000, `Discount (LOCALS10)` -2400, `Service fees` 1500, `Tax` 1944, `Total` 25044 |
| 3 | The discount is negative and names the promo. Place a second order with no promo code: its receipt shows `Discount` with amount 0 |
| 5 | 24000 = 24000, and 24000 − 2400 + 1500 + 1944 = 25044 |

Criterion 6 (the price changes after the order) needs a database change, so your test is the check. You don't need to try it by hand.

### 4. Cancel the order (criterion 7)

1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and click **POST /orders/{order_id}/cancel**. Click **Try it out**, enter your order number in **order_id**, and click **Execute**.

   <img src="img/lab1b-6-cancel-execute.png" alt="Try it out on the cancel endpoint, with your order number" width="600">

2. Scroll down to **Server response**. The code is **200**.

   <img src="img/lab1b-7-cancel-200.png" alt="Code 200" width="600">

3. Reload your receipt. `status` is now `cancelled`, and every amount is unchanged.

   <img src="img/lab1b-8-receipt-cancelled.png" alt="The same receipt, now cancelled" width="450">

### 5. An unknown order (criterion 8)

Open [http://127.0.0.1:8000/orders/99999/receipt](http://127.0.0.1:8000/orders/99999/receipt). You should see the detail `Order 99999 not found`. If you see `{"detail":"Not Found"}` instead, the receipt route doesn't exist: that's the 404 you got before building anything.

<img src="img/lab1b-9-unknown-order.png" alt="Order 99999 not found" width="600">

**Something doesn't match?** Don't fix it by hand. Tell Claude which criterion failed and what you saw.

### 6. Stop the app

When you're done checking:

```text
Stop the app.
```

Other ways to stop it, and what "address already in use" means: [Stop the app](01-getting-started.md#stop-the-app).

## Checklist: What Done Means

- [ ] A test for each of the 8 criteria, all passing
- [ ] The tests you committed in step 2 weren't changed to make them pass
- [ ] The receipt never recalculates a price; it only reads stored values
- [ ] Every test asserts exact values (exact cents for money), not "smaller" or "not empty"
- [ ] `uv run pytest` is fully green and still finishes in under 5 seconds
- [ ] All money math is in `app/pricing.py`, in integer cents; no floats
- [ ] Routes in `main.py` and `web.py` only call into domain modules
- [ ] You tried it by hand in /docs with values you worked out yourself
- [ ] You can explain every line of `git diff main`, and nothing unrelated changed

## Optional stretch

Finished early? Pick one:

- **A "View receipt" link** on the order confirmation page that opens `/orders/{id}/receipt`. Add a test that the confirmation page contains the link.
- **Keep the tier's *name* at purchase,** not just its price. Today, renaming a tier changes the name on old receipts. Write a failing test first. This needs a new column on `order_lines`, so [reset the local database](01-getting-started.md#reset-the-database) afterwards:

  ```text
  ! uv run python -m app.seed
  ```

Either one goes through the same workflow, starting at step 2.

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc23810383b1dd968c3eeccc). Open one level at a time.
