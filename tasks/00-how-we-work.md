# How we work in these labs

Every lab uses the same seven-step workflow. This page explains each step and why it's good practice. To learn how to run commands and the app, see [Getting started](01-getting-started.md). This page takes about 5 minutes to read. Read it once before your first lab, and come back whenever a step is unclear. For diagrams of how the app works, see [Architecture](../docs/architecture.md). Your sheet has every prompt ready to copy, with its own file name filled in.

**Note**: You might read about "agent loops" elsewhere. That term means something different: the model calls tools over and over until a task is done. Lab 2c calls this a tool loop, and you build one there. This page is about the workflow that you follow.

## The workflow at a glance

<img src="../docs/img/5-workflow-compact.svg" alt="Align; review and commit tests; clear and implement; check evidence; review the diff; get a second opinion; commit. Real findings loop back through a failing test, a fix and another evidence check." width="1000">

The [detailed version](../docs/architecture.md#5-the-workflow) of the diagram shows what happens in each step.

The workflow has the following steps:

1. **Align.** Settle what "done" means. On the Advanced labs (1e, 1f, 2c), Claude first explains the code, and you settle the open decisions with it. Every lab ends step 1 with your expected results, written without Claude.
2. **Write the tests first.** Type `/clear`, and then Claude writes failing tests. You check them against your expected results, and then you commit them.
3. **Make the tests pass.** Type `/clear`, and then Claude makes your tests pass without changing them.
4. **Check the evidence.** Run the tests yourself, confirm that the tests didn't change, and try the feature in your browser.
5. **Review the diff.** Read every change that Claude made.
6. **Get a second opinion.** A reviewer subagent checks the change, and you fix what's real.
7. **Commit.** Save the change when you're satisfied with it.

Start every lab with `/clear`, so that Claude doesn't carry anything over from the last one.

## 1. Align on what "done" means

Before Claude writes anything, you decide exactly what the feature does. Every lab's step 1 ends with your expected results. On the harder labs, two parts come first, in this order: explore, and then decide.

### Explore the code

On the Advanced labs (1e, 1f, 2c), you explore first, because you can't decide how to change code that you've never seen. Your sheet's first prompt asks Claude to explain the part of the code that you'll change, in plain words and short enough to read in 2 minutes. The prompt also asks which routes and pages reach that code, so that the proposal can cover each one. This step changes nothing. For the big picture, see the architecture document linked at the top of this page.

### Decide the open questions

The Intermediate and Advanced sheets fall into the following two groups:

- **Sheets with a "Decisions to make" section** (1e, 1f, 2c). Ask Claude to propose an answer to every decision in one message, and then correct the picks that you disagree with. For example:

  ```text
  Read tasks/lab1e-waitlist.md and the relevant code. Work through the
  "Decisions to make" for me in one message: for each bullet, your pick in one
  line, why, and the alternative you rejected. If a pick depends on how the code
  works, explain that part in plain words first. Then imagine this shipped and a
  customer hit a problem: name the three most likely things our picks don't
  cover and say which one, if any, you'd make a criterion. Don't write any code
  or tests. End by asking me which picks to change. Once I've answered, replace
  the placeholder criteria (3 onward) in Acceptance criteria with at most 5 new
  criteria: one numbered, testable criterion each, describing behavior rather
  than which functions to create, with exact status codes and messages; under
  each, a "Why:" line with the reason we chose it; right after them, a short
  "Not doing" list for everything we deferred, including problems we didn't make
  criteria; and last, a "Slices" list of at most 3 vertical slices (each a piece
  of behavior that works end to end, small enough to review in a few minutes),
  in build order, with the criteria each covers. Then replace everything under
  the Decisions to make heading (the intro sentence, the bullets and the
  paragraph after them) with one line: "Decided: see criteria 3 onward, each
  with its Why. Deferred items are under Not doing." Change nothing else in the
  sheet. Show me what you changed so I can check it.
  ```

  You still choose, by exception. Reply with the picks to change, such as "Change 2 to the simplest option you listed. Keep the rest.", or reply "Keep all your picks." The proposal ends with a pre-mortem, which asks what a customer can still run into. The caps of 5 new criteria and 3 slices keep the build inside the lab, and anything that doesn't fit goes on the Not doing list. Spend about 15 minutes on exploring and the proposal together.
- **Sheets that ask for your own edge cases** (1c, 1d, 2b). Think them through yourself first, and type them into the sheet. If you're stuck, ask Claude for a hint:

  ```text
  Read tasks/lab1c-group-discount.md and the relevant code. I'm stuck finding edge cases
  the criteria don't cover. Give me one hint at a time, as a question, not the
  edge case itself. If I say "just tell me", suggest 3 edge cases, one sentence
  each, and I'll pick. Don't write any code or change any files.
  ```

**Why the decisions go in the sheet.** A file survives `/clear`, and the conversation doesn't. You type `/clear` before you write tests and again before you implement, so the sheet and your committed tests are everything that the next session knows.

### Write your expected results (every lab, without Claude)

Your expected results are a list of what happens for each acceptance criterion. A few lines per criterion is enough, and you can keep them wherever you like.

Go through the sheet's acceptance criteria one by one, including any that you added, and write down exactly what happens for each one: which shows come back, which status code, the exact message, and the exact cents. The data that the app starts with is in [Seed data](../docs/seed-data.md): every show, night, price, seat count, promo code, and seeded order, plus how a price is built. If Claude wrote exact values into your new criteria, check them yourself there or in the `/docs` page instead of copying them.

**Why.** Claude is fast and sounds confident, and it writes tests that agree with its own understanding. If you don't know the right answer before you see Claude's answer, you can't tell a test that checks the right thing from one that checks the wrong thing. While this app was being built, Claude once added 36000 + 2250 + 3240 and got 40590. The right answer is 41490. Expected results catch that error, and nodding along doesn't.

Acceptance criteria are the definition of "done." Turning each one into an exact expected value is what makes it testable. On the Starter labs, this is all of step 1: you agree with yourself on what right looks like before Claude does anything.

## 2. Write the tests first

Type `/clear`, and then ask Claude for the tests, and only the tests:

```text
Read tasks/lab1a-category-filter.md and the relevant code. Write a failing
test for each acceptance criterion. Test behavior through the API, the pages,
or functions that already exist, not new functions or exact HTML. Don't change
anything in app/. Run the tests and show me which ones fail.
```

Compare each test with your expected results: same shows, same status code, same message, and same cents. A test that checks that "the total got smaller" instead of "the total is 25044 ($250.44)" is a weak test. A test must also check behavior through the API or the page, not call a function that doesn't exist yet. A test like that designs the code for Claude, and step 3 doesn't let Claude change it. If a test is wrong, tell Claude what it must be and why:

```text
The test for criterion 4 expects ___, but it should be ___ because ___. Fix
that test.
```

When you're satisfied with the tests, commit them:

```text
! git add -A && git commit -m "lab1a: tests"
```

The tests come first for the following reasons:

- **A test that has never failed proves nothing.** It might not test anything at all. A test that fails first proves that it can detect the missing behavior. When it passes after the change, you know that your change made it pass. This cycle is called red, then green.
- **Checking tests is less work than checking code.** Each test is one criterion with one expected result, so you can hold it against your expected results line by line. After the tests are right, they're the target that Claude works toward.
- **Committing the tests makes them tamper-evident.** If a test is awkward to pass, an AI can quietly loosen it. After your reviewed tests are committed, any later change to them shows up in `git diff`.
- **A test that already passes isn't always a mistake.** If the behavior exists today, such as a request without the new filter that returns everything as before, the test passes. Your sheet says when to expect that.

## 3. Make the tests pass

Type `/clear`, and then ask Claude to make the tests pass:

```text
Make the new tests from my last commit pass (see git show HEAD). Don't change
any test. If you change anything the tests don't need, tell me what and why.
Read tasks/lab1a-category-filter.md for context. Run the full suite and show
me the output.
```

**Big features: one vertical slice at a time.** On the Advanced labs, step 1 ends with a Slices list in the sheet, based on what you decided. Step 3 builds the slices in that order, and Claude stops after each one. The number of slices depends on the feature. A vertical slice is a piece that works end to end and is small enough to review in a few minutes, such as "customers can join the waitlist", not a layer such as "all the database code". After each slice, read its diff, commit it, and then ask for the next one.

**Why slices?** One feature built in one go can touch seven files at once, and a diff that big is too large to review honestly. Slices keep each diff small enough to read, give you a commit to go back to if the next slice goes wrong, and catch a misunderstanding after one slice instead of after the whole feature is built on it. Tests for later slices fail until their slice is built, which is expected. On a real project, you usually go one step further and write and review the tests for each slice right before you build it. Here, the whole feature's tests come first to save time.

The prompt is written this way for the following reasons:

- **`/clear` gives the implementing session a clean start.** It works from your sheet and your committed tests, not from a long conversation full of options that you didn't choose.
- **"Don't change any test."** Your tests are the definition of done. The code moves to meet them, not the other way around.
- **"Run the full suite."** Your change can break something somewhere else, which is called a regression. The full suite runs in a few seconds, so run all of it, not only your new tests.
- **"Show me the output."** Evidence, not claims. "All tests pass" on its own tells you very little, and the actual output tells you what ran and what happened.

## 4. Check the evidence

Don't take Claude's word for it. The `!` prefix runs a command yourself, not through Claude, and Claude sees the output too.

- **Run the tests yourself.** The last line must say only `passed`, with no `skipped`, `deselected`, or `xfailed`:

  ```text
  ! uv run pytest
  ```

- **Check that Claude changed only app code.** Every file that this command lists must be under `app/`:

  ```text
  ! git status --short
  ```

  A file in `tests/`, whether changed or new with `??`, a `conftest.py` file, or `pyproject.toml` means that Claude touched your tests or how they run. Ask Claude why. On labs built slice by slice (1e, 1f, 2c), also check the slice commits. For more information, see [Check your tests didn't change](01-getting-started.md#check-your-tests-didnt-change).
- **Lab 2 only: run your eval.** The eval is a set of real prompts with expected answers, scored against the live API. Run it twice, and read any failing case before you change anything. Your sheet explains how.
- **Try the feature yourself.** On Labs 1a and 1b, the browser section of your sheet has the exact links, clicks, and results to expect. On later labs, choose your own checks from your expected results. To start and stop the app, see [Start the app](01-getting-started.md#start-the-app) and [Stop the app](01-getting-started.md#stop-the-app).

Use the values from your expected results, and check whether the running app agrees.

**Why `git status` and not `git diff`?** The `git diff` command shows only files that git already tracks, so a new test file or a new `conftest.py` file that skips tests doesn't show up. Test settings can also live outside `tests/`, in `pyproject.toml`.

## 5. Review the diff

To see everything that changed, including new files, stage the changes and show the staged diff:

```text
! git add -A && git diff --staged
```

The **Source Control** panel in VS Code shows the same changes side by side. The `git status` command gives only the list of changed files. Your tests are already committed, so this diff shows only the code that Claude wrote. The `git add -A` command only stages the changes, and it doesn't commit anything.

Ask yourself the following two questions:

- Can I explain every change?
- Did anything change that has nothing to do with this feature?

## 6. Get a second opinion

Have a subagent review the work. It starts with a fresh context, so it hasn't seen your conversation and your conversation can't influence it:

```text
Use a subagent to review this branch's changes (git diff main) against
tasks/lab1a-category-filter.md. It hasn't seen our conversation. It should
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

**Why "don't report style"?** A reviewer that's asked to find problems always finds something. If you fix every finding, you end up with extra layers of code and tests for cases that can't happen. You want bugs and unmet criteria, not someone else's taste.

**What to do with the findings.** Claude shows the MUST FIX findings as a numbered list and asks which ones to fix. The labels are the reviewer's opinion, so check the evidence yourself before you answer.

Answer with the numbers that you want fixed, for example "1 and 3". Claude writes a failing test for each one, and then fixes it. You can also decide not to fix one, or talk it through with Claude before you decide.

Then repeat steps 4 and 5. One review round is enough unless the fixes were big.

## 7. Commit

When you're satisfied with the change, commit it:

```text
! git add -A && git commit -m "lab1a: category filter"
```

On labs built slice by slice, your slices are already committed. If you didn't fix anything in step 6, there's nothing left to commit.

**Why.** A commit is a safe point. If anything goes wrong later, you can get back to it. Keep one feature per branch, and keep changes small. Small diffs take less time to review and to undo.

## When Claude gets something wrong

Find out why before you correct it. If Claude is still working, press Esc to stop it. Then follow these steps:

1. **Ask first.** Ask Claude "What did you understand the requirement to be, and what in the sheet or code led you there?" The answer usually shows the misunderstanding: a sentence that it misread, or a pattern in the code that it copied. Ask on the first miss, not after several tries, because this question is the fastest way to the fix.
2. **Correct it with the reason.** Say what you want and why. "Cap only the service fees, not the total, because tax and ticket prices are separate charges" works better than "don't do that."
3. **If it's still wrong, start the step over.** The conversation is now full of wrong turns. Type `/clear` to wipe the conversation. That wipe is why you ask first. Then start the step over with your sheet's prompt plus three additions:
   - The rule that it got wrong, stated as what you want, with the reason.
   - One example from your expected results, with the exact result.
   - Where the change belongs, if Claude put it somewhere else.

   For example, for the fee cap from Demo 1:

   ```text
   Make the new tests from my last commit pass (see git show HEAD). Don't change
   any test. If you change anything the tests don't need, tell me what and why.
   Read tasks/demo1-fee-cap.md for context. Important: cap only the service
   fees, not the total or the tax, because tax and ticket prices are separate
   charges. For example, 8 tickets have fees of 3000 cents (not 6000), and
   their tax doesn't change. All of the money math belongs in app/pricing.py.
   Run the full suite and show me the output.
   ```

4. **If it's a rule for the whole project, add it to `CLAUDE.md`** so that every session knows it.

## When you're stuck

Each lab sheet ends with a link to its hints page, which lists the places where students get stuck in that lab, each with what to check and what to tell Claude. Open the section whose heading matches what you see, and only after you've tried without it. If you're still stuck, raise your hand.

## Commands

For how to run a command yourself, run the tests, start and stop the app, reset the database, and use git, see the Getting started page linked at the top of this page.

## Appendix: sources behind the workflow

This workflow isn't ours alone. Each step follows advice from the people who build and use coding agents most. Quotes and links were checked on November 3, 2026.

**Anthropic's guidance.** [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) is the source for the following table. The older Anthropic engineering post on the same topic redirects to that page.

| Step | What the page says | Section |
| --- | --- | --- |
| 1. Align | "Interview me until you could write the spec, then write it to SPEC.md." Then "start a fresh session to build from it, so the build begins with a clean context and a written definition of done." | Brainstorm with Claude first |
| 2. Tests first | Its example of a good prompt: "write a failing test that reproduces it, then fix it." | Write a specific prompt |
| 3. Clear | "`/clear` between unrelated tasks … a focused context gets you better answers." | Keep cost and context down |
| 4. Evidence | "Ask Claude for *evidence*: the command it ran and its output … 'All tests pass' on its own tells you very little." | Give Claude a check to run |
| 6. Second opinion | `/code-review` "reviews the diff in a fresh subagent that never saw your conversation." Subagents help when "getting a reviewer that hasn't seen how the code was written." | Give Claude a check to run; Know what subagents cost |
| 6. "Don't report style" | "A reviewer that's asked to find problems will always find *something*. If you fix every finding, you end up with extra abstraction layers and tests for cases that can't happen." | Review against your spec |
| When Claude goes wrong | "After two failed corrections run `/clear` and write a better prompt instead of a third." We go one step further: ask why on the first miss. | Steer the session |

**Other sources, by step.** The following list gives the other sources that each step follows:

- **1. Align: explore before deciding.** Dex Horthy (HumanLayer), [Getting AI to Work in Complex Codebases](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) (August 29, 2025): research first, to "understand the codebase, the files relevant to the issue, and how information flows," because a misunderstanding there "could land you with thousands of bad lines of code." His 2026 revision adds questioning first: [Lessons Learned Rolling Out RPI to Hundreds of Engineers](https://www.youtube.com/watch?v=YwZR6tc7qYg) (March 24, 2026) and [Everything We Got Wrong About Research-Plan-Implement](https://www.youtube.com/live/6IxSbMhT7v4?t=1947) (April 20, 2026).
- **1. Align: the interview and the spec.** Matt Pocock, [mattpocock/skills](https://github.com/mattpocock/skills): `/grill-me`, "Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved," and `/to-spec`, "Turn the current conversation into a spec."
- **1. Align: plan before you build.** Simon Willison, [Vibe engineering](https://simonwillison.net/2025/Oct/7/vibe-engineering/) (October 7, 2025): "Sitting down to hack something together goes much better if you start with a high level plan."
- **2. Tests first.** Jesse Vincent, [Superpowers](https://github.com/obra/superpowers): "write failing test, watch it fail, write minimal code, watch it pass, commit." Kent Beck's system prompt in [Augmented Coding: Beyond the Vibes](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) (June 25, 2025): "Always follow the TDD cycle: Red → Green → Refactor." The classic book is Kent Beck, _Test-Driven Development: By Example_ (2002).
- **2. Test behavior, not implementation.** Andrew Trenk, [Testing on the Toilet: Test Behavior, Not Implementation](https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html) (Google Testing Blog, August 5, 2013): "Tests that are independent of implementation details are easier to maintain."
- **2. Commit your tests so changes show.** Kent Beck, in the same essay, lists a warning sign to watch for: "Any indication that the genie was cheating, for example by disabling or deleting tests." Committing the reviewed tests makes that kind of cheating visible in `git diff`. That part is our own practice, from our dry runs.
- **3. Vertical slices.** Addy Osmani, [agent-skills](https://github.com/addyosmani/agent-skills): "Thin vertical slices - implement, test, verify, commit." Matt Pocock's `/tdd` "builds features or fixes bugs one vertical slice at a time," and his `/to-tickets` breaks a spec into "tracer-bullet tickets."
- **4. Check the evidence.** Boris Cherny, who created Claude Code, in [Inside the Development Workflow of Claude Code's Creator](https://www.infoq.com/news/2026/01/claude-code-creator-workflow/) (InfoQ, January 10, 2026): the most important tip is to "give Claude a way to verify its work," which he says improves the result 2 to 3 times. Simon Willison: with a good test suite, "agentic coding tools can *fly*."
- **5. Review the diff.** Addy Osmani, [The 70% Problem](https://addyosmani.com/agentic-engineering/the-70-percent-problem/): "AI gets you 70% of the way fast. The remaining 30% is where experienced engineers earn their keep." Simon Willison: "If you're fast and productive at code review you're going to have a much better time working with LLMs."
- **6. A second opinion.** Superpowers runs code review "between tasks," reporting issues "by severity," and "critical issues block progress."
- **7. Commit.** Simon Willison: "Being able to undo mistakes and understand when and how something was changed is even more important" with agents.
- **Why there's no plan-mode step.** In January 2026, Boris Cherny described starting in plan mode (InfoQ, earlier in this list). By September he wrote, on [Hacker News](https://news.ycombinator.com/item?id=49840054), "plan mode was useful, and is no longer useful," agreeing with Ayman Nadeem's [Plan mode is dead](https://www.aymannadeem.com/artificial/intelligence,/developer/tools/2026/09/24/plan-mode-is-dead.html) (September 24, 2026). In our workflow, the proposal round and the test review do that job.
