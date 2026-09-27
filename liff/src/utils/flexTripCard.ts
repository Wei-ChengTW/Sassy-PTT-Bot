// 把旅行事件 detail 轉成 LINE Messaging API 規範的純 JSON Flex Message，
// 供 liff.sendMessages / liff.shareTargetPicker 使用（不是 SDK 物件形式）。
import { rarityOf, RARITY } from '@/constants/rarity'
import { labelFor } from '@/constants/tripTypes'

// 紀念冊色票（與 line_bot/stats_cards.py 同步）
const CLOTH = '#1E3A2F'
const FOIL = '#B8943A'
const INK = '#191D1A'
const MUTED = '#646B65'
const RULE = '#DDE1DC'

// 稀有度主題色（hex）直接取 constants/rarity.ts 的 line 色，不再手動同步。
const RARITY_HEX: Record<string, string> = Object.fromEntries(
  Object.values(RARITY).map((r) => [r.key, r.line]),
)

function fmtDate(ts: number): string {
  const d = new Date(ts * 1000)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

function dateRange(t: any): string {
  if (!t?.start_date) return ''
  const start = fmtDate(t.start_date)
  if (!t.end_date || t.end_date === t.start_date) return start
  return `${start} – ${fmtDate(t.end_date)}`
}

export interface FlexMessage {
  type: 'flex'
  altText: string
  contents: any
}

/**
 * 依 detail（含 trip / participants / stats）產生事件回顧小卡。
 * 對缺欄位（timeline 情境的空 stats/participants）做防呆，缺則略過區塊。
 */
export function buildTripFlex(detail: any): FlexMessage {
  const trip = detail?.trip ?? {}
  const participants: any[] = detail?.participants ?? []
  const messageCount: number | undefined = detail?.stats?.message_count

  const rarity = rarityOf(trip.rarity)
  const line = RARITY_HEX[rarity.key] || RARITY_HEX.common
  const title: string = trip.title || '旅行回顧'
  const location: string = trip.location || ''
  const range = dateRange(trip)
  const liffId = import.meta.env.VITE_LIFF_ID as string
  const seal = trip.custom_emoji || trip.badge_emoji || ''

  const altText = location
    ? `[旅行回顧] ${title}（${location}・${rarity.zh}）`
    : `[旅行回顧] ${title}（${rarity.zh}）`

  // ── 資料列（逐一防呆組裝；缺就不放） ──
  const rows: any[] = []
  if (location) rows.push(infoRow('地點', location))
  if (range) rows.push(infoRow('日期', range))
  const tripTypes: string[] = Array.isArray(trip.trip_types) ? trip.trip_types : []
  if (tripTypes.length) rows.push(infoRow('類型', tripTypes.slice(0, 4).map(labelFor).join('、')))
  if (participants.length) {
    const names = participants.slice(0, 3).map((p) => p.user_name || p.user_id).filter(Boolean).join('、')
    const extra = participants.length > 3 ? ` 等 ${participants.length} 人` : ''
    rows.push(infoRow('成員', `${names}${extra}`))
  }
  if (typeof messageCount === 'number') rows.push(infoRow('訊息', `${messageCount.toLocaleString()} 則`))

  // 紀念章 + 標題
  const hero = {
    type: 'box', layout: 'horizontal', spacing: 'md', alignItems: 'center',
    contents: [
      {
        type: 'box', layout: 'vertical', width: '60px', height: '60px', cornerRadius: '30px', flex: 0,
        borderWidth: '3px', borderColor: line, backgroundColor: '#FFFFFF',
        justifyContent: 'center', alignItems: 'center',
        contents: [{ type: 'text', text: seal || '🎒', size: 'xxl', align: 'center' }],
      },
      {
        type: 'box', layout: 'vertical', flex: 1,
        contents: [
          { type: 'text', text: title, size: 'lg', weight: 'bold', color: INK, wrap: true },
          {
            type: 'box', layout: 'horizontal', margin: 'sm',
            contents: [{
              type: 'box', layout: 'vertical', flex: 0, paddingStart: '6px', paddingEnd: '6px',
              cornerRadius: '3px', backgroundColor: line,
              contents: [{ type: 'text', text: rarity.zh, size: 'xxs', weight: 'bold', color: '#FFFFFF' }],
            }],
          },
        ],
      },
    ],
  }

  const bubble = {
    type: 'bubble',
    header: {
      type: 'box', layout: 'vertical', backgroundColor: CLOTH, paddingAll: '16px',
      contents: [
        { type: 'text', text: '旅行回顧', size: 'lg', weight: 'bold', color: '#FFFFFF' },
        { type: 'box', layout: 'vertical', contents: [], width: '40px', height: '1px', backgroundColor: FOIL, margin: 'md' },
      ],
    },
    body: {
      type: 'box', layout: 'vertical', spacing: 'md', paddingAll: '16px',
      contents: rows.length
        ? [hero, { type: 'separator', color: RULE }, ...rows]
        : [hero],
    },
    footer: {
      type: 'box', layout: 'vertical', paddingAll: '12px', paddingTop: '0px',
      contents: [{
        type: 'button', style: 'primary', color: CLOTH, height: 'sm',
        action: { type: 'uri', label: '打開回顧', uri: `https://liff.line.me/${liffId}/trips/${trip.id}` },
      }],
    },
  }

  return { type: 'flex', altText, contents: bubble }
}

function infoRow(label: string, text: string): any {
  return {
    type: 'box', layout: 'horizontal', spacing: 'md',
    contents: [
      { type: 'text', text: label, size: 'sm', color: MUTED, flex: 0 },
      { type: 'text', text, size: 'sm', color: INK, weight: 'bold', wrap: true, flex: 1 },
    ],
  }
}
