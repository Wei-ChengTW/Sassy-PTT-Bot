<template>
  <div>
    <PageSign title="回憶時光軸" en="Memories" line="trip">
      共 <span class="font-num">{{ trips.length }}</span> 段群組記憶
      <span v-if="trips.length"> · <span class="font-num">{{ oldestYear }}–{{ newestYear }}</span></span>
    </PageSign>

    <!-- 稀有度圖例 -->
    <div v-if="trips.length" class="flex flex-wrap gap-x-3.5 gap-y-1.5 mb-2">
      <span v-for="r in legend" :key="r.key" class="inline-flex items-center gap-1.5 text-xs text-slate-600">
        <span class="w-2.5 h-2.5 rounded-full" :style="{ background: r.line }" aria-hidden="true" />
        {{ r.zh }}
        <span class="font-num font-semibold text-slate-900">{{ counts[r.key] || 0 }}</span>
      </span>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-2">
      <div v-for="i in 5" :key="i" class="skeleton h-14 rounded-xl" />
    </div>

    <EmptyState
      v-else-if="error"
      title="載入失敗"
      :description="error"
    />
    <EmptyState
      v-else-if="!trips.length"
      title="尚無回憶紀錄"
      description="發起新的群組旅行與活動，解鎖第一段回憶。"
    />

    <div v-else>
      <section v-for="group in grouped" :key="group.year" class="mt-8 first:mt-6">
        <!-- 年度章節 -->
        <h2 class="flex items-end gap-3 mb-3">
          <span class="font-num text-[40px] leading-none font-semibold text-slate-900">{{ group.year }}</span>
          <span class="flex-1 foil-rule mb-2" aria-hidden="true" />
          <span class="text-xs text-slate-500 mb-0.5"><span class="font-num">{{ group.items.length }}</span> 段</span>
        </h2>
        <ol class="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
          <li v-for="(t, i) in group.items" :key="t.id">
            <FoilCard :rarity="t.rarity" :delay="0.6 + (i % 5) * 1.1"
                      class="flex items-center gap-3 pl-3 pr-1.5 py-2.5 touch-pan-y"
                      :class="t.rarity === 'legendary' ? 'bg-danger-50/50' : t.rarity === 'epic' ? 'bg-accent-50/80' : ''">
            <RaritySeal :rarity="t.rarity" :emoji="t.custom_emoji || t.badge_emoji" :size="40" />
            <div class="flex-1 min-w-0">
              <p class="font-bold text-[15px] truncate text-slate-900">{{ t.title }}</p>
              <p class="text-xs mt-0.5 text-slate-500"><span class="font-num">{{ formatRange(t) }}</span><template v-if="tripAgo(t)"> · <span class="text-accent-700 font-bold">{{ tripAgo(t) }}</span></template></p>
            </div>
            <span class="shrink-0 inline-flex items-center px-1.5 py-px rounded text-[11px] font-bold" :class="rarityOf(t.rarity).pill">
              {{ rarityOf(t.rarity).zh }}
            </span>
            <button
              @click.stop="onQuickShare(t.id)"
              :disabled="sharingId === t.id"
              class="shrink-0 w-10 h-10 flex items-center justify-center rounded-md text-slate-500 hover:text-brand-600 hover:bg-slate-50 disabled:opacity-40 btn-press"
              aria-label="分享這段回憶"
            >
              <svg v-if="sharingId !== t.id" class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 12v7a1 1 0 001 1h14a1 1 0 001-1v-7" />
                <path d="M16 6l-4-4-4 4" />
                <path d="M12 2v14" />
              </svg>
              <svg v-else class="w-[18px] h-[18px] animate-spin text-brand-600" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" stroke-opacity="0.25" />
                <path d="M21 12a9 9 0 00-9-9" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
            </FoilCard>
          </li>
        </ol>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import RaritySeal from '@/components/RaritySeal.vue'
import FoilCard from '@/components/FoilCard.vue'
import { tripAgo } from '@/utils/ago'
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api/client'
import { RARITY, rarityOf } from '@/constants/rarity'
import { buildTripFlex } from '@/utils/flexTripCard'
import { shareFlexMessage } from '@/utils/liffShare'
import { useToast } from '@/composables/useToast'
import EmptyState from '@/components/EmptyState.vue'

const toast = useToast()
const trips = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const sharingId = ref<string | null>(null)

async function onQuickShare(id: string) {
  if (sharingId.value) return
  sharingId.value = id
  try {
    const detail = await api.tripDetail(id)
    const res = await shareFlexMessage(buildTripFlex(detail))
    if (res.success) toast.success('已分享回顧小卡')
    else if (res.mode === 'picker') toast.error('已取消分享')
  } catch (e: any) {
    toast.error(e?.message || '分享失敗，請稍後再試')
  } finally {
    sharingId.value = null
  }
}

const legend = Object.values(RARITY)

const sorted = computed(() =>
  [...trips.value].sort((a, b) => (b.start_date || 0) - (a.start_date || 0)),
)

const counts = computed<Record<string, number>>(() => {
  const c: Record<string, number> = {}
  for (const t of trips.value) {
    const key = rarityOf(t.rarity).key
    c[key] = (c[key] || 0) + 1
  }
  return c
})

const grouped = computed(() => {
  const map = new Map<number, any[]>()
  for (const t of sorted.value) {
    const y = new Date((t.start_date || 0) * 1000).getFullYear()
    if (!map.has(y)) map.set(y, [])
    map.get(y)!.push(t)
  }
  return [...map.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([year, items]) => ({ year, items }))
})

const oldestYear = computed(() =>
  trips.value.length ? Math.min(...trips.value.map((t) => new Date((t.start_date || 0) * 1000).getFullYear())) : '',
)
const newestYear = computed(() =>
  trips.value.length ? Math.max(...trips.value.map((t) => new Date((t.start_date || 0) * 1000).getFullYear())) : '',
)

function fmt(ts: number): string {
  const d = new Date(ts * 1000)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function formatRange(t: any): string {
  const start = fmt(t.start_date)
  if (!t.end_date || t.end_date === t.start_date) return start
  return `${start}–${fmt(t.end_date)}`
}

onMounted(async () => {
  try { trips.value = await api.trips() }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
  finally { loading.value = false }
})
</script>
