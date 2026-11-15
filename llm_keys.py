"""CGU 金鑰分工：每類任務先用自己的 key，遇到額度用完／限流／金鑰無效再換下一把。

.env 設定（沒設的會略過，全部沒設就只用 CLI_PROXY_API_KEY）：
    CHAT_API_KEY      即時：插嘴、@提及、問答、摘要、畢業倒數
    ANALYSIS_API_KEY  每日主題分析、情緒分析
    JOBS_API_KEY      精選金句、每週稱號

timeout 或模型本身的錯誤不換 key（換了也一樣），交給呼叫端改用備援供應商。
環境變數在呼叫時才讀：以 script 執行時 .env 可能在 import 之後才載入。
"""
import os

CGU_BASE_URL = "https://air.cgu.edu.tw/cgullmapi/v1"

ROLE_KEY_ENV = {
    "chat": "CHAT_API_KEY",
    "analysis": "ANALYSIS_API_KEY",
    "jobs": "JOBS_API_KEY",
}
_POOL_ORDER = ("CHAT_API_KEY", "JOBS_API_KEY", "ANALYSIS_API_KEY", "CLI_PROXY_API_KEY")

_KEY_PROBLEM_WORDS = ("429", "rate limit", "quota", "insufficient", "額度", "invalid_api_key", "invalid api key")


def base_url() -> str:
    return os.getenv("CLI_PROXY_BASE_URL") or CGU_BASE_URL


def key_pool(role: str) -> list[str]:
    """該任務的 key 排第一，其餘可用的 key 依序接在後面（去空、去重）。"""
    keys: list[str] = []
    for name in (ROLE_KEY_ENV.get(role, ""), *_POOL_ORDER):
        k = (os.getenv(name) or "").strip() if name else ""
        if k and k not in keys:
            keys.append(k)
    return keys


def is_key_problem(err: Exception) -> bool:
    """額度、限流、金鑰無效 → 換別把 key 有意義。"""
    if getattr(err, "status_code", None) in (401, 402, 403, 429):
        return True
    s = str(err).lower()
    return any(w in s for w in _KEY_PROBLEM_WORDS)


async def cgu_chat(role: str, **create_kwargs) -> str:
    """依 key_pool(role) 依序呼叫 chat.completions；key 的問題換下一把，其他錯誤直接拋出。"""
    from openai import AsyncOpenAI

    last: Exception | None = None
    for key in key_pool(role):
        async with AsyncOpenAI(base_url=base_url(), api_key=key, max_retries=1) as client:
            try:
                resp = await client.chat.completions.create(**create_kwargs)
                return resp.choices[0].message.content or ""
            except Exception as e:
                last = e
                if not is_key_problem(e):
                    raise
    raise last or RuntimeError("沒有可用的 CGU key")
