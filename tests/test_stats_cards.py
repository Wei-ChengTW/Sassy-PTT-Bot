"""測試 line_bot/stats_cards.py Flex 卡片產生器（純函式，需 linebot SDK）。"""
import pytest

pytest.importorskip("linebot.v3.messaging")

from line_bot import stats_cards as cards  # noqa: E402

LIFF = "https://liff.line.me/test-id"


def _all_text(node) -> str:
    """遞迴收集 Flex 節點內所有 text。"""
    out = getattr(node, "text", "") or ""
    for child in (getattr(node, "contents", None) or []):
        out += " " + _all_text(child)
    return out

DASH = {
    "summary": {"total_messages": 100, "active_days": 7, "member_count": 5, "active_trips": 1},
    "top_users": [{"user_id": "U1", "user_name": "阿明", "total": 40, "active_days": 6}],
    "type_distribution": [{"type": "text", "count": 80}, {"type": "sticker", "count": 20}],
}
LEAD = {
    "rankings": [
        {"user_id": "U1", "user_name": "阿明", "total": 40, "text_count": 30,
         "sticker_count": 10, "image_count": 0},
        {"user_id": "U2", "user_name": "小華", "total": 25, "text_count": 20,
         "sticker_count": 5, "image_count": 0},
    ],
    "night_owls": [{"user_id": "U2", "user_name": "小華", "night_count": 12}],
    "type_distribution": [],
}
INTER = {
    "best_pairs": [
        {"user1_id": "U1", "user1_name": "阿明", "user2_id": "U2",
         "user2_name": "小華", "count": 8},
    ],
    "network_nodes": [], "network_edges": [],
}
TOPICS = {
    "top_keywords": [{"keyword": "露營", "count": 9}, {"keyword": "美食", "count": 7}],
    "highlight_quotes": [{"user_name": "阿明", "content": "這趟真的太扯了啦",
                          "summary": "", "sentiment": 0.9, "tone": "戲劇", "timestamp": 0}],
    "hot_locations": [], "top_topics": [],
}
PROFILE = {
    "summary": {"total": 40, "active_days": 6, "avg_per_day": 6.6},
    "time_slots": {"night": 8, "morning": 5, "daytime": 20, "evening": 7},
    "personality": [{"tag": "夜貓子", "reason": ""}, {"tag": "貼圖狂魔", "reason": ""}],
    "top_topics": [], "avg_sentiment": 0.3,
}
BADGES = [{"badge_name": "露營王", "badge_rarity": "epic", "badge_emoji": "🏕️"}]


def test_leaderboard_card_has_ranking():
    b = cards.build_leaderboard_card(LEAD, LIFF)
    assert b.header.contents[0].text == "發言排行"
    # 第 1 名放大（hero）+ 第 2 名一列
    assert len(b.body.contents) == 2
    assert "阿明" in _all_text(b.body.contents[0]) and "小華" in _all_text(b.body.contents[1])


def test_leaderboard_alt_shows_first_place():
    assert cards.leaderboard_alt(LEAD) == "發言排行：第 1 名 阿明 40 則"
    assert cards.leaderboard_alt({"rankings": []}).startswith("發言排行：")


def test_leaderboard_card_empty_graceful():
    b = cards.build_leaderboard_card({"rankings": []}, LIFF)
    assert b.body.contents  # 有 fallback 文字


def test_nightowl_and_pairs_and_topics_build():
    assert cards.build_nightowl_card(LEAD, LIFF).header.contents[0].text == "夜貓榜"
    assert cards.build_pairs_card(INTER, LIFF).header.contents[0].text == "最佳拍檔"
    tcard = cards.build_topics_card(TOPICS, LIFF)
    # 關鍵字與金句都在 body
    joined = _all_text(tcard.body)
    assert "露營" in joined and "太扯" in joined


def test_report_carousel_has_three_bubbles():
    msg = cards.build_report_carousel(DASH, LEAD, INTER, TOPICS, LIFF, "本週")
    assert msg.alt_text.startswith("[本週群組戰報]")
    assert len(msg.contents.contents) == 3


def test_personal_card_includes_name_and_best_friend():
    bf = cards.best_friend_of(INTER, "U1")
    assert bf == "小華"
    msg = cards.build_personal_card(
        PROFILE, BADGES, bf, "阿明", LIFF, "U1", picture_url="https://profile.line-scdn.net/abc"
    )
    assert "阿明" in msg.alt_text
    assert "小華" in _all_text(msg.contents.body)  # 最佳拍檔
    # 檢查 header 是否包含頭像 FlexImage
    header = msg.contents.header
    assert header is not None
    # 尋找 header 內是否有 image 節點且 url 相符
    images = [c for c in header.contents if getattr(c, "type", "") == "image" or getattr(c, "url", None)]
    # 或在 header 的子 box 裡
    all_imgs = []
    def find_imgs(node):
        if getattr(node, "type", "") == "image" or getattr(node, "url", None):
            all_imgs.append(node)
        for child in (getattr(node, "contents", None) or []):
            find_imgs(child)
    find_imgs(header)
    assert len(all_imgs) == 1
    assert all_imgs[0].url == "https://profile.line-scdn.net/abc"


def test_quick_reply_fills_line_limit():
    qr = cards.stats_quick_reply(LIFF)
    assert len(qr.items) == 13   # LINE Quick Reply 上限
    labels = [i.action.label for i in qr.items]
    assert "晨型人" in labels and labels[-1] == "打開紀念冊"


def test_board_card_deep_links_to_board_and_inverts_ascending():
    board = {"id": "reply_speed", "title": "閃電回覆王", "subtitle": "平均回覆分鐘",
             "rows": [{"name": "A", "value": 2, "value_str": "2 分"},
                      {"name": "B", "value": 8, "value_str": "8 分"}],
             "highlight": None}
    b = cards.build_board_card(board, LIFF)
    assert b.footer.contents[0].action.uri == f"{LIFF}/leaderboard?board=reply_speed"
    # 第 2 名比例條：數值越小越好 → 2/8 = 25%
    bar = b.body.contents[1].contents[1].contents[0]
    assert bar.width == "25%"
    assert cards.board_alt(board) == "閃電回覆王：第 1 名 A 2 分"


def test_entry_card_has_four_links_and_admin_button():
    msg = cards.build_entry_card(LIFF, is_admin=True)
    rows = msg.contents.body.contents
    uris = [cell.action.uri for row in rows for cell in row.contents]
    assert uris == [f"{LIFF}/", f"{LIFF}/leaderboard", f"{LIFF}/timeline", f"{LIFF}/profile"]
    assert msg.contents.footer.contents[0].action.uri == f"{LIFF}/admin"
    assert cards.build_entry_card(LIFF).contents.footer is None


def test_countdown_card_alt_and_link():
    trip = {"id": "t1", "title": "韓國小滑雪", "location": "韓國", "start_date": 1800000000,
            "rarity": "epic", "badge_emoji": "🏂"}
    assert cards.build_countdown_card(trip, 7, LIFF).alt_text == "韓國小滑雪：還有 7 天出發"
    assert cards.build_countdown_card(trip, 0, LIFF).alt_text == "韓國小滑雪：今天出發"
    assert cards.build_countdown_card(trip, 7, LIFF).contents.footer.contents[0].action.uri == f"{LIFF}/trips/t1"


def test_badge_award_card_lists_everyone():
    trip = {"id": "t1", "title": "墾丁一日遊"}
    awarded = [{"user_name": "阿明", "badge_emoji": "🏖️", "badge_rarity": "legendary"},
               {"user_name": "小華", "badge_emoji": "🏖️", "badge_rarity": "legendary"}]
    msg = cards.build_badge_award_card(trip, awarded, LIFF)
    assert msg.alt_text == "徽章頒發：墾丁一日遊（傳說）2 人獲得"
    assert "阿明、小華" in _all_text(msg.contents.body)


def test_on_this_day_card_none_when_empty():
    assert cards.build_on_this_day_card([], None, LIFF) is None
    trips = [{"id": "t9", "title": "花東三日遊", "years_ago": 2, "rarity": "rare"}]
    msg = cards.build_on_this_day_card(trips, {"content": "笑死", "user_name": "阿明"}, LIFF)
    assert msg.alt_text.startswith("那年今日：2 年前的今天")
    assert "笑死" in _all_text(msg.contents.body)


def test_competition_ranks_ties_share_rank():
    from line_bot.stats_cards import competition_ranks
    assert competition_ranks([9, 9, 8, 8, 8, 5]) == [1, 1, 2, 2, 2, 3]
    assert competition_ranks([]) == []
