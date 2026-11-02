import socket

import anthropic
import pytest
from fastapi import Depends

from app import llm
from app.errors import ServiceUnavailable
from tests.fakes import FakeClaude, api_error, connection_error


@pytest.fixture
def env(monkeypatch, tmp_path):
    """No key anywhere: an empty .env and neither variable set. Returns the .env path to write to."""
    env_file = tmp_path / ".env"
    env_file.write_text("")
    monkeypatch.setattr(llm, "ENV_PATH", env_file)
    for var in ("SHOWTIX_CLAUDE_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")  # records the original, so a key load_dotenv sets is undone too
        monkeypatch.delenv(var)
    return env_file


def test_missing_key_raises_503(env):
    with pytest.raises(ServiceUnavailable) as exc:
        llm.get_llm()
    assert exc.value.status_code == 503
    assert str(exc.value) == "Claude API key not configured: set SHOWTIX_CLAUDE_KEY in .env"


def test_blank_key_counts_as_missing(env, monkeypatch):
    monkeypatch.setenv("SHOWTIX_CLAUDE_KEY", "  ")
    with pytest.raises(ServiceUnavailable):
        llm.get_llm()


def test_anthropic_api_key_is_ignored(env, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-wrong")
    with pytest.raises(ServiceUnavailable):
        llm.get_llm()


def test_key_comes_from_showtix_claude_key(env, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-wrong")
    monkeypatch.setenv("SHOWTIX_CLAUDE_KEY", "sk-ant-showtix")
    client = llm.get_llm()
    assert isinstance(client, anthropic.Anthropic)
    assert client.api_key == "sk-ant-showtix"
    assert client.timeout == 30
    assert client.max_retries == 1


def test_key_is_loaded_from_env_file(env):
    env.write_text("SHOWTIX_CLAUDE_KEY=sk-ant-from-file\n")
    client = llm.get_llm()
    assert client.api_key == "sk-ant-from-file"


def test_fake_returns_queued_text_then_tool_call():
    fake = FakeClaude()
    fake.queue("Hello", {"tool_use": "find_shows", "input": {"category": "comedy"}})

    first = fake.messages.create(model=llm.MODEL, max_tokens=100, messages=[])
    assert first.stop_reason == "end_turn"
    assert first.model == llm.MODEL
    assert [(b.type, b.text) for b in first.content] == [("text", "Hello")]

    second = fake.messages.create(model=llm.MODEL, max_tokens=100, messages=[])
    assert second.stop_reason == "tool_use"
    [block] = second.content
    assert (block.type, block.id, block.name, block.input) == (
        "tool_use", "toolu_fake_1", "find_shows", {"category": "comedy"}
    )


def test_fake_raises_queued_exception():
    fake = FakeClaude()
    fake.queue(ValueError("boom"))
    with pytest.raises(ValueError, match="boom"):
        fake.messages.create(model=llm.MODEL, messages=[])


def test_api_error_builds_sdk_errors():
    err = api_error(429, "Rate limited")
    assert isinstance(err, anthropic.RateLimitError)
    assert err.status_code == 429
    assert err.message == "Rate limited"
    assert isinstance(api_error(), anthropic.OverloadedError)
    assert type(api_error(503)) is anthropic.APIStatusError

    fake = FakeClaude()
    fake.queue(api_error(500, "Server error"))
    with pytest.raises(anthropic.InternalServerError):
        fake.messages.create(model=llm.MODEL, messages=[])


def test_fake_records_calls_and_last_prompt():
    fake = FakeClaude()
    fake.queue("one", "two")
    fake.messages.create(model=llm.MODEL, system="Be brief.", messages=[{"role": "user", "content": "First"}])
    fake.messages.create(
        model=llm.MODEL,
        system=[{"type": "text", "text": "You sell tickets."}],
        messages=[
            {"role": "user", "content": "Any comedy?"},
            {"role": "assistant", "content": "Let me check."},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "toolu_fake_1", "content": "2 shows"},
                {"type": "text", "text": "Cheapest?"},
            ]},
        ],
    )
    assert len(fake.calls) == 2
    assert fake.calls[0]["system"] == "Be brief."
    assert fake.last_prompt == "You sell tickets.\nAny comedy?\nCheapest?"


def test_fake_fails_on_unexpected_call():
    fake = FakeClaude()
    with pytest.raises(pytest.fail.Exception, match="FakeClaude got an unexpected call"):
        fake.messages.create(model=llm.MODEL, messages=[])


def test_fake_claude_fixture_replaces_get_llm(fake_claude):
    from app.main import app

    assert app.dependency_overrides[llm.get_llm]() is fake_claude


def test_routes_get_the_fake_without_asking_for_it(client, monkeypatch):
    """No fake_claude fixture here: the autouse fake still answers, and the network is never touched."""
    from app.main import app

    def no_network(*args):
        raise AssertionError("test tried to open a network connection")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setenv("SHOWTIX_CLAUDE_KEY", "sk-ant-real-looking")  # the real client would build fine

    def probe(claude=Depends(llm.get_llm)):
        reply = claude.messages.create(model=llm.MODEL, max_tokens=10, messages=[])
        return {"client": type(claude).__name__, "text": reply.content[0].text}

    app.add_api_route("/_probe", probe)
    try:
        fake = app.dependency_overrides[llm.get_llm]()
        fake.queue("hi from the fake")
        response = client.get("/_probe")
    finally:
        app.router.routes.pop()

    assert response.json() == {"client": "FakeClaude", "text": "hi from the fake"}
    assert len(fake.calls) == 1


def test_key_check_ok_makes_one_tiny_call():
    fake = FakeClaude()
    fake.queue("OK")
    assert llm.check_key(lambda: fake) == (True, "OK: Claude API key works")
    assert fake.calls == [
        {"model": llm.MODEL, "max_tokens": 1024, "messages": [{"role": "user", "content": "Reply with OK"}]}
    ]


def test_key_check_missing_key(env):
    assert llm.check_key() == (False, "Claude API key not configured: set SHOWTIX_CLAUDE_KEY in .env")


CREDIT_MESSAGE = (
    "Your credit balance is too low to access the Anthropic API. "
    "Please go to Plans & Billing to upgrade or purchase credits."
)


@pytest.mark.parametrize(
    "error, message",
    [
        (api_error(401, "invalid x-api-key"),
         "Claude API key rejected (401): paste a current key from the Claude Console into SHOWTIX_CLAUDE_KEY in .env"),
        (api_error(400, CREDIT_MESSAGE),
         "No credits or a billing problem (400): redeem your credit code or add credits in the Claude Console"),
        (api_error(402, "Billing error"),
         "No credits or a billing problem (402): redeem your credit code or add credits in the Claude Console"),
        (api_error(429, "Rate limited"),
         "Claude API is rate limited or overloaded (429): wait a minute and run the check again"),
        (api_error(529, "Overloaded"),
         "Claude API is rate limited or overloaded (529): wait a minute and run the check again"),
        (connection_error(),
         "Can't reach the Claude API: check your internet connection, VPN or proxy"),
        (api_error(500, "Server error"), "Claude API error (500): Server error"),
    ],
)
def test_key_check_failure_messages(error, message):
    fake = FakeClaude()
    fake.queue(error)
    assert llm.check_key(lambda: fake) == (False, message)


@pytest.mark.parametrize(
    "result, code, out, err",
    [
        ((True, "OK: Claude API key works"), 0, "OK: Claude API key works\n", ""),
        ((False, "Can't reach the Claude API"), 1, "", "Can't reach the Claude API\n"),
    ],
)
def test_key_check_main_prints_one_line_and_sets_exit_code(monkeypatch, capsys, result, code, out, err):
    monkeypatch.setattr(llm, "check_key", lambda: result)
    assert llm.main() == code
    assert capsys.readouterr() == (out, err)
