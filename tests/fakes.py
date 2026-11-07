"""Test doubles. FakeClaude stands in for anthropic.Anthropic so tests never touch the network."""

from types import SimpleNamespace

import anthropic
import httpx2
import pytest

ERRORS_BY_STATUS = {
    400: anthropic.BadRequestError,
    401: anthropic.AuthenticationError,
    429: anthropic.RateLimitError,
    500: anthropic.InternalServerError,
    529: anthropic.OverloadedError,
}


def api_error(status_code: int = 529, message: str = "Overloaded") -> anthropic.APIStatusError:
    """An SDK error as the real client would raise it, for fake.queue(api_error(429, "Rate limited"))."""
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    body = {"type": "error", "error": {"type": "api_error", "message": message}}
    response = httpx2.Response(status_code, request=request, json=body)
    error_class = ERRORS_BY_STATUS.get(status_code, anthropic.APIStatusError)
    return error_class(message, response=response, body=body)


def connection_error() -> anthropic.APIConnectionError:
    """The SDK error for a network failure (no Wi-Fi, DNS, proxy), for fake.queue(connection_error())."""
    return anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))


def timeout_error() -> anthropic.APITimeoutError:
    """The SDK error for a request that timed out, for fake.queue(timeout_error())."""
    return anthropic.APITimeoutError(request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))


FAKE_SIGNATURE = "sig_fake"


class FakeClaude:
    """Shaped like anthropic.Anthropic: fake.messages.create(**kwargs) returns queued replies in order.

    fake.queue("text reply", {"tool_use": "name", "input": {...}}, api_error(500))

    Add "thinking" to a tool call to put a thinking block before it, as the real model can:
    {"thinking": "Let me check.", "tool_use": "name", "input": {...}}
    """

    def __init__(self):
        self.calls: list[dict] = []
        self._replies: list = []
        self._tool_ids = 0
        self.messages = SimpleNamespace(create=self._create)

    def queue(self, *items) -> None:
        self._replies.extend(items)

    @property
    def last_prompt(self) -> str:
        """The last call's system prompt plus the text of all its user messages."""
        if not self.calls:
            return ""
        call = self.calls[-1]
        parts = [_text(call.get("system", ""))]
        parts += [_text(m["content"]) for m in call.get("messages", []) if m["role"] == "user"]
        return "\n".join(p for p in parts if p)

    def _create(self, **kwargs):
        # Snapshot the messages list: a tool loop appends to the same list after this call,
        # and each record should show what was sent at the time.
        self.calls.append({**kwargs, "messages": list(kwargs.get("messages", []))})
        if not self._replies:
            pytest.fail("FakeClaude got an unexpected call")
        item = self._replies.pop(0)
        if isinstance(item, Exception):
            raise item
        model = kwargs.get("model")
        if isinstance(item, str):
            block = SimpleNamespace(type="text", text=item)
            return SimpleNamespace(content=[block], stop_reason="end_turn", model=model)
        self._tool_ids += 1
        block = SimpleNamespace(
            type="tool_use", id=f"toolu_fake_{self._tool_ids}", name=item["tool_use"], input=item["input"]
        )
        content = [block]
        if "thinking" in item:
            thinking = SimpleNamespace(type="thinking", thinking=item["thinking"], signature=FAKE_SIGNATURE)
            content = [thinking, block]
        return SimpleNamespace(content=content, stop_reason="tool_use", model=model)


def _text(content) -> str:
    """Text from a string or a list of content blocks; non-text blocks are skipped."""
    if isinstance(content, str):
        return content
    return "\n".join(b["text"] for b in content if b.get("type") == "text")
