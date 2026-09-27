// 各區塊的識別色（目前只用在「更多」選單的圖示）：群組數據、旅行回憶、個人。
export type LineKey = 'data' | 'trip' | 'people'

export const LINE_COLORS: Record<LineKey, string> = {
  data: '#2346A0',
  trip: '#9A7040',
  people: '#2E7D4F',
}
