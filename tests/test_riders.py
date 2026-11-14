"""測試 line_bot/riders.py：搭便車小卡的排隊、取出、放回與 reply hook。"""
import os
import tempfile
import time
from datetime import datetime

import pytest
from linebot.v3.messaging import FlexMessage, ReplyMessageRequest, TextMessage
from linebot.v3.messaging.exceptions import ApiException

from line_bot import riders
from line_bot import stats_cards as cards
from line_bot.notify import TZ
from travel.db import init_db


@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DB_PATH", path)
    init_db()
    yield path
    for ext in ("", "-wal", "-shm"):
        if os.path.exists(path + ext):
            os.unlink(path + ext)


def _later(sec=3600):
    return int(time.time()) + sec


def test_enqueue_dedupes_by_group_and_key(temp_db):
    card = cards.build_entry_card("https://liff.line.me/x", False)
    assert riders.enqueue("G1", "k", card, _later()) is True
    assert riders.enqueue("G1", "k", card, _later()) is False
    assert riders.enqueue("G2", "k", card, _later()) is True


def test_take_roundtrips_message_and_marks_delivered(temp_db):
    card = cards.build_entry_card("https://liff.line.me/x", False)
    riders.enqueue("G1", "a", card, _later())
    ids, msgs = riders.take("G1", 4)
    assert len(ids) == 1 and isinstance(msgs[0], FlexMessage)
    assert msgs[0].to_dict() == card.to_dict()
    assert riders.take("G1", 4) == ([], [])          # 已送出不會再拿到


def test_take_skips_expired_other_groups_and_respects_room(temp_db):
    riders.enqueue("G1", "old", TextMessage(text="過期"), int(time.time()) - 1)
    for i in range(3):
        riders.enqueue("G1", f"k{i}", TextMessage(text=str(i)), _later())
    riders.enqueue("G2", "x", TextMessage(text="別群"), _later())
    ids, msgs = riders.take("G1", 2)
    assert [m.text for m in msgs] == ["0", "1"]       # 先排先送、不超過空位
    assert riders.take("G1", 0) == ([], [])


def test_release_puts_cards_back(temp_db):
    riders.enqueue("G1", "a", TextMessage(text="a"), _later())
    ids, _ = riders.take("G1", 4)
    riders.release(ids)
    assert len(riders.take("G1", 4)[1]) == 1


def test_end_of_day_is_local_midnight():
    now = datetime(2026, 9, 28, 23, 30, tzinfo=TZ)
    assert riders.end_of_day(TZ, now) == int(datetime(2026, 9, 29, tzinfo=TZ).timestamp())


class _FakeApi:
    def __init__(self, fail_first=None):
        self.sent, self.fail_first = [], fail_first

    def reply_message(self, request, *a, **kw):
        if self.fail_first:
            e, self.fail_first = self.fail_first, None
            raise e
        self.sent.append(request)


def _reply(text="嗆你"):
    return ReplyMessageRequest(reply_token="T", messages=[TextMessage(text=text)])


def test_hook_appends_riders_for_registered_group(temp_db):
    api, tokens = _FakeApi(), {"T": "G1"}
    riders.install_reply_hook(api, tokens)
    riders.enqueue("G1", "a", TextMessage(text="附卡"), _later())
    api.reply_message(_reply())
    assert [m.text for m in api.sent[0].messages] == ["嗆你", "附卡"]
    assert "T" not in tokens


def test_hook_passes_through_unknown_token(temp_db):
    api = _FakeApi()
    riders.install_reply_hook(api, {})
    riders.enqueue("G1", "a", TextMessage(text="附卡"), _later())
    api.reply_message(_reply())
    assert len(api.sent[0].messages) == 1
    assert len(riders.take("G1", 4)[1]) == 1          # 沒被拿走


def test_hook_drops_invalid_rider_and_still_sends_reply(temp_db):
    err = ApiException(status=400)
    err.body = '{"message":"A message (messages[1]) in the request body is invalid"}'
    api = _FakeApi(fail_first=err)
    riders.install_reply_hook(api, {"T": "G1"})
    riders.enqueue("G1", "a", TextMessage(text="壞卡"), _later())
    api.reply_message(_reply())
    assert [m.text for m in api.sent[0].messages] == ["嗆你"]
    assert riders.take("G1", 4) == ([], [])          # 壞卡不放回


def test_hook_releases_riders_when_reply_token_expired(temp_db):
    err = ApiException(status=400)
    err.body = '{"message":"Invalid reply token"}'
    api = _FakeApi(fail_first=err)
    riders.install_reply_hook(api, {"T": "G1"})
    riders.enqueue("G1", "a", TextMessage(text="附卡"), _later())
    with pytest.raises(ApiException):
        api.reply_message(_reply())
    assert len(riders.take("G1", 4)[1]) == 1          # 留給下一次
