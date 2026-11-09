# Demo 2: Add a show tagline

This sheet is for the instructor, who follows it on screen during the demo. Attendees watch along, because every Lab 2 sheet relies on the three items that this demo covers.

- **Tier**: Instructor demo (before Lab 2)
- **Time**: 10 minutes

## Start here

This sheet has the same structure as every Lab 2 sheet. The feature is already built on the `demo` branch, so you don't run steps 1 to 3 of the seven-step workflow from scratch. Instead, you present the finished feature, build one test live, and run the evaluation (eval). This feature isn't one of the Lab 2 options.

To run this demo, follow these steps:

1. Run the command in the [Starting branch](#starting-branch) section of this document.
2. Read the [Goal](#goal), [Background](#background), and [Acceptance criteria](#acceptance-criteria) sections.
3. Follow the [Workflow](#workflow) section.

Attendees take the following items into Lab 2:

- The `get_llm` dependency.
- A test that uses the `fake_claude` fixture.
- An eval score that you read before you change anything.

## Goal

Add the `POST /shows/{id}/tagline` endpoint. Claude writes a one-line tagline for a show from the show's real facts through a strict tool, and the app's code checks the result.

## Starting branch

The feature is on the `demo` branch, which isn't in the public repository. To prepare the demo, enter the following command:

```text
! git switch demo && uv run python -m app.seed && uv run python -m app.llm && uv run pytest
```

The command does the following, in order:

1. Switches to the `demo` branch, which is the `main` branch plus the tagline feature.
2. Resets the database to the seed data.
3. Checks the Claude API key.
4. Runs the tests.

The key check prints `OK: Claude API key works`, and every test passes. In Lab 2, attendees use a starting command with the same structure, with a `git switch -c` step that creates their lab branch.

## Background

The following list describes the feature and the rules that every Lab 2 sheet shares:

- **`get_llm` dependency**: the `app/llm.py` file gives routes the `get_llm` dependency and the `MODEL` constant (`claude-haiku-5-5`). The file reads `SHOWTIX_CLAUDE_KEY` from the `.env` file and doesn't fall back to `ANTHROPIC_API_KEY`. Every Claude call goes through the `get_llm` dependency, and tests replace it with a fake. This single dependency lets Lab 2 tests run offline in about 0.5 seconds.
- **Feature**: the `app/tagline.py` file contains a one-line `SYSTEM` prompt, the `facts` function, and the `TAGLINE_TOOL` constant. The prompt requires facts only, fewer than 80 characters, and no quotation marks. The `facts` function builds its output from the show in the database. `TAGLINE_TOOL` defines `save_tagline`, a strict tool with a `tagline` field and a `mood` enum. Strict mode enforces the structure of the reply but not its content, so the code still checks that the tagline is one line and that the mood is on the list.
- **Two request patterns**: the first demo commit asks for free text and parses it, which is the Lab 2a pattern. The second commit sends the same facts through the strict tool, which is the Lab 2b pattern. Lab 2c adds a tool loop in which Claude calls the app's functions.
- **Offline tests**: every test takes the `fake_claude` fixture, which is the `FakeClaude` class in the `tests/fakes.py` file. To write a test, queue what Claude will say, call the route, and assert on what the app returned and what the app sent. The fake can queue a thinking block before a tool call, which the real model sometimes sends. The fake can also queue failures by using the `api_error`, `connection_error`, and `timeout_error` helpers.
- **Strict-mode error**: an `enum` on a nullable field causes the API to return an HTTP `400 Bad Request` status code, and the app then returns an HTTP `502 Bad Gateway` status code. The Lab 2b sheet warns about this error.
- **Validation**: the app's code decides what's valid, and the model doesn't. In this demo, the code validates the tagline and the mood. In Lab 2, the code validates prices and seats.

**Warning**: Don't give Claude your API key. Keep the key in the `.env` file, and open that file only in your editor, with the projector off.

For more information about where Claude fits between the route and the domain modules, see [How a Lab 2 feature fits](../docs/architecture.md#4-how-a-lab-2-feature-fits).

### Unit tests and evals

Unit tests and evals check different things:

- **Unit tests**: these tests check the app's code with scripted replies. They're fast and offline, and they return the same result on every run.
- **Eval**: the eval checks the real model's behavior. The `tests/evals/tagline.json` file has three shows and the moods that fit them. The `tests/evals/run_tagline.py` file calls the API and scores each tagline on four conditions: one line, fewer than 80 characters, no quotation marks or prices, and a mood that fits.
- **`--repeat 2` flag**: attendees use the same flag on their sheets. A score that changes between runs is normal.
- **Test collection**: `pytest` doesn't collect the `tests/evals/` directory, so unit tests stay offline and fast. Evals cost money, so you run them on purpose.

## Acceptance criteria

The `demo` branch already implements and tests the following criteria. Each of criteria 1 to 6 has a test in the `tests/test_tagline.py` file, and criterion 7 is the eval:

1. The `POST /shows/{id}/tagline` endpoint returns an HTTP `200 OK` status code with `show_id`, `tagline`, and `mood`, read from the `save_tagline` tool call. The endpoint trims surrounding whitespace.
2. The request to Claude uses `MODEL`, offers exactly one tool, `save_tagline`, with `"strict": true`, and requires that tool by using `tool_choice`. The request puts the instructions in the system prompt and sends the show's facts (title, category, venue, and upcoming performances) in the user message.
3. For an unknown show ID, the endpoint returns an HTTP `404 Not Found` status code without calling Claude, and `fake_claude.calls` stays empty.
4. If the Claude call fails, the endpoint returns an HTTP `502 Bad Gateway` status code with the detail `Tagline writer unavailable`.
5. If a reply has no tool call, an empty or multi-line tagline, or a mood that isn't on the list, the endpoint returns the same status code and detail.
6. Unit tests use `fake_claude` and don't access the network, and the full test suite finishes in less than 5 seconds.
7. The eval's three cases pass when the tagline is one line of fewer than 80 characters with no quotation marks or prices, and the mood fits the show.

During the demo, you build one more test live. The test confirms that the route still works when the real model puts a thinking block before the tool call. The test covers criterion 1 with a reply format that the fake can produce.

## Workflow

The first three steps of the Lab 1 workflow are complete before the demo. For more information about why each step matters, see [How we work](00-how-we-work.md).

The demo has the following eight steps:

1. Explain the `get_llm` dependency.
2. Explain the tagline code.
3. Make two live calls.
4. Compare the two request patterns.
5. Build a test live.
6. Run the tagline tests.
7. Run the eval and read the results.
8. Prepare attendees for Lab 2.

### Step 1: Explain the `get_llm` dependency

To explain the dependency, follow these steps:

1. Open the `app/llm.py` file.
2. Highlight the `KEY_VAR = "SHOWTIX_CLAUDE_KEY"` line and the comment that says that the code doesn't fall back to `ANTHROPIC_API_KEY`.
3. In one sentence, explain that every Claude call goes through the `get_llm` dependency and that tests replace it with a fake.

### Step 2: Explain the tagline code

To explain the code, follow these steps:

1. Open the `app/tagline.py` file.
2. Explain the following parts of the file, in order:

   - The `SYSTEM` prompt
   - The `facts` function
   - `TAGLINE_TOOL` with `"strict": True`
   - The `enum` for the mood
   - The `required` list
   - `additionalProperties: False`
   - The code that reads `call.input`
   - The HTTP `502 Bad Gateway` status code for any unusable reply

### Step 3: Make two live calls

To call the endpoint on the `/docs` page, follow the steps in the [Test the endpoint in your browser](#test-the-endpoint-in-your-browser) section of this document. The text changes between calls, but the response has the same fields.

### Step 4: Compare the two request patterns

To compare the patterns, follow these steps:

1. Explain that pattern 1 is the same feature without the tool. You present pattern 1 as a diff between the two demo commits instead of a live switch.
2. List the last three commits:

   ```text
   ! git log --oneline -3
   ```

3. Compare the two commits:

   ```text
   ! git diff PLAIN_CALL_COMMIT STRICT_TOOL_COMMIT -- app/tagline.py
   ```

   Replace the following:

   - `PLAIN_CALL_COMMIT`: the hash of the commit that uses the plain call
   - `STRICT_TOOL_COMMIT`: the hash of the commit that uses the strict tool

### Step 5: Build a test live

This test has the same structure as step 2 on every Lab 2 sheet. To build the test, follow these steps:

1. Start a new conversation:

   ```text
   /clear
   ```

2. Ask Claude to add one test:

   ```text
   Read tasks/demo2-show-tagline.md, tests/test_tagline.py and tests/fakes.py. Add
   one test: the real model sometimes puts a thinking block before the tool call.
   Queue a reply on fake_claude with a thinking block and then the save_tagline
   tool call, using the fake's {"thinking": ..., "tool_use": ..., "input": {...}}
   shape, POST /shows/{id}/tagline, and assert the response is 200 with that
   tagline and mood. Also assert the request sent exactly one strict tool and that
   the show's facts are in the user message. Don't change app/. Run the file.
   ```

3. Explain that every Lab 2 test has this structure: queue what Claude will say, call the route, and assert on what the app returned and what the app sent.
4. Explain why the test passes on the first run. The code reads only `tool_use` blocks, so this test protects against a later regression.
5. Explain why the thinking block matters. In Lab 2c, attendees send Claude's reply back in a loop, and omitting the thinking block breaks the call. The fake reproduces this case at no cost. Reproducing it with the real API is expensive.

### Step 6: Run the tagline tests

To confirm that the tests pass, enter the following command:

```text
! uv run pytest tests/test_tagline.py -q
```

The tests finish in less than one second, and all of the tests pass.

### Step 7: Run the eval and read the results

To check the real model's behavior, follow these steps:

1. Run the eval against the real API:

   ```text
   ! uv run python -m tests.evals.run_tagline --repeat 2
   ```

   The output has one line per case, either `PASS (2/2) …` or `FAIL (1/2) … (80 characters)`, followed by a score out of 6.

2. Read any failing line before you change anything, and decide whether the model or the eval is wrong. For example, a tagline of exactly 80 characters breaks the rule of fewer than 80 characters. In that case, the model reached the limit, so fix the prompt and leave the eval as it is.
3. Explain that a score of 6 out of 6 tells you little by itself. Each Lab 2 sheet tells attendees to run the eval twice and read any miss.

### Step 8: Prepare attendees for Lab 2

To close the demo, follow these steps:

1. Explain that Lab 2 uses the same seven steps as Lab 1, with two additions: Claude writes an eval runner in step 3, and step 4 runs it twice.
2. Tell attendees that every Lab 2 sheet ends with an eval score, and ask them to bring their scores to the share-out.

## Test the endpoint in your browser

Use this section during [Step 3: Make two live calls](#step-3-make-two-live-calls).

### Start the app

Ask Claude to start the app:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

### Call the endpoint twice

To check criterion 1, follow these steps:

1. Open the [API documentation page](http://127.0.0.1:8000/docs).
2. Click **POST /shows/{show_id}/tagline**, and then click **Try it out**.
3. For `show_id`, enter `1`. After a fresh seed, this ID belongs to The Vanishing Ace.
4. Click **Execute**, and then read the tagline and the mood out loud.
5. Click **Execute** again. The text changes, but the response has the same fields: `show_id`, `tagline`, and `mood`.

### Stop the app

Ask Claude to stop the app:

```text
Stop the app.
```

## Completion checklist

The demo is complete when the following statements are true:

- [ ] Each of criteria 1 to 6 has a test that passes offline.
- [ ] The live test queues a thinking block before the tool call and passes.
- [ ] The request offers exactly one strict tool and sends the show's facts in the user message.
- [ ] API failures and unusable replies both return an HTTP `502 Bad Gateway` status code with the detail `Tagline writer unavailable`.
- [ ] The eval has run twice against the real API, and you read every miss before you changed anything.
- [ ] The `uv run pytest` command passes and finishes in less than 5 seconds.
- [ ] Only the `app/llm.py` file reads the key, and the key never appeared on screen.
