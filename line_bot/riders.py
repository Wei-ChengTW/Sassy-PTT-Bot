"""搭便車小卡：非必要的群組通知不推播，改附在機器人下一次在該群組的回覆後面。

推播吃每月額度（免費方案 200 則，推到群組按人數計），回覆不計額度、一次最多 5 則訊息。
通知先 enqueue 進 pending_riders，bot.py 的 reply hook 回覆時 take 出來接在後面；
reply token 過期就 release 放回佇列；卡片本身不合規則丟棄。同一群組同一 key 只會排一次。
"""
import json
import logging
import threading
import time
from datetime import datetime, timedelta

from travel.db import get_conn

logger = logging.getLogger(__name__)

MAX_REPLY_MESSAGES = 5
_lock = threading.Lock()   # take 的查詢與標記要一起做，避免兩則同時回覆拿到同一張卡


def end_of_day(tz, now: datetime | None = None) -> int:
    """當地今天結束的 epoch 秒（那年今日、倒數這類「當天才有意義」的卡片用）。"""
    now = now or datetime.now(tz)
    return int((now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).timestamp())


def enqueue(group_id: str, key: str, message, expires_at: int) -> bool:
    """排一張卡；同群組同 key 已排過（不論送出與否）就略過，回傳是否新排入。"""
    if not group_id or message is None:
        return False
    payload = json.dumps(message if isinstance(message, dict) else message.to_dict(), ensure_ascii=False)
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO pending_riders (group_id, rider_key, payload, created_at, expires_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (group_id, key, payload, int(time.time()), expires_at),
        )
        added = cur.rowcount > 0
    if added:
        logger.info(f"[RIDER] 排入 group={group_id} key={key}")
    return added


def take(group_id: str, room: int) -> tuple[list[int], list]:
    """取出最多 room 張還沒過期、還沒送出的卡（先排先送），並先標記為已送出。"""
    if not group_id or room <= 0:
        return [], []
    from linebot.v3.messaging import Message
    now = int(time.time())
    with _lock, get_conn() as conn:
        rows = conn.execute(
            "SELECT id, payload FROM pending_riders "
            "WHERE group_id=? AND delivered_at IS NULL AND expires_at > ? ORDER BY id LIMIT ?",
            (group_id, now, room),
        ).fetchall()
        if not rows:
            return [], []
        ids = [r["id"] for r in rows]
        conn.execute(
            f"UPDATE pending_riders SET delivered_at=? WHERE id IN ({','.join('?' * len(ids))})",
            (now, *ids),
        )
    return ids, [Message.from_dict(json.loads(r["payload"])) for r in rows]


def release(ids: list[int]) -> None:
    """回覆沒送出去，把卡放回佇列。"""
    if not ids:
        return
    with get_conn() as conn:
        conn.execute(
            f"UPDATE pending_riders SET delivered_at=NULL WHERE id IN ({','.join('?' * len(ids))})",
            ids,
        )


def install_reply_hook(line_api, token_groups: dict) -> None:
    """包住 line_api.reply_message：reply token 對得到群組就把該群的待送卡接在回覆後面。

    token_groups：reply_token → group_id，由收到事件時登記（ReplyMessageRequest 本身不帶群組）。
    """
    from linebot.v3.messaging import ReplyMessageRequest
    from linebot.v3.messaging.exceptions import ApiException

    original = line_api.reply_message

    def reply_message(request, *args, **kwargs):
        group_id = token_groups.pop(request.reply_token, None)
        ids, extra = take(group_id, MAX_REPLY_MESSAGES - len(request.messages or []))
        if not extra:
            return original(request, *args, **kwargs)
        merged = ReplyMessageRequest(
            reply_token=request.reply_token,
            messages=[*request.messages, *extra],
            notification_disabled=request.notification_disabled,
        )
        try:
            result = original(merged, *args, **kwargs)
            logger.info(f"[RIDER] 隨回覆送出 {len(extra)} 張 group={group_id}")
            return result
        except ApiException as e:
            if e.status != 400:
                raise
            body = str(getattr(e, "body", "") or e)
            if "reply token" in body.lower():
                release(ids)   # token 過期，原回覆也送不出去；卡片留給下一次
                raise
            # 其他 400＝附上的卡片不合規：丟掉這幾張（不放回，免得每次回覆都重試失敗），只送原回覆
            logger.warning(f"[RIDER] 附卡被拒已丟棄 ids={ids}: {body[:300]}")
            return original(request, *args, **kwargs)

    line_api.reply_message = reply_message
