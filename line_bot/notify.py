"""群組主動推播：旅行出發倒數、徽章頒發、那年今日。

bot.py 的排程與 liff_api 的管理員操作共用這裡。卡片樣式在 stats_cards。
日期一律以台灣時間（UTC+8）判斷「今天」。
"""
import logging
import os
from datetime import date, datetime, timedelta, timezone

from travel.db import get_conn

logger = logging.getLogger(__name__)

TZ = timezone(timedelta(hours=8))
COUNTDOWN_DAYS = {30, 14, 7, 3, 1, 0}   # 出發前這幾天推倒數卡（0＝當天）


def liff_url() -> str:
    liff_id = os.getenv("LIFF_ID", "")
    return f"https://liff.line.me/{liff_id}" if liff_id else "https://liff.line.me/placeholder"


def _local_date(ts: int) -> date:
    return datetime.fromtimestamp(ts, TZ).date()


def today_local() -> date:
    return datetime.now(TZ).date()


def push_flex(group_id: str, message) -> bool:
    """推一則 Flex 到群組；沒有 token 或失敗回 False（只記 log，不拋錯）。"""
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    if not token or not group_id:
        return False
    try:
        from linebot.v3.messaging import ApiClient, Configuration, MessagingApi, PushMessageRequest
        api = MessagingApi(ApiClient(Configuration(access_token=token)))
        api.push_message(PushMessageRequest(to=group_id, messages=[message]), _request_timeout=10.0)
        return True
    except Exception as e:
        logger.warning(f"[NOTIFY] 推播失敗 group={group_id}: {e}")
        return False


# ── 徽章頒發 ───────────────────────────────────────────────────────

def announce_badges(trip_id: str, awarded: list[dict]) -> bool:
    """有新發出的徽章才推頒獎卡（重新發放但沒有新徽章時不吵群組）。"""
    if not awarded:
        return False
    from travel.trip_crud import get_trip
    from line_bot import stats_cards as cards
    trip = get_trip(trip_id)
    if not trip or not trip.get("group_id"):
        return False
    ok = push_flex(trip["group_id"], cards.build_badge_award_card(trip, awarded, liff_url()))
    logger.info(f"[BADGE] 頒獎卡 trip={trip_id} 人數={len(awarded)} 推播={'成功' if ok else '失敗'}")
    return ok


def award_and_announce_ended_trips() -> None:
    """排程：對已結束但還沒發徽章的旅行發放，並在群組推頒獎卡。"""
    from travel.badges import award_badges_for_trip, get_ended_trips_without_badges
    for trip in get_ended_trips_without_badges():
        try:
            awarded = award_badges_for_trip(trip["id"])
            logger.info(f"[BADGE] trip {trip['id']} 發放 {len(awarded)} 枚徽章")
            announce_badges(trip["id"], awarded)
        except Exception as e:
            logger.exception(f"[BADGE] trip {trip['id']} 失敗: {e}")


# ── 旅行出發倒數 ───────────────────────────────────────────────────

def countdown_days(start_ts: int | None, today: date) -> int | None:
    """距離出發還有幾天（以日期算，不看時分）；已出發回 None。"""
    if not start_ts:
        return None
    days = (_local_date(start_ts) - today).days
    return days if days >= 0 else None


def trips_due_for_countdown(trips: list[dict], today: date) -> list[tuple[dict, int]]:
    out = []
    for t in trips:
        if t.get("status") == "ended":
            continue
        d = countdown_days(t.get("start_date"), today)
        if d is not None and d in COUNTDOWN_DAYS:
            out.append((t, d))
    return out


def send_trip_countdowns() -> None:
    """排程（每日）：出發前 30／14／7／3／1 天與當天，推倒數卡到該旅行的群組。"""
    from line_bot import stats_cards as cards
    with get_conn() as conn:
        trips = [dict(r) for r in conn.execute(
            "SELECT * FROM trips WHERE status != 'ended' AND start_date IS NOT NULL")]
    for trip, days in trips_due_for_countdown(trips, today_local()):
        ok = push_flex(trip.get("group_id", ""), cards.build_countdown_card(trip, days, liff_url()))
        logger.info(f"[COUNTDOWN] trip={trip['id']} 還有 {days} 天 推播={'成功' if ok else '失敗'}")


# ── 那年今日 ───────────────────────────────────────────────────────

def on_this_day_trips(trips: list[dict], today: date) -> list[dict]:
    """開始日與今天同月同日、且在往年的旅行；附 years_ago，近的排前面。"""
    out = []
    for t in trips:
        if not t.get("start_date"):
            continue
        d = _local_date(t["start_date"])
        if (d.month, d.day) == (today.month, today.day) and d.year < today.year:
            out.append({**t, "years_ago": today.year - d.year})
    return sorted(out, key=lambda t: t["years_ago"])


def one_year_ago_quote(group_id: str, today: date) -> dict | None:
    """一年前的今天那一天，反應最好的一句（沿用精選金句的規則分數）。"""
    from travel.quotes import fetch_candidates
    try:
        target = today.replace(year=today.year - 1)
    except ValueError:          # 2/29 → 去年沒有這天
        return None
    try:
        cands = fetch_candidates(group_id, f"{target:%Y-%m}")
    except Exception as e:
        logger.warning(f"[ON_THIS_DAY] 撈金句失敗: {e}")
        return None
    day = [c for c in cands if datetime.fromtimestamp(c["timestamp"] / 1000, TZ).date() == target
           and (c.get("laughs") or c.get("replies"))]
    return max(day, key=lambda c: c["score"], default=None)


def send_on_this_day() -> None:
    """排程（每日）：往年同一天出發的旅行 + 一年前今天的金句，有內容才推。"""
    from line_bot import stats_cards as cards
    today = today_local()
    with get_conn() as conn:
        all_trips = [dict(r) for r in conn.execute("SELECT * FROM trips WHERE start_date IS NOT NULL")]
    by_group: dict[str, list[dict]] = {}
    for t in on_this_day_trips(all_trips, today):
        by_group.setdefault(t.get("group_id") or "", []).append(t)
    main = os.getenv("MAIN_LINE_GROUP_ID", "")
    groups = {g for g in by_group if g} | ({main} if main else set())
    for group_id in groups:
        quote = one_year_ago_quote(group_id, today)
        msg = cards.build_on_this_day_card(by_group.get(group_id, []), quote, liff_url())
        if msg is None:
            continue
        ok = push_flex(group_id, msg)
        logger.info(f"[ON_THIS_DAY] group={group_id} 推播={'成功' if ok else '失敗'}")
