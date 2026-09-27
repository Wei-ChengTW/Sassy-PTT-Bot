<template>
  <div>
    <PageSign :title="data ? userName : '個人成就檔案'" en="Member Page" line="people">
      <template v-if="data" #action>
        <div class="w-14 h-14 rounded-full overflow-hidden bg-slate-700 flex items-center justify-center border-[3px] border-foil">
          <img v-if="userAvatar" :src="userAvatar" :alt="userName" class="w-full h-full object-cover" />
          <svg v-else class="w-7 h-7 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.5 20.1a7.5 7.5 0 0115 0" /></svg>
        </div>
      </template>
      <template v-if="data">個人成就檔案 · 首度發言：{{ firstSeenText }}</template>
      <template v-if="data" #figures>
        <div class="grid grid-cols-2 gap-px bg-white/15 border border-white/15 rounded-md overflow-hidden">
          <StatCard tone="cover" label="總發言量" :value="data.summary.total" />
          <StatCard tone="cover" label="活躍天數" :value="data.summary.active_days" />
          <StatCard tone="cover" label="平均日發言" :value="data.summary.avg_per_day" />
          <StatCard
            tone="cover"
            label="平均情緒指數"
            :value="data.avg_sentiment != null ? (data.avg_sentiment >= 0 ? '+' : '') + data.avg_sentiment.toFixed(2) : 'N/A'"
          />
        </div>
      </template>
    </PageSign>

    <div v-if="loading" class="space-y-4">
      <!-- Skeleton header -->
      <div class="flex items-center gap-3.5 bg-white rounded-xl p-4 border border-slate-100">
        <div class="skeleton w-14 h-14 rounded-full shrink-0" />
        <div class="flex-1 space-y-2">
          <div class="skeleton h-5 w-28 rounded-full" />
          <div class="skeleton h-3 w-40 rounded-full" />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div v-for="i in 4" :key="i" class="bg-white rounded-xl p-4 border border-slate-100">
          <div class="skeleton h-8 w-14 rounded mb-2" />
          <div class="skeleton h-3 w-16 rounded-full" />
        </div>
      </div>
    </div>

    <EmptyState
      v-else-if="error"
      title="無法載入個人資料"
      :description="error"
    />

    <div v-else-if="data">
      <!-- Summary cards -->

      <!-- 聊天人格 -->
      <template v-if="data.personality && data.personality.length">
        <div>
          <SectionHeader title="聊天人格特質" class="!mt-0" />
          <BaseCard class="px-4 divide-y divide-slate-100">
            <div v-for="(p, i) in data.personality" :key="i" class="flex items-start gap-3 py-3">
              <span class="line-dot shrink-0 mt-2" aria-hidden="true" />
              <div class="min-w-0">
                <p class="text-[15px] font-bold text-slate-900">{{ p.tag }}</p>
                <p class="text-[13px] text-slate-600 mt-0.5">{{ p.reason }}</p>
              </div>
            </div>
          </BaseCard>
        </div>
      </template>

      <!-- 訊息類型分佈 -->
      <div>
        <SectionHeader title="訊息類型偏好" />
        <BaseCard class="p-4">
          <Bar :data="typeBarData" :options="barOptions" style="max-height:180px" />
        </BaseCard>
      </div>

      <!-- 活躍時段分佈 -->
      <div>
        <SectionHeader title="時段活躍度" />
        <BaseCard class="p-4">
          <div class="grid grid-cols-4 divide-x divide-slate-200 text-center">
            <div v-for="slot in slotList" :key="slot.key" class="px-1">
              <p class="font-num text-xl font-semibold text-slate-900">{{ data.time_slots[slot.key] }}</p>
              <p class="text-[11px] text-slate-500 mt-0.5">{{ slot.label }}</p>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- 24h 分佈 -->
      <div>
        <SectionHeader title="24 小時作息分佈" />
        <BaseCard class="p-4">
          <Bar :data="hourlyBarData" :options="hourlyOptions" style="max-height:160px" />
        </BaseCard>
      </div>

      <!-- 常聊話題 -->
      <div>
        <SectionHeader title="常聊話題詞彙" />
        <BaseCard class="overflow-hidden">
          <div class="divide-y divide-slate-100">
            <div v-for="t in data.top_topics" :key="t.topic"
                 class="flex items-center px-4 py-3">
              <span class="flex-1 text-sm font-bold text-slate-900">{{ t.topic }}</span>
              <span class="font-num text-[15px] font-semibold text-slate-900">{{ t.count }}<span class="font-sans text-xs font-normal text-slate-500 ml-1">次</span></span>
            </div>
            <div v-if="!data.top_topics.length" class="px-4 py-6 text-sm text-slate-500 text-center">
              尚無常聊話題資料
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- 里程碑 -->
      <template v-if="milestones && milestones.total">
        <div>
          <SectionHeader title="個人里程碑榮譽" />
          <!-- 獎狀：累積總量為主角，第 N 則達成是紀念戳記 -->
          <div class="sign rounded-xl px-4 pt-4 pb-4 text-white">
            <p class="text-xs text-[#D6B872]">累積發言總量</p>
            <p class="font-num text-[40px] leading-none font-semibold text-[#E6D09A] mt-1">
              {{ milestones.total.toLocaleString() }}<span class="font-sans text-sm font-normal text-[#C9D3CC] ml-1.5">則</span>
            </p>
            <div class="foil-rule w-12 mt-3.5 opacity-80" aria-hidden="true" />
            <div v-if="milestones.nth" class="flex items-center gap-3 mt-3">
              <span class="w-9 h-9 rounded-full border-2 border-[#C6A252] flex items-center justify-center shrink-0" aria-hidden="true">
                <svg class="w-4 h-4 text-[#E6D09A]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.4 6.7 19.1l1-5.8L3.5 9.2l5.9-.9L12 3z" /></svg>
              </span>
              <div class="min-w-0">
                <p class="text-sm font-bold">第 <span class="font-num">{{ milestones.nth.n.toLocaleString() }}</span> 則達成</p>
                <p class="text-xs text-[#C9D3CC]"><span class="font-num">{{ fmtMs(milestones.nth.timestamp) }}</span> · {{ ago(milestones.nth.timestamp / 1000) }}</p>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 mt-2">
            <div v-if="milestones.busiest_day" class="medal--gold relative overflow-hidden rounded-xl border px-3.5 pt-3.5 pb-3">
              <span class="medal-foil" aria-hidden="true" />
              <p class="text-xs text-accent-700">單日最高紀錄</p>
              <p class="font-num text-[26px] leading-none font-semibold text-slate-900 mt-1.5">{{ milestones.busiest_day.count }}<span class="font-sans text-xs font-normal text-slate-500 ml-1">則</span></p>
              <p class="text-[11px] text-slate-600 mt-1.5 font-num">{{ milestones.busiest_day.date }}</p>
            </div>
            <div v-if="milestones.longest_streak" class="medal--silver relative overflow-hidden rounded-xl border px-3.5 pt-3.5 pb-3">
              <span class="medal-foil" aria-hidden="true" />
              <p class="text-xs text-slate-600">最長連續發言</p>
              <p class="font-num text-[26px] leading-none font-semibold text-slate-900 mt-1.5">{{ milestones.longest_streak.days }}<span class="font-sans text-xs font-normal text-slate-500 ml-1">天</span></p>
              <p class="text-[11px] text-slate-600 mt-1.5 font-num leading-snug">{{ milestones.longest_streak.start }}<br />～{{ milestones.longest_streak.end }}</p>
            </div>
          </div>
        </div>
      </template>

      <!-- 成長曲線 -->
      <template v-if="hasGrowth">
        <div>
          <SectionHeader title="發言成長軌跡" subtitle="累積訊息總數" />
          <BaseCard class="p-4">
            <Line :data="growthLineData" :options="lineOptions" style="max-height:180px" />
          </BaseCard>
        </div>
      </template>

      <!-- 情緒曲線 -->
      <template v-if="hasSentiment">
        <div>
          <SectionHeader title="每日情緒起伏" subtitle="正負向平均" />
          <BaseCard class="p-4">
            <Line :data="sentimentLineData" :options="lineOptions" style="max-height:180px" />
          </BaseCard>
        </div>
      </template>

      <!-- 社交圈 -->
      <template v-if="socialCircle.length">
        <div>
          <SectionHeader title="最常互動的夥伴" />
          <BaseCard class="overflow-hidden">
            <div class="divide-y divide-slate-100">
              <div v-for="p in socialCircle" :key="p.user_id" class="px-4 py-3.5">
                <div class="flex items-center">
                  <span class="flex-1 text-[15px] font-bold text-slate-900 truncate">{{ p.name }}</span>
                  <span class="font-num text-[17px] font-semibold text-slate-900">
                    {{ p.count }}<span class="font-sans text-xs font-normal text-slate-500 ml-1">次互動</span>
                  </span>
                </div>
                <div v-if="p.shared_topics.length" class="flex flex-wrap gap-1 mt-2">
                  <span v-for="t in p.shared_topics" :key="t"
                        class="text-xs px-1.5 py-px rounded border border-slate-200 text-slate-600">
                    {{ t }}
                  </span>
                </div>
              </div>
            </div>
          </BaseCard>
        </div>
      </template>

      <!-- 徽章收藏牆 -->
      <template v-if="badges.length">
        <div>
          <SectionHeader title="勳章收藏牆" :subtitle="`已獲得 ${badges.length} 枚`" />
          <BaseCard class="p-4">
            <div class="grid grid-cols-4 gap-3">
              <div v-for="b in badges" :key="b.badge_id || b.trip_id"
                   class="flex flex-col items-center text-center">
                <RaritySeal :rarity="b.badge_rarity" :emoji="b.badge_emoji" :size="56" />
                <p class="text-[11px] font-bold text-slate-700 mt-1.5 line-clamp-2 leading-tight">
                  {{ (b.badge_name || b.title || b.location || '').split('・')[0] }}
                </p>
              </div>
            </div>
          </BaseCard>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import { ago } from '@/utils/ago'
import RaritySeal from '@/components/RaritySeal.vue'
import { TYPE_COLORS, TYPE_LABELS, CHART_INK, CHART_INK_FILL, peakColors } from '@/constants/chartColors'
import { ref, computed, onMounted } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, Filler, Tooltip, Legend,
} from 'chart.js'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useRoute } from 'vue-router'
import { useRefreshOnAnalysis } from '@/composables/useRefreshOnAnalysis'
import { rarityOf } from '@/constants/rarity'
import BaseCard from '@/components/BaseCard.vue'
import StatCard from '@/components/StatCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SectionHeader from '@/components/SectionHeader.vue'

ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, Filler, Tooltip, Legend,
)

const auth = useAuthStore()
const route = useRoute()
// /profile 看自己；/profile/:userId 看指定成員（群組裡的個人戰績卡會帶 user_id）
const targetId = computed(() => (route.params.userId as string) || auth.userId)
const isSelf = computed(() => targetId.value === auth.userId)
const data = ref<any>(null)
const loading = ref(true)
const error = ref('')

const slotList = [
  { key: 'night', label: '深夜 0-4' },
  { key: 'morning', label: '早晨 5-8' },
  { key: 'daytime', label: '白天 9-17' },
  { key: 'evening', label: '晚上 18-23' },
]



const typeBarData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const breakdown = data.value.type_breakdown
  return {
    labels: breakdown.map((d: any) => TYPE_LABELS[d.type] || d.type),
    datasets: [{
      label: '訊息數',
      data: breakdown.map((d: any) => d.count),
      backgroundColor: breakdown.map((d: any) => TYPE_COLORS[d.type] || '#8C938C'),
      borderRadius: 2,
    }],
  }
})

const barOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { grid: { color: '#EEF0ED' } },
  },
}

const hourlyBarData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const h = data.value.hourly_distribution
  return {
    labels: h.map((d: any) => `${d.hour}h`),
    datasets: [{
      data: h.map((d: any) => d.count),
      backgroundColor: peakColors(h.map((d: any) => d.count)),
      borderRadius: 2,
    }],
  }
})

const hourlyOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { grid: { color: '#EEF0ED' } },
  },
}

const lineOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  elements: { point: { radius: 0 } },
  scales: {
    x: { ticks: { maxTicksLimit: 6 }, grid: { display: false } },
    y: { grid: { color: '#EEF0ED' } },
  },
}

const growthLineData = computed(() => {
  const g = data.value?.growth || []
  return {
    labels: g.map((d: any) => d.date),
    datasets: [{
      data: g.map((d: any) => d.cumulative),
      borderColor: CHART_INK,
      backgroundColor: CHART_INK_FILL,
      fill: true,
      tension: 0,
      borderWidth: 2.5,
    }],
  }
})

const sentimentLineData = computed(() => {
  const s = data.value?.sentiment_series || []
  return {
    labels: s.map((d: any) => d.date),
    datasets: [{
      data: s.map((d: any) => d.avg_sentiment),
      borderColor: CHART_INK,
      backgroundColor: CHART_INK_FILL,
      fill: true,
      tension: 0,
      borderWidth: 2.5,
    }],
  }
})

function fmtMs(ts: number | null | undefined): string {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

const milestones = computed(() => data.value?.milestones || null)
const socialCircle = computed(() => data.value?.social_circle || [])
const badges = computed(() => data.value?.badges || [])
const hasGrowth = computed(() => (data.value?.growth || []).length > 1)
const hasSentiment = computed(() => (data.value?.sentiment_series || []).length > 1)

const userName = computed(() => {
  if (!isSelf.value) return data.value?.display_name || '群組成員'
  return auth.displayName || data.value?.display_name || '群組成員'
})

const userAvatar = computed(() => {
  return isSelf.value ? auth.pictureUrl || '' : ''
})

const firstSeenText = computed(() => {
  const ts = data.value?.summary?.first_seen
  if (!ts) return '近期'
  const d = new Date(ts)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
})

async function loadProfile() {
  try { data.value = await api.profile(targetId.value) }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
}

onMounted(async () => {
  await loadProfile()
  loading.value = false
})
useRefreshOnAnalysis(loadProfile)
</script>
