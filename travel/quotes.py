"""精選金句：規則挑候選（A）→ LLM 當評審選 10 則並配標籤（B），每天算一次。

A. 規則分數 = 情緒強度 + 引起的反應（被回覆數、之後 2 分鐘內別人笑的次數）。
   限長度（擋長篇複製文）、同時段只留最高分、每人在候選池與最終結果都有上限。
B. 把候選池（附前文）交給 Gemini 選最經典／最好笑的 10 則並配一個短標籤；
   LLM 失敗或回傳不足時退回規則版（正負各半）。
"""
import bisect
import json
import os
import re
from datetime import datetime, timedelta, timezone

from travel.db import get_conn
from travel.period import period_filter

QUOTES_MODEL = os.getenv("QUOTES_MODEL", "gpt-6.1-sol")
QUOTES_TTL = 86400            # LLM 評審結果快取一天

MAX_LEN = 80                  # 超過視為長篇複製文
REACTION_WINDOW_MS = 120 * 1000
SAME_MOMENT_MS = 600 * 1000   # 同一時段（10 分鐘內）只留最高分一則
POOL_SIZE = 60
POOL_PER_PERSON = 6
PICK = 10
PICK_PER_PERSON = 2

_LAUGH_RE = re.compile(r"笑死|哈哈|XD|xd|😂|🤣|笑爛|靠北|超好笑|好好笑|草")
_TZ = timezone(timedelta(hours=8))


def _day(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, _TZ).strftime("%Y/%m/%d")


def count_laughs_after(cand: dict, stream: list[dict], stream_ts: list[int]) -> int:
    """cand 之後 REACTION_WINDOW_MS 內，別人發的笑聲訊息數（stream 依時間升序）。"""
    start = bisect.bisect_right(stream_ts, cand["timestamp"])
    end = bisect.bisect_right(stream_ts, cand["timestamp"] + REACTION_WINDOW_MS)
    return sum(1 for m in stream[start:end]
               if m["user_id"] != cand["user_id"] and _LAUGH_RE.search(m["content"] or ""))


def quote_score(sentiment: float, replies: int, laughs: int) -> float:
    """情緒強度為底，引起反應（尤其是別人笑）加分；反應各最多算 3 次，避免洗版串過度加分。"""
    return abs(sentiment) + 0.3 * min(replies, 3) + 0.4 * min(laughs, 3)


def build_pool(cands: list[dict], size: int = POOL_SIZE, per_person: int = POOL_PER_PERSON) -> list[dict]:
    """cands 需已有 score。同時段只留最高分 → 依分數取前 size 則，每人最多 per_person 則。"""
    best_in_moment: list[dict] = []
    for c in sorted(cands, key=lambda x: x["timestamp"]):
        if best_in_moment and c["timestamp"] - best_in_moment[-1]["timestamp"] <= SAME_MOMENT_MS:
            prev = best_in_moment[-1]
            if (c["score"], len(c["content"])) > (prev["score"], len(prev["content"])):
                best_in_moment[-1] = c   # 同分留較完整（較長）的
        else:
            best_in_moment.append(c)
    pool, per = [], {}
    for c in sorted(best_in_moment, key=lambda x: -x["score"]):
        if per.get(c["user_name"], 0) >= per_person:
            continue
        per[c["user_name"]] = per.get(c["user_name"], 0) + 1
        pool.append(c)
        if len(pool) >= size:
            break
    return pool


def pick_rule_based(pool: list[dict], limit: int = PICK, per_person: int = PICK_PER_PERSON) -> list[dict]:
    """LLM 失敗時的退路：正負各半、依分數高低、每人最多 per_person 則。"""
    ranked = sorted(pool, key=lambda x: -x["score"])
    picked, per = [], {}

    def take(rows, n):
        for r in rows:
            if n <= 0:
                return
            if r in picked or per.get(r["user_name"], 0) >= per_person:
                continue
            per[r["user_name"]] = per.get(r["user_name"], 0) + 1
            picked.append(r)
            n -= 1

    take([r for r in ranked if r["sentiment"] >= 0], limit // 2)
    take([r for r in ranked if r["sentiment"] < 0], limit // 2)
    take(ranked, limit - len(picked))
    return picked


def build_curate_prompt(pool: list[dict]) -> str:
    lines = []
    for c in pool:
        ctx = " / ".join(f"{m['user_name']}: {m['content'][:40]}" for m in c.get("context", []))
        lines.append(f"id={c['id']}｜{_day(c['timestamp'])}｜{c['user_name']}：「{c['content']}」"
                     + (f"（前文：{ctx}）" if ctx else ""))
    return (
        "你是台灣大學生 LINE 群組的年度金句評審。以下是候選訊息（附前文幫助理解梗）。\n"
        f"請選出 {PICK} 則最經典、最好笑、最有梗、最能代表這群人的金句。\n"
        "規則：\n"
        f"1. 同一個人最多 {PICK_PER_PERSON} 則；普通的事務對話（約時間、問路）不要選。\n"
        "2. 每則配一個標籤：1 個 emoji + 2～6 個字，要貼切好笑（例：「💀 社死現場」「🤡 自爆代表」「🧠 神邏輯」）。\n"
        '3. 只輸出 JSON 陣列：[{"id": 123, "label": "💀 社死現場"}, ...]\n\n'
        + "\n".join(lines)
    )


def parse_curation(raw: str | None, pool: list[dict]) -> list[dict]:
    """解析 LLM 選擇，只保留候選池內的 id，並套用每人上限。"""
    m = re.search(r"\[.*\]", raw or "", re.DOTALL)
    try:
        items = json.loads(m.group(0)) if m else []
    except json.JSONDecodeError:
        return []
    by_id = {c["id"]: c for c in pool}
    out, per, seen = [], {}, set()
    for it in items:
        if not isinstance(it, dict):
            continue
        try:
            c = by_id.get(int(it.get("id")))
        except (TypeError, ValueError):
            continue
        if not c or c["id"] in seen or per.get(c["user_name"], 0) >= PICK_PER_PERSON:
            continue
        seen.add(c["id"])
        per[c["user_name"]] = per.get(c["user_name"], 0) + 1
        out.append({**c, "label": str(it.get("label") or "").strip()[:12] or None})
    return out[:PICK]


def fetch_candidates(group_id: str, period: str) -> list[dict]:
    """撈有情緒分數的候選句，並計算反應分數與前文。"""
    from travel.stats_extended import _is_quote_worthy
    pf, pp = period_filter(period)
    with get_conn() as conn:
        stream = [dict(r) for r in conn.execute(
            f"""SELECT id, line_message_id, user_id, user_name, content, summary, sentiment, timestamp
                FROM messages
                WHERE group_id=?{pf} AND type='text' AND content IS NOT NULL
                  AND user_id NOT LIKE 'imported:%'
                ORDER BY timestamp""",
            (group_id, *pp),
        )]
        replies = dict(conn.execute(
            f"""SELECT reply_to_message_id, COUNT(*) FROM messages
                WHERE group_id=?{pf} AND reply_to_message_id IS NOT NULL
                GROUP BY reply_to_message_id""",
            (group_id, *pp),
        ).fetchall())
    stream_ts = [m["timestamp"] for m in stream]
    cands = []
    for i, m in enumerate(stream):
        text = (m["content"] or "").strip()
        if m["sentiment"] is None or len(text) > MAX_LEN or not _is_quote_worthy(text):
            continue
        n_replies = replies.get(m["line_message_id"], 0)
        n_laughs = count_laughs_after(m, stream, stream_ts)
        cands.append({
            **m, "content": text, "replies": n_replies, "laughs": n_laughs,
            "score": quote_score(m["sentiment"], n_replies, n_laughs),
            "context": [{"user_name": p["user_name"], "content": (p["content"] or "").strip()}
                        for p in stream[max(0, i - 2):i]],
        })
    return cands


def _curate(pool: list[dict]) -> list[dict]:
    """呼叫 LLM 評審選金句；任何失敗回 []（呼叫端退回規則版）。"""
    import asyncio

    from llm_keys import cgu_chat

    async def call():
        return await cgu_chat(
            "jobs", model=QUOTES_MODEL, temperature=0.7, max_completion_tokens=4000, timeout=60,
            messages=[{"role": "user", "content": build_curate_prompt(pool)}],
        )
    try:
        return parse_curation(asyncio.run(call()), pool)
    except Exception as e:
        print(f"[QUOTES] LLM 評審失敗，改用規則版：{e}")
        return []


def compute_highlight_quotes(group_id: str, period: str) -> list[dict]:
    pool = build_pool(fetch_candidates(group_id, period))
    if not pool:
        return []
    picked = _curate(pool)
    if len(picked) < PICK // 2:
        picked = pick_rule_based(pool)
    return [
        {"user_name": r["user_name"], "content": r["content"], "summary": r.get("summary"),
         "sentiment": round(r["sentiment"], 3),
         "tone": "positive" if r["sentiment"] >= 0 else "negative",
         "label": r.get("label"), "replies": r["replies"], "laughs": r["laughs"],
         "timestamp": r["timestamp"]}
        for r in picked
    ]


def get_highlight_quotes(group_id: str, period: str = "all") -> list[dict]:
    """快取一天；過期時背景重算（先回舊值），冷啟時同步算一次。"""
    from travel.cache import cached
    return cached("quotes", group_id, period, lambda: compute_highlight_quotes(group_id, period),
                  ttl=QUOTES_TTL)


def warm_highlight_quotes(group_id: str | None = None) -> None:
    """每天凌晨預先重算常用期間（全部／今年／本月），白天第一次打開話題頁不用等 LLM。"""
    from travel.cache import _write
    group_id = group_id or os.getenv("MAIN_LINE_GROUP_ID", "")
    if not group_id:
        return
    now = datetime.now(_TZ)
    for period in ("all", f"{now:%Y}", f"{now:%Y-%m}"):
        try:
            _write(f"quotes:{group_id}:{period}", compute_highlight_quotes(group_id, period))
        except Exception as e:
            print(f"[QUOTES] 預算 {period} 失敗：{e}")
