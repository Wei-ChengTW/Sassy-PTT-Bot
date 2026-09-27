// 同分同名次、不跳號（1,1,2）：rows 須已依分數由高到低排好，key 相同視為同分。
export function competitionRanks<T>(rows: T[], key: (r: T) => unknown): number[] {
  const ranks: number[] = []
  rows.forEach((r, i) => {
    if (i === 0) ranks.push(1)
    else ranks.push(key(r) === key(rows[i - 1]) ? ranks[i - 1] : ranks[i - 1] + 1)
  })
  return ranks
}

export function medal(rank: number): string {
  return ['🥇', '🥈', '🥉'][rank - 1] || String(rank)
}
