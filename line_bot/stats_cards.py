"""統計 Flex 卡片產生器（方案 A–D 共用）。

把 travel.stats / travel.stats_extended 的查詢結果轉成 LINE Messaging API 的
Flex Message / Carousel 與 Quick Reply。純函式、無副作用，方便單元測試。

視覺與 LIFF 同一套「畢業紀念冊」：深綠布面標頭 + 燙金細線、第 1 名放大、
2–3 名銀／銅座號、其餘附比例條。色碼需與 liff/tailwind.config.js 同步。

這裡在模組頂層 import linebot SDK——僅由 bot.py 在 line_api 可用時才 lazy import
本模組，故不影響「無 SDK 也能跑」的設計。
"""
from linebot.v3.messaging import (
    FlexMessage, FlexBubble, FlexBox, FlexText, FlexButton, FlexSeparator, FlexImage,
    FlexCarousel, URIAction, MessageAction, QuickReply, QuickReplyItem,
)

# ── 紀念冊色票（與 LIFF 一致） ──
CLOTH = "#1E3A2F"        # 布面深綠：標頭、主按鈕、比例條
FOIL = "#B8943A"         # 燙金：細線、第 1 名
FOIL_DARK = "#8F7020"    # 燙金文字（淺底上）
FOIL_LIGHT = "#E6D09A"   # 燙金文字（深綠底上）
FOIL_BG = "#FAF5E9"      # 第 1 名淡金底
SAGE = "#C9D3CC"         # 深綠底上的次要文字
INK = "#191D1A"          # 主要文字
MUTED = "#646B65"        # 次要文字
RULE = "#DDE1DC"         # 分隔線、比例條底
PEN = "#2346A0"          # 原子筆藍：留言
PEN_BG = "#EEF1FA"       # 留言信紙底
SEAL = "#B8332A"         # 印章紅

MEDAL = {1: "#C6A252", 2: "#BFC7C5", 3: "#C8956A"}   # 金／銀／銅座號

RARITY_LINE = {
    "common": "#8C938C", "rare": "#2346A0", "super_rare": "#2E7D4F",
    "epic": "#B8943A", "legendary": "#B8332A",
}
RARITY_ZH = {"common": "普通", "rare": "稀有", "super_rare": "極稀有", "epic": "史詩", "legendary": "傳說"}

# 舊色名保留給外部引用（travel.leaderboards 的 accent 已不再用於卡片）
BLUE, GOLD = PEN, FOIL


def best_friend_of(inter: dict, user_id: str) -> str | None:
    """從 best_pairs 找出與該 user 互動最密切的對象名字（已按 count 排序）。"""
    for p in (inter.get("best_pairs") or []):
        if p.get("user1_id") == user_id:
            return p.get("user2_name")
        if p.get("user2_id") == user_id:
            return p.get("user1_name")
    return None


def competition_ranks(values: list) -> list[int]:
    """同分同名次、不跳號（1,1,2）：values 須已由高到低排好。"""
    ranks: list[int] = []
    for i, v in enumerate(values):
        if i == 0:
            ranks.append(1)
        else:
            ranks.append(ranks[-1] if v == values[i - 1] else ranks[-1] + 1)
    return ranks


# ── 低階組裝 helpers ────────────────────────────────────────────────

def _txt(text: str, **kw) -> FlexText:
    kw.setdefault("color", INK)
    kw.setdefault("size", "sm")
    return FlexText(text=text, **kw)


def _foil_rule(margin: str = "md") -> FlexBox:
    """燙金細線（40px × 1px）。"""
    return FlexBox(layout="vertical", contents=[], width="40px", height="1px",
                   backgroundColor=FOIL, margin=margin)


def _header(title: str, subtitle: str | None = None) -> FlexBox:
    contents: list = [_txt(title, size="lg", weight="bold", color="#FFFFFF", wrap=True)]
    if subtitle:
        contents.append(_txt(subtitle, size="xs", color=SAGE, wrap=True, margin="xs"))
    contents.append(_foil_rule())
    return FlexBox(layout="vertical", backgroundColor=CLOTH, paddingAll="16px", contents=contents)


def _button(label: str, uri: str) -> FlexButton:
    return FlexButton(action=URIAction(label=label, uri=uri), style="primary",
                      color=CLOTH, height="sm")


def _bubble(title: str, body: list, button: FlexButton | None = None,
            subtitle: str | None = None) -> FlexBubble:
    return FlexBubble(
        header=_header(title, subtitle),
        body=FlexBox(layout="vertical", spacing="md", paddingAll="16px", contents=body),
        footer=(FlexBox(layout="vertical", paddingAll="12px", paddingTop="0px", contents=[button])
                if button else None),
    )


def _empty_body(msg: str) -> list:
    return [_txt(msg, color=MUTED, wrap=True)]


def _seat(rank: int) -> FlexBox:
    """座號方塊：1–3 名金銀銅實心，其餘灰框。"""
    fill = MEDAL.get(rank)
    return FlexBox(
        layout="vertical", width="24px", height="24px", cornerRadius="3px", flex=0,
        justifyContent="center", alignItems="center",
        backgroundColor=fill or "#FFFFFF",
        borderWidth="0px" if fill else "1.5px", borderColor=RULE,
        contents=[_txt(str(rank), size="xs", weight="bold", align="center")],
    )


def _bar(ratio: int) -> FlexBox:
    """比例條：4px 高，ratio 為 0–100。"""
    ratio = max(3, min(100, ratio))
    return FlexBox(layout="vertical", height="4px", backgroundColor=RULE, cornerRadius="2px",
                   margin="sm", contents=[
                       FlexBox(layout="vertical", contents=[], width=f"{ratio}%", height="4px",
                               backgroundColor=CLOTH, cornerRadius="2px"),
                   ])


def _hero(name: str, value: str, label: str = "第 1 名", note: str | None = None) -> FlexBox:
    """第 1 名：淡金底、名字與數字放大。"""
    left: list = [_txt(label, size="xxs", color=FOIL_DARK),
                  _txt(name, size="xl", weight="bold", wrap=True)]
    if note:
        left.append(_txt(note, size="xs", color=MUTED, wrap=True))
    return FlexBox(
        layout="horizontal", backgroundColor=FOIL_BG, cornerRadius="4px", paddingAll="12px",
        alignItems="center", spacing="md",
        contents=[
            FlexBox(layout="vertical", flex=1, contents=left),
            _txt(value, size="xl", weight="bold", color=FOIL_DARK, flex=0, align="end"),
        ],
    )


def _ranked(rows: list[tuple[str, float, str]], invert: bool = False) -> list:
    """rows = [(name, 數值, 顯示字串)]，須已排好序。第 1 名 hero，其餘座號 + 比例條。

    invert=True 表示數值越小越好（例如回覆分鐘數），比例條以最佳值為滿格。
    """
    if not rows:
        return []
    ranks = competition_ranks([r[1] for r in rows])
    out: list = [_hero(rows[0][0], rows[0][2], f"第 {ranks[0]} 名")]
    values = [abs(r[1] or 0) for r in rows]
    top, best = max(values) or 1, min(values) or 1
    for rank, (name, value, value_str) in zip(ranks[1:], rows[1:]):
        v = abs(value or 0)
        ratio = round(best / v * 100) if invert and v else round(v / top * 100)
        out.append(FlexBox(layout="vertical", contents=[
            FlexBox(layout="horizontal", spacing="md", alignItems="center", contents=[
                _seat(rank),
                _txt(name, flex=1, weight="bold"),
                _txt(value_str, flex=0, align="end", weight="bold"),
            ]),
            _bar(ratio),
        ]))
    return out


def _top_alt(title: str, rows: list[tuple[str, float, str]], fallback: str) -> str:
    """通知預覽：不點開也看得到第 1 名。"""
    if not rows:
        return f"{title}：{fallback}"
    return f"{title}：第 1 名 {rows[0][0]} {rows[0][2]}"


# ── 各維度單卡（quick-reply 點擊回覆） ──────────────────────────────

def _leader_rows(lead: dict) -> list:
    return [(r.get("user_name") or "路人", r.get("total", 0), f"{r.get('total', 0):,} 則")
            for r in (lead.get("rankings") or [])[:5]]


def build_leaderboard_card(lead: dict, liff_url: str) -> FlexBubble:
    rows = _leader_rows(lead)
    body = _ranked(rows) or _empty_body("這段期間還沒有人發言。")
    return _bubble("發言排行", body, _button("看完整排行", f"{liff_url}/leaderboard"),
                   subtitle="全部時間 · 前 5 名")


def leaderboard_alt(lead: dict) -> str:
    return _top_alt("發言排行", _leader_rows(lead), "還沒有人發言")


def _owl_rows(lead: dict) -> list:
    return [(r.get("user_name") or "路人", r.get("night_count", 0), f"{r.get('night_count', 0):,} 則")
            for r in (lead.get("night_owls") or [])[:5]]


def build_nightowl_card(lead: dict, liff_url: str) -> FlexBubble:
    body = _ranked(_owl_rows(lead)) or _empty_body("最近沒有人熬夜。")
    return _bubble("夜貓榜", body, _button("看完整排行", f"{liff_url}/leaderboard"),
                   subtitle="凌晨 00:00–04:00 發言")


def nightowl_alt(lead: dict) -> str:
    return _top_alt("夜貓榜", _owl_rows(lead), "最近沒有人熬夜")


def _pair_rows(inter: dict) -> list:
    return [(f"{p.get('user1_name') or '路人'} × {p.get('user2_name') or '路人'}",
             p.get("count", 0), f"{p.get('count', 0):,} 次")
            for p in (inter.get("best_pairs") or [])[:5]]


def build_pairs_card(inter: dict, liff_url: str) -> FlexBubble:
    body = _ranked(_pair_rows(inter)) or _empty_body("還沒有互相回覆的紀錄。")
    return _bubble("最佳拍檔", body, _button("看互動網絡", f"{liff_url}/interactions"),
                   subtitle="依雙向回覆次數")


def pairs_alt(inter: dict) -> str:
    return _top_alt("最佳拍檔", _pair_rows(inter), "還沒有互相回覆的紀錄")


def _quote_box(q: dict, label: str | None = None) -> FlexBox:
    """同學留言：淡藍信紙、原子筆藍字。"""
    contents: list = []
    if label:
        contents.append(_txt(label, size="xxs", color=MUTED))
    contents.append(_txt(f"「{(q.get('content') or '').strip()[:60]}」", size="md",
                         weight="bold", color=PEN, wrap=True))
    contents.append(_txt(f"— {q.get('user_name') or '匿名'}", size="xs", color=PEN, align="end"))
    return FlexBox(layout="vertical", spacing="xs", backgroundColor=PEN_BG, cornerRadius="4px",
                   paddingAll="12px", contents=contents)


def build_topics_card(topics: dict, liff_url: str) -> FlexBubble:
    keywords = (topics.get("top_keywords") or [])[:8]
    quotes = topics.get("highlight_quotes") or []
    body: list = []
    if keywords:
        body.append(_txt("熱門關鍵字", size="xs", color=MUTED))
        body.append(_txt("、".join(k.get("keyword", "") for k in keywords),
                         weight="bold", wrap=True, margin="xs"))
    if quotes:
        body.append(_quote_box(quotes[0], quotes[0].get("label") or "本期金句"))
    if not body:
        body = _empty_body("還沒有足夠的話題資料。")
    return _bubble("熱門話題與金句", body, _button("看話題分析", f"{liff_url}/topics"))


def topics_alt(topics: dict) -> str:
    kws = [k.get("keyword", "") for k in (topics.get("top_keywords") or [])[:3]]
    return f"熱門話題：{'、'.join(kws)}" if kws else "熱門話題：還沒有足夠的資料"


def _board_rows(board: dict) -> list:
    return [(r.get("name") or "路人", r.get("value") or 0, r.get("value_str") or "")
            for r in (board.get("rows") or [])[:5]]


def build_board_card(board: dict, liff_url: str) -> FlexBubble:
    """通用排行榜卡片：吃 travel.leaderboards 的 board spec，前 5 名 + highlight。

    按鈕直接開 LIFF 並選好這個排行榜（/leaderboard?board=<id>）。
    """
    rows = _board_rows(board)
    # 由小到大排的榜（例如閃電回覆王）比例條要反過來
    invert = len(rows) > 1 and rows[0][1] < rows[-1][1]
    body: list = []
    if board.get("sparse"):
        body.append(_txt("資料量少，僅供參考", size="xxs", color=FOIL_DARK))
    body.extend(_ranked(rows, invert=invert) or _empty_body("尚無資料。"))
    hi = board.get("highlight")
    if hi:
        box: list = [_txt(hi.get("label", ""), size="xxs", color=MUTED),
                     FlexBox(layout="horizontal", contents=[
                         _txt(hi.get("name", ""), weight="bold", flex=1),
                         _txt(hi.get("value_str", ""), weight="bold", flex=0, align="end"),
                     ])]
        if hi.get("note"):
            box.append(_txt(hi["note"], size="xs", color=MUTED, wrap=True))
        body.append(FlexBox(layout="vertical", spacing="xs", paddingAll="10px",
                            cornerRadius="4px", borderWidth="1px", borderColor=RULE, contents=box))
    board_id = board.get("id")
    uri = f"{liff_url}/leaderboard" + (f"?board={board_id}" if board_id else "")
    return _bubble(board.get("title", "排行榜"), body, _button("看完整排行", uri),
                   subtitle=board.get("subtitle") or None)


def board_alt(board: dict) -> str:
    return _top_alt(board.get("title", "排行榜"), _board_rows(board), "尚無資料")


# ── 方案 A / D：週報 / 月報 Carousel（多頁輪播） ─────────────────────

def _stat_line(label: str, name: str, value: str = "") -> FlexBox:
    row: list = [_txt(name, size="md", weight="bold", flex=1)]
    if value:   # LINE 不接受空字串的 text
        row.append(_txt(value, weight="bold", flex=0, align="end"))
    return FlexBox(layout="vertical", contents=[
        _txt(label, size="xxs", color=MUTED),
        FlexBox(layout="horizontal", contents=row),
    ])


def build_report_carousel(dash: dict, lead: dict, inter: dict, topics: dict,
                          liff_url: str, period_label: str) -> FlexMessage:
    """三頁輪播：風雲榜 / 互動拍檔 / 話題金句。"""
    top_users = dash.get("top_users") or []
    owls = lead.get("night_owls") or []
    rankings = lead.get("rankings") or []
    sticker_master = max(rankings, key=lambda r: r.get("sticker_count", 0), default=None)

    b1_body: list = []
    if top_users:
        b1_body.append(_hero(top_users[0].get("user_name") or "路人",
                             f"{top_users[0].get('total', 0):,} 則", "發話冠軍"))
    if owls:
        b1_body.append(_stat_line("夜貓王（凌晨 0–4 點）", owls[0].get("user_name") or "路人",
                                  f"{owls[0].get('night_count', 0)} 則"))
    if sticker_master and sticker_master.get("sticker_count", 0) > 0:
        b1_body.append(_stat_line("貼圖大師", sticker_master.get("user_name") or "路人",
                                  f"{sticker_master.get('sticker_count', 0)} 張"))
    if not b1_body:
        b1_body = _empty_body("這段期間群組很安靜。")
    bubble1 = _bubble(f"{period_label}風雲榜", b1_body, _button("看儀表板", f"{liff_url}/"))

    bubble2 = build_pairs_card(inter, liff_url)
    bubble2.header.contents[0].text = f"{period_label}最佳拍檔"
    bubble3 = build_topics_card(topics, liff_url)
    bubble3.header.contents[0].text = f"{period_label}話題與金句"

    champion = f"發話冠軍 {top_users[0].get('user_name')}" if top_users else "風雲榜"
    return FlexMessage(
        alt_text=f"[{period_label}群組戰報] {champion}・最佳拍檔・熱門話題",
        contents=FlexCarousel(contents=[bubble1, bubble2, bubble3]),
    )


# ── 方案 C：個人戰績卡 ──────────────────────────────────────────────

def _figure(value: str, label: str) -> FlexBox:
    return FlexBox(layout="vertical", flex=1, contents=[
        _txt(value, size="xl", weight="bold"),
        _txt(label, size="xxs", color=MUTED),
    ])


def build_personal_card(profile: dict, badges: list, best_friend: str | None,
                        user_name: str, liff_url: str, user_id: str = "",
                        picture_url: str | None = None) -> FlexMessage:
    summary = profile.get("summary") or {}
    slots = profile.get("time_slots") or {}
    tags = [p.get("tag") for p in (profile.get("personality") or []) if p.get("tag")]
    total = summary.get("total", 0)
    night_pct = round(slots.get("night", 0) / total * 100) if total else 0

    body: list = [
        FlexBox(layout="horizontal", spacing="md", contents=[
            _figure(f"{total:,}", "發話量（則）"),
            _figure(str(summary.get("active_days", 0)), "活躍天數"),
            _figure(f"{night_pct}%", "深夜發言"),
        ]),
    ]
    if best_friend:
        body.append(_stat_line("最佳拍檔", best_friend))
    if tags:
        body.append(FlexSeparator(color=RULE))
        body.append(_txt("聊天人格", size="xxs", color=MUTED))
        body.append(_txt("・".join(tags[:4]), weight="bold", color=CLOTH, wrap=True, margin="xs"))
    if badges:
        emojis = "".join(b.get("badge_emoji", "") for b in badges[:8])
        body.append(_txt(f"徽章 {len(badges)} 枚　{emojis}", color=FOIL_DARK, wrap=True))

    header_contents: list = []
    if picture_url:
        header_contents.append(FlexBox(
            layout="vertical", width="56px", height="56px", cornerRadius="28px", flex=0,
            borderWidth="2px", borderColor=FOIL,
            contents=[FlexImage(url=picture_url, size="full", aspect_ratio="1:1", aspect_mode="cover")],
        ))
    header_contents.append(FlexBox(layout="vertical", flex=1, justifyContent="center", contents=[
        _txt(user_name, size="xl", weight="bold", color="#FFFFFF", wrap=True),
        _txt("個人戰績", size="xs", color=SAGE, margin="xs"),
        _foil_rule("sm"),
    ]))

    bubble = FlexBubble(
        header=FlexBox(layout="horizontal", backgroundColor=CLOTH, paddingAll="16px",
                       spacing="md", alignItems="center", contents=header_contents),
        body=FlexBox(layout="vertical", spacing="md", paddingAll="16px", contents=body),
        footer=FlexBox(layout="vertical", paddingAll="12px", paddingTop="0px", contents=[
            _button("看個人頁", f"{liff_url}/profile" + (f"/{user_id}" if user_id else "")),
        ]),
    )
    return FlexMessage(alt_text=f"[個人戰績] {user_name}：{total:,} 則、活躍 {summary.get('active_days', 0)} 天",
                       contents=bubble)


# ── @bot 入口卡：四格選單 ───────────────────────────────────────────

ENTRY_ITEMS = [("儀表板", "群組數據", "/"), ("排行榜", "榮譽排行", "/leaderboard"),
               ("回憶", "時光軸", "/timeline"), ("個人", "我的檔案", "/profile")]


def _entry_cell(label: str, sub: str, uri: str) -> FlexBox:
    return FlexBox(layout="vertical", flex=1, paddingAll="12px", cornerRadius="4px",
                   borderWidth="1px", borderColor=RULE, action=URIAction(label=label, uri=uri),
                   contents=[_txt(label, size="md", weight="bold"),
                             _txt(sub, size="xxs", color=MUTED)])


def build_entry_card(liff_url: str, is_admin: bool = False) -> FlexMessage:
    cells = [_entry_cell(label, sub, f"{liff_url}{path}") for label, sub, path in ENTRY_ITEMS]
    body = [
        FlexBox(layout="horizontal", spacing="sm", contents=cells[:2]),
        FlexBox(layout="horizontal", spacing="sm", contents=cells[2:]),
    ]
    footer = None
    if is_admin:
        footer = FlexBox(layout="vertical", paddingAll="12px", paddingTop="0px", contents=[
            FlexButton(action=URIAction(label="管理後台", uri=f"{liff_url}/admin"),
                       style="secondary", height="sm"),
        ])
    bubble = FlexBubble(
        header=_header("群組紀念冊", "點一格直接打開"),
        body=FlexBox(layout="vertical", spacing="sm", paddingAll="16px", contents=body),
        footer=footer,
    )
    return FlexMessage(alt_text="群組紀念冊：儀表板・排行榜・回憶・個人", contents=bubble)


# ── 旅行：紀念章、倒數卡、頒獎卡、N 年前的今天 ─────────────────────────

def _seal(emoji: str, rarity: str | None, size: str = "64px") -> FlexBox:
    """紀念章：稀有度線色外框 + emoji。"""
    line = RARITY_LINE.get(rarity or "common", RARITY_LINE["common"])
    px = int(size.rstrip("px"))
    return FlexBox(layout="vertical", width=size, height=size, cornerRadius=f"{px // 2}px",
                   borderWidth="3px", borderColor=line, backgroundColor="#FFFFFF", flex=0,
                   justifyContent="center", alignItems="center",
                   contents=[_txt(emoji or "🎒", size="xxl" if px >= 60 else "xl", align="center")])


def _fmt_date(ts: int | None) -> str:
    if not ts:
        return ""
    from datetime import datetime, timedelta, timezone
    d = datetime.fromtimestamp(ts, timezone(timedelta(hours=8)))
    return f"{d.year}/{d.month}/{d.day}"


def build_countdown_card(trip: dict, days: int, liff_url: str) -> FlexMessage:
    """出發倒數：紀念章 + 「還有 N 天」。days=0 表示今天出發。"""
    title = trip.get("title") or "旅行"
    meta = "・".join(x for x in [trip.get("location") or "", _fmt_date(trip.get("start_date"))] if x)
    big = FlexBox(layout="vertical", flex=0, alignItems="flex-end", contents=(
        [_txt("今天", size="xxs", color=FOIL_DARK, align="end"),
         _txt("出發", size="xxl", weight="bold", color=FOIL_DARK, align="end")]
        if days <= 0 else
        [_txt("還有", size="xxs", color=FOIL_DARK, align="end"),
         _txt(str(days), size="3xl", weight="bold", color=FOIL_DARK, align="end"),
         _txt("天", size="xxs", color=FOIL_DARK, align="end")]
    ))
    body = [FlexBox(layout="horizontal", spacing="md", alignItems="center", contents=[
        _seal(trip.get("custom_emoji") or trip.get("badge_emoji") or "", trip.get("rarity")),
        FlexBox(layout="vertical", flex=1, contents=[
            _txt(title, size="lg", weight="bold", wrap=True),
            *([_txt(meta, size="xs", color=MUTED, wrap=True)] if meta else []),
        ]),
        big,
    ])]
    bubble = _bubble("下一趟旅行", body, _button("看旅行內容", f"{liff_url}/trips/{trip.get('id', '')}"))
    alt = f"{title}：今天出發" if days <= 0 else f"{title}：還有 {days} 天出發"
    return FlexMessage(alt_text=alt, contents=bubble)


def build_badge_award_card(trip: dict, awarded: list[dict], liff_url: str) -> FlexMessage:
    """頒獎卡：同一趟旅行的徽章都相同，所以一張卡列出所有得獎者。"""
    first = awarded[0] if awarded else {}
    rarity = first.get("badge_rarity") or trip.get("rarity") or "common"
    rarity_zh = RARITY_ZH.get(rarity, "普通")
    names = [a.get("user_name") or "旅伴" for a in awarded]
    body = [
        FlexBox(layout="horizontal", spacing="md", alignItems="center", contents=[
            _seal(first.get("badge_emoji") or "", rarity, "72px"),
            FlexBox(layout="vertical", flex=1, contents=[
                _txt(trip.get("title") or "旅行", size="lg", weight="bold", wrap=True),
                FlexBox(layout="horizontal", margin="sm", contents=[
                    FlexBox(layout="vertical", flex=0, paddingStart="6px", paddingEnd="6px",
                            cornerRadius="3px", backgroundColor=RARITY_LINE.get(rarity, MUTED),
                            contents=[_txt(rarity_zh, size="xxs", weight="bold", color="#FFFFFF")]),
                ]),
            ]),
        ]),
        FlexSeparator(color=RULE),
        _txt(f"獲頒 {len(names)} 人", size="xxs", color=MUTED),
        _txt("、".join(names), weight="bold", wrap=True),
    ]
    bubble = _bubble("徽章頒發", body, _button("看我的徽章", f"{liff_url}/badges"))
    return FlexMessage(alt_text=f"徽章頒發：{trip.get('title') or '旅行'}（{rarity_zh}）{len(names)} 人獲得",
                       contents=bubble)


def build_on_this_day_card(trips: list[dict], quote: dict | None, liff_url: str) -> FlexMessage | None:
    """N 年前的今天：當天出發的旅行 + 一年前今天的金句。沒有內容回 None。

    trips 每筆需帶 years_ago。
    """
    body: list = []
    for t in trips[:3]:
        body.append(FlexBox(layout="horizontal", spacing="md", alignItems="center", contents=[
            _seal(t.get("custom_emoji") or t.get("badge_emoji") or "", t.get("rarity"), "48px"),
            FlexBox(layout="vertical", flex=1, contents=[
                _txt(f"{t.get('years_ago', 1)} 年前", size="xxs", color=FOIL_DARK),
                _txt(t.get("title") or "旅行", size="md", weight="bold", wrap=True),
                *([_txt(t["location"], size="xs", color=MUTED)] if t.get("location") else []),
            ]),
        ]))
    if quote:
        body.append(_quote_box(quote, "一年前的今天，有人說"))
    if not body:
        return None
    uri = f"{liff_url}/trips/{trips[0]['id']}" if trips else f"{liff_url}/timeline"
    bubble = _bubble("那年今日", body, _button("打開回憶", uri))
    if trips:
        alt = f"那年今日：{trips[0].get('years_ago', 1)} 年前的今天，{trips[0].get('title') or '旅行'}"
    else:
        alt = f"那年今日：「{(quote.get('content') or '')[:30]}」— {quote.get('user_name') or ''}"
    return FlexMessage(alt_text=alt, contents=bubble)


# ── Quick Reply（互動選單，LINE 上限 13 顆） ─────────────────────────

QUICK_BOARDS = ["正能量大使", "晨型人", "閃電回覆王", "貼圖狂魔", "長文王", "冷場王",
                "話題發起王", "最受歡迎"]


def stats_quick_reply(liff_url: str) -> QuickReply:
    items = [
        QuickReplyItem(action=MessageAction(label="發言排行", text="/stats 排行")),
        QuickReplyItem(action=MessageAction(label="夜貓榜", text="/stats 夜貓")),
        QuickReplyItem(action=MessageAction(label="最佳拍檔", text="/stats cp")),
        QuickReplyItem(action=MessageAction(label="熱門話題", text="/stats 話題")),
    ]
    items += [QuickReplyItem(action=MessageAction(label=t, text=f"/stats 排行 {t}"))
              for t in QUICK_BOARDS]
    items.append(QuickReplyItem(action=URIAction(label="打開紀念冊", uri=f"{liff_url}/")))
    return QuickReply(items=items[:13])


def wrap_single(bubble: FlexBubble, alt_text: str, quick_reply: QuickReply | None = None) -> FlexMessage:
    return FlexMessage(alt_text=alt_text, contents=bubble, quick_reply=quick_reply)
