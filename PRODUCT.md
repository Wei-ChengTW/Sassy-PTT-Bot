# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

A small number of fixed friend groups on LINE. Members already know each other; the bot lives in their group chat. They open the LIFF app from inside LINE on their phones (LINE in-app browser), usually right after the bot posts a link or someone asks "who talks the most". An admin (the bot owner) can switch between the groups.

## Product Purpose

The LIFF app lets a friend group look back at what they have accumulated together: chat activity, rankings, badges, nicknames, topics, interaction graphs, and trips they have taken. Success is members opening it, finding themselves and their friends in it, and having something to bring back into the chat.

## Positioning

The data is their own: real messages, real trips, real nicknames from one specific group of friends, not generic analytics. Every number is about people the viewer knows personally.

## Operating Context

- Opened inside LINE's in-app browser on phones (portrait, one hand); desktop is incidental.
- Short sessions: check a ranking, view a profile, browse a trip, then return to the chat.
- Pages: dashboard, leaderboard, timeline/memories, profile, badges, trips (list/detail/create/manage), map/footprints, interactions (D3 network), topics, group pulse, compare, nicknames, admin.
- Some content can be shared back into LINE as Flex messages (trip cards).

## Capabilities and Constraints

- Vue 3 + Vite + TypeScript + Tailwind + Pinia; Chart.js and D3 v7 for charts.
- Auth through LIFF token; members only see their own group; admin sees all groups.
- Period selector (time range) is global across analytics pages.
- Traditional Chinese (zh-TW) UI throughout.

## Brand Commitments

- The LINE bot itself has a PTT Gossiping-board sarcastic persona. The LIFF app deliberately does **not** carry that voice: it is a neutral, clear tool. Copy is plain and informative, not snarky.

## Evidence on Hand

- Real group data comes from the SQLite database at runtime; there is no marketing content, testimonials, or imagery. Do not fabricate any.

## Product Principles

1. The people are the content: names, nicknames, and faces of friends lead; chrome recedes.
2. Readable at a glance on a phone inside LINE, in one hand, in a few seconds.
3. Neutral voice: the tool reports, it does not joke.
4. One coherent system across all pages; no page gets its own style.
