---
version: 1
slug: "liff-src-app-vue"
primary_target: "liff/src/App.vue"
related_targets: ["liff/src"]
---

# LIFF app (all routes)

Scope: the whole LIFF Vue app in liff/ (App shell, shared components, every view). Visitor mode: Operate.
Audience: members of a few fixed friend groups, opening it inside LINE on a phone for short checks (rankings, a profile, a trip). Neutral voice; copy reports, never jokes.
Constraints: keep every route, API call, state and behavior; zh-TW copy; Chart.js and D3 stay.

## Direction contract

THESIS: The group is a class, and the LIFF app is its yearbook (畢業紀念冊): every member has a seat number and a portrait slot, rankings are class records, badges are awards. Refuses the indigo SaaS card dashboard (gradient stat tiles, glow blobs, emoji icons, glass nav) and the soft nostalgic scrapbook.

OWN-WORLD: Deep bottle-green bookcloth (#1E3A2F) cover band with a fine woven texture and a single gold-foil hairline (#B8943A). Pages are coated-paper white panels on a neutral grey-green page (#EEF0ED, never cream), 1px rules, 4px radius, no shadows. Ballpoint-pen blue (#2346A0) for anything interactive. Gold foil = first place and epic; seal red (#B8332A) = legendary, errors. Seat-number chips (square, numeral in Barlow Semi Condensed) for ranks; initial monogram portrait slots for members. Chapter headings: bold Noto Sans TC with a short gold rule.

STORY: A member opens it, sees the group's name on the green cover, finds their seat on the class record, taps into their own page, and returns to the chat with a fact.

FIRST VIEWPORT: Dashboard: green cloth cover band full width (group name 28px black, gold hairline, "Class Record" line), then a 4-cell record table on white (28px numerals, label under), then the class's top 5 as portrait rows: seat chip, monogram slot, name, count. Bottom nav is a row of index tabs; a gold tab marker slides to the active one.

FORM: 畢業紀念冊 (Taiwanese school yearbook), position 1 on the first-round grounded list; chosen by the user over the rolled and re-rolled directions (after briefly building the Taipei Metro direction, which the user rejected on sight). Seed key 8174795c.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

Signature interaction: the index-tab marker slides between tabs (transform only, 240ms ease-out). Motion grammar: short fades and one-axis slides; nothing bounces or glows.
