<template>
  <div>
    <PageSign :title="data?.group_name || '群組儀表板'" en="Class Record">
      <template v-if="data?.group_name">群組儀表板</template>
      <template v-if="data" #figures>
        <div class="grid grid-cols-2 gap-px bg-white/15 border border-white/15 rounded-md overflow-hidden">
          <StatCard tone="cover" label="總訊息量" :value="data.summary.total_messages" />
          <StatCard tone="cover" label="群組成員" :value="data.summary.member_count" />
          <StatCard tone="cover" label="預計進行的行程" :value="data.summary.active_trips" />
          <StatCard tone="cover" label="活躍天數" :value="data.summary.active_days" />
        </div>
      </template>
    </PageSign>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="space-y-6">
      <div class="grid grid-cols-2 gap-px bg-slate-200 border border-slate-200 rounded-xl overflow-hidden">
        <div v-for="i in 4" :key="i" class="bg-white px-4 py-3.5">
          <div class="skeleton h-7 w-20 rounded mb-2" />
          <div class="skeleton h-3 w-14 rounded" />
        </div>
      </div>
      <div class="bg-white rounded-xl border border-slate-200 px-4 divide-y divide-slate-100">
        <div v-for="i in 5" :key="i" class="flex items-center py-3 gap-3">
          <div class="skeleton w-7 h-7 rounded-md" />
          <div class="skeleton flex-1 h-4 rounded" />
          <div class="skeleton w-12 h-4 rounded" />
        </div>
      </div>
    </div>

    <!-- Error State -->
    <EmptyState
      v-else-if="error"
      title="無法載入資料"
      :description="error"
    />

    <!-- Main Content -->
    <div v-else-if="data">
      <!-- 到站看板：Top 話癆 -->
      <SectionHeader title="Top 話癆榜" class="!mt-0">
        <template #action>
          <router-link to="/leaderboard" class="text-xs font-medium text-brand-600 py-1">完整排行 →</router-link>
        </template>
      </SectionHeader>
      <BaseCard class="overflow-hidden">
        <ol class="divide-y divide-slate-100">
          <li
            v-for="(u, i) in data.top_users.slice(0, 5)"
            :key="u.user_id"
            class="flex items-center px-3.5 py-3 gap-3"
            :class="topRanks[i] === 1 ? 'bg-accent-50' : ''"
          >
            <RankChip :rank="topRanks[i]" />
            <div class="flex-1 min-w-0">
              <p class="text-[15px] font-bold text-slate-900 truncate">{{ u.user_name || u.user_id }}</p>
              <p v-if="data.summary.total_messages" class="text-xs text-slate-500 mt-0.5">
                佔全群 <span class="font-num text-slate-700">{{ (u.total / data.summary.total_messages * 100).toFixed(1) }}%</span>
              </p>
            </div>
            <span class="font-num text-lg font-semibold text-slate-900">
              {{ u.total.toLocaleString() }}<span class="font-sans text-xs font-normal text-slate-500 ml-1">則</span>
            </span>
          </li>
        </ol>
      </BaseCard>

      <!-- 群組健康度 -->
      <template v-if="data.health">
        <div>
          <SectionHeader title="群組健康指數" />
          <BaseCard class="p-4">
            <div class="flex items-center gap-4">
              <div class="shrink-0 pl-1">
                <p class="font-num text-[44px] font-semibold text-slate-900 leading-none">
                  {{ data.health.overall }}<span class="text-base text-slate-500 font-medium">/100</span>
                </p>
                <p class="text-xs text-slate-500 mt-1.5">綜合分數</p>
              </div>
              <div class="flex-1 min-w-0" style="max-height:180px">
                <Radar :data="healthRadarData" :options="healthRadarOptions" style="max-height:180px" />
              </div>
            </div>
            <ul v-if="data.health.suggestions?.length" class="mt-4 pt-3 border-t border-slate-100 space-y-1.5">
              <li v-for="s in data.health.suggestions" :key="s" class="text-xs text-slate-600 flex items-start gap-2">
                <span class="w-1.5 h-1.5 mt-1.5 rounded-full bg-brand-500 shrink-0" aria-hidden="true" />
                <span>{{ s }}</span>
              </li>
            </ul>
          </BaseCard>
        </div>
      </template>

      <!-- 活躍時段熱力圖 -->
      <template v-if="data.heatmap && data.heatmap.length">
        <div>
          <SectionHeader title="群組活躍時段分佈" />
          <BaseCard class="p-4">
            <HeatmapChart :data="data.heatmap" :date-data="data.recent_date_heatmap" />
          </BaseCard>
        </div>
      </template>

      <!-- 每週趨勢對比 -->
      <template v-if="weekly && weekly.weeks.length">
        <div>
          <SectionHeader title="每週發言趨勢" />
          <BaseCard class="p-4">
            <div class="flex items-baseline gap-2 mb-3">
              <span class="font-num text-[28px] font-semibold text-slate-900 leading-none">
                {{ weekly.this_week.toLocaleString() }}
              </span>
              <span class="text-xs text-slate-500">本週至今</span>
              <span class="text-xs text-slate-500">· 進行中，第 <span class="font-num">{{ weekDay }}</span> 天</span>
              <span class="text-xs text-slate-500 ml-auto">
                上週 {{ weekly.last_week.toLocaleString() }}
              </span>
            </div>
            <Bar :data="weeklyBarData" :options="weeklyOptions" style="max-height:160px" />
          </BaseCard>
        </div>
      </template>

      <!-- 月成長趨勢 -->
      <template v-if="data.monthly_trend && data.monthly_trend.length">
        <div>
          <SectionHeader title="月份成長軌跡" />
          <BaseCard class="p-4">
            <Line :data="monthlyLineData" :options="monthlyOptions" style="max-height:180px" />
          </BaseCard>
          <div v-if="latestGrowth !== null" class="mt-2 text-xs text-slate-500 px-1 flex items-center justify-between">
            <span>最近一個月相對前月：</span>
            <span
              class="font-num text-sm font-semibold"
              :class="latestGrowth >= 0 ? 'text-success-600' : 'text-danger-600'"
            >
              {{ latestGrowth >= 0 ? '成長 ↑' : '減少 ↓' }} {{ Math.abs(latestGrowth) }}%
            </span>
          </div>
        </div>
      </template>

      <!-- 季節性 -->
      <template v-if="data.seasonality && data.seasonality.length">
        <div>
          <SectionHeader title="季節月份合計" />
          <BaseCard class="p-4">
            <Bar :data="seasonBarData" :options="seasonOptions" style="max-height:160px" />
          </BaseCard>
        </div>
      </template>

      <!-- 旅行類型分佈 -->
      <template v-if="data.trip_type_distribution && data.trip_type_distribution.length">
        <div>
          <SectionHeader title="旅行類型分佈" />
          <BaseCard class="p-4 flex flex-wrap gap-2">
            <span
              v-for="d in data.trip_type_distribution"
              :key="d.type"
              class="inline-flex items-center gap-1.5 rounded-md border border-trip-500 px-2.5 py-1 text-xs text-slate-800"
            >
              <span>{{ labelFor(d.type) }}</span>
              <span class="font-num text-trip-700 font-semibold">{{ d.count }}</span>
            </span>
          </BaseCard>
        </div>
      </template>

      <!-- Message type breakdown -->
      <div>
        <SectionHeader title="訊息類型分佈" />
        <BaseCard class="overflow-hidden">
          <div class="divide-y divide-slate-100">
            <div
              v-for="t in data.type_distribution"
              :key="t.type"
              class="flex items-center px-4 py-3 gap-3"
            >
              <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ background: TYPE_COLORS[t.type] || '#8C938C' }" />
              <span class="flex-1 text-sm text-slate-800">{{ TYPE_LABELS[t.type] || t.type }}</span>
              <span class="font-num text-[15px] font-semibold text-slate-900">
                {{ t.count.toLocaleString() }}
              </span>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Bar, Line, Radar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, RadialLinearScale,
  BarElement, PointElement, LineElement, Tooltip, Legend, Filler,
} from 'chart.js'
import { api } from '@/api/client'
import { competitionRanks } from '@/utils/rank'
import { useRefreshOnAnalysis } from '@/composables/useRefreshOnAnalysis'
import { labelFor } from '@/constants/tripTypes'
import { TYPE_COLORS, TYPE_LABELS, CHART_INK, CHART_INK_FILL, CHART_FOIL, peakColors } from '@/constants/chartColors'
import HeatmapChart from '@/components/HeatmapChart.vue'
import BaseCard from '@/components/BaseCard.vue'
import StatCard from '@/components/StatCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SectionHeader from '@/components/SectionHeader.vue'
import PageSign from '@/components/PageSign.vue'
import RankChip from '@/components/RankChip.vue'

ChartJS.register(CategoryScale, LinearScale, RadialLinearScale, BarElement, PointElement, LineElement, Tooltip, Legend, Filler)

const data = ref<any>(null)
// 同分同名次
const topRanks = computed(() => competitionRanks((data.value?.top_users || []).slice(0, 5), (u: any) => u.total))
const loading = ref(true)
const error = ref('')

const MONTH_LABELS = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']

const monthlyLineData = computed(() => {
  if (!data.value?.monthly_trend) return { labels: [], datasets: [] }
  const rows = data.value.monthly_trend
  return {
    labels: rows.map((r: any) => r.month),
    datasets: [{
      label: '訊息數',
      data: rows.map((r: any) => r.count),
      borderColor: CHART_INK,
      backgroundColor: CHART_INK_FILL,
      fill: true,
      tension: 0,
      borderWidth: 2,
      // 只在最高的月份放一顆金點
      pointRadius: peakPoint(rows.map((r: any) => r.count), 5),
      pointBackgroundColor: CHART_FOIL,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointHoverRadius: 4,
      pointHoverBackgroundColor: CHART_INK,
    }],
  }
})

const monthlyOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { grid: { color: '#EEF0ED' } },
  },
}

const latestGrowth = computed(() => {
  const rows = data.value?.monthly_trend
  if (!rows || !rows.length) return null
  return rows[rows.length - 1].growth_rate_percent
})

const seasonBarData = computed(() => {
  if (!data.value?.seasonality) return { labels: [], datasets: [] }
  const map: Record<number, number> = {}
  data.value.seasonality.forEach((r: any) => { map[r.month] = r.count })
  return {
    labels: MONTH_LABELS,
    datasets: [{
      data: MONTH_LABELS.map((_, i) => map[i + 1] || 0),
      backgroundColor: peakColors(MONTH_LABELS.map((_, i) => map[i + 1] || 0)),
      borderRadius: 2,
    }],
  }
})

const seasonOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: false, font: { size: 10 } } },
    y: { grid: { color: '#EEF0ED' } },
  },
}

const HEALTH_LABELS: Record<string, string> = {
  activity: '活躍度', diversity: '多樣性', sentiment: '正面情緒', participation: '參與度',
}

const healthRadarData = computed(() => {
  const h = data.value?.health
  if (!h) return { labels: [], datasets: [] }
  const keys = ['activity', 'diversity', 'sentiment', 'participation']
    .filter((k) => h[k] !== null && h[k] !== undefined)
  return {
    labels: keys.map((k) => HEALTH_LABELS[k]),
    datasets: [{
      data: keys.map((k) => h[k]),
      borderColor: CHART_INK,
      backgroundColor: 'rgba(30,58,47,0.10)',
      pointBackgroundColor: CHART_INK,
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: CHART_INK,
      borderWidth: 2,
    }],
  }
})

const healthRadarOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: { stepSize: 25, display: false },
      grid: { color: '#EEF0ED' },
      angleLines: { color: '#EEF0ED' },
      pointLabels: { font: { size: 11, family: '"Noto Sans TC", sans-serif' }, color: '#646B65' },
    },
  },
}

const weekly = computed(() => data.value?.weekly_trend || null)

// 已完成各週中最高的那一週（本週未完成，不參與比較）
const pastPeak = computed(() => {
  const weeks = weekly.value?.weeks || []
  const past = weeks.slice(0, -1).map((r: any) => r.count)
  return past.length ? past.indexOf(Math.max(...past)) : -1
})

// 本週第幾天（週一為第 1 天）
const weekDay = ((new Date().getDay() + 6) % 7) + 1

function peakPoint(values: number[], r: number) {
  const max = Math.max(...values)
  return values.map(v => (v === max && max > 0 ? r : 0))
}

const weeklyBarData = computed(() => {
  const w = weekly.value
  if (!w) return { labels: [], datasets: [] }
  return {
    labels: w.weeks.map((r: any, i: number) => {
      const label = r.week.split('-')[1] ? `W${r.week.split('-')[1]}` : r.week
      return i === w.weeks.length - 1 ? [label, '進行中'] : label
    }),
    datasets: [{
      data: w.weeks.map((r: any) => r.count),
      // 已完成的週：深綠，最高那週燙金；本週（未完成）：淡綠外框
      backgroundColor: w.weeks.map((_: any, i: number) => {
        if (i === w.weeks.length - 1) return 'rgba(30,58,47,0.08)'
        return pastPeak.value === i ? CHART_FOIL : CHART_INK
      }),
      borderColor: w.weeks.map((_: any, i: number) => (i === w.weeks.length - 1 ? CHART_INK : 'transparent')),
      borderWidth: 1.5,
      borderRadius: 2,
    }],
  }
})

const weeklyOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: false, font: { size: 10 } } },
    y: { grid: { color: '#EEF0ED' } },
  },
}

async function loadDashboard() {
  try { data.value = await api.dashboard() }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
}

onMounted(async () => {
  await loadDashboard()
  loading.value = false
})
useRefreshOnAnalysis(loadDashboard)
</script>
