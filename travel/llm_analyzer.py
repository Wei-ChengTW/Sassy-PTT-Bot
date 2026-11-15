"""批次 LLM 訊息分析（主題 / 情緒 / 實體 / 摘要）。

每月由 APScheduler 觸發，分析尚未標記的訊息，回填 SQLite。
"""
import json
import os
import time
from typing import Any

from openai import AsyncOpenAI

from llm_keys import cgu_chat
from travel.db import get_conn

# CGU 的 key 由 llm_keys 分配（ANALYSIS_API_KEY 優先，額度／限流時換別把）
# 話題分析專用（與聊天的 PRIMARY_MODEL 分開）
PRIMARY_MODEL = os.getenv("ANALYZER_MODEL", "gpt-6.1-sol")
FALLBACK_BASE = os.getenv("FALLBACK_BASE_URL", "https://raygoai.cc/v1")
FALLBACK_KEY = os.getenv("FALLBACK_API_KEY", "")
FALLBACK_MODEL = os.getenv("FALLBACK_LIGHT_MODEL", "deepseek-v4.1-flash")
BATCH_SIZE = 50
# 一批 50 則的 JSON 約 4,000 token；2,000 會被截斷（gemma 會照上限截斷、解析失敗）
MAX_OUTPUT_TOKENS = 8000

PROMPT_TEMPLATE = """分析以下 LINE 群組訊息（多則），每則輸出 JSON。
欄位：
- id（訊息 id，必須保留）
- is_travel_related（0/1，是否跟旅行 / 旅遊 / 行程相關）
- topics（陣列，從這幾個選：travel/food/work/chat/joke/other）
- keywords（2~4 個具體主題詞陣列，用訊息實際內容，如 ["沖繩","機票","居酒屋"]，勿用抽象分類詞）
- sentiment（-1 ~ 1，-1 極負面、0 中性、1 極正面）
- locations（地點陣列，可空陣列）
- summary（一句話中文摘要，可空字串）

只輸出合法 JSON 陣列，不要 ```json 包裹。

訊息：
{messages}

JSON："""

KEYWORD_PROMPT_TEMPLATE = """為以下 LINE 群組訊息各抽取關鍵字，每則輸出 JSON。
欄位：
- id（訊息 id，必須保留）
- keywords（2~4 個具體主題詞陣列，用訊息實際內容，如 ["沖繩","機票","居酒屋"]，勿用抽象分類詞）

只輸出合法 JSON 陣列，不要 ```json 包裹。

訊息：
{messages}

JSON："""


def build_prompt(messages: list[dict]) -> str:
    """組 LLM prompt：多則訊息一次分析。"""
    lines = []
    for m in messages:
        ts = time.strftime("%Y-%m-%d", time.localtime(m["timestamp"] / 1000))
        content = m.get("content") or "(non-text)"
        lines.append(f"id={m['id']} [{ts}] {m.get('user_name', '?')}: {content}")
    return PROMPT_TEMPLATE.format(messages="\n".join(lines))


def parse_llm_response(raw: str) -> list[dict[str, Any]]:
    """解析 LLM 回傳為 JSON 陣列。處理 ```json ... ``` 包裹。"""
    s = raw.strip()
    if s.startswith("```"):
        s = s.split("```", 2)[1]
        if s.startswith("json"):
            s = s[4:]
        s = s.strip().rstrip("`").strip()
    try:
        data = json.loads(s)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 回傳非 JSON：{e}") from e
    if not isinstance(data, list):
        raise ValueError(f"預期 JSON 陣列，收到 {type(data).__name__}")
    return data


async def analyze_batch(messages: list[dict]) -> list[dict]:
    """呼叫 LLM 分析一批訊息，回傳結構化結果。"""
    prompt = build_prompt(messages)
    last_err = None

    try:
        return parse_llm_response(await cgu_chat(
            "analysis", model=PRIMARY_MODEL, messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_completion_tokens=MAX_OUTPUT_TOKENS,
        ))
    except Exception as e:
        last_err = e

    if FALLBACK_KEY:
        client = AsyncOpenAI(base_url=FALLBACK_BASE, api_key=FALLBACK_KEY)
        resp = await client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_completion_tokens=MAX_OUTPUT_TOKENS,
        )
        return parse_llm_response(resp.choices[0].message.content)

    raise RuntimeError(f"LLM 全部失敗: {last_err}")


RECENT_DAYS = 31  # 按鈕／每月排程：分析最近這麼多天內所有待分析訊息


def fetch_pending_analysis(since_ms: int | None = None, limit: int | None = None,
                           newest_first: bool = True) -> list[dict]:
    """撈尚未分析（analyzed_at IS NULL）的文字訊息。"""
    q = """SELECT id, user_name, content, timestamp
           FROM messages
           WHERE analyzed_at IS NULL AND content IS NOT NULL
             AND type = 'text' AND length(content) > 1"""
    params: list = []
    if since_ms:
        q += " AND timestamp > ?"
        params.append(since_ms)
    q += f" ORDER BY timestamp {'DESC' if newest_first else 'ASC'}"
    if limit:
        q += f" LIMIT {int(limit)}"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, params)]


def write_analysis_results(results: list[dict]) -> int:
    """寫回話題／關鍵字／地點／摘要。

    注意：sentiment 不在此寫入。逐則 flash 情緒判讀雜訊過高，情緒改由
    travel.sentiment_windows 的視窗式 pro 模型分析負責（見 run_sentiment_backfill）。
    """
    now = int(time.time())
    updated = 0
    with get_conn() as conn:
        for r in results:
            if "id" not in r:
                continue
            conn.execute(
                """UPDATE messages
                   SET is_travel_related=?, topics=?, keywords=?,
                       locations=?, summary=?, analyzed_at=?
                   WHERE id=?""",
                (
                    r.get("is_travel_related", 0),
                    json.dumps(r.get("topics", []), ensure_ascii=False),
                    json.dumps(r.get("keywords", []), ensure_ascii=False),
                    json.dumps(r.get("locations", []), ensure_ascii=False),
                    r.get("summary", ""),
                    now,
                    r["id"],
                ),
            )
            updated += 1
    return updated


async def analyze_pending(since_ms: int | None = None, limit: int | None = None,
                          concurrency: int = 2, newest_first: bool = True) -> int:
    """把待分析訊息切成 BATCH_SIZE 一批、並發送 LLM，逐批寫回。可中斷續跑。回傳寫入則數。"""
    import asyncio

    pending = fetch_pending_analysis(since_ms, limit, newest_first)
    if not pending:
        print("[ANALYZER] 沒有未分析的訊息")
        return 0
    batches = [pending[i:i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
    print(f"[ANALYZER] 待分析 {len(pending)} 則 → {len(batches)} 批（並發 {concurrency}）")
    sem = asyncio.Semaphore(concurrency)
    done = {"msgs": 0, "batches": 0, "fail": 0}
    t0 = time.time()

    async def worker(batch):
        async with sem:
            try:
                results = await analyze_batch(batch)
            except Exception as e:
                done["fail"] += 1
                print(f"[ANALYZER] ⚠️ 批次失敗（{len(batch)} 則，下次重跑會補）：{e}")
                return
        done["msgs"] += await asyncio.to_thread(write_analysis_results, results)
        done["batches"] += 1
        if done["batches"] % 20 == 0 or done["batches"] == len(batches):
            el = time.time() - t0
            print(f"[ANALYZER] 進度 {done['batches']}/{len(batches)} 批 | {done['msgs']} 則 | "
                  f"{el / 60:.1f} 分")

    await asyncio.gather(*(worker(b) for b in batches))
    print(f"[ANALYZER] 完成 {done['msgs']} 則，失敗批 {done['fail']}，耗時 {(time.time() - t0) / 60:.1f} 分")
    return done["msgs"]


def run_recent_analysis(days: int = RECENT_DAYS) -> int:
    """按鈕與每月排程：分析最近 days 天內所有待分析訊息（由新到舊）。"""
    import asyncio
    since_ms = int((time.time() - days * 86400) * 1000)
    return asyncio.run(analyze_pending(since_ms=since_ms))


# 舊名稱：排程與既有呼叫點沿用
run_monthly_analysis = run_recent_analysis


async def _keyword_batch(messages: list[dict]) -> list[dict]:
    """呼叫 LLM 只抽 keywords，沿用 primary/fallback。"""
    prompt = KEYWORD_PROMPT_TEMPLATE.format(
        messages="\n".join(
            f"id={m['id']} {m.get('user_name','?')}: {m.get('content') or '(non-text)'}"
            for m in messages
        )
    )
    last_err = None
    try:
        return parse_llm_response(await cgu_chat(
            "analysis", model=PRIMARY_MODEL, messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_completion_tokens=MAX_OUTPUT_TOKENS,
        ))
    except Exception as e:
        last_err = e
    if FALLBACK_KEY:
        client = AsyncOpenAI(base_url=FALLBACK_BASE, api_key=FALLBACK_KEY)
        resp = await client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_completion_tokens=MAX_OUTPUT_TOKENS,
        )
        return parse_llm_response(resp.choices[0].message.content)
    raise RuntimeError(f"LLM 全部失敗: {last_err}")


def run_keyword_backfill() -> int:
    """對已分析但無 keywords 的訊息補抽關鍵字。回傳更新筆數。"""
    import asyncio

    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, user_name, content
               FROM messages
               WHERE analyzed_at IS NOT NULL AND keywords IS NULL
                 AND content IS NOT NULL AND type='text' AND length(content) > 1
               ORDER BY timestamp ASC LIMIT ?""",
            (BATCH_SIZE,),
        ).fetchall()

    if not rows:
        print("[KEYWORD] 沒有待補關鍵字的訊息")
        return 0

    messages = [dict(r) for r in rows]
    try:
        results = asyncio.run(_keyword_batch(messages))
    except Exception as e:
        print(f"[KEYWORD] LLM 失敗：{e}")
        return 0

    by_id = {r["id"]: r.get("keywords", []) for r in results if "id" in r}
    updated = 0
    with get_conn() as conn:
        for m in messages:
            kw = by_id.get(m["id"])
            # 即使 LLM 沒回也寫入空陣列，避免下輪重撈
            conn.execute(
                "UPDATE messages SET keywords=? WHERE id=?",
                (json.dumps(kw if kw is not None else [], ensure_ascii=False), m["id"]),
            )
            updated += 1
    print(f"[KEYWORD] 補完 {updated} 則（輸入 {len(messages)} 則）")
    return updated


if __name__ == "__main__":
    run_monthly_analysis()