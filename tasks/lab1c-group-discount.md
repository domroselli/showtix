# Lab 1c: Group discount

**Tier:** Intermediate · **Time:** 50 minutes · Solo or with a partner

## Start here

A new pricing rule that has to fit the existing pricing order, built with the full workflow.

1. New here? Read [Getting started](01-getting-started.md) for running commands and the app, then [How we work](00-how-we-work.md) for the workflow (about 5 minutes).
2. Run the command under [Starting branch](#starting-branch), then read [Goal](#goal), [Background](#background) and [Acceptance criteria](#acceptance-criteria).
3. Follow [The workflow](#the-workflow) step by step. Step 1 starts with a quick brainstorm with Claude about edge cases; then you write your answer key yourself.

You're done when every box under [Done means](#done-means) is checked. Stuck? See [Hints](#hints).

## Goal

Reward groups: 6 or more tickets in one tier get 15% off that tier.

## Starting branch

Create this lab's branch from `main`, reset the database, and check that the tests pass:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1c-group-discount && uv run pytest
```

Every test should pass before you change anything. Trouble? See [Start a lab branch](01-getting-started.md#start-a-lab-branch).

## Background

Where the pricing code you'll change lives:

- **Pricing happens in `pricing.price_order()`** in `app/pricing.py`, in a fixed order (see CLAUDE.md): subtotal, discount, service fee, tax, total. `orders.quote()` merges cart items by tier, so each `pricing.Line` it passes in is one tier.
- **A promo discount is computed by `pricing.discount()`.** Quotes and orders carry a single `discount_cents` today. `pricing.pricing_lines()` turns a breakdown into the ordered lines (Subtotal, Discount, Service fees, Tax, Total) that quotes and orders return as `pricing_lines`. The UI's quote and confirmation pages loop over that list, so a line you add there shows up in the UI with no template changes.
- **Quotes (`Quote`) and stored orders (`Order`, `orders` table) must show the same numbers.** Tests use an in-memory database, but the running app uses a local SQLite file. If you change the schema, [reset the database](01-getting-started.md#reset-the-database), or the UI will break even while tests pass.

For a picture of the pricing order, see [How a price is built](../docs/architecture.md#3-how-a-price-is-built).

## Acceptance criteria

Most criteria are given. **Add one or two edge cases of your own** before you write tests.

1. 6 or more tickets in the same tier get 15% off that tier's subtotal (rounded half up to the cent).
2. 5 tickets get no discount; exactly 6 do.
3. If a promo code also applies, the customer gets whichever discount is larger. They never stack.
4. The quote breakdown shows the group discount as its own line: its own field, and its own entry in `pricing_lines` (labelled exactly `Group discount (15%)`, negative, right after `Subtotal`, and only when it's non-zero).
5. All amounts stay in integer cents; tax follows the existing pricing order (9% of the subtotal after the discount that won).
6. The stored order matches the quote, including the group discount line.
7. If the group discount beats a promo, the promo isn't applied: the order doesn't record the promo code, and the promo's use count doesn't go up.

Worked examples (cents):

| Cart | Subtotal | Discount that wins | Fees | Tax | Total |
| --- | --- | --- | --- | --- | --- |
| 6 GA, no promo | 41400 | group 6210 | 4500 | 3167 | 42857 |
| 6 GA + LOCALS10 | 41400 | group 6210 (promo would be 4140) | 4500 | 3167 | 42857 |
| 6 GA + 2 VIP + LOCALS10 | 81398 | promo 8140 (group would be 6210) | 6000 | 6593 | 85851 |
| 7 VIP, no promo | 139993 | group 20999 | 5250 | 10709 | 134953 |

Your edge cases:

8. _..._
9. _..._ (optional)

Think about: ties, the 8-ticket limit, a fixed promo, which discount the breakdown reports when one loses.

## The workflow

Settle what "done" means (with Claude's help on edge cases), then have Claude write the tests, check them yourself, and let Claude make them pass.

- Steps that use Claude have a prompt to copy; commands start with `!`.
- Why each step matters: [How we work](00-how-we-work.md).
- Start with a fresh conversation:

  ```text
  /clear
  ```

### 1. Align: find your edge cases, then write your answer key

This sheet asks for one or two edge cases of your own. Ask Claude for ideas, then choose:

```text
Read tasks/lab1c-group-discount.md and the relevant code. Suggest 3 edge cases
the criteria don't cover, one sentence each. Don't write any code. I'll pick
which ones to add.
```

Add the ones you pick to the sheet's edge-case lines. Then, without Claude, write down exactly what each criterion should return:

- Go through [Acceptance criteria](#acceptance-criteria) one by one: which status code, the exact message, the exact cents.
- Check you get the same numbers as the worked examples. Prices, fees, tax rules and promo codes are in [`docs/seed-data.md`](../docs/seed-data.md).
- Want to see it in the running app? See [Start the app](01-getting-started.md#start-the-app) and [Try an endpoint in /docs](01-getting-started.md#try-an-endpoint-in-docs).

You'll compare Claude's tests against this answer key in step 2.

### 2. Tests first

Have Claude write failing tests, then check them against your answer key.

```text
Read tasks/lab1c-group-discount.md and the relevant code. Write a failing test
for each acceptance criterion. Test behavior through the API, the pages, or
functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

Check especially:

- **Tests check behavior through the API or the page**, not functions that don't exist yet. A test that calls a new function is designing the code for Claude.
- **The four worked examples are tests**, with every line asserted in exact cents.
- **Your own edge cases have tests too.**

If a test doesn't match your answer key, tell Claude what it should be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

When every test matches your answer key, commit them:

```text
! git add -A && git commit -m "lab1c: tests"
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
Read tasks/lab1c-group-discount.md for context. Run the full suite and show me
the output.
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

- Try it yourself. Ask Claude to start the app in the background ([more on starting the app](01-getting-started.md#start-the-app)):

  ```text
  Start the app in the background with uv run uvicorn app.main:app --reload,
  and tell me when it's ready.
  ```

  Then open http://127.0.0.1:8000/docs (click your endpoint, **Try it out**, **Execute**) or the UI at http://127.0.0.1:8000/. Use values from your answer key. When you're done, stop it:

  ```text
  Stop the app.
  ```

Something doesn't match? Tell Claude which criterion failed and what you saw.

### 5. Review the diff

Read every change Claude made before you accept it.

```text
! git add -A && git diff --staged
```

- Can you explain every change?
- Was anything touched that has nothing to do with the group discount?
- Prefer side by side? Use VS Code's **Source Control** panel.

Your tests are already committed, so this shows only the code Claude wrote.

### 6. Get a second opinion

A reviewer that hasn't seen your conversation checks the change against this sheet.

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
! git add -A && git commit -m "lab1c: group discount"
```

## Done means

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
