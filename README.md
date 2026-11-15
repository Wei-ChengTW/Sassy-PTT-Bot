# 八卦分身 (Sassy PTT Bot)

一個模仿 PTT 八卦版 (Gossiping) 風格的 **LINE** 群組機器人。介面有 LINE 對話 + LIFF「畢業紀念冊」前端（群組數據、旅行回憶、個人檔案）+ 旅遊擴充模組 + 群組分析。不提供幫助，只提供毒舌。

## 功能一覽

| 分類 | 功能 | 怎麼用 |
|------|------|--------|
| 毒舌對話 | PTT 鄉民口吻隨緣插嘴、被點名精準開酸 | 群組聊天、`@機器人`、私訊 |
| 群組問答 | 從全部聊天紀錄 + 旅行紀錄找答案，先答再酸 | `@機器人 ？問題`（只打「？」會被嗆） |
| 聊天摘要 | 摘要你上次講話之後錯過的對話 | `@機器人 現在是怎樣` |
| G8 偵查器 | 偵測 ji／ju + ba 同音詞（雞巴、居吧…）與 G8／JB | 自動，引用該則訊息回覆 |
| 統計戰報 | 近 30 天摘要輪播 + 快速選單 | `/stats`、`統計`、`戰報` |
| 單項排行 | 發言排行、夜貓榜、最佳拍檔、熱門話題 | `/stats 排行`、`/stats 夜貓`、`/stats cp`、`/stats 話題` |
| 趣味排行榜 | 16 種資料驅動排行（正能量大使、閃電回覆王、冷場王…） | `/stats 排行 <名稱>` |
| 個人戰績 | 個人數據卡（最佳拍檔、徽章） | `/me` |
| 紀念冊入口 | 回一張入口卡，直接打開 LIFF | 只 `@機器人` 不打字 |
| 自動稱號 | 每週依每人最近發言取暫時稱號，機器人稱呼人時會用 | 自動；LIFF「稱號」頁查看 |
| 精選金句 | 規則挑候選 → LLM 評審選 10 則並配標籤，可分享成小卡 | LIFF「話題」頁 |
| 旅行與徽章 | 建立旅行、自動算稀有度（5 級）、結束後頒徽章 | LIFF 管理員後台 |
| 群組通知 | 畢業倒數、出發當天倒數（推播）；頒獎卡、那年今日（附在機器人回覆後面） | 排程自動（見步驟 E） |
| 出發倒數小卡 | 依按下當下的剩餘天數產生（今天／明天／還有 N 天，久的附週、月換算），以按的人的名義送到群組 | LIFF 旅行詳情頁「發送倒數小卡」 |
| 管理員戰報 | 週報／月報：所在群組直接回覆，其他群組等下次回話時附上 | `/stats 推播週`、`/stats 推播月` |

## 核心理念

- 透過 RAG（Retrieval-Augmented Generation）將真實 PTT 推文與群組歷史對話記憶注入 LLM Prompt
- 半語意 few-shot + 對話脈絡感知 + 群組人物別名與事件百科，產出像熟人互嗆、神回覆的短句
- LINE 群組行為模擬真實鄉民「隨緣」特性（不一定每則都回，但被點名精準開酸）
- 附帶旅遊 / 徽章 / 群組分析作為「附加價值」，讓群組回頭看得到累積

## 技術架構

| 元件 | 技術 |
|------|------|
| LLM（Primary） | 任一 OpenAI 相容端點（`CLI_PROXY_BASE_URL`），依用途分模型：對話／問答／摘要／金句用 `gpt-6.1-sol`，分析／情緒／稱號／問答關鍵字用免費的 `gemma-4-26b-a4b-it` |
| LLM（Fallback） | 不同供應商的 `deepseek-v4.1-flash`（`FALLBACK_*`），Primary 掛掉時自動切換；分析與稱號則退回 `CGU_LLM_*` |
| LLM 共通 | 單次 timeout（`LLM_TIMEOUT`，目前 25s）+ 429 retry 3 次 |
| 向量資料庫 | ChromaDB（含 PTT 語料與群組對話記憶 `group_memory` 雙 collection） |
| 嵌入模型 | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`（多語，中文檢索較準） |
| LINE 框架 | `line-bot-sdk` v3 + Flask webhook |
| 排程 | APScheduler（每日倒數 / 聚合 / 徽章 + 每週爬蟲 + 每月 LLM 分析） |
| 後端 | Python 3.11+ |
| 前端 | Vite + Vue 3 + TypeScript + Tailwind + Pinia + Vue Router |
| 前端圖表 | Chart.js + vue-chartjs（柱狀 / 圓餅 / 折線）+ D3 v7（力導向網絡圖）+ Leaflet（旅行地圖） |
| LINE 小卡 | Flex Message（`line_bot/stats_cards.py`、LIFF 端 `utils/flex*.ts`），與 LIFF 同一套紀念冊色票 |
| 分析儲存 | SQLite（WAL 模式）：訊息、trip、participant、badge、daily / lifetime stats、members |

### 運作流程（對話引擎）

**步驟 A：觸發判定**

Bot 不會對每則訊息回應，模擬真實鄉民的「隨緣」：

| 場景 | 觸發率 |
|------|--------|
| LINE 私訊（1:1） | 100% |
| 群組內 `@bot` 直接提及 | 100%（精準對焦問題，不被前文雜訊干擾） |
| `@bot ？問題` / `@bot 現在是怎樣` | 100%，改走群組問答 / 聊天摘要 |
| 群組內 bare `@bot`（無其他文字） | 回紀念冊入口卡 |
| 管理員私訊 | 回含管理員後台的入口卡 |
| 統計指令（`/stats`、`/me`…） | 100%，回 Flex 小卡 |
| G8 同音詞 | 100%，優先於 LLM |
| 群組內含關鍵字（為什麼、怎麼、推薦、八卦⋯⋯等 30+ 詞） | 15% 機率 |
| 群組其他訊息 | 3% 機率隨機發作（短詞附和自動回溯上文主旨插嘴） |

**步驟 B：語料與記憶雙軌檢索 (RAG & Group Memory)**

- **PTT 語料檢索**：用戶輸入轉向量，在 ChromaDB 約 8.8 萬條 PTT 語料中語義搜索
  - **Top 1** 標為「真實推文範例」
  - **Top 2-3** 標為「其他相關語料」，作為風格參考
- **群組記憶與實體檢索**：
  - **人物與外號對照**：載入 `data/aliases.json`，精確識別發言者與被提及者本名/綽號與代表作
  - **重大歷史事件百科**：載入 `data/events.json` 與 SQLite 對話紀錄，檢索經典黑歷史與名言佳句
  - **向量記憶檢索**：在 `group_memory` 向量庫中檢索相關對話視窗

**步驟 C：毒舌生成**

- **半語意 few-shot**：對 15 個 example Q&A 算 2-gram overlap，取 top 2 語意相近 + 3 個隨機，混搭後塞 prompt
- **短句回溯對齊**：若群友發「會」「真的」「笑死」等短附和詞觸發，自動往前鎖定最近有實質內容的話題
- **對話 window**：群聊保留最近對話歷史，訊息前綴 sender display_name（例如 `Alice 說：「三小」`）
- **Anti-repeat**：當下 prompt 附帶「前幾輪 bot 已用過的回應」，強迫模型切換不同切入點與句型
- **System prompt**：PTT 鄉民 + 群內毒舌老友雙重人設，指名道姓精準開酸，杜絕捏造假人名與罐頭話
- **LINE 引用回覆**：回應時自動帶 `quote_token` 引用觸發的那則訊息

**步驟 D：LLM 雙 Provider**

- 先試 **PRIMARY**（`CLI_PROXY_BASE_URL` + 該用途的模型，見下表），timeout 為 `LLM_TIMEOUT`
- 失敗（timeout / 連線錯誤 / 全部 429 重試耗盡）→ 自動切到 **FALLBACK**（`FALLBACK_BASE_URL` / `FALLBACK_MODEL`，建議用不同供應商，避免同時掛掉；沒設時沿用 `CGU_LLM_*`）
- 兩邊都掛 → 回「懶得理你，自己想。」
- 觸發 semaphore：`@mention` 走 2-slot semaphore（避免 reply_token 過期），自發觸發走 `non-blocking lock`（搶不到就跳過）

各用途的模型都可用環境變數個別指定（目前設定）：

| 環境變數 | 用途 | 目前模型 |
|----------|------|----------|
| `PRIMARY_MODEL` | 毒舌對話（插嘴、@提及、私訊）、畢業倒數文案 | `gpt-6.1-sol` |
| `QA_MODEL` | 群組問答的回答 | `gpt-6.1-sol` |
| `SUMMARY_MODEL` | 聊天摘要 | `gpt-6.1-sol` |
| `QUOTES_MODEL` | 精選金句 LLM 評審 | `gpt-6.1-sol` |
| `QA_INTENT_MODEL` | 群組問答抽關鍵字（要快） | `gemma-4-26b-a4b-it` |
| `ANALYZER_MODEL` | 每月主題／旅行偵測 | `gemma-4-26b-a4b-it` |
| `SENTIMENT_MODEL` | 視窗式情緒分析 | `gemma-4-26b-a4b-it` |
| `NICKNAME_MODEL` | 每週自動稱號 | `gemma-4-26b-a4b-it` |
| `FALLBACK_MODEL` | 對話／問答／摘要備援 | `deepseek-v4.1-flash` |
| `CGU_LLM_MODEL` | 分析與稱號的備援 | `gpt-6-luna` |

高頻、要好笑的用途用付費強模型，背景批次工作用免費模型；整體一週約 75 次 LLM 呼叫。

**步驟 E：自動排程**

| 排程 | 動作 | 方式 |
|------|------|--------|
| 每日 09:00 | 推播畢業倒數 + 當日 PTT 熱門時事到 `LINE_GROUP_ID`（快取至 `data/news_cache.json`） | ✔ |
| 每日 09:05 | watchdog 補推（如果當天沒推到） | ✔ |
| 每日 00:00 | 旅行出發**當天**的倒數卡，推到該旅行的群組 | ✔ |
| 每日 00:05 | 那年今日：往年同一天的旅行 + 一年前今天的金句，有內容才排入（當天有效） | 🚌 |
| 每小時 :05 | 對已結束旅行發徽章，有新徽章才排一張頒獎卡（7 天有效） | 🚌 |
| 每日 03:30 | 主群新訊息增量寫入 `group_memory` 向量庫 | |
| 每日 04:00 | 聚合前一日的 `daily_user_stats` / `user_lifetime_stats` / group-level `daily_stats` | |
| 每日 04:30 | 預先重算精選金句（全部／今年／本月） | |
| 每月 1 號 03:00 | 對已收集訊息跑 LLM 主題 / 旅行偵測，回寫 `messages` 表 | |
| 每月 1 號 03:30 | 視窗式情緒分析（只處理新視窗） | |
| 每週日 03:00 | 自動爬取最新 PTT 八卦板文章並重建 ChromaDB 索引 | |
| 每週日 04:00 | 自動稱號：替每位成員取暫時稱號寫入 `aliases.json` | |

✔＝推播；🚌＝搭便車：排進 `pending_riders` 佇列，等機器人下次在該群組回覆時接在回覆後面（見 `line_bot/riders.py`）。週報／月報自動排程目前停用，改由管理員 `/stats 推播週`／`/stats 推播月` 手動觸發，同樣走搭便車。

> **推播額度**：LINE 官方帳號免費方案每月 200 則、不能加購。回覆不計額度且一次最多帶 5 則訊息；推播到群組**按群組人數**計（14 人的群推 1 次＝14 則）。所以只有畢業倒數（5 人群，每月約 155 則）與出發當天倒數（每趟 14 則）走推播，其餘通知一律搭便車；聊天摘要逾時回覆失敗時也改排入佇列，不推播。可用 `GET /v2/bot/message/quota/consumption` 查本月用量。

## 模組總覽

### 1. LINE 對話引擎 — `line_bot/`

LINE webhook 主程式，包含 webhook handler、LLM 雙 provider、ChromaDB 查詢、對話歷史、sender 標記。Flask 同時掛載 LIFF API blueprint（後述）。

| 檔案 | 內容 |
|------|------|
| `bot.py` | webhook、觸發判定、毒舌生成、G8 偵查器、`/stats` 指令、APScheduler |
| `group_qa.py` | 群組問答：LLM 抽關鍵字（含日期同義詞）→ SQL 掃全部歷史訊息取視窗 → LLM 依聊天 + 旅行紀錄回答 |
| `chat_summary.py` | 聊天摘要：從發問者上次講話之後摘要到現在；沒講過話就摘要「最近一輪」（停頓 30 分鐘切輪），少於 10 則直接嗆 |
| `auto_nickname.py` | 每週自動稱號，寫進 `aliases.json` 的 `auto_aliases`（每人最多 3 個），不在群組公布 |
| `stats_cards.py` | 所有 Flex 小卡：戰報輪播、各排行榜、個人戰績、入口卡、旅行倒數、頒獎、那年今日 |
| `notify.py` | 群組通知：出發當天倒數推播；頒獎卡、那年今日排進搭便車佇列（日期一律以台灣時間判斷） |
| `riders.py` | 搭便車佇列：`reply_message` hook 把群組待送小卡接在回覆後面（最多湊滿 5 則），token 過期放回、卡片不合規丟棄 |
| `liff_api.py` | `/liff/*` API（後述） |

```bash
python -m line_bot.auto_nickname --dry-run   # 只印稱號不寫檔
```

**啟動**：
```bash
./run_bot.sh                    # 等同：./venv/bin/python line_bot/bot.py
```

### 2. LIFF 畢業紀念冊 — `liff/`

Vue 3 + Vite 的 LINE 前端框架應用，以手機為主要裝置。視覺是「畢業紀念冊」：綠色布面封面、燙金、原子筆藍的互動元素，旅行回憶依稀有度做不同的印刷效果（平印／壓紋／燙綠箔／燙金／鐳射箔，鐳射箔可隨手指傾斜）。設計規範見 [`DESIGN.md`](DESIGN.md)，產品定位見 [`PRODUCT.md`](PRODUCT.md)。所有頁面透過 Vite proxy 把 `/liff/*` 轉發到 bot 的 Flask port 5000。

頁面可切換期間（全部時間／單一年份／單一月份），管理員可切換群組；旅行與金句可用 `shareTargetPicker` 分享成 LINE 小卡。

**啟動**：
```bash
cd liff
npm install                     # 首次
npm run dev                     # 開發：http://localhost:5174
npm run build                   # 生產：vue-tsc + vite build → dist/
```

**路由總覽**：
| 路由 | 頁面 | 內容 |
|------|------|------|
| `/` | 群組總覽 | 總訊息、成員、預計進行的行程、活躍天數、Top 5 話癆（佔全群比例）、每週／每月趨勢、活躍熱力圖、訊息類型 |
| `/leaderboard` | 排行榜 | 16 種趣味排行（第 1 名封面、2–3 名銀銅牌、其餘比例條），支援 `?board=` 直達 |
| `/pulse` | 群組脈動 | 群組回應速度、閃電神回手排行、話題爆發時段（平均的幾倍）、潛水員偵測 |
| `/interactions` | 互動關係 | 最佳拍檔 + D3 力導向互動網絡圖 |
| `/topics` | 話題 | 熱門話題、文字雲、情緒曲線、精選金句（可分享） |
| `/compare` | 兩人比較 | 任選兩位成員並排比較 |
| `/nicknames` | 稱號 | 每人的自動稱號與由來，附 LINE 頭像 |
| `/profile`、`/profile/:userId` | 個人檔案 | 里程碑獎狀、成長／情緒曲線、24h 分佈、社交圈、旅行足跡、徽章 |
| `/trips`、`/trips/:id` | 旅行 | 預計進行的行程（倒數）＋ 已完成的相簿（距今多久），詳情頁含參與者、統計、分享回顧小卡，還沒出發的可發送倒數小卡 |
| `/timeline` | 時間軸 | 依年份分章的旅行回憶 |
| `/map` | 地圖 | Leaflet 旅行足跡 |
| `/badges` | 徽章牆 | 個人徽章 |
| `/admin/*` | 管理員後台 | 建立／編輯／結束旅行、參與者、發徽章（會推頒獎卡）、主題分析（需 `ADMIN_USER_IDS`） |

### 3. 旅遊擴充 — `travel/`

後端分析 / 旅遊邏輯模組，啟動時若 `TRAVEL_STORAGE_ENABLED=true` 會自動 `init_db()` + 跑 migrations。每次 LINE 訊息都會 `_store_line_event` 寫入 SQLite（`messages` 表），再由排程聚合到 `daily_user_stats` / `user_lifetime_stats` / `daily_stats`。

包含：
- `trip_crud.py` — Trip CRUD（建立 / 結束 / 參與者）
- `trip_types.py` — 旅行分類（校園回憶、經典名場面、聚會派對、運動競技、雪地滑雪…）
- `badges.py` — 依地點 + 旅行天數 + 參與人數計算稀有度（普通 / 稀有 / 極稀有 / 史詩 / 傳說），自動發徽章
- `aggregator.py` — 每日 / 終身統計聚合
- `llm_analyzer.py` — 每月 LLM 主題 / 旅行偵測
- `sentiment_windows.py` — 視窗式情緒分析（10 分鐘內最多 4 則帶上下文判情緒）
- `quotes.py` — 精選金句（規則候選 + LLM 評審，每日快取）
- `leaderboards.py` — 16 種趣味排行榜
- `stats.py` / `stats_extended.py` — Dashboard / Leaderboard / Interactions / Topics / Profile / Pulse / Compare 查詢
- `period.py` / `cache.py` — 期間篩選與 stale-while-revalidate 快取

**API endpoints**（`/liff/*`，全部需 LIFF ID token）：
- 一般：`/me`、`/dashboard`、`/periods`、`/trips`、`/trips/:id`、`/badges/:user_id`
- 分析：`/leaderboard`、`/leaderboards`、`/interactions`、`/topics`、`/profile/:user_id`、`/pulse`、`/compare`、`/nicknames`
- 管理員：`/admin/trips`、`/admin/trips/:id/update`、`/admin/trips/:id/title`、`/admin/trips/:id/participants`、`/admin/trips/:id/end`、`/admin/trips/:id/award-badges`、`/admin/analyze-topics`、`/admin/groups`、`/admin/members`

**啟動**：跟著 `line_bot/bot.py` 一起啟動，不需獨立指令。

### 4. 分析 CLI — `scripts/show_stats.py`

不想開 LIFF 時，從 terminal 直接看 SQLite 統計。

```bash
python scripts/show_stats.py overview          # 總訊息 / 已分析 / 旅行相關 / 類型分佈
python scripts/show_stats.py user <user_id>    # 單一使用者統計
python scripts/show_stats.py top-users          # Top 10 話癆
python scripts/show_stats.py topics             # 主題分佈
python scripts/show_stats.py travel             # 旅行相關訊息排行
python scripts/show_stats.py dashboard          # 群組 dashboard 摘要
```

## 專案結構

```
Sassy-PTT-Bot/
├── line_bot/
│   ├── bot.py                  # LINE webhook 主程式 + APScheduler
│   ├── group_qa.py             # 群組問答
│   ├── chat_summary.py         # 聊天摘要（錯過的對話）
│   ├── auto_nickname.py        # 每週自動稱號
│   ├── stats_cards.py          # Flex 小卡
│   ├── notify.py               # 旅行倒數／頒獎／那年今日
│   ├── riders.py               # 搭便車佇列（通知附在回覆後面）
│   └── liff_api.py             # Flask Blueprint：/liff/* API endpoints
├── liff/                       # LIFF 前端（Vue 3 + Vite + Tailwind）
│   ├── src/
│   │   ├── views/              # 各頁面（見上方路由表）
│   │   ├── components/         # PageSign / RankList / FoilCard / RaritySeal / Heatmap…
│   │   ├── constants/          # rarity / tripTypes / tripStatus / locations / chartColors
│   │   ├── utils/              # flexTripCard / flexQuoteCard / flexCountdownCard（以本人名義發送的小卡）、liffShare、rank、ago
│   │   ├── api/client.ts       # API client wrapper
│   │   ├── stores/, router.ts, App.vue, main.ts, style.css
│   ├── package.json            # v5 d3 / chart.js 4 / vue-chartjs 5
│   └── vite.config.ts          # dev port 5174, proxy /liff → :5000
├── travel/                     # 旅遊擴充 + 群組分析
│   ├── db.py                   # SQLite schema + get_conn() (WAL)
│   ├── trip_crud.py            # Trip CRUD
│   ├── trip_types.py           # 旅行分類
│   ├── badges.py               # 稀有度計算 + 自動發徽章
│   ├── aggregator.py           # 每日 / 終身 / group-level 聚合
│   ├── llm_analyzer.py         # 每月 LLM 主題分析
│   ├── sentiment_windows.py    # 視窗式情緒分析
│   ├── quotes.py               # 精選金句
│   ├── leaderboards.py         # 16 種趣味排行榜
│   ├── line_event_parser.py    # LINE event → SQLite row
│   ├── stats.py                # Dashboard / Trip / User badge 查詢
│   ├── stats_extended.py       # 分析查詢
│   ├── period.py, cache.py     # 期間篩選、快取
│   └── migrations.py
├── PRODUCT.md                  # 產品定位（使用者、語氣）
├── DESIGN.md                   # LIFF 紀念冊設計規範
├── corpus_config.py            # 語料與群組記憶設定、別名與重大事件載入
├── indexer.py                  # PTT 語料 → ChromaDB 索引
├── index_group_memory.py       # 群組歷史對話視窗 → ChromaDB 索引 (group_memory)
├── scripts/
│   ├── import_line_export.py   # LINE 匯出文字紀錄匯入資料庫
│   ├── import_memories.py      # 匯入群組回憶（冪等去重）
│   ├── seed_members.py         # 建立成員資料
│   ├── backfill_analysis.py    # LLM 分析批次回填
│   ├── backfill_sentiment.py   # 情緒分析批次回填
│   └── show_stats.py           # CLI 統計工具
├── data/                       # 自動產生（git ignored）
│   ├── chat.db                 # SQLite
│   ├── aliases.json            # 群組成員別名/外號對照表（可選）
│   ├── events.json             # 群組歷史重大事件百科（可選）
│   ├── news_cache.json         # 每日新聞快取
│   └── graduation_state.json   # 倒數推送狀態
├── PTT-Crawler-master/         # PTT 爬蟲（submodule）
│   ├── data_Gossiping_2025/    # 原始 JSON 語料（不入 repo）
│   └── chroma_db/              # 向量資料庫（不入 repo）
├── docs/superpowers/
│   ├── specs/                  # 設計規格
│   └── plans/                  # 實作計畫
├── tests/                      # pytest
├── requirements.txt
├── run_bot.sh                  # 啟動 bot 的 launcher
├── ngrok.yml                   # 兩個 tunnel：bot :5000 + liff :5174
├── .env                        # 環境變數（不入 repo）
└── bot.log                     # 滾動日誌（5MB × 7 份）
```

## 從零開始準備語料

本專案的向量資料庫（`chroma_db/`）和原始語料（GB 等級）不包含於 repo，需自行建立。

### 步驟 1：爬取 PTT 八卦板文章

使用 `PTT-Crawler-master/` 內的爬蟲抓取文章，輸出為 JSON 格式：
```json
[
  {
    "Content": "文章內文",
    "Responses": [{ "Content": "推文內容" }]
  }
]
```

將所有 JSON 檔放入 `PTT-Crawler-master/data_Gossiping_2025/`。

### 步驟 2：建立向量索引
```bash
source venv/bin/activate
python indexer.py
```

執行完成會在 `PTT-Crawler-master/chroma_db/` 建立向量資料庫，預設最多索引 100,000 筆（可在 `indexer.py` 的 `MAX_DOCUMENTS` 調整）。啟動後每週日 03:00 會自動增量爬取並重建索引。

> 語料越多、涵蓋話題越廣，RAG 檢索效果越好。建議至少準備 **5 萬筆以上**的推文。

---

## 啟動指南

### 環境需求

- Python 3.11+
- Node.js 18+（LIFF 前端開發）
- 一個 OpenAI 相容的 LLM 端點（學校 API、CLIProxyAPI、其他中轉站皆可），建議再準備一個不同供應商的當備援

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bash
cd liff && npm install && cd ..
```

### 環境變數

在專案根目錄建立 `.env`：

```env
# LINE（必填）
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_WEBHOOK_PORT=5000

# 主群：所有功能（訊息記憶 / 旅行紀錄 / 統計 / LIFF）都在這個群
MAIN_LINE_GROUP_ID=your_main_line_group_id
# 次要群組：只接收 graduation 倒數 + 一般統計戰報，本身無訊息記憶
LINE_GROUP_ID=your_secondary_line_group_id

# LLM — Primary（任一 OpenAI 相容端點，所有用途都走這裡）
CLI_PROXY_BASE_URL=https://your-llm-endpoint/v1
CLI_PROXY_API_KEY=your_api_key
PRIMARY_MODEL=gpt-6.1-sol
QA_MODEL=gpt-6.1-sol
SUMMARY_MODEL=gpt-6.1-sol
QUOTES_MODEL=gpt-6.1-sol
QA_INTENT_MODEL=gemma-4-26b-a4b-it
ANALYZER_MODEL=gemma-4-26b-a4b-it
SENTIMENT_MODEL=gemma-4-26b-a4b-it
NICKNAME_MODEL=gemma-4-26b-a4b-it

# LLM — Fallback（對話／問答／摘要；建議不同供應商，沒設時沿用 CGU_LLM_*）
FALLBACK_BASE_URL=https://your-fallback-endpoint/v1
FALLBACK_API_KEY=your_fallback_key
FALLBACK_MODEL=deepseek-v4.1-flash

# LLM — CGU 學術 API（分析與稱號的備援）
CGU_LLM_BASE_URL=https://air.cgu.edu.tw/cgullmapi/v1
CGU_LLM_API_KEY=your_cgu_api_key
CGU_LLM_MODEL=gpt-6-luna

# 單次 LLM 請求 timeout（秒，預設 15）
LLM_TIMEOUT=25.0

# LIFF
LIFF_ID=your-liff-id
# 設定後 /liff/* 每個請求都必須帶有效的 LINE ID token；本機開發可不設
LIFF_CHANNEL_ID=your_liff_channel_id

# 旅遊擴充
TRAVEL_STORAGE_ENABLED=true
DB_PATH=data/chat.db

# 管理員（LINE user_id，逗號分隔；可從 LINE Bot 私訊收訊息時的 source.user_id 取得）
ADMIN_USER_IDS=user_id_1,user_id_2

# 畢業倒數（選填）
GRADUATION_DATE=2027-05-22

# scripts/seed_members.py 用：群組成員 display_name，逗號分隔（避免把真名寫進 repo）
LINE_GROUP_MEMBERS=Alice,Bob,Carol
```

### 啟動

#### Bot

正式環境以 systemd user 服務常駐（`~/.config/systemd/user/sassy-bot.service`，`ExecStart` 指向 `run_bot.sh`，掛掉 3 秒後自動重啟）：
```bash
systemctl --user restart sassy-bot.service   # 改完程式或 .env 後重啟
systemctl --user status sassy-bot.service
tail -f bot.log
```

本機手動跑：
```bash
./run_bot.sh
```

啟動成功會看到：
```
[LLM] Primary: gpt-6.1-sol @ https://<your-llm-endpoint>/v1
[LLM] Fallback: deepseek-v4.1-flash @ https://<your-fallback-endpoint>/v1
LINE Bot 已啟用
[TRAVEL] SQLite 已初始化並完成 migration
[GRADUATION] 排程已啟動，目標群組: ...
LINE webhook server 啟動於 port 5000
```

#### LIFF 前端（開發）
```bash
cd liff
npm run dev
```
開 `http://localhost:5174/`，Vite 會把 `/liff/*` 轉發到 bot 的 :5000。

### 對外 HTTPS（LINE webhook + LIFF）

LINE Bot 跟 LIFF 都需要公開的 HTTPS 端點。本機開發用 `ngrok.yml`（已配置兩個 tunnel）：
```bash
ngrok start --all              # 啟動 nlp_final_project (5000) + sassy_liff (5174)
```

把 ngrok 給的網址填入：
- LINE Developers Console → Webhook URL：`https://<bot-tunnel>.ngrok-free.app/line/callback`
- LINE LIFF Endpoint URL：`https://<liff-tunnel>.ngrok-free.app`

> 若只用雲端部署（不用 ngrok），替換成正式 HTTPS 網域即可。

日誌寫入 `bot.log`（RotatingFileHandler，5MB × 7 份，重啟不清除）。

## 開發規格

設計決策記錄在 `docs/superpowers/specs/` 下，commit 進 repo 供 reviewer 參考：
- 對話感知設計（2026-08-07）
- 畢業倒數機制（2026-05-30）
- Phase 2 徽章 + LIFF 設計（2026-08-12）

實作計畫：
- `plans/2026-05-30-daily-graduation-countdown.md`
- `plans/2026-08-12-phase2-badges-liff.md`
- `plans/2026-08-12-phase3-analytics-dashboard.md`
- `plans/2026-08-12-travel-badge-extension.md`
