# How we work in these labs

Every lab uses the same six-step loop. This page explains each step, why it's good practice, and the commands you'll need. Read it once before your first lab (about 5 minutes), then come back whenever a step is unclear.

## The loop at a glance

1. **Write your answer key** (no Claude yet)
2. **One good prompt:** failing tests first, then the implementation, then the full suite, with the output as evidence
3. **Check the evidence** against your answer key
4. **Try it yourself** in the running app
5. **Review the diff**
6. **Get a second opinion** from Claude

## 1. Write your answer key

Go through the sheet's **Acceptance criteria** one by one and write down exactly what should happen for each: which shows come back, which status code, the exact message, the exact cents.

**Why:** Claude is fast and sounds confident, and it writes tests that agree with its own understanding. If you don't know the right answer before you see Claude's, you can't tell a test that checks the right thing from one that checks the wrong thing. While this app was being built, Claude once added 36000 + 2250 + 3240 and got 40590. The right answer is 41490. An answer key catches that; nodding along doesn't.

Acceptance criteria are the definition of "done." Turning each one into an exact expected value is what makes it testable.

## 2. One good prompt

The sheet gives you an example, shaped like this:

> Read tasks/<sheet>.md and the relevant code. Write failing tests for each acceptance criterion, then implement it. Run the full suite and show me the output before and after.

Each part has a reason:

- **"Read the sheet and the relevant code":** context. Claude does far better when it knows the goal and has looked at how the code already works.
- **"Write failing tests first":** a test that has never failed proves nothing. It might not test anything at all. A test that fails first proves it can detect the missing behavior; when it passes after the change, you know *your change* made it pass. This is called red, then green. The tests also become a target Claude can check its own work against.
- **"Then implement it":** with the tests in place, Claude knows exactly what done means and can keep going until they pass.
- **"Run the full suite":** your change can break something somewhere else. That's called a regression. The full suite runs in a few seconds, so always run all of it, not just your new tests.
- **"Show me the output before and after":** evidence, not claims. "All tests pass" on its own tells you very little; the actual output tells you what ran and what happened.

**Related good practices:**

- **One feature per branch, small changes.** Small diffs are easy to review and easy to undo.
- **Bigger features: start in plan mode** (press Shift+Tab in Claude Code until it shows plan mode). Claude proposes a plan without changing anything; you review it, then let it build.
- **If Claude drifts, press Esc** to stop it, and tell it what you actually want. If you've corrected the same thing twice and it's still wrong, type `/clear` and write one better prompt that includes what you learned.

## 3. Check the evidence

Look at the test output Claude showed you:

- **Did the new tests fail before the change, and pass after?**
- **Does each test match your answer key?** Same shows, same status code, same message, same cents. A test that checks "the total got smaller" instead of "the total is 25044" is a weak test.

## 4. Try it yourself

Start the app in a **second terminal** and leave it running:

```
uv run uvicorn app.main:app --reload
```

- **API:** open http://127.0.0.1:8000/docs, click your endpoint, then **Try it out**, fill in the values and **Execute**.
- **Web UI:** open http://127.0.0.1:8000/
- **Stop the app:** Ctrl+C in that terminal.
- **Reset the database** if things look strange, or after a schema change: `uv run python -m app.seed`

Use the values from your answer key. Does the running app agree?

## 5. Review the diff

See everything that changed, including new files:

```
git add -A
git diff --staged
```

Press Space to page down and `q` to quit. Or use the **Source Control** panel in VS Code, which shows the same thing side by side. `git status` gives just the list of changed files.

Ask yourself: can I explain every change? Did anything change that has nothing to do with this feature? (`git add -A` only stages; it doesn't commit anything.)

## 6. Get a second opinion

Ask Claude: "Review this diff against tasks/<sheet>.md." Then decide which findings actually matter.

**Why:** a fresh review catches things the first pass missed. But a reviewer asked to find problems always finds *something*, so it's your job to judge. Fix what's real; skip what isn't.

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
- **Plan mode:** Shift+Tab until it shows plan mode. Claude plans but changes nothing until you approve.
- **Stop Claude mid-task:** Esc.
- **Start fresh:** `/clear` (useful when a conversation has gone off track).
- **Permission prompts:** Claude asks before running commands or editing files. Running tests is always fine. Read anything that deletes files or touches things outside this project before you approve it.

## Git basics for the labs

| What | Command |
| --- | --- |
| Which branch am I on? | `git branch --show-current` |
| What changed? | `git status` |
| Save your work | `git add -A && git commit -m "message"` |
| Start a new branch from main | `git switch main && git switch -c <name>` |
