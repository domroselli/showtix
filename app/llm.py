"""The one place the app talks to the Claude API. Run `uv run python -m app.llm` to check your key."""

import os
import sys
from collections.abc import Callable
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from app.errors import ServiceUnavailable

MODEL = "claude-haiku-5-5"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
KEY_VAR = "SHOWTIX_CLAUDE_KEY"


def get_llm() -> anthropic.Anthropic:
    """FastAPI dependency: a Claude client built from SHOWTIX_CLAUDE_KEY. Tests override it with fake_claude."""
    load_dotenv(ENV_PATH)
    key = os.environ.get(KEY_VAR, "").strip()
    if not key:
        raise ServiceUnavailable(f"Claude API key not configured: set {KEY_VAR} in .env")
    # Pass the key explicitly so the SDK never falls back to ANTHROPIC_API_KEY.
    return anthropic.Anthropic(api_key=key, timeout=30, max_retries=1)


def check_key(get_client: Callable = get_llm) -> tuple[bool, str]:
    """Make one tiny call and return (ok, one line to print), with a fix-it hint on failure."""
    try:
        client = get_client()
        client.messages.create(
            model=MODEL, max_tokens=1024, messages=[{"role": "user", "content": "Reply with OK"}]
        )
    except ServiceUnavailable as e:
        return False, str(e)
    except anthropic.AuthenticationError:
        return False, f"Claude API key rejected (401): paste a current key from the Claude Console into {KEY_VAR} in .env"
    except (anthropic.RateLimitError, anthropic.OverloadedError) as e:
        return False, f"Claude API is rate limited or overloaded ({e.status_code}): wait a minute and run the check again"
    except anthropic.APIStatusError as e:
        if e.status_code == 402 or "credit balance" in e.message.lower():
            return False, f"No credits or a billing problem ({e.status_code}): redeem your credit code or add credits in the Claude Console"
        return False, f"Claude API error ({e.status_code}): {e.message}"
    except anthropic.APIConnectionError:
        return False, "Can't reach the Claude API: check your internet connection, VPN or proxy"
    return True, "OK: Claude API key works"


def main() -> int:
    ok, message = check_key()
    print(message, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
