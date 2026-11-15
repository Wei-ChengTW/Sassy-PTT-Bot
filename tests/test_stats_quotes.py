"""精選語錄：內容過濾（stats_extended）＋ 規則分數／候選池／LLM 解析（travel/quotes.py）。"""
import pytest
from travel.stats_extended import _is_quote_worthy


def _row(content, sentiment, timestamp, user_name="A"):
    return {"user_name": user_name, "content": content,
            "summary": "", "sentiment": sentiment, "timestamp": timestamp}


# ─── 內容過濾 ───────────────────────────────────────────────────────────────

def test_worthy_rejects_none_and_blank():
    assert not _is_quote_worthy(None)
    assert not _is_quote_worthy("")
    assert not _is_quote_worthy("   ")


def test_worthy_rejects_short_ack():
    for text in ("真的", "確實", "好喔", "笑死", "哈哈", "嗯嗯"):
        assert not _is_quote_worthy(text), f"應過濾短附和: {text}"


def test_worthy_rejects_pure_url():
    for text in ("https://youtu.be/abc123", "http://example.com", "https://www.ptt.cc/bbs/index.html"):
        assert not _is_quote_worthy(text), f"應過濾純網址: {text}"


def test_worthy_rejects_placeholder():
    for text in ("[照片]", "[貼圖]", "[語音]", "[影片]"):
        assert not _is_quote_worthy(text), f"應過濾佔位符: {text}"


def test_worthy_rejects_noise_quotes():
    for text in ("哈哈哈哈", "呵呵呵呵", "好喔好喔"):
        assert not _is_quote_worthy(text), f"應過濾無意義笑聲/附和: {text}"


def test_worthy_accepts_real_sentence():
    assert _is_quote_worthy("這趟真的太扯了啦")
    assert _is_quote_worthy("今天天氣爛到爆炸")
    assert _is_quote_worthy("居然連這種地方都能吃到超好吃的小籠包")


# ─── 規則分數與候選池（travel/quotes.py）────────────────────────────────────

from travel.quotes import (  # noqa: E402
    build_pool, count_laughs_after, parse_curation, pick_rule_based, quote_score,
)


def _cand(id, user, score, ts, sentiment=0.5, content=None):
    return {"id": id, "user_name": user, "score": score, "timestamp": ts,
            "sentiment": sentiment, "content": content or f"第{id}句"}


def test_quote_score_rewards_reactions_with_cap():
    assert quote_score(-0.5, 0, 0) == 0.5
    assert quote_score(0.5, 1, 2) > quote_score(0.9, 0, 0)       # 有人笑比情緒強更重要
    assert quote_score(0.5, 10, 10) == quote_score(0.5, 3, 3)    # 反應最多算 3 次


def test_count_laughs_after_only_others_within_window():
    stream = [
        {"user_id": "A", "content": "我連車都停不進去", "timestamp": 0},
        {"user_id": "A", "content": "哈哈哈", "timestamp": 1000},        # 自己笑不算
        {"user_id": "B", "content": "笑死", "timestamp": 2000},
        {"user_id": "C", "content": "XD", "timestamp": 60_000},
        {"user_id": "D", "content": "好", "timestamp": 70_000},          # 不是笑
        {"user_id": "E", "content": "笑死", "timestamp": 200_000},       # 超過 2 分鐘
    ]
    ts = [m["timestamp"] for m in stream]
    assert count_laughs_after(stream[0], stream, ts) == 2


def test_build_pool_one_per_moment_and_per_person_cap():
    cands = [
        _cand(1, "A", 1.0, 0), _cand(2, "B", 2.0, 1000),           # 同一時段 → 留高分的 2
        _cand(3, "A", 1.5, 10**7), _cand(4, "A", 1.4, 2 * 10**7), _cand(5, "A", 1.3, 3 * 10**7),
    ]
    pool = build_pool(cands, size=10, per_person=2)
    assert [c["id"] for c in pool] == [2, 3, 4]


def test_pick_rule_based_balances_and_caps_person():
    pool = ([_cand(i, "A", 2 - i * 0.1, i, sentiment=0.8) for i in range(4)]
            + [_cand(10 + i, f"N{i}", 1 - i * 0.1, 100 + i, sentiment=-0.8) for i in range(3)])
    picked = pick_rule_based(pool, limit=4, per_person=2)
    assert [c["id"] for c in picked] == [0, 1, 10, 11]


def test_parse_curation_filters_unknown_ids_and_caps_person():
    pool = [_cand(1, "A", 1, 0), _cand(2, "A", 1, 1), _cand(3, "A", 1, 2), _cand(4, "B", 1, 3)]
    raw = '```json\n[{"id": 1, "label": "💀 社死現場"}, {"id": 99, "label": "x"}, {"id": "2"},' \
          ' {"id": 3, "label": "y"}, {"id": 4, "label": "🤡 自爆代表"}]\n```'
    out = parse_curation(raw, pool)
    assert [c["id"] for c in out] == [1, 2, 4]
    assert out[0]["label"] == "💀 社死現場" and out[1]["label"] is None
    assert parse_curation("不是 JSON", pool) == []


def test_quotes_exclude_personal_info():
    from travel.stats_extended import _is_quote_worthy
    for text in ("新北市汐止區東勢街201巷106弄21號", "我家在中山路 12 號 3 樓", "打給我 0912-345-678",
                 "市話 02-23456789", "寄到 abc@gmail.com", "身分證 A123456789", "帳號：abc 密碼：xyz"):
        assert not _is_quote_worthy(text), text
    for text in ("我有男朋友 我不演了", "其實我有不小心講21歲", "黃金我要做多還是做空 All_in", "第3名就好", "他今天才知道12號有沒有空"):
        assert _is_quote_worthy(text), text
