// 稀有度 5 階權威清單。line 是該階的印刷加工主色（紀念章外框、LINE 卡片）：
// 普通灰（平印）→ 稀有原子筆藍（壓紋）→ 極稀有綠（燙綠箔）→ 史詩燙金 → 傳說印章紅（鐳射箔）。
export type RarityKey = 'common' | 'rare' | 'super_rare' | 'epic' | 'legendary'

export interface RarityDef {
  key: RarityKey
  zh: string
  emoji: string
  order: number
  card: string
  icon: string
  name: string
  pill: string
  date: string
  dot: string
  line: string
}

export const RARITY: Record<RarityKey, RarityDef> = {
  common: {
    key: 'common', zh: '普通', emoji: '', order: 1, line: '#8C938C',
    card: 'bg-white border-slate-200',
    icon: 'bg-white text-slate-600',
    name: 'text-slate-900',
    pill: 'text-slate-600 border border-slate-300',
    date: 'text-slate-500',
    dot: 'bg-slate-400',
  },
  rare: {
    key: 'rare', zh: '稀有', emoji: '', order: 2, line: '#2346A0',
    card: 'bg-white border-slate-200',
    icon: 'bg-white text-brand-700',
    name: 'text-slate-900',
    pill: 'text-brand-700 border border-brand-500',
    date: 'text-slate-500',
    dot: 'bg-brand-500',
  },
  super_rare: {
    key: 'super_rare', zh: '極稀有', emoji: '', order: 3, line: '#2E7D4F',
    card: 'bg-white border-slate-200',
    icon: 'bg-white text-success-700',
    name: 'text-slate-900',
    pill: 'text-success-700 border border-success-500',
    date: 'text-slate-500',
    dot: 'bg-success-500',
  },
  epic: {
    key: 'epic', zh: '史詩', emoji: '', order: 4, line: '#B8943A',
    card: 'bg-white border-slate-200',
    icon: 'bg-white text-accent-700',
    name: 'text-slate-900',
    pill: 'text-slate-900 bg-accent-400 border border-accent-400',
    date: 'text-slate-500',
    dot: 'bg-accent-400',
  },
  legendary: {
    key: 'legendary', zh: '傳說', emoji: '', order: 5, line: '#B8332A',
    card: 'bg-white border-danger-500',
    icon: 'bg-white text-danger-700',
    name: 'text-slate-900',
    pill: 'text-white bg-danger-500 border border-danger-500',
    date: 'text-slate-500',
    dot: 'bg-danger-500',
  },
}

export function rarityOf(key: string | null | undefined): RarityDef {
  return (key && RARITY[key as RarityKey]) || RARITY.common
}
