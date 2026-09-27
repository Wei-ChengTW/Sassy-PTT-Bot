// 旅程狀態：DB 只有 planning / ended，「進行中」要看日期。
// 已按結束 → 已結束；開始日還沒到 → 規劃中；開始了但還沒按結束 → 進行中。
export type TripPhase = 'ended' | 'upcoming' | 'ongoing'

export function tripPhase(t: { status?: string; start_date?: number | null }): TripPhase {
  if (t.status === 'ended') return 'ended'
  if (t.start_date && t.start_date > Date.now() / 1000) return 'upcoming'
  return 'ongoing'
}

export const PHASE_LABEL: Record<TripPhase, string> = {
  ended: '已結束',
  upcoming: '規劃中',
  ongoing: '進行中',
}
