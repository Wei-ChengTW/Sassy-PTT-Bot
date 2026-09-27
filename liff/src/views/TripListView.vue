<template>
  <div>
    <PageSign title="群組旅行與活動" en="Trips &amp; Events" line="trip">
      <template v-if="isAdmin" #action>
        <router-link
          to="/admin/trips/new"
          class="text-xs font-bold px-3 py-2 rounded-md bg-white text-cloth hover:bg-slate-100 btn-press inline-flex items-center gap-1"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>
          發起旅行
        </router-link>
      </template>
    </PageSign>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-3">
      <div class="skeleton h-8 w-full rounded-full" />
      <div v-for="i in 3" :key="i" class="skeleton h-20 rounded-xl" />
    </div>

    <EmptyState
      v-else-if="error"
      title="載入失敗"
      :description="error"
    />
    <EmptyState
      v-else-if="trips.length === 0"
      title="尚無旅行紀錄"
      description="發起第一場群組旅行或聚會，把回憶記下來。"
    >
      <template #action>
        <router-link
          v-if="isAdmin"
          to="/admin/trips/new"
          class="text-sm font-bold px-4 py-2 rounded-md bg-brand-500 text-white btn-press inline-block"
        >
          立即發起旅行
        </router-link>
      </template>
    </EmptyState>

    <template v-else>
      <!-- 即將出發 / 進行中 -->
      <section v-if="activeTrips.length" class="space-y-2 mb-6">
        <router-link
          v-for="t in activeTrips" :key="t.id" :to="`/trips/${t.id}`"
          class="sign rounded-xl p-4 flex items-center gap-4 text-white btn-press"
        >
          <RaritySeal :rarity="t.rarity" :emoji="t.custom_emoji || t.badge_emoji" :size="60" />
          <div class="flex-1 min-w-0">
            <p class="text-xs text-[#D6B872]">{{ tripPhase(t) === 'upcoming' ? '下一趟' : '進行中' }}</p>
            <p class="text-lg font-black truncate">{{ t.title }}</p>
            <p class="text-xs text-[#C9D3CC] truncate mt-0.5">
              {{ t.location || '群組回憶' }}<template v-if="t.start_date"> · <span class="font-num">{{ fmtRange(t) }}</span></template>
            </p>
          </div>
          <div v-if="countdown(t)" class="text-right shrink-0">
            <p class="text-[11px] text-[#C9D3CC]">{{ countdown(t)!.label }}</p>
            <p class="font-num text-[32px] leading-none font-semibold text-[#E6D09A]">{{ countdown(t)!.n }}</p>
            <p class="text-[11px] text-[#C9D3CC]">天</p>
          </div>
        </router-link>
      </section>

      <!-- 類型過濾 -->
      <div v-if="typeFilters.length" class="mb-4">
        <ChipFilter v-model="activeType" :options="chipOptions" all-label="全部類型" scroll />
      </div>

      <!-- 回憶相簿：兩欄紀念章卡 -->
      <div v-if="pastTrips.length" class="grid grid-cols-2 gap-2">
        <router-link v-for="(t, i) in pastTrips" :key="t.id" :to="`/trips/${t.id}`" class="block">
          <FoilCard
            :rarity="t.rarity" :delay="0.5 + (i % 6) * 0.8"
            class="h-full rounded-xl border bg-white px-3 pt-4 pb-3 flex flex-col items-center text-center touch-pan-y"
            :class="rarityOf(t.rarity).card"
          >
            <RaritySeal :rarity="t.rarity" :emoji="t.custom_emoji || t.badge_emoji" :size="64" />
            <p class="mt-3 text-[15px] leading-snug font-bold text-slate-900 line-clamp-2 relative z-[3]">{{ t.title }}</p>
            <p class="mt-1 text-xs text-slate-600 truncate w-full relative z-[3]">{{ t.location || '群組回憶' }}</p>
            <p v-if="t.start_date" class="text-[11px] text-slate-500 font-num relative z-[3]">{{ fmtRange(t) }}</p>
            <p v-if="tripAgo(t)" class="text-[11px] font-bold text-accent-700 relative z-[3]">{{ tripAgo(t) }}</p>
            <span class="mt-2 text-[11px] px-1.5 py-px rounded font-bold relative z-[3]" :class="rarityOf(t.rarity).pill">
              {{ rarityOf(t.rarity).zh }}
            </span>
          </FoilCard>
        </router-link>
      </div>
      <p v-else-if="!activeTrips.length" class="text-sm text-slate-500 text-center py-8">這個類型還沒有旅行</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import RaritySeal from '@/components/RaritySeal.vue'
import FoilCard from '@/components/FoilCard.vue'
import { tripAgo } from '@/utils/ago'
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api/client'
import { labelFor } from '@/constants/tripTypes'
import { rarityOf } from '@/constants/rarity'
import ChipFilter from '@/components/ChipFilter.vue'
import EmptyState from '@/components/EmptyState.vue'
import { useAuthStore } from '@/stores/auth'
import { tripPhase } from '@/constants/tripStatus'

const auth = useAuthStore()
// 建立旅行頁與 API 皆限管理員（router: /admin/trips/new）
const isAdmin = computed(() => auth.role === 'admin')
const trips = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const activeType = ref('')

const typeFilters = computed(() => {
  const seen = new Set<string>()
  for (const t of trips.value) for (const ty of (t.trip_types || [])) seen.add(ty)
  return [...seen]
})

const chipOptions = computed(() => {
  return typeFilters.value.map((ty) => ({
    value: ty,
    label: labelFor(ty),
    count: trips.value.filter(t => (t.trip_types || []).includes(ty)).length,
  }))
})

const filteredTrips = computed(() =>
  activeType.value
    ? trips.value.filter((t) => (t.trip_types || []).includes(activeType.value))
    : trips.value,
)

onMounted(async () => {
  try { trips.value = await api.trips() }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
  finally { loading.value = false }
})

// 規劃中／進行中放最上面的封面卡；已結束的進相簿（依開始日新到舊）
const activeTrips = computed(() => filteredTrips.value
  .filter(t => tripPhase(t) !== 'ended')
  .sort((a, b) => (a.start_date || 0) - (b.start_date || 0)))
const pastTrips = computed(() => filteredTrips.value
  .filter(t => tripPhase(t) === 'ended')
  .sort((a, b) => (b.start_date || 0) - (a.start_date || 0)))

const DAY = 86400
function countdown(t: any): { label: string; n: number } | null {
  if (!t.start_date) return null
  const now = Date.now() / 1000
  if (tripPhase(t) === 'upcoming') return { label: '還有', n: Math.max(1, Math.ceil((t.start_date - now) / DAY)) }
  return { label: '第', n: Math.floor((now - t.start_date) / DAY) + 1 }
}

function fmtDate(ts: number) {
  const d = new Date(ts * 1000)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}
function fmtRange(t: any) {
  if (!t.start_date) return ''
  if (!t.end_date || t.end_date === t.start_date) return fmtDate(t.start_date)
  const e = new Date(t.end_date * 1000)
  return `${fmtDate(t.start_date)}–${e.getMonth() + 1}/${e.getDate()}`
}
</script>
