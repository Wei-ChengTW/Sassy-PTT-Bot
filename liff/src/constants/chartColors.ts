// 訊息類型統一配色（原本在 Dashboard/Leaderboard/Profile 三處各自複製一份）。
// 訊息類型是唯一的「類別色」例外：需要六種可區分的顏色，取自紀念冊色票。
export const TYPE_COLORS: Record<string, string> = {
  text: '#2346A0',
  sticker: '#B8332A',
  image: '#2E7D4F',
  video: '#B8943A',
  audio: '#9A7040',
  file: '#8C938C',
}

// 圖表共用：字體、格線、文字色
export const CHART_FONT = '"Noto Sans TC", sans-serif'
export const CHART_NUM_FONT = '"Barlow Semi Condensed", "Noto Sans TC", sans-serif'
export const CHART_GRID = '#EEF0ED'
export const CHART_TEXT = '#646B65'

export const TYPE_LABELS: Record<string, string> = {
  text: '文字',
  sticker: '貼圖',
  image: '圖片',
  video: '影片',
  audio: '語音',
  file: '檔案',
  location: '位置',
}

// 圖表資料色規則：資料一律用布面深綠（群組本身），燙金只標最值得看的那一點；
// 原子筆藍保留給可點擊的介面元素，不用在資料上。
export const CHART_INK = '#1E3A2F'
export const CHART_INK_FILL = 'rgba(30,58,47,0.07)'
export const CHART_FOIL = '#B8943A'
export const CHART_MUTED = '#C5CAC4'

/** 每根柱子的顏色：最大值燙金，其餘深綠 */
export function peakColors(values: number[]): string[] {
  const max = Math.max(...values)
  return values.map(v => (v === max && max > 0 ? CHART_FOIL : CHART_INK))
}
