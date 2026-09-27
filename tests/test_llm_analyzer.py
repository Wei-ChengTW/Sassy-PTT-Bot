import pytest

from travel.llm_analyzer import build_prompt, parse_llm_response


def test_build_prompt_includes_all_messages():
    messages = [
        {"id": 1, "user_name": "Alice", "content": "周末去墾丁", "timestamp": 1700000000000},
        {"id": 2, "user_name": "Bob", "content": "+1", "timestamp": 1700000001000},
    ]
    prompt = build_prompt(messages)
    assert "Alice" in prompt
    assert "Bob" in prompt
    assert "周末去墾丁" in prompt


def test_build_prompt_handles_none_content():
    messages = [{"id": 1, "user_name": "Alice", "content": None, "timestamp": 1700000000000}]
    prompt = build_prompt(messages)
    assert "Alice" in prompt


def test_parse_llm_response_strips_json_block():
    raw = '```json\n[{"id": 1, "is_travel_related": 1}]\n```'
    result = parse_llm_response(raw)
    assert result == [{"id": 1, "is_travel_related": 1}]


def test_parse_llm_response_handles_plain_json():
    raw = '[{"id": 1, "topics": ["travel"]}]'
    result = parse_llm_response(raw)
    assert result == [{"id": 1, "topics": ["travel"]}]


def test_parse_llm_response_raises_on_invalid():
    with pytest.raises(ValueError):
        parse_llm_response("not json at all")


def test_parse_llm_response_raises_on_non_array():
    raw = '{"id": 1}'
    with pytest.raises(ValueError):
        parse_llm_response(raw)

def test_write_analysis_results_keeps_sentiment(monkeypatch, tmp_path):
    """話題分析不可覆寫情緒（情緒由視窗式分析負責）；待分析預設由新到舊。"""
    import time
    from travel.db import init_db, insert_message, get_conn
    from travel.migrations import migrate
    from travel.llm_analyzer import fetch_pending_analysis, write_analysis_results
    monkeypatch.setenv("DB_PATH", str(tmp_path / "t.db"))
    init_db()
    migrate()
    for i, ts in enumerate((1000, 3000, 2000)):
        insert_message({"line_message_id": f"m{i}", "group_id": "C1", "user_id": "U1", "user_name": "A",
                        "type": "text", "content": f"訊息{i}", "metadata": {},
                        "reply_to_message_id": None, "timestamp": ts})
    assert [m["timestamp"] for m in fetch_pending_analysis()] == [3000, 2000, 1000]
    with get_conn() as conn:
        conn.execute("UPDATE messages SET sentiment = 0.7")
        mid = conn.execute("SELECT id FROM messages WHERE timestamp = 3000").fetchone()[0]
    assert write_analysis_results([{"id": mid, "topics": ["chat"], "sentiment": -1}]) == 1
    with get_conn() as conn:
        row = conn.execute("SELECT sentiment, analyzed_at FROM messages WHERE id = ?", (mid,)).fetchone()
    assert row[0] == 0.7 and row[1] is not None


def test_sentiment_write_accepts_string_window_ids(monkeypatch, tmp_path):
    """模型回傳字串 id 也要寫入（之前比對不到，約 1/4 視窗永遠評不到）。"""
    from travel.db import init_db, insert_message, get_conn
    from travel.migrations import migrate
    from travel.sentiment_windows import _write
    monkeypatch.setenv("DB_PATH", str(tmp_path / "t.db"))
    init_db()
    migrate()
    insert_message({"line_message_id": "m1", "group_id": "C1", "user_id": "U1", "user_name": "A",
                    "type": "text", "content": "超爽", "metadata": {},
                    "reply_to_message_id": None, "timestamp": 1})
    with get_conn() as conn:
        mid = conn.execute("SELECT id FROM messages").fetchone()[0]
    assert _write({7: [mid]}, [{"id": "7", "sentiment": 0.8}]) == 1
    with get_conn() as conn:
        assert conn.execute("SELECT sentiment FROM messages").fetchone()[0] == 0.8
