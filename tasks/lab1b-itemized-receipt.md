# Lab 1b: Itemized receipt

**Tier:** Starter · **Time:** 50 minutes · Solo or with a partner

## Start here

0. New to this? Read [`tasks/00-how-we-work.md`](00-how-we-work.md) first: it explains the working loop, why it works, and the commands you'll need.
1. Run the commands under **Starting branch**.
2. Read **Goal**, **Background** and **Acceptance criteria**.
3. Follow **The working loop**, step by step. Step 1 is yours: write your answer key before you ask Claude anything.
4. You're done when everything under **Done means** is checked. **Optional stretch** is for extra time; **Hints** are at the very end, for when you're stuck.

## Goal

Add `GET /orders/{id}/receipt`: every pricing line of a stored order, matching its stored totals to the cent.

## Starting branch

```sh
git switch main
git switch -c lab1b-itemized-receipt
uv run pytest          # green before you change anything
```

## Background

- An order stores its money when it's created: `subtotal_cents`, `discount_cents`, `fees_cents`, `tax_cents`, `total_cents`, plus `promo_code` (null when no promo was used).
- Each order line stores `unit_price_cents`, the price paid at purchase time. Tier prices can change later; receipts must not.
- `orders.get_order()` in `app/orders.py` already loads an order with its ticket `lines` and its `pricing_lines` (Subtotal, Discount, Service fees, Tax, Total), rebuilt from the stored totals. `shows.show_for_performance()` gives the show title and the venue name (`.venue`), and `inventory.availability(conn, performance_id).starts_at` gives the start time.
- `GET /orders/{id}` is the UI's confirmation page (HTML, in `app/web.py`). The receipt is a new JSON endpoint next to it.

## Acceptance criteria

The full criteria are given. Write one test for each.

1. `GET /orders/{id}/receipt` returns 200 with `order_id`, `status`, `email`, `show_title`, `venue_name`, `starts_at`, `promo_code` and `lines`. `starts_at` uses the same format `GET /shows/{id}` returns.
2. `lines` is a list of `{"label": str, "amount_cents": int}` in this order: one line per tier bought, labelled like `2 × Premium` (the × sign, U+00D7, not the letter x); then `Subtotal`, `Discount`, `Service fees`, `Tax`, `Total`.
3. The discount line is negative. Its label names the promo when one was used (`Discount (LOCALS10)`); with no promo, it's `Discount` with amount 0.
4. Every amount comes from the stored order, not from recalculating. 2 Premium with LOCALS10 gives: `2 × Premium` 24000, `Subtotal` 24000, `Discount (LOCALS10)` -2400, `Service fees` 1500, `Tax` 1944, `Total` 25044.
5. The tier lines add up to `Subtotal`, and `Subtotal + Discount + Service fees + Tax` equals `Total`.
6. If the tier's price changes after the order, the receipt still shows the price paid.
7. A cancelled order still has a receipt, with `status` `cancelled`.
8. An unknown order id returns 404 with the detail `Order 99999 not found` (for id 99999), the message `orders.get_order()` already raises.

## The working loop

Write the tests first and check them yourself, then let Claude make them pass. Each step has a prompt you can copy. Start with `/clear` so Claude begins fresh.

1. **Write your answer key (no Claude yet).** Go through **Acceptance criteria** one by one and write down exactly what should happen for each: which status code, which fields, which labels, the exact cents. Some criteria already state the answer; others you work out. Check you get the same numbers as the worked example in criterion 4. In step 2, you'll compare Claude's tests against this answer key.
2. **Tests first.** Ask Claude:

   > Read tasks/lab1b-itemized-receipt.md and the relevant code. Write a failing test for each acceptance criterion. Don't change anything in app/. Run the tests and show me which ones fail.

   Compare each test with your answer key. If one is wrong, tell Claude what it should be and why:

   > The test for criterion 4 expects ___, but it should be ___ because ___. Fix that test.

   Two things to check:
   - **Criterion 8 should fail for the right reason.** Before the route exists, every receipt request returns FastAPI's generic `{"detail":"Not Found"}`. A test that checks only the 404 status would pass already and prove nothing; a test that checks the exact detail fails until your route is in place.
   - **Criterion 6's test must change the tier's price *after* placing the order**, then check the receipt still shows the old price. A test that never changes the price proves nothing.

   When you're satisfied with the tests, commit them:

   ```sh
   git add -A && git commit -m "lab1b: tests"
   ```

3. **Clear, then implement.** Type `/clear`, then ask:

   > Make the new tests from my last commit pass (see git show HEAD). Don't change any test. Read tasks/lab1b-itemized-receipt.md for context. Run the full suite and show me the output.

4. **Check the evidence.**
   - Run `uv run pytest` yourself. Is everything green?
   - Run `git diff HEAD --stat -- tests/`. It should print nothing, which means Claude didn't change your tests.
   - Try it yourself: follow **Check it in your browser** below.
5. **Review the diff.** Run `git add -A` then `git diff --staged` (Space to page, `q` to quit), or use VS Code's Source Control panel. Your tests are already committed, so this shows only the code Claude wrote. Can you explain every change? Was anything unexpected touched?
6. **Get a second opinion.** Ask Claude:

   > Use a subagent to review this branch's changes (git diff main) against tasks/lab1b-itemized-receipt.md. It hasn't seen our conversation. Check every acceptance criterion, and don't report style. For each finding, give:
   > - a label: MUST FIX (a criterion isn't met, or a bug), UNSURE, or OPTIONAL
   > - which criterion it's about
   > - evidence: the file and line, or an input that gives the wrong result
   >
   > Don't change any files or the database; if you need to experiment, do it in a test. Just show me the findings.

   **Why "don't report style"?** A reviewer asked to find problems always finds something. If you fix every finding, you end up with extra layers of code and tests for cases that can't happen. You want bugs and unmet criteria, not someone else's taste.

   The labels are the reviewer's opinion; you decide. Check the evidence for each MUST FIX yourself, ask for a failing test on anything UNSURE, and skip OPTIONAL. If a finding is real but not in your criteria (often something that was there before you started), write it down and move on: fixing it is a new feature, not this one. Then fix the real ones test-first:

   > Findings 1 and 3 are real; ignore the rest. For each, write a failing test that shows the problem, then fix it. Run the full suite and show me the output.

   Then repeat step 4.
7. **Commit** when you're satisfied with the change:

   ```sh
   git add -A && git commit -m "lab1b: itemized receipt"
   ```

## Check it in your browser

Use this for step 4. You'll place a real order in the app, then look at its receipt. Compare every result with your answer key.

### 1. Start the app

Open a second terminal, go to your `showtix` folder, and run:

```sh
uv run uvicorn app.main:app --reload
```

Wait for `Application startup complete`. Leave this terminal running; keep working with Claude in the first one.

### 2. Place the worked-example order

1. Open http://127.0.0.1:8000/ and click any date under any show.

   ![Click any date under any show](img/lab1b-1-pick-a-date.png)

2. In the **Qty** column, enter `2` for **Premium**. Type `LOCALS10` in **Promo code** and click **Get quote**.

   ![2 Premium, promo code LOCALS10, then Get quote](img/lab1b-2-quote-form.png)

3. Check the quote: Subtotal $240.00, Discount (LOCALS10) −$24.00, Service fees $15.00, Tax $19.44, Total $250.44. Enter any email and click **Place order**.

   ![The quote totals $250.44; enter an email, then Place order](img/lab1b-3-quote-and-place-order.png)

4. The confirmation page's heading shows your order number, for example **Order 4: paid**. The seed data already has a few orders, so yours won't be 1. Write it down.

   ![The order number is in the heading](img/lab1b-4-confirmation.png)

### 3. Open the receipt (criteria 1–5)

Open http://127.0.0.1:8000/orders/4/receipt, using your order number. In Chrome or Edge, tick **Pretty-print**; it then looks like this (the show and time depend on which date you picked):

![The receipt for the worked-example order](img/lab1b-5-receipt.png)

| Criterion | You should see |
| --- | --- |
| 1 | `order_id`, `status` (`paid`), `email`, `show_title`, `venue_name`, `starts_at`, `promo_code` (`LOCALS10`) and `lines`. `starts_at` has the same format as in http://127.0.0.1:8000/shows/1 |
| 2, 4 | `lines` in this order: `2 × Premium` 24000, `Subtotal` 24000, `Discount (LOCALS10)` -2400, `Service fees` 1500, `Tax` 1944, `Total` 25044 |
| 3 | The discount is negative and names the promo. Place a second order with no promo code: its receipt shows `Discount` with amount 0 |
| 5 | 24000 = 24000, and 24000 − 2400 + 1500 + 1944 = 25044 |

Criterion 6 (the price changes after the order) needs a database change, so your test is the check. You don't need to try it by hand.

### 4. Cancel the order (criterion 7)

1. Open http://127.0.0.1:8000/docs and click **POST /orders/{order_id}/cancel**. Click **Try it out**, enter your order number in **order_id**, and click **Execute**.

   ![Try it out on the cancel endpoint, with your order number](img/lab1b-6-cancel-execute.png)

2. Scroll down to **Server response**. The code is **200**.

   ![Code 200](img/lab1b-7-cancel-200.png)

3. Reload your receipt. `status` is now `cancelled`, and every amount is unchanged.

   ![The same receipt, now cancelled](img/lab1b-8-receipt-cancelled.png)

### 5. An unknown order (criterion 8)

Open http://127.0.0.1:8000/orders/99999/receipt. You should see the detail `Order 99999 not found`. If you see `{"detail":"Not Found"}` instead, the receipt route doesn't exist: that's the 404 you got before building anything.

![Order 99999 not found](img/lab1b-9-unknown-order.png)

**Something doesn't match?** Don't fix it by hand. Tell Claude which criterion failed and what you saw.

### 6. Stop the app

Click in the terminal where the app is running and press **Ctrl+C** (on a Mac too: Control, not Command). You'll see `Shutting down`. If you later get "address already in use," the app is still running in another terminal: find it and press Ctrl+C there.

## Done means

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

Finished early? Add a "View receipt" link to the order confirmation page that opens `/orders/{id}/receipt`. Add a test that the confirmation page contains the link.

Or: make receipts keep the tier's *name* at purchase, not just its price. Today, renaming a tier changes the name on old receipts. Write a failing test first. This needs a new column on `order_lines`, so reset the local database afterwards with `uv run python -m app.seed`.

## Hints

Stuck? Hints (nudge, stronger nudge, near-answer) are on the [workshop hints page](https://www.notion.so/409be0acdc23810383b1dd968c3eeccc). Open one level at a time.
