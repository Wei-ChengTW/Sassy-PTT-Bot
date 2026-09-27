// 金句分享小卡（紀念冊「同學留言」樣式）：純 JSON Flex，供 liff.sendMessages / shareTargetPicker。
// 色碼需與 line_bot/stats_cards.py 同步。
import type { FlexMessage } from './flexTripCard'

const CLOTH = '#1E3A2F'
const FOIL = '#B8943A'
const SAGE = '#C9D3CC'
const PEN = '#2346A0'
const PEN_BG = '#EEF1FA'
const MUTED = '#646B65'

export interface Quote {
  content: string
  user_name: string
  label?: string | null
  timestamp: number
  laughs?: number
  replies?: number
}

function fmtDate(ms: number): string {
  const d = new Date(ms)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

export function buildQuoteFlex(q: Quote): FlexMessage {
  const liffId = import.meta.env.VITE_LIFF_ID as string
  const content = (q.content || '').trim()
  const reactions = [
    q.laughs ? `${q.laughs} 人笑` : '',
    q.replies ? `${q.replies} 則回覆` : '',
  ].filter(Boolean).join(' · ')

  return {
    type: 'flex',
    altText: `[群組金句] 「${content.slice(0, 40)}」— ${q.user_name}`,
    contents: {
      type: 'bubble',
      header: {
        type: 'box', layout: 'vertical', backgroundColor: CLOTH, paddingAll: '16px',
        contents: [
          { type: 'text', text: q.label || '群組金句', size: 'lg', weight: 'bold', color: '#FFFFFF', wrap: true },
          { type: 'text', text: fmtDate(q.timestamp), size: 'xs', color: SAGE, margin: 'xs' },
          { type: 'box', layout: 'vertical', contents: [], width: '40px', height: '1px', backgroundColor: FOIL, margin: 'md' },
        ],
      },
      body: {
        type: 'box', layout: 'vertical', paddingAll: '16px', spacing: 'sm',
        contents: [
          {
            type: 'box', layout: 'vertical', backgroundColor: PEN_BG, cornerRadius: '4px', paddingAll: '14px', spacing: 'sm',
            contents: [
              { type: 'text', text: `「${content}」`, size: 'lg', weight: 'bold', color: PEN, wrap: true },
              { type: 'text', text: `— ${q.user_name}`, size: 'sm', color: PEN, align: 'end' },
            ],
          },
          ...(reactions ? [{ type: 'text', text: reactions, size: 'xs', color: MUTED }] : []),
        ],
      },
      footer: {
        type: 'box', layout: 'vertical', paddingAll: '12px', paddingTop: '0px',
        contents: [{
          type: 'button', style: 'primary', color: CLOTH, height: 'sm',
          action: { type: 'uri', label: '看更多金句', uri: `https://liff.line.me/${liffId}/topics` },
        }],
      },
    },
  }
}
