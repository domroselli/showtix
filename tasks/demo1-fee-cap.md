# Demo 1: Cap the service fees

This sheet is for the instructor, who follows it on screen during the demo. Attendees watch along to see the seven steps that Lab 1 uses.

- **Tier**: Instructor demo (before Lab 1)
- **Time**: 10 minutes

## Start here

This sheet has the same structure as every Lab 1 sheet, so attendees have seen the shape before they open their own. The feature isn't one of the Lab 1 options, so the demo spoils nothing. The prompts match the Lab 1 prompts, with three extra sentences in the step 2b prompt: don't change app values, update old tests and name them, and pick the simplest answer where the sheet is open. This feature changes a rule that an existing test asserts, and the Lab 1 features add behavior, so the Lab 1 sheets don't need those sentences.

To run this demo, follow these steps:

1. Type `/clear` in Claude Code to start a fresh conversation.
2. Read the [Goal](#goal) section.
3. Run the command in the [Starting branch](#starting-branch) section of this document.
4. Read the [Background](#background) and [Acceptance criteria](#acceptance-criteria) sections.
5. Follow the [Workflow](#workflow) section.

Step 1 has no Claude in it. Work out the expected results before you ask Claude anything. In the demo, the expected results are on a slide. Have that slide open before you run the starting command.

The demo is complete when every item in the [Completion checklist](#completion-checklist) section of this document is true.

## Goal

Cap the service fees at 3000 cents ($30.00) per order. Under the cap, fees stay 750 cents ($7.50) per ticket.

## Starting branch

To prepare the demo, enter the following command in Claude Code:

```text
! git switch main && uv run python -m app.seed && git switch -c demo1-fee-cap && uv run pytest
```

The command does the following, in order:

1. Switches to the `main` branch, so the new branch starts from the original code.
2. Resets the database to the seed data.
3. Creates the `demo1-fee-cap` feature branch from the `main` branch.
4. Runs the tests.

Every test passes before you change anything.

## Background

The following list describes the code that this feature changes:

- **Money math**: all money math is in the `app/pricing.py` file. The `service_fees(ticket_count)` function returns 750 cents per ticket, and the `price_order()` function assembles the subtotal, discount, fees, tax, and total in the order that the `CLAUDE.md` file describes.
- **Seed data**: a GA ticket is 6900 cents ($69.00). Tax is 9% of the discounted ticket subtotal only, never of fees. The `docs/seed-data.md` file has all of the seed data.
- **Two traps**: Claude might cap the total instead of the fees, or put the cap outside the `app/pricing.py` file. Step 3b lists the mistakes to watch for.
- **The rule that changes**: on the `main` branch, the fee is 750 cents ($7.50) per ticket with no limit, and this sheet changes that rule. The app never re-prices a stored order, so orders already placed keep what was charged, with no new code or test.
- **Docs**: the `CLAUDE.md` file, module docstrings, and code comments describe the rule that this sheet changes. Update them in step 3 with the code, not in step 2. Leave the `docs/` directory as it is. It describes the `main` branch, which every lab starts from.

For an illustration of where pricing sits in the app, see [Architecture](../docs/architecture.md).

## Acceptance criteria

This demo gives the full criteria, so there's nothing left to decide. Every criterion needs at least one test:

1. Service fees on an order are `min(750 × tickets, 3000)` cents. The cap applies to the order's fee total, not to a ticket count.
2. `POST /orders/quote` for 3 GA returns fees 2250 ($22.50), tax 1863 ($18.63), and total 24813 ($248.13). This result is the same as on the `main` branch.
3. `POST /orders/quote` for 4 GA returns fees 3000 ($30.00), tax 2484 ($24.84), and total 33084 ($330.84). This order is exactly at the cap, and the result is the same as on the `main` branch.
4. `POST /orders/quote` for 8 GA returns fees 3000 ($30.00), tax 4968 ($49.68), and total 63168 ($631.68). The `main` branch returns fees 6000 ($60.00) and total 66168 ($661.68).
5. Tax doesn't change. It's still 9% of the discounted ticket subtotal, never of fees.

The following table gives the worked examples, in cents with dollars in parentheses:

| Order | Subtotal | Fees on `main` | Fees with cap | Tax | Total with cap |
| --- | --- | --- | --- | --- | --- |
| 3 GA | 20700 ($207.00) | 2250 ($22.50) | 2250 ($22.50), under cap | 1863 ($18.63) | 24813 ($248.13), unchanged |
| 4 GA | 27600 ($276.00) | 3000 ($30.00) | 3000 ($30.00), exactly at cap | 2484 ($24.84) | 33084 ($330.84), unchanged |
| 8 GA | 55200 ($552.00) | 6000 ($60.00) | 3000 ($30.00), capped | 4968 ($49.68) | 63168 ($631.68), was 66168 ($661.68) |
| 5 Premium | 60000 ($600.00) | 3750 ($37.50) | 3000 ($30.00) | 5400 ($54.00) | 68400 ($684.00), was 69150 ($691.50) |

## Workflow

The demo has the following seven steps:

1. Write your expected results, without Claude.
2. Start a fresh conversation. Claude writes failing tests, you check them against your expected results, and then you commit them.
3. Start a fresh conversation. Claude makes the tests pass without changing them.
4. Check the evidence: run the tests, confirm that only the `app/` directory changed, and try the feature on the `/docs` page.
5. Review the diff.
6. A subagent (a separate Claude that starts with no memory of this conversation) reviews the change. The demo names this step but doesn't run it, because it takes two or three minutes.
7. Commit.

For more information about why each step matters, see [How we work](00-how-we-work.md).

### Step 1: Align on what done means

This step has no Claude in it.

#### 1a: Review the acceptance criteria

Work out exactly what each criterion returns before Claude writes anything. In the demo, the worked-examples table is on a slide. In a lab, attendees write the table themselves.

Point out the following two points:

- Tax doesn't change. Only the fees line changes. "Cap the fees" is often misread as "cap the total."
- A rule change can leave old tests behind. You don't need to know which ones. In step 2, Claude finds and updates them, and you check its old and new answers against the table.

### Step 2: Write the tests first

#### 2a: Start a fresh conversation

Start a new conversation:

```text
/clear
```

#### 2b: Ask Claude for failing tests

Ask Claude to write a failing test for each criterion:

```text
Read tasks/demo1-fee-cap.md and the relevant code. Write a failing test for
each acceptance criterion. Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML, and don't change
app values to set up a scenario. Also update any existing test that still
asserts the old rule, including tests of helper functions, and tell me which
ones. Where the sheet leaves a detail open, pick the simplest answer. Don't
change anything in app/. Run the tests and show me which ones fail.
```

Then check the tests against your expected results.

#### 2c: Check the tests that Claude created

Claude's reply is your checklist: one line per test with the criterion that it covers, the value that it expects, and whether it passes before your change. If the reply doesn't give you that list, ask for it:

```text
For each new or updated test, give me one table: the criterion it covers, the
route or app function it calls and whether that already exists in app/, the
exact value it expects, the values that failed, and pass or fail right now.
```

Then check the following items:

- **Expected values match the worked examples.** Check exact cents: 2250, 3000, and 3000 for fees; 1863, 2484, and 4968 for tax; 24813, 33084, and 63168 for totals; and 68400 for 5 Premium. For a case that Claude invented, such as a promo order or a mixed-tier order, work out the discounted subtotal, fees of `min(750 × tickets, 3000)`, tax of 9% of the discounted subtotal, and the total.
- **Every route or function that a test calls exists in the `app/` directory.** The `client.get(...)` and `client.post(...)` calls are the API. A test that calls a function that doesn't exist yet designs the code for Claude. For that test, use step 2d.
- **Claude names the existing tests that it updated.** Expect two: the fee helper test (8 tickets, 6000 to 3000 cents) and the 5 Premium total (69150 to 68400 cents). In step 2 or step 3, Claude might ask whether the cap must be inside the `service_fees()` function. The answer is yes, because anyone who calls that helper must get the real fee.
- **Criteria 2 and 3 pass before you build anything.** This result is expected. These tests guard behavior that your change must not break. Criterion 4 and both updated tests must fail.
- **At least one test fails.** If every test passes, a test is wrong.
- **Claude changed only test files.** If Claude updated the `CLAUDE.md` file or a docstring, ask it to revert that change. The rule text moves with the code in step 3.

#### 2d: Correct a test that doesn't match your expected results

If a test expects the wrong value, tell Claude what the value is and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

If a test calls a function that doesn't exist yet, ask Claude to rewrite it:

```text
The test ___ calls ___, which doesn't exist yet. Rewrite it to check the same
behavior through the API or the page.
```

#### 2e: Commit the tests

When every test matches your expected results, commit them:

```text
! git add -A && git commit -m "demo1: fee cap tests"
```

Committed tests are tamper-evident. If Claude loosens one later, the diff shows the change.

### Step 3: Make the tests pass

#### 3a: Clear the conversation

Start a new conversation:

```text
/clear
```

#### 3b: Ask Claude to make the tests pass

Ask Claude to write the code:

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/demo1-fee-cap.md for context. Run the full suite and show me the
output.
```

Claude must not touch any test file.

Watch for the following mistakes:

- **A cap on the total, or on fees plus tax.** The example in [When Claude gets something wrong](00-how-we-work.md#when-claude-gets-something-wrong) is this exact feature.
- **A cap in the `price_order()` function that leaves the `service_fees()` function uncapped.** The updated helper test catches this mistake. The function that computes the fee must give the real fee.
- **Money math outside the `app/pricing.py` file, or a float anywhere.** The rules in the `CLAUDE.md` file forbid both.
- **A ticket-count threshold, such as `if tickets >= 4`.** The 4 is a consequence of 750 × 4 = 3000, not a rule. If the fee changes, the threshold moves, and `min()` doesn't depend on it.

Claude usually ends by asking whether to update the `CLAUDE.md` file, the README, and the docs, which still describe the uncapped fee. Answer as follows:

```text
Yes: update CLAUDE.md, README.md, the pricing.py docstring and any comment
that states the old fee. Leave docs/ alone.
```

The `CLAUDE.md` file is where the rule lives for every future session, so it moves with the code. The `docs/` directory describes the `main` branch and stays as it is on a lab branch. If Claude already updated these files and told you, skip the answer and say so. If it changed the `docs/` directory, ask it to revert that directory.

### Step 4: Check the evidence

Don't take Claude's word for it. Check for yourself.

#### 4a: Run the tests

Run the full suite:

```text
! uv run pytest
```

The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`.

#### 4b: Check that Claude changed only app code

List the changed files:

```text
! git status --short
```

Every file in the list must be under the `app/` directory. The `CLAUDE.md` and `README.md` files can also appear, if Claude updated the rule text with the code. A file in the `tests/` directory means that Claude touched your tests after you committed them. Ask why.

#### 4c: Try the feature on the /docs page

Follow the [Check it in your browser](#check-it-in-your-browser) section of this document.

#### 4d: Report a mismatch

If something doesn't match, tell Claude which criterion failed and what you saw.

### Step 5: Review the diff

#### 5a: Read every change before you accept it

Stage the changes and show the diff against the last commit on your branch:

```text
! git add -A && git diff --staged
```

Expect one constant, a `min()` call inside the `service_fees()` function, an updated pricing-order docstring, and the rule text in the `CLAUDE.md` and `README.md` files. Nothing else changes.

Ask yourself the following questions:

- Can you explain every change?
- Did anything change that has nothing to do with fees?

### Step 6: Get a second opinion

The demo names this step but doesn't run it. In a lab, attendees run it, and it takes two or three minutes.

A reviewer subagent that hasn't seen the conversation checks the branch against this sheet and labels each finding `MUST FIX`, `OUT OF SCOPE`, `UNSURE`, or `OPTIONAL`. The attendee picks which findings to fix, and Claude writes a failing test for each one first. The prompt is on every Lab 1 sheet, and the labs mark this step optional for attendees who are short on time.

### Step 7: Commit

Commit the change:

```text
! git add -A && git commit -m "demo1: cap service fees at 30 dollars per order"
```

After this commit, the `git diff --staged` output is empty. To see the whole change again, run the `git diff main` command, which is the command that the completion checklist names.

These are the seven steps on every Lab 1 sheet: decide what right is, get tests that you can read, let Claude code against them, check the evidence yourself, read the diff, get a second opinion, and commit.

## Check it in your browser

Use this section during step 4c of the workflow.

### Start the app

In the same conversation as step 3, ask Claude to start the app in the background:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

For more information, see [Start the app](01-getting-started.md#start-the-app).

### Quote 8 GA tickets on the /docs page

After a fresh seed, performance 1 is The Vanishing Ace on November 10, and tier 1 is its GA tier. To check criterion 4, follow these steps:

1. Open the [API documentation page](http://127.0.0.1:8000/docs).
2. Click **POST /orders/quote**, and then click **Try it out**.
3. Replace the request body with the following:

   ```json
   {"performance_id": 1, "items": [{"tier_id": 1, "qty": 8}]}
   ```

4. Click **Execute**. In the response, `fees_cents` is 3000 ($30.00) and `total_cents` is 63168 ($631.68). Match them to the worked examples.

### Stop the app

Ask Claude to stop the app:

```text
Stop the app.
```

Then go back to [4d: Report a mismatch](#4d-report-a-mismatch) and continue with [Step 5: Review the diff](#step-5-review-the-diff).

## Completion checklist

The demo is complete when the following statements are true:

- [ ] Each of the five criteria has a test, and every test passes.
- [ ] The tests committed in step 2 weren't changed to make them pass.
- [ ] The existing tests that changed are the ones that Claude named in step 2, with old and new answers that match the rule change.
- [ ] Every test asserts exact cents, not "smaller than before."
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] The cap is in the `app/pricing.py` file, inside the function that computes the fee, and tax is unchanged.
- [ ] You quoted 8 GA on the `/docs` page and read 3000 and 63168 from the response.
- [ ] You can explain every line of the `git diff main` output, and nothing unrelated changed.
