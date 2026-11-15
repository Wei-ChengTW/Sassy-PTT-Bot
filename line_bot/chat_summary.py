"""聊天摘要：群組內 @機器人「現在是怎樣」→ 摘要發問者錯過的對話，給爬樓爬不完的人。

範圍＝從發問者「上次在群組講話」之後到發問前（LINE 不提供個人已讀位置，用上次講話近似），不設上限。
發問者從沒講過話 → 改用「最近一輪」：從最新訊息往回走，碰到停頓超過 ROUND_GAP_MS 就停。
少於 MIN_MSGS 則不摘要，直接嗆回去。
"""
import os
import random
import re
from datetime import datetime, timedelta, timezone

SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gpt-6.1-sol")

SUMMARY_TRIGGER = "現在是怎樣"
_TRAILING_PUNCT_RE = re.compile(r"[\s?？!！.。~～]+$")

ROUND_GAP_MS = 30 * 60 * 1000       # 停頓超過 30 分鐘視為新的一輪
MIN_MSGS = 10                        # 少於此數不摘要，直接嗆「不會自己看喔」
FETCH_LIMIT = 2000                   # 「最近一輪」撈 DB 的保險上限（實際一輪最長約數百則）
MAX_CONTENT_CHARS = 200

_TZ = timezone(timedelta(hours=8))
_MEDIA_LABELS = {
    "sticker": "[貼圖]", "image": "[照片]", "video": "[影片]",
    "audio": "[語音]", "file": "[檔案]", "location": "[位置]",
}


def is_summary_request(text: str) -> bool:
    """只認「現在是怎樣」整句（@機器人 已先去掉），句尾可帶問號、驚嘆號等。"""
    return _TRAILING_PUNCT_RE.sub("", text.strip()) == SUMMARY_TRIGGER


def select_round(msgs: list[dict]) -> list[dict]:
    """msgs 依 timestamp 升序（不含發問那則）。回傳最後一輪：往回走到第一個超過 ROUND_GAP_MS 的停頓為止。"""
    if not msgs:
        return []
    start = len(msgs) - 1
    while start > 0 and msgs[start]["timestamp"] - msgs[start - 1]["timestamp"] <= ROUND_GAP_MS:
        start -= 1
    return msgs[start:]


def too_short_reply(n: int) -> str:
    if n == 0:  # 發問者就是最後講話的人
        return random.choice([
            "你就是最後講話的人，還問？",
            "最後一句就是你講的欸，是在問三小",
            "你講完就沒人理你了，沒東西好整理 🙃",
        ])
    return random.choice([
        f"才 {n} 則是不會自己往上滑喔 🙄",
        f"{n} 則而已，手指斷了？自己看啦",
        f"就 {n} 則你也要懶人包，懶到一個境界",
    ])


def fetch_messages(group_id: str, before_ts: int) -> list[dict]:
    """撈發問之前的訊息（升序），量足夠 select_round 做判斷即可。"""
    from travel.db import get_conn
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT user_name, content, type, timestamp FROM messages
               WHERE group_id = ? AND timestamp < ? AND is_deleted = 0
               ORDER BY timestamp DESC LIMIT ?""",
            (group_id, before_ts, FETCH_LIMIT),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def last_spoke_ts(group_id: str, user_id: str, before_ts: int) -> int | None:
    """發問者在此群組、發問前最後一則訊息的時間；從沒講過話回 None。"""
    from travel.db import get_conn
    with get_conn() as conn:
        row = conn.execute(
            "SELECT MAX(timestamp) FROM messages WHERE group_id = ? AND user_id = ? AND timestamp < ?",
            (group_id, user_id, before_ts),
        ).fetchone()
    return row[0] if row and row[0] is not None else None


def fetch_between(group_id: str, after_ts: int, before_ts: int) -> list[dict]:
    """after_ts 之後、before_ts 之前的全部訊息（升序，不設上限）。"""
    from travel.db import get_conn
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT user_name, content, type, timestamp FROM messages
               WHERE group_id = ? AND timestamp > ? AND timestamp < ? AND is_deleted = 0
               ORDER BY timestamp""",
            (group_id, after_ts, before_ts),
        ).fetchall()
    return [dict(r) for r in rows]


def _fmt_time(ts_ms: int, with_date: bool = False) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, _TZ).strftime("%m/%d %H:%M" if with_date else "%H:%M")


def format_transcript(msgs: list[dict], with_date: bool = False) -> str:
    """一行一則：`HH:MM 名字: 內容`；with_date=True 時為 `MM/DD HH:MM`（跨天逐字稿用）。"""
    lines = []
    for m in msgs:
        content = (m.get("content") or "").replace("\n", " ").strip()
        if m.get("type") != "text":
            content = _MEDIA_LABELS.get(m.get("type"), f"[{m.get('type')}]")
        lines.append(f"{_fmt_time(m['timestamp'], with_date)} {m['user_name']}: {content[:MAX_CONTENT_CHARS]}")
    return "\n".join(lines)


def summary_header(msgs: list[dict], since_ts: int | None = None) -> str:
    """since_ts 有給（發問者上次講話時間）→「從你上次講話（…）到現在」；否則顯示這一輪的時間範圍。"""
    def when(ts):
        day = datetime.fromtimestamp(ts / 1000, _TZ)
        same_day = day.date() == datetime.now(_TZ).date()
        return _fmt_time(ts) if same_day else _fmt_time(ts, with_date=True)
    if since_ts is not None:
        return f"📋 從你上次講話（{when(since_ts)}）到現在，共 {len(msgs)} 則"
    return f"📋 {when(msgs[0]['timestamp'])}～{_fmt_time(msgs[-1]['timestamp'])}，共 {len(msgs)} 則"


def bullet_range(n_msgs: int) -> str:
    """錯過的越多，條列點數越多（16000 則實測只給 3～6 點會壓縮過頭）。"""
    if n_msgs < 200:
        return "3～6 點"
    if n_msgs < 1000:
        return "5～10 點"
    return "8～15 點，依日期或話題分段"


def select_missed(group_id: str, user_id: str, before_ts: int) -> tuple[list[dict], int | None]:
    """發問者上次講話之後到發問前的訊息，回傳 (msgs, 上次講話時間)。從沒講過話 → 最近一輪、None。"""
    since = last_spoke_ts(group_id, user_id, before_ts) if user_id else None
    if since is None:
        return select_round(fetch_messages(group_id, before_ts)), None
    return fetch_between(group_id, since, before_ts), since


def build_messages(transcript: str, asker: str, n_msgs: int = 0) -> list[dict]:
    system = (
        "你是這個 LINE 群組裡嘴很賤的 PTT 鄉民老成員「鍵盤俠」。"
        f"{asker} 錯過了一段對話，爬樓爬不完，請你幫他整理。\n"
        "規則：\n"
        f"1. 用 {bullet_range(n_msgs)}條列，每點以「・」開頭，一點一行，交代誰說了什麼、吵了什麼、結論是什麼。\n"
        "2. 一定要點名（用對話裡的名字），可以帶一點酸，但事實不能亂編。\n"
        "3. 貼圖、照片只是氣氛，不用特別提。\n"
        "4. 最後一行用一句話酸總結，以「總之：」開頭。\n"
        "5. 只輸出條列和總結，不要加標題、前言或解釋。"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"對話紀錄：\n{transcript}"},
    ]
