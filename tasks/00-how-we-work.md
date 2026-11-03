# How we work in these labs

Every lab uses the same seven-step loop. This page explains each step, why it's good practice, and the commands you'll need. Read it once before your first lab (about 5 minutes), then come back whenever a step is unclear. Your sheet has every prompt ready to copy, with its own file name filled in.

## The loop at a glance

1. **Write your answer key** (no Claude yet). If your sheet has **Decisions to make** or asks for your own edge cases, settle those with Claude first.
2. **Tests first:** Claude writes failing tests, you check them against your answer key, then you commit them
3. **Clear, then implement:** `/clear`, then Claude makes your tests pass without changing them
4. **Check the evidence:** run the tests yourself, confirm they weren't changed, and try it in your browser
5. **Review the diff**
6. **Get a second opinion** from a reviewer subagent, then fix what's real
7. **Commit** when you're satisfied with the change

Start every lab with `/clear`, so Claude doesn't carry anything over from the last one.

## 1. Write your answer key

Go through the sheet's **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents.

**Why:** Claude is fast and sounds confident, and it writes tests that agree with its own understanding. If you don't know the right answer before you see Claude's, you can't tell a test that checks the right thing from one that checks the wrong thing. While this app was being built, Claude once added 36000 + 2250 + 3240 and got 40590. The right answer is 41490. An answer key catches that; nodding along doesn't.

Acceptance criteria are the definition of "done." Turning each one into an exact expected value is what makes it testable.

**If your sheet leaves decisions open,** settle them with Claude before you write the answer key:

- **Sheets with "Decisions to make"** (the Breakthrough and Advanced labs): have Claude interview you. For example:

  > Read tasks/lab1e-waitlist.md and the relevant code. Interview me about the "Decisions to make", one question at a time. For each, give me 2-3 options and your recommendation. Don't write any code or tests. When we've covered every decision, update "Your criteria" in the sheet and change nothing else: one numbered, testable criterion per decision, with exact status codes and messages; under each, a "Why:" line with the reason we chose it; and a short "Not doing" list for what we deferred. Then show me the section so I can check it.

  You choose; Claude only offers options. Spend about 10 minutes. If a decision drags on, pick the simplest option and put the other on the "Not doing" list. Then write the expected values for your new criteria into your answer key yourself.
- **Sheets that ask for your own edge cases** (the Intermediate labs): ask for ideas, then choose.

  > Read tasks/lab1c-group-discount.md and the relevant code. Suggest 3 edge cases the criteria don't cover, one sentence each. Don't write any code. I'll pick which ones to add.

**Why:** the decisions end up in the sheet, a file, not just in the conversation. That matters because you'll `/clear` before implementing: the sheet and your committed tests are everything the next session knows.

## 2. Tests first

Ask Claude for the tests, and only the tests:

> Read tasks/lab1a-category-filter.md and the relevant code. Write a failing test for each acceptance criterion. Don't change anything in app/. Run the tests and show me which ones fail.

Compare each test with your answer key. Same shows, same status code, same message, same cents? A test that checks "the total got smaller" instead of "the total is 25044" is a weak test. If one is wrong, tell Claude what it should be and why:

> The test for criterion 4 expects ___, but it should be ___ because ___. Fix that test.

When you're satisfied with the tests, commit them:

```
git add -A && git commit -m "lab1a: tests"
```

**Why:**

- **A test that has never failed proves nothing.** It might not test anything at all. A test that fails first proves it can detect the missing behavior; when it passes after the change, you know *your change* made it pass. This is called red, then green.
- **Checking tests is easier than checking code.** Each test is one criterion with one expected result, so you can hold it against your answer key line by line. Once the tests are right, they're the target Claude works toward.
- **Committing them makes them tamper-evident.** If a test is awkward to pass, an AI can quietly loosen it. Once your reviewed tests are committed, any later change to them shows up in `git diff`.
- **A test that already passes isn't always a mistake.** If the behavior exists today (a request without the new filter returns everything, as before), the test should pass. Your sheet says when to expect that.

## 3. Clear, then implement

Type `/clear`, then:

> Make the new tests from my last commit pass (see git show HEAD). Don't change any test. Read tasks/lab1a-category-filter.md for context. Run the full suite and show me the output.

For a big feature, build one slice at a time: "Start with criteria 1 and 2 only. Stop when those tests pass." Commit each slice when you're satisfied with it.

**Why:**

- **`/clear` gives the implementing session a clean start.** It works from your sheet and your committed tests, not from a long conversation full of options you didn't choose.
- **"Don't change any test":** your tests are the definition of done. The code moves to meet them, not the other way around.
- **"Run the full suite":** your change can break something somewhere else. That's called a regression. The full suite runs in a few seconds, so always run all of it, not just your new tests.
- **"Show me the output":** evidence, not claims. "All tests pass" on its own tells you very little; the actual output tells you what ran and what happened.

## 4. Check the evidence

- **Run the tests yourself:** `uv run pytest`. Don't take Claude's word for it.
- **Check your tests weren't changed:** `git diff HEAD --stat -- tests/` should print nothing.
- **Lab 2 only: run your eval** twice and read any failing case before changing anything. Your sheet explains how.
- **Try it in your browser.** Your sheet's **Check it in your browser** section has the exact links, clicks and results to expect. In short:
  - **Start the app** in a **second terminal** and leave it running: `uv run uvicorn app.main:app --reload`
  - **API:** open http://127.0.0.1:8000/docs, click your endpoint, then **Try it out**, fill in the values and **Execute**.
  - **Web UI:** open http://127.0.0.1:8000/
  - **Stop the app:** click in that terminal and press **Ctrl+C** (on a Mac too: Control, not Command).
  - **Reset the database** if things look strange, or after a schema change: `uv run python -m app.seed`

Use the values from your answer key. Does the running app agree?

## 5. Review the diff

See everything that changed, including new files:

```
git add -A
git diff --staged
```

Press Space to page down and `q` to quit. Or use the **Source Control** panel in VS Code, which shows the same thing side by side. `git status` gives just the list of changed files. Your tests are already committed, so this shows only the code Claude wrote.

Ask yourself: can I explain every change? Did anything change that has nothing to do with this feature? (`git add -A` only stages; it doesn't commit anything.)

## 6. Get a second opinion

Have a subagent review the work. It starts with a fresh context, so it hasn't seen your conversation and can't be talked into agreeing with it:

> Use a subagent to review this branch's changes (git diff main) against tasks/lab1a-category-filter.md. It hasn't seen our conversation. Check every acceptance criterion, and don't report style. For each finding, give:
> - a label: MUST FIX (a criterion isn't met, or a bug), UNSURE, or OPTIONAL
> - which criterion it's about
> - evidence: the file and line, or an input that gives the wrong result
>
> Don't change any files or the database; if you need to experiment, do it in a test. Just show me the findings.

**Why "don't report style"?** A reviewer asked to find problems always finds something. If you fix every finding, you end up with extra layers of code and tests for cases that can't happen. You want bugs and unmet criteria, not someone else's taste.

**What to do with the findings.** The labels are the reviewer's opinion; you decide.

- **MUST FIX:** check the evidence yourself. If it's real, fix it.
- **UNSURE:** ask Claude to prove it with a failing test. No failing test, no fix.
- **OPTIONAL:** skip it.
- **Real, but not in your criteria** (often something that was there before you started): write it down and move on. Fixing it is a new feature, not this one.

Fix the real ones test-first:

> Findings 1 and 3 are real; ignore the rest. For each, write a failing test that shows the problem, then fix it. Run the full suite and show me the output.

Then repeat step 4. One review round is enough unless the fixes were big.

## 7. Commit

When you're satisfied with the change:

```
git add -A && git commit -m "lab1a: category filter"
```

**Why:** a commit is a safe point. If anything goes wrong later, you can get back here.

## When Claude gets something wrong

Find out why before you correct it. Press Esc to stop it if it's still going, then:

1. **Ask first:** "What did you understand the requirement to be, and what in the sheet or code led you there?" Its answer usually shows the misunderstanding: a sentence it misread, or a pattern in the code it copied. Do this the first time, not after several tries; it's the fastest way to the fix.
2. **Correct it with the reason:** say what you want and why. "Cap only the service fees, not the total, because tax and ticket prices are separate charges" works better than "don't do that."
3. **Still wrong after that?** The conversation is now full of wrong turns. Type `/clear` (it wipes the conversation, which is why you ask first) and start the step over with your sheet's prompt plus three additions:
   - **The rule it got wrong, stated as what you want, with the reason.**
   - **One example from your answer key,** with the exact result.
   - **Where the change belongs**, if Claude put it somewhere else.

   For example, for the fee cap from Demo 1:

   > Make the new tests from my last commit pass (see git show HEAD). Don't change any test. Important: cap only the service fees, not the total or the tax, because tax and ticket prices are separate charges. For example, 8 tickets have fees of 3000 cents (not 6000), and their tax doesn't change. All of the money math belongs in app/pricing.py. Run the full suite and show me the output.
4. **If it's a rule for the whole project,** add it to `CLAUDE.md` so every session knows it.

Also: one feature per branch, small changes. Small diffs are easy to review and easy to undo.

## When you're stuck

Each sheet ends with a link to its hints: three levels, from a gentle nudge to a near-answer. Open one level at a time, and only after you've tried without it. Still stuck? Raise your hand.

## Running tests

| What | Command |
| --- | --- |
| Everything | `uv run pytest` |
| One file | `uv run pytest tests/test_shows.py` |
| One test | `uv run pytest tests/test_shows.py::test_name` |
| Tests whose name contains a word | `uv run pytest -k category` |
| Stop at the first failure | `uv run pytest -x` |
| Show each test's name | `uv run pytest -v` |

## Claude Code basics

- **Start it** in the project folder: `claude`. **Leave:** `/exit`.
- **Stop Claude mid-task:** Esc.
- **Start fresh:** `/clear`. Use it at the start of every lab, before implementing (step 3), and when a conversation has gone off track.
- **Permission prompts:** Claude asks before running commands or editing files. Running tests is always fine. Read anything that deletes files or touches things outside this project before you approve it.

## Git basics for the labs

| What | Command |
| --- | --- |
| Which branch am I on? | `git branch --show-current` |
| What changed? | `git status` |
| Save your work | `git add -A && git commit -m "message"` |
| Did my committed tests change? | `git diff HEAD --stat -- tests/` (prints nothing if not) |
| Start a new branch from main | `git switch main && git switch -c <name>` |
