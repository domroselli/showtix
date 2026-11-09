# Getting started

**How to do the everyday things in the labs:** run commands, run the tests, start the app, and save your work.

- After [Prerequisites](#prerequisites) and [Get the code](#get-the-code), everything here runs inside Claude Code in a terminal. Not the desktop app: it runs your code in a cloud sandbox, so the app you start there isn't on your laptop and `/clear` isn't available.
- Every terminal command block has a copy button. Paste it into Claude Code and press Enter.

New to the workflow itself? Read `00-how-we-work.md` if you want the full detail.

## Prerequisites

Install these once, before the workshop. It takes about 20 minutes.

| You need | Why | Get it |
| --- | --- | --- |
| A Claude Pro or Max plan | Claude Code runs on it. The free plan doesn't include Claude Code. | [claude.com/pricing](https://claude.com/pricing) |
| git | Downloads the code and saves your work. On Windows, it also gives Claude Code the shell the lab commands run in. | Mac: [git-scm.com/downloads/mac](https://git-scm.com/downloads/mac) · Windows: [Git for Windows](https://git-scm.com/downloads/win) |
| uv | Installs Python and the app's packages, and runs the tests. You don't need to install Python yourself. | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Claude Code | The coding agent you'll work with. Use the terminal version; the desktop app doesn't work for these labs. | [Install Claude Code](https://code.claude.com/docs/en/setup) |
| A code editor, such as VS Code | Read the code and review Claude's changes side by side. | [code.visualstudio.com](https://code.visualstudio.com/download) |

### Install on a Mac

In **Terminal** (press Cmd+Space, type `Terminal`, press Enter). The first line offers to install git if you don't have it: accept.

```sh
git --version
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://claude.ai/install.sh | bash
```

### Install on Windows

Install [Git for Windows](https://git-scm.com/downloads/win) first, with its default options. Then, in **PowerShell** (press the Windows key, type `PowerShell`, press Enter):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
irm https://claude.ai/install.ps1 | iex
```

### Check

Open a **new** Terminal or PowerShell window, so it sees what you just installed, and run:

```sh
git --version
uv --version
claude --version
```

Each line should print a version number. Then start Claude Code once and sign in with your Pro or Max account, not a Console account (type `/exit` to leave):

```sh
claude
```

Last, make sure `ANTHROPIC_API_KEY` isn't set. If it is, Claude Code bills that key instead of your plan. Each of these should print an empty line:

- Mac:

  ```sh
  echo $ANTHROPIC_API_KEY
  ```

- Windows:

  ```powershell
  echo $env:ANTHROPIC_API_KEY
  ```

If it prints a key, remove it (on a Mac, the `export ANTHROPIC_API_KEY=...` line in `~/.zshrc`) and open a new window.

## Get the code

Download your own copy of ShowTix and check that it works. Install the [Prerequisites](#prerequisites) first.

### Mac

1. Open **Terminal** (press Cmd+Space, type `Terminal`, press Enter).
2. Copy the code into a `showtix` folder in your home folder, install what it needs, and run the tests:

   ```sh
   cd ~
   git clone https://github.com/domroselli/showtix.git
   cd showtix
   uv sync
   uv run pytest
   ```

3. Your copy is in `/Users/<your name>/showtix`.

### Windows

1. Open **PowerShell** (press the Windows key, type `PowerShell`, press Enter).
2. Copy the code into a `showtix` folder in your user folder, install what it needs, and run the tests:

   ```powershell
   cd $HOME
   git clone https://github.com/domroselli/showtix.git
   cd showtix
   uv sync
   uv run pytest
   ```

3. Your copy is in `C:\Users\<your name>\showtix`.

The last line should say something like `113 passed`. A "not found" error means a prerequisite isn't installed yet: see [Check](#check).

## Open ShowTix in Claude Code

Claude Code works on the folder it was started in, so start it in your `showtix` folder.

- **In a terminal** (Terminal on a Mac, PowerShell on Windows): go to the folder and start Claude Code. Type `/exit` to leave.

  ```sh
  cd ~/showtix
  claude
  ```

- **Not the desktop app.** It runs commands in a cloud sandbox, so the app wouldn't be at `127.0.0.1:8000` on your laptop, and `/clear` doesn't exist there. If it's what you have installed, install the terminal version too (see [Prerequisites](#prerequisites)).
- **Sign in** with your own Claude Pro or Max plan, not a Console account.

You're ready when Claude Code shows a prompt waiting for you to type.

## Set up VS Code (optional)

ShowTix recommends four extensions. Open your `showtix` folder in VS Code (**File > Open Folder**) and click **Install** when VS Code offers them. Missed the offer? Open the Extensions panel and search for `@recommended`.

| Extension | What it gives you |
| --- | --- |
| Claude Code | Shows Claude's proposed edits in VS Code's side-by-side diff view. |
| Markdown Preview GitHub Styling | Makes VS Code's preview of the lab sheets look like GitHub. |
| Python | Colors the code, flags errors, and lets you Cmd-click or Ctrl-click a function to jump to it. |
| SQLite Viewer | Click `showtix.db` to look at the shows, orders and other tables. |

To use Claude Code with VS Code, open **Terminal > New Terminal** and run `claude` there. It connects to the extension on its own.

**Use the terminal, not the Claude Code chat panel.** The panel doesn't support the `!` commands in the lab sheets.

To read a lab sheet, open it and press Cmd+Shift+V (Mac) or Ctrl+Shift+V (Windows).

## Run a command yourself

To run a terminal command yourself from Claude Code, without asking Claude to do it, start the line with `!`. The output shows up in the conversation, and Claude sees it too.

```text
! uv run pytest
```

- `&&` runs commands one after another and stops at the first one that fails.
- A line without `!` goes to Claude as a request.
- Pasting a line that starts with `!` switches Claude Code to command mode on its own.

Every command in the lab sheets starts with `!`, so you can copy it as is.

## Start fresh

`/clear` empties Claude's memory of the conversation, so it starts the next task without old ideas.

```text
/clear
```

- Use it at the start of every lab.
- Use it before writing tests and before implementing (steps 2 and 3 of the workflow), so Claude works from the sheet and your committed tests, not the chat.
- Use it when a conversation has gone off track.

Your files and commits aren't affected; only the conversation is cleared.

## Start a lab branch

Each lab gets its own branch, made from `main`, so labs don't mix. The command also resets the database, so every lab starts from the same data. Your sheet's **Starting branch** section has the exact command. It looks like this:

```text
! git switch main && uv run python -m app.seed && git switch -c lab1a-category-filter && uv run pytest
```

That's four commands joined by `&&`. Here's what each one does, in order:

| Command | What it does |
| --- | --- |
| `git switch main` | Moves you to the `main` branch, so your new branch starts from the original code, not from another lab. |
| `uv run python -m app.seed` | Resets the database to the starting data. See [Reset the database](#reset-the-database). |
| `git switch -c lab1a-category-filter` | Creates a new branch with this name and moves you onto it. `-c` means create. Your commits for this lab go here. |
| `uv run pytest` | Runs all the tests, to prove everything works before you start. |

- Every test should pass before you change anything.
- If you have uncommitted work from another lab, `git switch` stops and says so. [Commit](#commit) it first.
- To see which branch you're on:

  ```text
  ! git branch --show-current
  ```

The last line of the test run should say `passed`, with no `failed`.

## Run the tests

The full suite takes under 5 seconds, so run it often.

```text
! uv run pytest
```

- One file:

  ```text
  ! uv run pytest tests/test_shows.py
  ```

- Only tests whose name contains a word:

  ```text
  ! uv run pytest -k category
  ```

- Stop at the first failure, and show each test's name:

  ```text
  ! uv run pytest -x -v
  ```

The last line counts what passed and failed. Read the first failure first; later ones often follow from it.

## Start the app

The app is a web server, and a server keeps running until you stop it. A `!` command waits for its command to finish, so ask Claude to start the app in the background instead:

```text
Start the app in the background with uv run uvicorn app.main:app --reload,
and tell me when it's ready.
```

- Claude asks permission to run it: approve.
- Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) for the ticket shop, or [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try the API (see [Try an endpoint in /docs](#try-an-endpoint-in-docs)).
- `--reload` restarts the app whenever the code changes, so you don't have to.

Changed the database schema? [Reset the database](#reset-the-database) first, or the pages will break even while the tests pass.

## Try an endpoint in /docs

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) lists every API endpoint and lets you call one from your browser.

1. Click an endpoint, for example **GET /shows**.
2. Click **Try it out**, fill in any parameters, then click **Execute**.
3. Scroll down to **Server response**: **Code** is the status code (200, 400, 404 …) and **Response body** is what came back.

The **Request URL** box shows the link for the same request, which you can open directly in your browser.

## Use the web UI

[http://127.0.0.1:8000/](http://127.0.0.1:8000/) is the ShowTix site. To place an order:

1. Click a date under any show.
2. In the **Qty** column, enter how many tickets you want. If you have a promo code, type it in **Promo code**. Click **Get quote**.
3. Read the price breakdown. To try a different cart, go back to the date page.
4. Enter any email and click **Place order**. You land on the order's page.

## Stop the app

Stop the app when you're done checking, or before starting it again.

```text
Stop the app.
```

- You can also stop it yourself: type `/tasks` and stop it from the list.
- Quitting Claude Code stops it too.
- "Address already in use" means the app is still running: stop it, then start it again.

## Reset the database

The running app keeps its data in `showtix.db`. Resetting puts back the starting data from [`docs/seed-data.md`](../docs/seed-data.md).

```text
! uv run python -m app.seed
```

- Do it after a schema change (a new table or column in `app/db.py`).
- Do it when the pages look strange, or you want a clean start.
- It deletes everything you added in the browser. Tests aren't affected: they use their own database.

The running app picks up the fresh database on its next request; no restart needed.

## See what changed

Before you commit, look at what you're about to save.

```text
! git status
```

That lists the changed files.

To see every change, including new files:

```text
! git add -A && git diff --staged
```

- `git add -A` only stages changes; nothing is saved until you commit.
- In VS Code, the **Source Control** panel shows the same changes side by side.

Your tests are committed before Claude implements, so the diff after that shows only the code Claude wrote.

## Check your tests didn't change

Your tests are committed before Claude implements, so a change to them, or to how they run, shows up in git.

```text
! git status --short
```

- Every file it lists should be under `app/` (or be `CLAUDE.md`, if Claude updated the rule text with the code).
- A file in `tests/` (changed, or new with `??`), a `conftest.py`, or `pyproject.toml` means Claude touched your tests or how they run. Ask Claude what it changed and why.
- On labs built slice by slice (1e, 1f, 2c), you commit after each slice, so also run this. It should list only your tests commit:

  ```text
  ! git log --oneline --stat main..HEAD -- tests/ conftest.py pyproject.toml
  ```

Then check the last line of the test run: it should say only `passed`, with no `skipped`, `deselected` or `xfailed`. Changed tests aren't always wrong, but you decide, not Claude.

## Commit

A commit is a safe point: if anything goes wrong later, you can get back here.

```text
! git add -A && git commit -m "lab1a: tests"
```

- Your sheet gives the exact message for each commit.
- `-A` includes new files, such as a new test file.
- Commit your tests before Claude implements, and again when you're happy with the change.

Committing often costs nothing, and every commit is a point you can return to.

## Set up your API key (Lab 2)

Lab 2 features call the Claude API with a key of their own, kept in a file called `.env` that git never saves.

1. Make your own `.env` from the example:

   ```text
   ! cp .env.example .env
   ```

2. Open `.env` in your editor and paste your key after `SHOWTIX_CLAUDE_KEY=`. Use `.env`, never `.env.example`, which git does save.

   **Never paste the key into Claude Code**, in a prompt or a `!` command. Anything you type there becomes part of the conversation, and Claude can copy it into a file and from there into a commit. Your editor is the only place the key should go.

3. Check that the key works. It should print `OK: Claude API key works`:

   ```text
   ! uv run python -m app.llm
   ```

If the check fails, its message says what to fix (a missing key, a rejected key, no credits, no connection). The app only reads `SHOWTIX_CLAUDE_KEY`; never put the key in `ANTHROPIC_API_KEY`, or Claude Code bills that key instead of your plan.
