"""Dashboard / trips / badges 查詢業務邏輯。被 liff_api.py 呼叫。"""
import json
import time
from collections import Counter

from travel.db import get_conn
from travel.badges import compute_badge_emoji
from travel.period import period_filter
from travel.trip_types import parse_trip_types


def get_dashboard_data(group_id: str, days: int = 30, period: str = "all") -> dict:
    """回傳群組儀表板資料。period 過濾套用於逐訊息統計，排除非正式成員的純記憶匯入訊息。"""
    since_ms = int((time.time() - days * 86400) * 1000)
    pf, pp = period_filter(period)
    with get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM messages WHERE group_id=?{pf} AND user_id NOT LIKE 'imported:%'", (group_id, *pp)
        ).fetchone()[0]
        member_count = conn.execute(
            f"SELECT COUNT(DISTINCT user_id) FROM messages WHERE group_id=?{pf} AND user_id NOT LIKE 'imported:%'",
            (group_id, *pp),
        ).fetchone()[0]
        # 預計進行＝還沒按結束（還沒出發的、正在進行的都算），對應總覽卡片「預計進行的行程」
        active_trips = conn.execute(
            "SELECT COUNT(*) FROM trips WHERE group_id=? AND status='planning'", (group_id,)
        ).fetchone()[0]
        active_days = conn.execute(
            f"""SELECT COUNT(DISTINCT date(timestamp/1000, 'unixepoch', 'localtime'))
               FROM messages WHERE group_id=?{pf} AND user_id NOT LIKE 'imported:%'""",
            (group_id, *pp),
        ).fetchone()[0]

        top_users = conn.execute(
            f"""SELECT user_id, user_name, COUNT(*) AS total,
                      COUNT(DISTINCT date(timestamp/1000,'unixepoch','localtime')) AS active_days
               FROM messages WHERE group_id=?{pf} AND user_id NOT LIKE 'imported:%'
               GROUP BY user_id ORDER BY total DESC LIMIT 10""",
            (group_id, *pp),
        ).fetchall()

        type_dist = conn.execute(
            f"""SELECT type, COUNT(*) AS count FROM messages
               WHERE group_id=?{pf} AND user_id NOT LIKE 'imported:%' GROUP BY type ORDER BY count DESC""",
            (group_id, *pp),
        ).fetchall()

        # daily_counts：period 已選時用區間，否則用 days 視窗
        if pf:
            daily_counts = conn.execute(
                f"""SELECT date(timestamp/1000,'unixepoch','localtime') AS date, COUNT(*) AS count
                   FROM messages WHERE group_id=?{pf} AND user_id NOT LIKE 'imported:%'
                   GROUP BY date ORDER BY date ASC""",
                (group_id, *pp),
            ).fetchall()
        else:
            daily_counts = conn.execute(
                """SELECT date(timestamp/1000,'unixepoch','localtime') AS date, COUNT(*) AS count
                   FROM messages WHERE group_id=? AND timestamp >= ? AND user_id NOT LIKE 'imported:%'
                   GROUP BY date ORDER BY date ASC""",
                (group_id, since_ms),
            ).fetchall()

        heatmap = conn.execute(
            f"""SELECT CAST(strftime('%w', timestamp/1000,'unixepoch','localtime') AS INTEGER) AS day_of_week,
                      CAST(strftime('%H', timestamp/1000,'unixepoch','localtime') AS INTEGER) AS hour,
                      COUNT(*) AS count
               FROM messages WHERE group_id=?{pf} AND user_id NOT LIKE 'imported:%'
               GROUP BY day_of_week, hour""",
            (group_id, *pp),
        ).fetchall()

        # 近期以日期維度的每日 24 小時熱力分佈 (供精確日期檢視)
        recent_date_heatmap = conn.execute(
            f"""SELECT date(timestamp/1000,'unixepoch','localtime') AS date,
                      CAST(strftime('%H', timestamp/1000,'unixepoch','localtime') AS INTEGER) AS hour,
                      COUNT(*) AS count
               FROM messages WHERE group_id=?{pf} AND user_id NOT LIKE 'imported:%'
               GROUP BY date, hour ORDER BY date DESC, hour ASC""",
            (group_id, *pp),
        ).fetchall()

        monthly_trend, seasonality = _monthly_and_seasonality(conn, group_id, period)

        health = _compute_group_health(conn, group_id, period)
        weekly_trend = _compute_weekly_trend(conn, group_id)

        # 旅行類型分佈：展開所有 trips 的 trip_type（JSON 陣列）計數
        trip_type_rows = conn.execute(
            "SELECT trip_type FROM trips WHERE group_id=?", (group_id,)
        ).fetchall()

    type_counter: Counter[str] = Counter()
    for tr in trip_type_rows:
        for t in parse_trip_types(tr["trip_type"]):
            type_counter[t] += 1
    trip_type_distribution = [
        {"type": t, "count": c} for t, c in type_counter.most_common()
    ]

    return {
        "summary": {
            "total_messages": total,
            "active_days": active_days,
            "member_count": member_count,
            "active_trips": active_trips,
        },
        "top_users": [dict(r) for r in top_users],
        "type_distribution": [dict(r) for r in type_dist],
        "daily_counts": [dict(r) for r in daily_counts],
        "heatmap": [dict(r) for r in heatmap],
        "recent_date_heatmap": [dict(r) for r in recent_date_heatmap],
        "monthly_trend": monthly_trend,
        "seasonality": seasonality,
        "trip_type_distribution": trip_type_distribution,
        "health": health,
        "weekly_trend": weekly_trend,
    }


_DAY_MS = 86_400_000
HEALTH_RECENT_DAYS = 30        # 選「全部時間」時看最近幾天
HEALTH_BASELINE_FACTOR = 3     # 基準＝比較區間之前、幾倍長度的時間
HEALTH_NORMAL = 70             # 「跟平常一樣」的分數
DIVERSITY_SAMPLE = 300         # 多樣性固定抽幾個關鍵字，避免資料量多寡影響結果
MIN_SENTIMENT_MSGS = 30        # 情緒有評分的訊息少於此數就不算
MIN_ACTIVE_MSGS = 3            # 參與度：區間內至少發言幾則才算有參與
MIN_KEYWORD_COVERAGE = 0.5     # 文字訊息有一半以上分析過，多樣性才算（分析跑到一半時不準）


def _clamp(x: float) -> float:
    return max(0.0, min(100.0, x))


def _health_window(period: str, now_ms: int) -> tuple[int, int, str]:
    """回傳 (start_ms, end_ms, 說明)。全部時間 → 最近 30 天；進行中的期間截到現在。"""
    from travel.period import parse_period
    start, end = parse_period(period)
    if start is None:
        return now_ms - HEALTH_RECENT_DAYS * _DAY_MS, now_ms, f"最近 {HEALTH_RECENT_DAYS} 天"
    end = min(end, now_ms)
    return start, end, period


def _keyword_spread(rows) -> float | None:
    """固定間隔抽 DIVERSITY_SAMPLE 個關鍵字，回傳不重複的比例；不夠多回 None。"""
    kws: list[str] = []
    for r in rows:
        try:
            kws.extend(k for k in json.loads(r[0]) if isinstance(k, str))
        except (json.JSONDecodeError, TypeError):
            pass
    if len(kws) < DIVERSITY_SAMPLE:
        return None
    step = len(kws) / DIVERSITY_SAMPLE
    sample = [kws[int(i * step)] for i in range(DIVERSITY_SAMPLE)]
    return len(set(sample)) / DIVERSITY_SAMPLE


def _range_stats(conn, group_id: str, start: int, end: int) -> dict:
    """某段時間的每日訊息量、關鍵字分散度、平均情緒。"""
    base = "FROM messages WHERE group_id=? AND timestamp>=? AND timestamp<? AND user_id NOT LIKE 'imported:%'"
    args = (group_id, start, end)
    n = conn.execute(f"SELECT COUNT(*) {base}", args).fetchone()[0]
    sent_avg, sent_n = conn.execute(
        f"SELECT AVG(sentiment), COUNT(sentiment) {base} AND sentiment IS NOT NULL", args).fetchone()
    kw_rows = conn.execute(
        f"SELECT keywords {base} AND keywords IS NOT NULL AND keywords != '[]' ORDER BY timestamp", args).fetchall()
    text_n = conn.execute(f"SELECT COUNT(*) {base} AND type='text' AND length(content)>1", args).fetchone()[0]
    covered = text_n and len(kw_rows) / text_n >= MIN_KEYWORD_COVERAGE
    days = max((end - start) / _DAY_MS, 1.0)
    return {
        "per_day": n / days,
        "msgs": n,
        "spread": _keyword_spread(kw_rows) if covered else None,
        "sentiment": sent_avg if sent_n >= MIN_SENTIMENT_MSGS else None,
    }


def _compute_group_health(conn, group_id: str, period: str = "all", now_ms: int | None = None) -> dict | None:
    """群組健康度：每一項都跟群組自己的過去比，「跟平常一樣」＝ 70 分。

    - 比較區間：選全部時間看最近 30 天，選年／月看該期間；基準是它之前 3 倍長度的時間。
    - 活躍度：每日訊息量 ÷ 基準，一樣 70、多一倍 100、少一半 40。
    - 多樣性：固定抽 300 個關鍵字的不重複比例 ÷ 基準（多 15% → 約 100）。
    - 情緒：平均情緒 − 基準，+0.15 → 100、−0.15 → 40。
    - 參與度：名冊上區間內發言 ≥ 3 則的人的比例（絕對值，不跟過去比）。
    資料不足的分項為 None、不列入加權；全部都不足回 None。
    """
    import math
    now_ms = now_ms or int(time.time() * 1000)
    start, end, label = _health_window(period, now_ms)
    length = end - start
    if length <= 0:
        return None
    cur = _range_stats(conn, group_id, start, end)
    base = _range_stats(conn, group_id, start - HEALTH_BASELINE_FACTOR * length, start)

    activity = None
    if cur["msgs"] and base["per_day"] > 0:
        activity = _clamp(HEALTH_NORMAL + 30 * math.log2(cur["per_day"] / base["per_day"]))
    elif cur["msgs"] == 0:
        activity = 0.0

    diversity = None
    if cur["spread"] is not None and base["spread"]:
        diversity = _clamp(HEALTH_NORMAL + 200 * (cur["spread"] / base["spread"] - 1))

    sentiment = None
    if cur["sentiment"] is not None and base["sentiment"] is not None:
        sentiment = _clamp(HEALTH_NORMAL + 200 * (cur["sentiment"] - base["sentiment"]))

    roster = conn.execute("SELECT COUNT(*) FROM members WHERE group_id=?", (group_id,)).fetchone()[0] or 0
    counts = [r[0] for r in conn.execute(
        """SELECT COUNT(*) FROM messages WHERE group_id=? AND timestamp>=? AND timestamp<?
             AND user_id NOT LIKE 'imported:%' GROUP BY user_id""", (group_id, start, end))]
    denom = roster or len(counts)
    participation = _clamp(sum(c >= MIN_ACTIVE_MSGS for c in counts) / denom * 100) if denom else None

    weights = {"activity": 0.30, "diversity": 0.25, "sentiment": 0.25, "participation": 0.20}
    scores = {"activity": activity, "diversity": diversity, "sentiment": sentiment, "participation": participation}
    present = {k: v for k, v in scores.items() if v is not None}
    if not present:
        return None
    overall = sum(v * weights[k] for k, v in present.items()) / sum(weights[k] for k in present)

    suggestions: list[str] = []
    if activity is not None and activity < 50:
        suggestions.append("聊天量比平常少，試著開個新話題")
    if participation is not None and participation < 60:
        suggestions.append("多鼓勵潛水員發言")
    if diversity is not None and diversity < 50:
        suggestions.append("最近都在聊同幾件事，換點新話題")
    if sentiment is not None and sentiment < 50:
        suggestions.append("氣氛比平常低迷，帶點正能量")
    if not suggestions:
        suggestions.append("跟平常差不多或更好，繼續保持！" if overall < 85 else "最近特別熱絡，繼續保持！")

    return {
        "overall": round(overall),
        "activity": round(activity) if activity is not None else None,
        "diversity": round(diversity) if diversity is not None else None,
        "sentiment": round(sentiment) if sentiment is not None else None,
        "participation": round(participation) if participation is not None else None,
        "window": label,
        "suggestions": suggestions,
    }


def _compute_weekly_trend(conn, group_id: str, weeks: int = 8) -> dict:
    """最近 N 週的每週訊息量與活躍人數 + 本週 vs 上週成長率。

    以現在往回推的滾動視窗（不套 period），缺資料的週補 0。
    """
    now_ms = int(time.time() * 1000)
    day_ms = 86_400_000
    since = now_ms - weeks * 7 * day_ms
    rows = conn.execute(
        """SELECT strftime('%Y-%W', timestamp/1000,'unixepoch','localtime') AS week,
                  COUNT(*) AS count,
                  COUNT(DISTINCT user_id) AS active_users
           FROM messages WHERE group_id=? AND timestamp >= ?
           GROUP BY week ORDER BY week ASC""",
        (group_id, since),
    ).fetchall()

    series = [
        {"week": r["week"], "count": r["count"], "active_users": r["active_users"]}
        for r in rows
    ]
    this_week = series[-1]["count"] if series else 0
    last_week = series[-2]["count"] if len(series) >= 2 else 0
    growth = (
        round((this_week - last_week) * 100.0 / last_week, 1) if last_week > 0 else None
    )

    return {
        "weeks": series,
        "this_week": this_week,
        "last_week": last_week,
        "growth_percent": growth,
    }


def _monthly_and_seasonality(conn, group_id: str, period: str):
    """月成長率趨勢 + 季節性（跨年同月）。period=年時月趨勢限該年，季節性一律跨全期。"""
    from travel.period import parse_period
    start, end = parse_period(period)
    # 月趨勢：若 period 指定年，限該年；否則全部
    if start is not None:
        month_rows = conn.execute(
            """SELECT strftime('%Y-%m', timestamp/1000,'unixepoch','localtime') AS month,
                      COUNT(*) AS count
               FROM messages WHERE group_id=? AND timestamp >= ? AND timestamp < ?
               GROUP BY month ORDER BY month ASC""",
            (group_id, start, end),
        ).fetchall()
    else:
        month_rows = conn.execute(
            """SELECT strftime('%Y-%m', timestamp/1000,'unixepoch','localtime') AS month,
                      COUNT(*) AS count
               FROM messages WHERE group_id=?
               GROUP BY month ORDER BY month ASC""",
            (group_id,),
        ).fetchall()

    monthly_trend = []
    prev = None
    for r in month_rows:
        count = r["count"]
        growth = None
        if prev is not None and prev > 0:
            growth = round((count - prev) * 100.0 / prev, 1)
        monthly_trend.append({"month": r["month"], "count": count, "growth_rate_percent": growth})
        prev = count

    season_rows = conn.execute(
        """SELECT CAST(strftime('%m', timestamp/1000,'unixepoch','localtime') AS INTEGER) AS month,
                  COUNT(*) AS count
           FROM messages WHERE group_id=?
           GROUP BY month ORDER BY month ASC""",
        (group_id,),
    ).fetchall()
    seasonality = [{"month": r["month"], "count": r["count"]} for r in season_rows]

    return monthly_trend, seasonality


def get_trips_list(group_id: str) -> list[dict]:
    """回傳群組所有旅行列表（含 badge_emoji）。"""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, title, location, start_date, end_date,
                      rarity, status, created_at, trip_type, custom_emoji
               FROM trips WHERE group_id=? ORDER BY created_at DESC""",
            (group_id,),
        ).fetchall()
    result = []
    for r in rows:
        trip = dict(r)
        rarity = trip.get("rarity") or "common"
        trip["badge_emoji"] = compute_badge_emoji(trip, rarity)
        trip["trip_types"] = parse_trip_types(trip.pop("trip_type", None))
        result.append(trip)
    return result


def get_trip_detail(trip_id: str) -> dict:
    """回傳單一旅行詳情（含 participants）。"""
    with get_conn() as conn:
        trip_row = conn.execute(
            "SELECT * FROM trips WHERE id=?", (trip_id,)
        ).fetchone()
        participants_rows = conn.execute(
            """SELECT tp.user_id, tp.role, tp.joined_at, tp.messages_count,
                      COALESCE(
                        (SELECT user_name FROM messages WHERE user_id=tp.user_id AND group_id=t.group_id LIMIT 1),
                        (SELECT display_name FROM members WHERE user_id=tp.user_id LIMIT 1)
                      ) AS user_name
               FROM trip_participants tp
               JOIN trips t ON t.id = tp.trip_id
               WHERE tp.trip_id=?""",
            (trip_id,),
        ).fetchall()
        
        trip = dict(trip_row) if trip_row else {}
        gid = trip.get("group_id")
        st = trip.get("start_date")
        et = trip.get("end_date")

        if gid and st:
            if et:
                # end_date 當天 23:59:59
                end_ts_ms = (et + 86400) * 1000 - 1
            elif trip.get("status") == "ended":
                # 單日事件若已結束但無 end_date，計算出發日當天 24 小時內訊息
                end_ts_ms = (st + 86400) * 1000 - 1
            else:
                # 進行中的旅行
                end_ts_ms = int(time.time() * 1000)

            start_ts_ms = st * 1000
            msg_count = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE group_id=? AND timestamp BETWEEN ? AND ?",
                (gid, start_ts_ms, end_ts_ms),
            ).fetchone()[0]
        else:
            msg_count = 0

    if trip:
        trip["trip_types"] = parse_trip_types(trip.get("trip_type"))

    return {
        "trip": trip,
        "participants": [dict(r) for r in participants_rows],
        "stats": {"message_count": msg_count},
        "memorable_quotes": [],
    }


def get_user_badges(user_id: str, group_id: str | None = None) -> list[dict]:
    """回傳 user 在某群組（若有指定）或全部的所有徽章。"""
    with get_conn() as conn:
        if group_id:
            rows = conn.execute(
                """SELECT b.id AS badge_id, b.badge_name, b.badge_rarity,
                          b.badge_image_url, b.earned_at, b.trip_id, b.description,
                          t.title, t.location, t.trip_type, t.start_date, t.end_date, t.custom_emoji
                   FROM badges b
                   LEFT JOIN trips t ON t.id = b.trip_id
                   WHERE b.user_id=? AND (t.group_id=? OR t.group_id IS NULL)
                     AND b.user_id IS NOT NULL
                   ORDER BY COALESCE(t.start_date, b.earned_at) DESC""",
                (user_id, group_id),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT b.id AS badge_id, b.badge_name, b.badge_rarity,
                          b.badge_image_url, b.earned_at, b.trip_id, b.description,
                          t.title, t.location, t.trip_type, t.start_date, t.end_date, t.custom_emoji
                   FROM badges b
                   LEFT JOIN trips t ON t.id = b.trip_id
                   WHERE b.user_id=? AND b.user_id IS NOT NULL
                   ORDER BY COALESCE(t.start_date, b.earned_at) DESC""",
                (user_id,),
            ).fetchall()
    result = []
    for r in rows:
        badge = dict(r)
        rarity = badge.get("badge_rarity") or "common"
        trip_info = {
            "title": badge.get("title") or "",
            "location": badge.get("location") or "",
            "trip_type": badge.get("trip_type") or "",
            "custom_emoji": badge.get("custom_emoji") or "",
        }
        badge["badge_emoji"] = compute_badge_emoji(trip_info, rarity)
        result.append(badge)
    return result