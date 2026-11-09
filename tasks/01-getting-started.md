# Getting started

This page explains the everyday tasks in the labs: how to run commands, run the tests, start the app, and save your work.

After you complete the [Prerequisites](#prerequisites) and [Get the code](#get-the-code) sections, everything on this page runs inside Claude Code in a terminal, not in the desktop app or the VS Code chat panel. For the reasons, see the [Open ShowTix in Claude Code](#open-showtix-in-claude-code) section of this document.

On GitHub, every command block on this page has a copy button. To run a command, paste it into Claude Code and press Enter.

For the workflow that every lab follows, see [How we work](00-how-we-work.md).

## Prerequisites

Install the following tools once, before the workshop. The installation takes about 20 minutes.

| You need | Why | Get it |
| --- | --- | --- |
| A Claude Pro or Max plan | Claude Code is included in these plans. The free plan doesn't include Claude Code. | [claude.com/pricing](https://claude.com/pricing) |
| git | Downloads the code and saves your work. On Windows, it also gives Claude Code the shell that the lab commands run in. | Mac: [git-scm.com/downloads/mac](https://git-scm.com/downloads/mac). Windows: [Git for Windows](https://git-scm.com/downloads/win) |
| uv | Installs Python and the app's packages, and runs the tests. You don't need to install Python yourself. | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Claude Code | The coding agent that you work with. Use the terminal version, because the desktop app doesn't work for these labs. | [Install Claude Code](https://code.claude.com/docs/en/setup) |
| A code editor, such as VS Code | Lets you read the code and review Claude's changes side by side. | [code.visualstudio.com](https://code.visualstudio.com/download) |

### Install on a Mac

Open Terminal: press Cmd+Space, type `Terminal`, and press Enter. Then install git, uv, and Claude Code:

```sh
git --version
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://claude.ai/install.sh | bash
```

If git isn't installed, the first line offers to install it. Accept the offer.

### Install on Windows

Install [Git for Windows](https://git-scm.com/downloads/win) first, with its default options. Then open PowerShell: press the Windows key, type `PowerShell`, and press Enter. Install uv and Claude Code:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
irm https://claude.ai/install.ps1 | iex
```

### Check

Open a new Terminal or PowerShell window, so that it detects the tools that you installed. Then print the version of each tool:

```sh
git --version
uv --version
claude --version
```

Each line prints a version number.

Next, start Claude Code and sign in with your Pro or Max account, not a Console account:

```sh
claude
```

To leave Claude Code, type `/exit`.

Last, confirm that the `ANTHROPIC_API_KEY` variable isn't set. If it's set, Claude Code offers to use that key instead of your plan, and an accepted offer is remembered. Print the variable for your system:

- Mac:

  ```sh
  echo $ANTHROPIC_API_KEY
  ```

- Windows:

  ```powershell
  echo $env:ANTHROPIC_API_KEY
  ```

The command prints an empty line. If it prints a key, remove the key and open a new window. On a Mac, look for an `export ANTHROPIC_API_KEY=...` line in the `~/.zshrc` file, or in the `~/.zprofile` or `~/.zshenv` file.

## Get the code

This section explains how to download your own copy of ShowTix and check that it works. Install the [Prerequisites](#prerequisites) first.

### Mac

To get the code on a Mac, follow these steps:

1. Open Terminal: press Cmd+Space, type `Terminal`, and press Enter.
2. Copy the code into a `showtix` folder in your home folder, install what it needs, and run the tests:

   ```sh
   cd ~
   git clone https://github.com/domroselli/showtix.git
   cd showtix
   uv sync
   uv run pytest
   ```

   Your copy is in the `/Users/<your name>/showtix` folder.

### Windows

To get the code on Windows, follow these steps:

1. Open PowerShell: press the Windows key, type `PowerShell`, and press Enter.
2. Copy the code into a `showtix` folder in your user folder, install what it needs, and run the tests:

   ```powershell
   cd $HOME
   git clone https://github.com/domroselli/showtix.git
   cd showtix
   uv sync
   uv run pytest
   ```

   Your copy is in the `C:\Users\<your name>\showtix` folder.

The last line of the test output says something like `113 passed`. A "not found" error means that a prerequisite isn't installed yet. For more information, see the [Check](#check) section of this document.

## Open ShowTix in Claude Code

Claude Code works on the folder that it starts in, so start it in your `showtix` folder.

To open ShowTix in Claude Code, follow these steps:

1. In a terminal (Terminal on a Mac, PowerShell on Windows), go to the folder and start Claude Code:

   ```sh
   cd ~/showtix
   claude
   ```

2. Sign in with your own Claude Pro or Max plan, not a Console account.

You're ready when Claude Code shows a prompt that waits for you to type.

**Caution**: Don't use the desktop app or the VS Code chat panel for the labs. The lab sheets rely on the terminal's `!` commands, which those two don't support, and on an app that runs at `127.0.0.1:8000` on your laptop. If the desktop app is what you have installed, also install the terminal version. For more information, see the [Prerequisites](#prerequisites) section of this document.

## Optional: Set up VS Code

ShowTix recommends four extensions. To install them, open your `showtix` folder in VS Code (**File > Open Folder**) and click **Install** when VS Code offers them. If you missed the offer, open the **Extensions** panel and search for `@recommended`.

The following table describes the extensions:

| Extension | What it gives you |
| --- | --- |
| Claude Code | Shows Claude's proposed edits in VS Code's side-by-side diff view. |
| Markdown Preview GitHub Styling | Makes VS Code's preview of the lab sheets look like GitHub. |
| Python | Colors the code, flags errors, and lets you Cmd-click or Ctrl-click a function to jump to it. |
| SQLite Viewer | Lets you click the `showtix.db` file to look at the shows, orders, and other tables. |

To use Claude Code with VS Code, open **Terminal > New Terminal** and run `claude` there. Claude Code connects to the extension on its own.

Use the terminal, not the Claude Code chat panel. The panel doesn't support the `!` commands in the lab sheets.

To read a lab sheet in VS Code, open the sheet and press Cmd+Shift+V (Mac) or Ctrl+Shift+V (Windows).

## Run a command yourself

To run a terminal command yourself from Claude Code, without asking Claude to do it, start the line with `!`. The output appears in the conversation, and Claude reads it too. For example, run the tests:

```text
! uv run pytest
```

The following notes apply to `!` commands:

- `&&` runs commands one after another and stops at the first one that fails.
- A line without `!` goes to Claude as a request.
- When you paste a line that starts with `!`, Claude Code switches to command mode on its own.

Every command in the lab sheets starts with `!`, so you can copy it as is.

## Start fresh

The `/clear` command empties Claude's memory of the conversation, so Claude starts the next task without old ideas:

```text
/clear
```

Use the command at the following times:

- At the start of every lab.
- Before steps 2 and 3 of the workflow, when Claude writes tests and when Claude implements. Claude then works from the sheet and your committed tests, not from the chat.
- When a conversation has gone off track.

The command clears only the conversation. Your files and commits aren't affected.

## Start a lab branch

Each lab gets its own branch, made from `main`, so that labs don't mix. The starting command also resets the database, so every lab starts from the same data. Your sheet's **Starting branch** section has the exact command, which looks like this:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1a-category-filter && uv run pytest
```

The Lab 1 line is four commands joined by `&&`. Lab 2 sheets add a fifth, `uv run python -m app.llm`, which checks your API key. The following table describes each command, in order:

| Command | What it does |
| --- | --- |
| `git switch main` | Moves you to the `main` branch, so that your new branch starts from the original code, not from another lab. |
| `uv run python -m app.seed` | Resets the database to the starting data. See [Reset the database](#reset-the-database). |
| `git switch -c lab1a-category-filter` | Creates a branch with this name and moves you onto it. The `-c` flag means create. Your commits for this lab go here. |
| `uv run pytest` | Runs all of the tests, to prove that everything works before you start. |
| `uv run python -m app.llm` (Lab 2) | Checks that your Claude API key works. See [Set up your API key](#set-up-your-api-key-lab-2). |

Every test must pass before you change anything. The last line of the test run says `passed`, with no `failed`.

The following notes apply to the starting command:

- If you have uncommitted work from another lab, [commit](#commit) it before you run the starting command. When the changes conflict with `main`, `git switch` stops and says so. When they don't, `git switch` carries them onto the new branch, and the lab starts with another lab's edits. Run `! git status --short` first; the list must be empty.
- To see which branch you're on, print its name:

  ```text
  ! git branch --show-current
  ```

## Run the tests

The full suite takes less than 5 seconds, so run it often:

```text
! uv run pytest
```

You can also run part of the suite:

- Run one file:

  ```text
  ! uv run pytest tests/test_shows.py
  ```

- Run only the tests whose name contains a word:

  ```text
  ! uv run pytest -k category
  ```

- Stop at the first failure, and show each test's name:

  ```text
  ! uv run pytest -x -v
  ```

The last line counts what passed and failed. Read the first failure first, because later failures often follow from it.

## Start the app

The app is a web server, and a server keeps running until you stop it. A `!` command waits for its command to finish, so ask Claude to start the app in the background instead:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

Claude asks for permission to run the command. Approve it.

When the app is ready, open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) for the ticket shop, or [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try the API. For more information, see the [Try an endpoint in /docs](#try-an-endpoint-in-docs) section of this document.

The `--reload` flag restarts the app whenever the code changes, so you don't have to.

**Caution**: If you changed the database schema, [reset the database](#reset-the-database) before you open the app. Otherwise, the pages break even though the tests pass.

## Try an endpoint in /docs

The page at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) lists every API endpoint and lets you call one from your browser.

To call an endpoint, follow these steps:

1. Click an endpoint, for example **GET /shows**.
2. Click **Try it out**, fill in any parameters, and then click **Execute**.
3. Scroll down to **Server response**. **Code** is the status code, such as `200`, `400`, or `404`, and **Response body** is what came back.

The **Request URL** box shows the link for the same request. You can open that link directly in your browser.

## Use the web UI

The ShowTix site is at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

To place an order, follow these steps:

1. Click a night under any show.
2. In the **Qty** column, enter how many tickets you want.
3. If you have a promo code, type it in **Promo code**.
4. Click **Get quote**, and read the price breakdown. To try a different cart, go back to the night's page.
5. Enter any email and click **Place order**. You land on the order's page.

## Stop the app

Stop the app when you're done checking, or before you start it again. Ask Claude to stop it:

```text
Stop the app.
```

You can also stop the app in the following ways:

- Type `/tasks` and stop the app from the list.
- Quit Claude Code, which stops the app too.

An "Address already in use" error means that the app is still running. Stop it, and then start it again.

## Reset the database

The running app keeps its data in the `showtix.db` file. A reset deletes the file and rebuilds it from the `app/seed.py` file. The [Seed data](../docs/seed-data.md) page lists that data:

```text
! uv run python -m app.seed
```

Reset the database at the following times:

- After a schema change, such as a new table or column in the `app/db.py` file.
- When the pages look strange, or when you want a clean start.

A reset deletes everything that you added in the browser. Tests aren't affected, because they use their own database. The running app picks up the fresh database on its next request, so you don't need to restart it.

## See what changed

Before you commit, look at what you're about to save. List the changed files:

```text
! git status
```

To see every change, including new files, stage the changes and show the diff:

```text
! git add -A && git diff --staged
```

The `git add -A` command only stages changes. Nothing is saved until you commit. In VS Code, the **Source Control** panel shows the same changes side by side.

Your tests are committed before Claude implements, so the diff after that point shows only the code that Claude wrote.

## Check your tests didn't change

Your tests are committed before Claude implements, so a change to them, or to how they run, appears in git. List the changed files:

```text
! git status --short
```

Check the list against the following rules:

- Every file in the list must be under `app/`.
- A changed or new (`??`) file in `tests/`, a `conftest.py` file, or the `pyproject.toml` file means that Claude touched your tests or how they run. Ask Claude what changed and why.
- On labs built slice by slice (1e, 1f, 2c), you commit after each slice, so also list the commits that touched the tests. The list contains your tests commit, plus any commit that your sheet tells you to expect, such as the eval runner on Lab 2c or a fix to a wrong test that you asked for:

  ```text
  ! git log --oneline --stat main..HEAD -- tests/ conftest.py pyproject.toml
  ```

Then check the last line of the test run. It says only `passed`, with no `skipped`, `deselected`, or `xfailed`. Changed tests aren't always wrong, but you decide, not Claude.

## Commit

A commit is a safe point. If anything goes wrong later, you can get back to it. Stage every change and commit it:

```text
! git add -A && git commit -m "lab1a: tests"
```

The following rules apply to commits in the labs:

- Your sheet gives the exact message for each commit.
- The `-A` flag includes new files, such as a new test file.
- Commit your tests before Claude implements, and commit again when you're satisfied with the change.

## Set up your API key (Lab 2)

Lab 2 features call the Claude API with a key of their own, kept in a file named `.env` that git never saves.

To set up the key, follow these steps:

1. Create a key in the Claude Console at platform.claude.com. Sign in with the account that holds your workshop credits, because the credits are tied to that account, not to the key. Open **API keys** and create a key. The key is shown once, so keep the page open until step 3.
2. Make your own `.env` file from the example:

   ```text
   ! cp .env.example .env
   ```

3. Open the `.env` file in your editor and paste your key after `SHOWTIX_CLAUDE_KEY=`. Use the `.env` file, never the `.env.example` file, which git does save.
4. Check that the key works:

   ```text
   ! uv run python -m app.llm
   ```

   The check prints `OK: Claude API key works`. If the check fails, its message says what to fix: a missing key, a rejected key, no credits, a rate limit, or no connection.

**Warning**: Never paste the key into Claude Code, in a prompt or in a `!` command. Anything that you type there becomes part of the conversation, and Claude can copy it into a file and from there into a commit. Your editor is the only place that the key goes. Also, don't put the key in `ANTHROPIC_API_KEY`: the app reads only `SHOWTIX_CLAUDE_KEY`, and Claude Code offers to bill a key in `ANTHROPIC_API_KEY` instead of your plan.
