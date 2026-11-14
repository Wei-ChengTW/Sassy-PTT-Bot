// 出發倒數小卡：由成員在 LIFF 手動發送（以本人名義，不吃官方帳號推播額度）。
// 樣式與 line_bot/stats_cards.py 的 build_countdown_card 一致；內容依按下當下的剩餘天數產生。
import { rarityOf, RARITY } from '@/constants/rarity'
import type { FlexMessage } from './flexTripCard'

const CLOTH = '#1E3A2F'
const FOIL = '#B8943A'
const FOIL_DARK = '#8F7020'
const INK = '#191D1A'
const MUTED = '#646B65'
const RULE = '#DDE1DC'
const WEEKDAYS = '日一二三四五六'

const RARITY_HEX: Record<string, string> = Object.fromEntries(
  Object.values(RARITY).map((r) => [r.key, r.line]),
)

// 台灣日期的「第幾天」：倒數以日曆日計，不看時分（與 bot 端 notify.countdown_days 相同）
const tpeDate = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Taipei' })
function tpeDayNumber(ms: number): number {
  return Date.parse(`${tpeDate.format(ms)}T00:00:00Z`) / 86400000
}

/** 距離出發還有幾天（0＝今天出發）；沒有開始日或已過回 null。 */
export function daysUntilDeparture(startSec: number | null | undefined, nowMs = Date.now()): number | null {
  if (!startSec) return null
  const d = tpeDayNumber(startSec * 1000) - tpeDayNumber(nowMs)
  return d >= 0 ? d : null
}

function fmtDeparture(startSec: number): string {
  const d = new Date(startSec * 1000 + 8 * 3600 * 1000)   // 以台灣時間取年月日
  return `${d.getUTCFullYear()}/${d.getUTCMonth() + 1}/${d.getUTCDate()}（${WEEKDAYS[d.getUTCDay()]}）`
}

// 天數較多時補上週／月的換算，讓「還有 138 天」有感
function roughSpan(days: number): string {
  if (days >= 60) return `約 ${Math.round(days / 30)} 個月`
  if (days >= 14) return `約 ${Math.round(days / 7)} 週`
  return ''
}

function txt(text: string, extra: Record<string, any> = {}) {
  return { type: 'text', text, color: INK, ...extra }
}

export function countdownAlt(title: string, days: number): string {
  if (days === 0) return `${title}：今天出發`
  if (days === 1) return `${title}：明天出發`
  return `${title}：還有 ${days} 天出發`
}

export function buildCountdownFlex(trip: any, nowMs = Date.now()): FlexMessage | null {
  const days = daysUntilDeparture(trip?.start_date, nowMs)
  if (days === null) return null
  const title: string = trip.title || '旅行'
  const rarity = rarityOf(trip.rarity)
  const line = RARITY_HEX[rarity.key] || RARITY_HEX.common
  const seal = trip.custom_emoji || trip.badge_emoji || '🎒'
  const liffId = import.meta.env.VITE_LIFF_ID as string

  const big = days <= 1
    ? [txt(days === 0 ? '今天' : '明天', { size: 'xxs', color: FOIL_DARK, align: 'end' }),
       txt('出發', { size: 'xxl', weight: 'bold', color: FOIL_DARK, align: 'end' })]
    : [txt('還有', { size: 'xxs', color: FOIL_DARK, align: 'end' }),
       txt(String(days), { size: '3xl', weight: 'bold', color: FOIL_DARK, align: 'end' }),
       txt('天', { size: 'xxs', color: FOIL_DARK, align: 'end' })]

  const rows: any[] = [txt(`出發日　${fmtDeparture(trip.start_date)}`, { size: 'sm', color: MUTED })]
  if (trip.location) rows.unshift(txt(`地點　${trip.location}`, { size: 'sm', color: MUTED, wrap: true }))
  const span = roughSpan(days)
  if (span) rows.push(txt(`距離出發${span}`, { size: 'sm', color: MUTED }))

  const bubble = {
    type: 'bubble',
    header: {
      type: 'box', layout: 'vertical', backgroundColor: CLOTH, paddingAll: '16px',
      contents: [
        txt(days === 0 ? '今天出發' : '下一趟旅行', { size: 'lg', weight: 'bold', color: '#FFFFFF' }),
        { type: 'box', layout: 'vertical', contents: [], width: '40px', height: '1px', backgroundColor: FOIL, margin: 'md' },
      ],
    },
    body: {
      type: 'box', layout: 'vertical', spacing: 'md', paddingAll: '16px',
      contents: [
        {
          type: 'box', layout: 'horizontal', spacing: 'md', alignItems: 'center',
          contents: [
            {
              type: 'box', layout: 'vertical', width: '64px', height: '64px', cornerRadius: '32px', flex: 0,
              borderWidth: '3px', borderColor: line, backgroundColor: '#FFFFFF',
              justifyContent: 'center', alignItems: 'center',
              contents: [txt(seal, { size: 'xxl', align: 'center' })],
            },
            { type: 'box', layout: 'vertical', flex: 1, contents: [txt(title, { size: 'lg', weight: 'bold', wrap: true })] },
            { type: 'box', layout: 'vertical', flex: 0, alignItems: 'flex-end', contents: big },
          ],
        },
        { type: 'separator', color: RULE },
        ...rows,
      ],
    },
    footer: {
      type: 'box', layout: 'vertical', paddingAll: '12px', paddingTop: '0px',
      contents: [{
        type: 'button', style: 'primary', color: CLOTH, height: 'sm',
        action: { type: 'uri', label: '看旅行內容', uri: `https://liff.line.me/${liffId}/trips/${trip.id}` },
      }],
    },
  }
  return { type: 'flex', altText: countdownAlt(title, days), contents: bubble }
}
