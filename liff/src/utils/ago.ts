// 距今多久（以台灣日曆日計）：今天／昨天／N 天前／N 週前／N 個月前／N 年前。
// ts 單位為秒；傳入毫秒請先 / 1000。
export function ago(ts: number | null | undefined, now = Date.now()): string {
  if (!ts) return ''
  const day = 86400000
  const start = (ms: number) => { const d = new Date(ms); d.setHours(0, 0, 0, 0); return d.getTime() }
  const days = Math.round((start(now) - start(ts * 1000)) / day)
  if (days < 0) return ''
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 14) return `${days} 天前`
  if (days < 60) return `${Math.floor(days / 7)} 週前`
  const then = new Date(ts * 1000)
  const cur = new Date(now)
  const months = (cur.getFullYear() - then.getFullYear()) * 12 + cur.getMonth() - then.getMonth()
  if (months < 12) return `${Math.max(2, months)} 個月前`
  const years = Math.floor(months / 12)
  const rest = months % 12
  return rest >= 6 ? `${years} 年半前` : `${years} 年前`
}

/** 旅行結束（或開始）距今多久；未結束回空字串 */
export function tripAgo(t: { status?: string; start_date?: number | null; end_date?: number | null }): string {
  if (t.status !== 'ended') return ''
  return ago(t.end_date || t.start_date)
}
