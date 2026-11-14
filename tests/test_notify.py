"""測試 line_bot/notify.py 的日期判斷（純函式）。"""
from datetime import date, datetime

from line_bot import notify


def _ts(y, m, d, h=12):
    return int(datetime(y, m, d, h, tzinfo=notify.TZ).timestamp())


def test_countdown_days_by_calendar_date():
    today = date(2026, 9, 28)
    assert notify.countdown_days(_ts(2026, 10, 5, 1), today) == 7   # 凌晨出發也算 7 天
    assert notify.countdown_days(_ts(2026, 9, 28, 23), today) == 0
    assert notify.countdown_days(_ts(2026, 9, 27), today) is None    # 已出發
    assert notify.countdown_days(None, today) is None


def test_trips_departing_today_skips_other_days_and_ended():
    today = date(2026, 9, 28)
    trips = [
        {"id": "a", "status": "planning", "start_date": _ts(2026, 10, 5)},   # 7 天後 ✗
        {"id": "c", "status": "ended", "start_date": _ts(2026, 9, 28)},      # 已結束 ✗
        {"id": "d", "status": "planning", "start_date": _ts(2026, 9, 28, 23)},  # 當天 ✓
    ]
    assert [t["id"] for t in notify.trips_departing_today(trips, today)] == ["d"]


def test_on_this_day_trips_same_month_day_past_years():
    today = date(2026, 9, 28)
    trips = [
        {"id": "old", "start_date": _ts(2023, 9, 28)},
        {"id": "last", "start_date": _ts(2025, 9, 28)},
        {"id": "this_year", "start_date": _ts(2026, 9, 28)},
        {"id": "other_day", "start_date": _ts(2025, 9, 27)},
    ]
    got = notify.on_this_day_trips(trips, today)
    assert [(t["id"], t["years_ago"]) for t in got] == [("last", 1), ("old", 3)]


def test_announce_badges_skips_when_nothing_new(monkeypatch):
    called = []
    monkeypatch.setattr(notify, "push_flex", lambda *a: called.append(a) or True)
    assert notify.announce_badges("t1", []) is False
    assert called == []


def test_announce_badges_queues_instead_of_pushing(monkeypatch):
    import travel.trip_crud as crud
    monkeypatch.setattr(crud, "get_trip", lambda tid: {"id": tid, "group_id": "G", "title": "t", "rarity": "rare"})
    queued, pushed = [], []
    monkeypatch.setattr(notify.riders, "enqueue", lambda g, k, m, e: queued.append(g) or True)
    monkeypatch.setattr(notify, "push_flex", lambda *a: pushed.append(a) or True)
    assert notify.announce_badges("t1", [{"user_id": "u", "user_name": "A", "badge_name": "x", "badge_rarity": "rare"}])
    assert queued == ["G"] and pushed == []
