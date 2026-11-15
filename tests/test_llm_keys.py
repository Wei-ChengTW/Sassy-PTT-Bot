"""測試 llm_keys：各任務的 key 順序、哪些錯誤要換 key、聊天路徑的換 key。"""
import asyncio

import pytest

from llm_keys import is_key_problem, key_pool


@pytest.fixture
def keys(monkeypatch):
    for name in ("CHAT_API_KEY", "ANALYSIS_API_KEY", "JOBS_API_KEY", "CLI_PROXY_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CHAT_API_KEY", "k-chat")
    monkeypatch.setenv("ANALYSIS_API_KEY", "k-analysis")
    monkeypatch.setenv("JOBS_API_KEY", "k-jobs")
    monkeypatch.setenv("CLI_PROXY_API_KEY", "k-chat")   # 跟 CHAT 同一把 → 去重


def test_key_pool_puts_role_key_first_and_dedupes(keys):
    assert key_pool("analysis") == ["k-analysis", "k-chat", "k-jobs"]
    assert key_pool("jobs") == ["k-jobs", "k-chat", "k-analysis"]
    assert key_pool("chat") == ["k-chat", "k-jobs", "k-analysis"]


def test_key_pool_falls_back_to_main_key(monkeypatch):
    for name in ("CHAT_API_KEY", "ANALYSIS_API_KEY", "JOBS_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CLI_PROXY_API_KEY", "only")
    assert key_pool("analysis") == ["only"]


class _StatusErr(Exception):
    def __init__(self, code, msg=""):
        super().__init__(msg)
        self.status_code = code


def test_is_key_problem():
    assert is_key_problem(_StatusErr(429))
    assert is_key_problem(_StatusErr(401))
    assert is_key_problem(Exception("本週額度已用完"))
    assert not is_key_problem(Exception("Request timed out"))
    assert not is_key_problem(_StatusErr(500, "upstream error"))


class _FakeClient:
    """chat.completions.create 依序丟出 error 或回 text。"""

    def __init__(self, outcome):
        self.outcome, self.calls = outcome, 0
        self.chat = self
        self.completions = self

    async def create(self, **_):
        self.calls += 1
        if isinstance(self.outcome, Exception):
            raise self.outcome

        class R:
            choices = [type("C", (), {"message": type("M", (), {"content": self.outcome})()})()]
        return R()


def _brain(clients, fallback=None):
    from line_bot.bot import SassyBrain
    b = SassyBrain.__new__(SassyBrain)
    b.primary_clients, b.primary_client, b.primary_model = clients, clients[0], "m"
    b.fallback_client, b.fallback_model = fallback, "fb"
    return b


def test_chat_switches_key_on_quota_without_waiting():
    first, second = _FakeClient(_StatusErr(429, "429 rate limit")), _FakeClient("好")
    out = asyncio.run(_brain([first, second])._generate_with_fallback([{"role": "user", "content": "hi"}]))
    assert out == "好"
    assert first.calls == 1          # 還有下一把 key 時不原地重試 429


def test_chat_timeout_goes_straight_to_fallback():
    first, second, fb = _FakeClient(Exception("Request timed out")), _FakeClient("不該用到"), _FakeClient("備援")
    out = asyncio.run(_brain([first, second], fb)._generate_with_fallback([{"role": "user", "content": "hi"}]))
    assert out == "備援"
    assert second.calls == 0
