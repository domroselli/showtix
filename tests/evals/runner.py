"""Shared eval runner. Evals call the real API, so pytest never collects this folder (see tests/conftest.py).

A feature's eval script, run with `uv run python -m tests.evals.run_<feature> [--repeat N]`:

    from tests.evals.runner import run

    def check(case) -> tuple[bool, str]:
        ...  # call your feature with the real client from app/llm.py
        return got == case["expected"], f"got {got}"

    if __name__ == "__main__":
        run("tests/evals/<feature>.json", check)
"""

import argparse
import json
from collections.abc import Callable
from pathlib import Path

Check = Callable[[dict], tuple[bool, str]]


def run(cases_file: str | Path, check: Check, argv: list[str] | None = None) -> tuple[int, int]:
    """Run check(case) on every case (N times with --repeat N), print one line per case and the score."""
    parser = argparse.ArgumentParser(description="Run an eval against the real Claude API.")
    parser.add_argument("--repeat", type=int, default=1, metavar="N", help="run every case N times")
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    cases = json.loads(Path(cases_file).read_text())
    passed = 0
    for number, case in enumerate(cases, 1):
        name = case.get("name", f"case {number}")
        results = [_check_once(check, case) for _ in range(args.repeat)]
        wins = sum(ok for ok, _ in results)
        passed += wins
        # Show the first failure's detail, since that's the one to read before changing anything.
        detail = next((d for ok, d in results if not ok), results[-1][1])
        mark = "PASS" if wins == args.repeat else "FAIL"
        count = f" ({wins}/{args.repeat})" if args.repeat > 1 else ""
        print(f"{mark}{count} {name}: {detail}")

    total = len(cases) * args.repeat
    print(f"Score: {passed}/{total}")
    return passed, total


def _check_once(check: Check, case: dict) -> tuple[bool, str]:
    """One run of check; an exception fails the case instead of stopping the eval."""
    try:
        ok, detail = check(case)
    except Exception as e:
        return False, f"error: {type(e).__name__}: {e}"
    return bool(ok), detail
