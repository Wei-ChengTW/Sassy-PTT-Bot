---
name: Sassy PTT Bot LIFF
description: 一個朋友群組的畢業紀念冊：布面深綠封面、燙金、銅版紙白頁、原子筆藍。
colors:
  cloth-green: "#1E3A2F"
  foil-gold: "#B8943A"
  foil-gold-light: "#E6D09A"
  foil-gold-pale: "#D6B872"
  foil-gold-deep: "#8F7020"
  foil-wash: "#FAF5E9"
  pen-blue: "#2346A0"
  pen-blue-hover: "#1E3C8A"
  pen-blue-deep: "#193272"
  letter-paper: "#EEF1FA"
  letter-paper-edge: "#D8DFF3"
  seal-red: "#B8332A"
  seal-wash: "#FBEDEB"
  ledger-green: "#2E7D4F"
  kraft-brown: "#9A7040"
  medal-gold: "#C6A252"
  medal-silver: "#BFC7C5"
  medal-bronze: "#C8956A"
  silver-card: "#F1F4F3"
  silver-edge: "#CDD4D2"
  bronze-card: "#F8EEE4"
  bronze-edge: "#E2C7AC"
  ink: "#191D1A"
  ink-soft: "#373D38"
  ink-muted: "#646B65"
  grey-mark: "#8C938C"
  sage-on-cloth: "#C9D3CC"
  rule-strong: "#C5CAC4"
  rule: "#DDE1DC"
  rule-soft: "#EEF0ED"
  paper-subtle: "#F7F8F6"
  paper: "#FFFFFF"
  page: "#E4EBE5"
  toast-ink: "#262B27"
typography:
  display:
    fontFamily: "\"Noto Serif TC\", serif"
    fontSize: "28px"
    fontWeight: 900
    lineHeight: 1.2
  display-name:
    fontFamily: "\"Noto Serif TC\", serif"
    fontSize: "24px"
    fontWeight: 900
    lineHeight: 1.25
  figure-cover:
    fontFamily: "\"Barlow Semi Condensed\", \"Noto Sans TC\", sans-serif"
    fontSize: "34px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0"
    fontFeature: "\"tnum\" 1"
  figure:
    fontFamily: "\"Barlow Semi Condensed\", \"Noto Sans TC\", sans-serif"
    fontSize: "30px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0"
    fontFeature: "\"tnum\" 1"
  figure-medal:
    fontFamily: "\"Barlow Semi Condensed\", \"Noto Sans TC\", sans-serif"
    fontSize: "22px"
    fontWeight: 600
    lineHeight: 1
    fontFeature: "\"tnum\" 1"
  figure-row:
    fontFamily: "\"Barlow Semi Condensed\", \"Noto Sans TC\", sans-serif"
    fontSize: "15px"
    fontWeight: 600
    lineHeight: 1.33
    fontFeature: "\"tnum\" 1"
  cover-subtitle:
    fontFamily: "\"Barlow Semi Condensed\", sans-serif"
    fontSize: "13px"
    fontWeight: 600
    letterSpacing: "0.02em"
  title:
    fontFamily: "\"Noto Sans TC\", system-ui, -apple-system, sans-serif"
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 1.33
  body:
    fontFamily: "\"Noto Sans TC\", system-ui, -apple-system, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.43
  label:
    fontFamily: "\"Noto Sans TC\", system-ui, -apple-system, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.33
  caption:
    fontFamily: "\"Noto Sans TC\", system-ui, -apple-system, sans-serif"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.45
  hand-quote:
    fontFamily: "\"LXGW WenKai TC\", \"Noto Sans TC\", serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: "28px"
  hand-name:
    fontFamily: "\"LXGW WenKai TC\", \"Noto Sans TC\", serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.25
rounded:
  sm: "2px"
  md: "3px"
  lg: "4px"
  3xl: "6px"
  full: "999px"
spacing:
  hairline: "1px"
  chip-gap: "6px"
  grid-gap: "8px"
  header-gap: "12px"
  card-x: "14px"
  gutter: "16px"
  cover-y: "20px"
  section: "32px"
components:
  cover-band:
    backgroundColor: "{colors.cloth-green}"
    textColor: "{colors.paper}"
    typography: "{typography.display}"
    padding: "20px 16px"
  card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "12px 14px"
  card-subtle:
    backgroundColor: "{colors.paper-subtle}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
  row-first-place:
    backgroundColor: "{colors.foil-wash}"
    textColor: "{colors.ink}"
    padding: "12px 14px"
  rank-cover:
    backgroundColor: "{colors.cloth-green}"
    textColor: "{colors.paper}"
    typography: "{typography.display-name}"
    rounded: "{rounded.lg}"
    padding: "14px 16px 16px"
  medal-silver:
    backgroundColor: "{colors.silver-card}"
    textColor: "{colors.ink}"
    typography: "{typography.figure-medal}"
    rounded: "{rounded.lg}"
    padding: "14px 14px 12px"
  medal-bronze:
    backgroundColor: "{colors.bronze-card}"
    textColor: "{colors.ink}"
    typography: "{typography.figure-medal}"
    rounded: "{rounded.lg}"
    padding: "14px 14px 12px"
  stat-cell:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.figure}"
    padding: "14px 16px"
  stat-cell-cover:
    backgroundColor: "{colors.cloth-green}"
    textColor: "{colors.paper}"
    typography: "{typography.figure}"
    padding: "14px 16px"
  seat-chip:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    size: "32px"
  quote-card:
    backgroundColor: "{colors.letter-paper}"
    textColor: "{colors.pen-blue-deep}"
    typography: "{typography.hand-quote}"
    rounded: "{rounded.lg}"
    padding: "14px 16px"
  button-primary:
    backgroundColor: "{colors.pen-blue}"
    textColor: "{colors.paper}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
  button-primary-hover:
    backgroundColor: "{colors.pen-blue-hover}"
    textColor: "{colors.paper}"
  chip-filter:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-soft}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "6px 12px"
  chip-filter-active:
    backgroundColor: "{colors.cloth-green}"
    textColor: "{colors.paper}"
  segmented-option:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "6px 12px"
  segmented-option-active:
    backgroundColor: "{colors.cloth-green}"
    textColor: "{colors.paper}"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "10px 14px"
  nav-tab:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.caption}"
  nav-tab-active:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.cloth-green}"
  toast:
    backgroundColor: "{colors.toast-ink}"
    textColor: "{colors.paper}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "10px 16px 10px 12px"
---

# Design System: Sassy PTT Bot LIFF

## Overview

**Creative North Star: "畢業紀念冊（The Class Yearbook）"**

群組就是一個班級，LIFF app 是這個班的畢業紀念冊。每位成員有座號、有自己的一頁；排行榜是班級紀錄，徽章是頒給同學的獎項。視覺語言全部來自一本實體紀念冊的材料：深綠布面精裝封面（帶細布紋）、一道燙金細線、銅版紙白頁、原子筆藍的筆跡、印章紅。系統取代了舊的靛藍 SaaS 卡片儀表板，也刻意不走柔焦懷舊剪貼簿路線：這是一本印刷品，不是手帳。

密度以手機（390px、LINE 內建瀏覽器、單手）為準：單欄、16px 頁邊、白色紙面卡片靠 1px 細線分隔，不靠陰影。顏色按「區域」出現，而不是灑在每個元件上：封面帶承載頁名與關鍵數字，第一名那一列染淡金，同學的金句寫在藍色信紙上，其餘都是白紙黑字。稀有度是「印刷加工」的階梯：平印、壓紋、燙綠箔、燙金、鐳射箔，越稀有，加工越貴。

動態只有短淡入與單軸滑動（180–240ms、out-expo），沒有彈跳、沒有發光；唯一持續運動的是箔面的慢速流光，且在 reduced-motion 下全部停止。

**Key Characteristics:**
- 布面深綠封面帶（細布紋）＋一道燙金細線，是每一頁的開頭。
- 灰綠色頁底上的白色紙面卡片，1px 細線、4px 圓角、無陰影。
- 數字一律 Barlow Semi Condensed 等寬數字；封面標題與第一名用 Noto Serif TC 900；同學說的話與綽號用霞鶩文楷。
- 原子筆藍只給可以點的東西；燙金只給第一名、史詩與單一峰值。
- 稀有度＝印刷加工（平印／壓紋／燙綠箔／燙金／鐳射箔）。
- 聊天室的 LINE Flex 卡片使用同一組色票，是同一本紀念冊的延伸。

## Colors

一本精裝紀念冊的材料色：深綠布面、燙金、原子筆藍、印章紅，放在帶一點綠意的中性灰紙上。

### Primary
- **布面深綠 Bookcloth Green** (`cloth-green`)：封面帶底色（PageSign、第一名封面塊、Dashboard 的封面數字格）、分段控制與篩選 chip 的選取狀態、底部導覽的選取文字、排行比例條、所有圖表的資料色。也是 `<meta name="theme-color">`。
- **燙金 Foil Gold** (`foil-gold`)：封面下的燙金細線（1px，寬 48px）、章節菱形記號、底部導覽 3px 滑動標記、史詩稀有度、圖表中唯一的最高值。
- **淺燙金** (`foil-gold-light`)：深綠封面上的大數字（第一名的數值）。
- **淡燙金** (`foil-gold-pale`)：深綠封面上的英文副標與小標（「第 N 名」、數字格標籤）。
- **深燙金** (`foil-gold-deep`)：淺底上需要金色的文字。
- **淡金底** (`foil-wash`)：第一名那一列的整列底色（Dashboard、GroupPulse、Interaction 排行列）與精選看板 highlight 區塊。

### Secondary
- **原子筆藍 Ballpoint Blue** (`pen-blue`)：主要按鈕、連結、輸入框 focus 邊框與 ring、稀有（rare）階。`pen-blue-hover` 為按鈕 hover。
- **信紙 Letter Paper** (`letter-paper`, 邊線 `letter-paper-edge`)：金句卡的底，加上每 28px 一道 10% 原子筆藍橫線的信紙格線；文字用 `pen-blue-deep`。

### Tertiary
- **印章紅 Seal Red** (`seal-red`)：傳說稀有度（外圈印章環）、錯誤、負面語氣標記；`seal-wash` 為傳說列的淡底。
- **帳本綠 Ledger Green** (`ledger-green`)：增加、完成、成功 toast、極稀有（super_rare）階。
- **牛皮紙棕 Kraft Brown** (`kraft-brown`)：旅行區域。
- **獎章金／銀／銅** (`medal-gold` / `medal-silver` / `medal-bronze`)：前三名座號 chip 的實心底色。銀、銅獎章卡使用 `silver-card`+`silver-edge`、`bronze-card`+`bronze-edge`。

### Neutral
- **墨 Ink** (`ink`)：主要文字。`ink-soft` 為次強文字（idle chip、數值旁強調）。
- **鉛筆灰** (`ink-muted`)：次要文字、單位、日期、未選取導覽、圖表軸文字。
- **灰記號** (`grey-mark`)：普通（common）稀有度、未分類資料、空狀態圖示。
- **封面鼠尾草** (`sage-on-cloth`)：深綠封面上的次要文字與返回鍵。
- **細線** (`rule-strong` / `rule` / `rule-soft`)：輸入框與分段控制外框／卡片邊線／列分隔、比例條底、圖表格線。
- **紙** (`paper`, `paper-subtle`)：卡片與導覽列是純白；`paper-subtle` 用於 subtle 卡片與 hover。
- **頁底** (`page`)：html/body 的灰綠頁底。絕不是米色。
- **Toast 墨** (`toast-ink`)：唯一的深色浮動提示底。

### Named Rules
**The Region Scale Rule.** 顏色以區域為單位出現：封面帶、第一名的淡金列、信紙金句。區域內的元件不再各自上色；一頁上不該出現三個以上的彩色區域。

**The Pen Is For Touch Rule.** 原子筆藍只用在可點擊、可輸入、選取中的介面元素，以及信紙上的同學筆跡。資料、圖表、裝飾一律不用藍。

**The Gold Is Earned Rule.** 燙金只標記「第一」：第一名、史詩、圖表中唯一的峰值、封面細線與章節記號。不拿金色當一般強調色。

**The Chart Ink Rule.** 圖表資料一律用布面深綠（填色 7% 深綠），最高值那一根改為燙金，其餘淡化用 `rule-strong`。訊息類型分布是唯一的類別色例外（文字／貼圖／圖片／影片／語音／檔案各一色）。

## Typography

**Display Font:** Noto Serif TC 900（fallback serif）
**Body Font:** Noto Sans TC 400/500/700/900（fallback system-ui, -apple-system, sans-serif）
**Numeral Font:** Barlow Semi Condensed 500/600/700（fallback Noto Sans TC）
**Hand Font:** LXGW WenKai TC 400/700（fallback Noto Sans TC, serif）

**Character:** 黑體負責清楚，明體負責封面的莊重，窄體數字像成績單一樣對齊，楷體是同學親手寫下的字。四種字體各守一個角色，不互相借位。

### Hierarchy
- **Display**（900, 28px, 1.2）：頁面封面帶上的頁名（PageSign）。
- **Display Name**（900, 24px）：排行第一名封面塊上的名字。
- **Figure Cover**（Barlow 600, 34px, 1）：第一名封面上的數值，淺燙金。
- **Figure**（Barlow 600, 30px, 1）：紀錄表數字格。
- **Figure Medal**（Barlow 600, 22px）：第二、三名獎章卡的數值。
- **Figure Row**（Barlow 600, 15px）：排行列與名單中的數值、名次。
- **Cover Subtitle**（Barlow 600, 13px, 0.02em, 淡燙金）：封面標題「下方」的英文副標（Class Record、Group Pulse）。
- **Title**（700, 15px）：章節標題（前置 7px 燙金菱形）與列中的人名。
- **Body**（400, 14px, 1.43）：一般內文、按鈕文字。
- **Label**（500, 12px）：chip、分段控制、數字格標籤、說明。
- **Caption**（400, 11px）：導覽列標籤、列下附註、單位。
- **Hand Quote**（700, 18px / 28px 行高）：信紙上的金句，行高與信紙格線同為 28px。
- **Hand Name**（700, 22px, 布面深綠）：綽號頁的主綽號；次要綽號 14px。

### Named Rules
**The Tabular Numerals Rule.** 所有數字（計數、百分比、名次、日期）用 `font-num`，強制 tabular-nums、letter-spacing 0，讓欄位像成績單一樣對齊。單位字回到 Noto Sans TC、縮小一級、鉛筆灰。

**The Serif Is For Covers Rule.** Noto Serif TC 900 只出現在封面頁名與第一名的名字。卡片標題、章節、按鈕一律用黑體。

**The Handwriting Rule.** 霞鶩文楷只用在「同學說過或被取的字」：金句、綽號、金句署名。介面文字永遠不用手寫體。

## Layout

手機優先的單欄版面：`main` 最大寬 512px 置中，左右 16px 頁邊。封面帶以負邊距撐滿全寬（-16px），內距 20px/16px，下接 24px 間距。章節之間 32px，章節標題到內容 12px。卡片內距 14px 橫向、12–14px 縱向；卡片組與獎章卡網格間距 8px；chip 間距 6px。

排行版面固定三段：第一名是一整塊深綠封面（名字、數值、燙金細線），第二、三名是並排兩欄的銀／銅獎章卡，第四名起是白卡列表，每列帶 4px 高的深綠比例條。

底部導覽固定在畫面底部（白底、上緣細線、safe-area 內距），5 格；「更多」以底部浮層展開 3 欄網格。頁面底部保留 112px 空間給導覽。

橫向標籤列在手機上單行可滑（右緣 40px 遮罩淡出暗示還有），寬度 ≥640px 時改為自動換行。

## Elevation & Depth

紙是平的。卡片、封面、獎章卡在靜止時都沒有陰影（Tailwind 的 sm/md/lg/xl/card/lift/glow 全部設為 none）；層次靠 1px 細線、區域色與頁底／白紙的明度差建立。唯一的投影 `pop` 只給真正浮在頁面上的東西：「更多」浮層與 toast。深度的另一個來源是印刷加工本身：壓紋的內陰影、箔面的光澤層。

### Shadow Vocabulary
- **Pop**（`box-shadow: 0 12px 28px -12px rgba(17,18,20,0.35)`）：只用於浮層與 toast。
- **Emboss**（稀有紀念章的多層 inset，見 sidecar）：只屬於 rare 階的壓紋紀念章，是印刷效果，不是元件陰影。

### Named Rules
**The Flat Paper Rule.** 貼在頁面上的東西不投影。需要分隔就用 1px 細線；需要強調就換區域色。投影只屬於離開紙面、浮在上方的浮層。

## Shapes

近乎直角的印刷品邊緣：chip 與輸入框 3px，卡片、封面塊、獎章卡 4px（程式中的 `rounded-xl` 已映射為 4px），浮層偶有 6px。完整圓形只留給三種東西：紀念章（稀有度印章）、狀態小圓點、比例條。邊線一律 1px；座號 chip 與紀念章用 2–4px 粗框，模仿印章與號碼牌。章節記號是旋轉 45° 的 7px 燙金菱形。

**The Near-Square Rule.** 圓角不超過 4px（浮層 6px）。大圓角膠囊按鈕與圓角卡片屬於被取代的 SaaS 外觀。

## Components

### Buttons
紀念冊的按鈕是原子筆寫下的字：藍、實、方。
- **Shape:** 3px 圓角。
- **Primary:** 原子筆藍底、白字、700、14px；表單送出為全寬、12px 縱向內距。
- **Hover / Active:** hover 換 `pen-blue-hover`；按下時 `scale(0.97)`，120ms。disabled 為 50–60% 不透明。
- **Icon button:** 40px 觸控區、原子筆藍線條圖示（inline SVG，stroke 2），hover 底為 `letter-paper-edge`。

### Chips
- **Style:** 白底、1px `rule` 邊、`ink-soft` 文字、12px 500、3px 圓角；可附 11px 等寬數字計數（70% 不透明）。
- **State:** 選取中為布面深綠實底、白字、深綠邊。長列表放進橫向可滑列。

### Segmented Control
外框 1px `rule-strong`、3px 圓角、白底；選取段為布面深綠白字，未選為鉛筆灰字、hover `paper-subtle`。時間區間選擇器同此。

### Cards / Containers
- **Corner Style:** 4px。
- **Background:** 預設白紙；`subtle` 變體為 `paper-subtle`；`brand` 變體為信紙色。
- **Shadow Strategy:** 無（見 Flat Paper Rule）。
- **Border:** 1px `rule`；可互動卡 hover 時邊線加深為 `rule-strong`，按下縮放 0.97。
- **Internal Padding:** 14px 橫向；列表列之間以 `rule-soft` 分隔。

### Inputs / Fields
- **Style:** 白底、1px `rule-strong`、3px 圓角、10px/14px 內距、14px 500。
- **Focus:** 邊框轉原子筆藍並加 1px 同色 ring；游標為原子筆藍。

### Navigation
底部索引標籤列：白底、上緣 1px `rule`、5 欄；每格為 22px 線條圖示＋11px 標籤。未選為鉛筆灰，選取為布面深綠 700。一條 3px 燙金標記沿頂緣以 transform 滑到選取的格（240ms out-expo），這是系統的招牌互動。「更多」浮層為白底、1px 邊、`pop` 投影、3 欄網格，選取項 `rule-soft` 底＋深綠字。

### 封面帶 PageSign（Signature）
每頁的開頭：全寬布面深綠，疊兩組極淡交織細線做布紋（0°：3.5% 白，90°：8% 黑，3px 週期）。內容依序為可選的返回鍵（鼠尾草色）、Display 頁名、淡燙金英文副標、一道寬 48px 的燙金細線、鼠尾草色附註，以及可選的 figures 插槽（封面上的數字格）。

### 座號 Chip（Seat Number）
32px 方形號碼牌：2px 邊、3px 圓角、白底、Barlow 700 16px 墨色數字。前三名改為實心底：金 `medal-gold`、銀 `medal-silver`、銅 `medal-bronze`，文字仍為墨色；其餘名次為 `rule-strong` 邊。小尺寸 26px。

### 排行榜 RankList（Signature）
第一名＝布面深綠封面塊（淡燙金「第 N 名」、Display Name 名字、34px 淺燙金數值、70% 燙金細線）。第二、三名＝兩欄銀／銅獎章卡，頂緣 4px 金屬漸層箔條慢速來回流光（6s，銅延遲 1.2s）。第四名起＝白卡列表：名次（鉛筆灰等寬數字）、人名、數值、4px 深綠比例條（寬度動畫 700ms out-expo）。

### 里程碑獎狀 Milestone Certificate
個人頁的里程碑用「獎狀」主從結構，而不是四格同等的表格：累積發言總量是主角，放在布面深綠塊上（40px 淺燙金數字＋燙金細線），「第 N 則達成」以燙金圓框星形戳記附在同一塊裡，並標示距今多久。其下兩張並排獎章卡：單日最高紀錄用金箔卡（`medal--gold`：淡金底、金色箔條），最長連續發言用銀箔卡（`medal--silver`）。金、銀、銅三種箔卡共用 `.medal-foil` 頂緣流光。

### 相對時間 Relative Time
已結束的旅行一律附「距今多久」（`utils/ago.ts`：今天／昨天／N 天前／N 週前／N 個月前／N 年前／N 年半前），以燙金深色 `accent-700` 粗體標在日期後；未出發的旅行改標「還有 N 天」。相對時間是輔助資訊，永遠跟在絕對日期旁邊，不取代日期。

### 紀錄表數字格 StatCard
30px 等寬數字＋12px 標籤。`cover` 色調為深綠底白數字、淡燙金標籤；預設為白底墨色數字、鉛筆灰標籤。

### 金句信紙 Quote Card
信紙色底、`letter-paper-edge` 邊、4px 圓角，底紋為每 28px 一道 10% 原子筆藍橫線（對齊 28px 行高）。金句以 Hand Quote 寫在 `pen-blue-deep`，署名為 15px 楷體 `pen-blue-hover`；語氣以 8px 圓點標示（正面帳本綠、吐槽印章紅）。

### 稀有度印刷加工 RaritySeal / FoilCard（Signature）
五階加工，對應 common → legendary：
- **平印（common）：** 白底、3px `rule-strong` 圓環。
- **壓紋（rare）：** 原子筆藍圓環加內側雙細環與內陰影，做出凸凹感。
- **燙綠箔（super_rare）：** 帳本綠系 conic 漸層圓環，9s 一圈緩轉。
- **燙金（epic）：** 燙金系 conic 漸層圓環、奶金內底，6s 一圈；卡片加上 115° 斜向掠光（每 7s 自動掠過一次，指標可驅動）。
- **鐳射箔（legendary）：** 4px 彩虹全像圓環，4s 一圈，外加 1.5px 印章紅外圈；卡片加上 color-dodge 全像層與 45° 細紋，隨指標位置與傾斜（perspective 700px）改變。

所有箔面動畫與傾斜在 `prefers-reduced-motion: reduce` 下停止。

### 空狀態 EmptyState
72×16 的虛線軌道＋空心圓（`rule-strong` / `grey-mark`），16px 700 標題、13px 鉛筆灰說明。

### Toast
`toast-ink` 底、白字 14px 500、3px 圓角、`pop` 投影；左側 10px 狀態圓點（成功帳本綠、失敗印章紅）。

### LINE Flex 聊天卡片
聊天室裡的 Flex 卡片（`line_bot/stats_cards.py`、`liff/src/utils/flexQuoteCard.ts`、`liff/src/utils/flexTripCard.ts`）是同一本紀念冊的散頁，直接鏡射上方色票：`CLOTH` 深綠用於卡片標頭、主按鈕與比例條；`FOIL` 燙金細線與第一名，`FOIL_LIGHT` 為深綠標頭上的金字，`FOIL_DARK` 為淺底上的金字，`FOIL_BG` 為第一名淡金列；`SAGE` 為標頭次要文字；`INK`／`MUTED`／`RULE` 為文字與分隔；`PEN` 與 `PEN_BG` 為金句的筆跡與信紙；`SEAL` 印章紅；前三名座號沿用獎章金／銀／銅，稀有度沿用同一組五階色。Flex 無法載入自訂字體，因此只承接色彩與區域規則，不承接字體。卡片標題不放 emoji；紀念章裡的 emoji 是旅行／徽章本身的內容，不是介面圖示。通知預覽（altText）必須帶結果本身（例如「發言排行：第 1 名 洪偉城 11,049 則」），不只是卡片名稱。

## Do's and Don'ts

### Do:
- **Do** 每頁以封面帶開頭：布面深綠＋布紋、Noto Serif TC 900 頁名、48px 燙金細線。
- **Do** 把第一名做成區域：列表中整列淡金底（`foil-wash`），排行版面中為深綠封面塊。
- **Do** 所有數字用 Barlow Semi Condensed tabular-nums，單位縮小一級、鉛筆灰。
- **Do** 圖表資料用布面深綠，唯一的最高值改燙金。
- **Do** 卡片用白紙＋1px 細線＋4px 圓角，靜止時不投影。
- **Do** 稀有度一律透過 RaritySeal／FoilCard 的五階印刷加工表現，並尊重 reduced-motion。
- **Do** 動態只用短淡入與單軸滑動（180–240ms, `cubic-bezier(0.16, 1, 0.3, 1)`），按下回饋 `scale(0.97)` 120ms。
- **Do** Flex 卡片使用與 LIFF 相同的色票常數。

### Don't:
- **Don't** 回到靛藍 SaaS 卡片儀表板：漸層數字磚、發光色塊、玻璃導覽列、大圓角膠囊。
- **Don't** 用 emoji 當介面圖示；圖示一律 inline SVG 線條（stroke 2）。成員自己選的旅行徽章 emoji 是內容，不是圖示。
- **Don't** 把原子筆藍用在資料、圖表系列或裝飾上。
- **Don't** 把燙金當一般強調色；一頁上的金只標第一。
- **Don't** 把頁底改成米色或奶油色；頁底是灰綠 `page`，暖色只出現在第一名淡金列與銅獎章卡。
- **Don't** 在非浮層元素上加投影。
- **Don't** 在介面文字上使用楷體或明體；楷體只給同學的話與綽號，明體只給封面與第一名。
- **Don't** 用漸層做背景或卡片填色；漸層只存在於材料本身（布紋、箔面、金屬箔條、信紙格線）。
