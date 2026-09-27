<template>
  <div>
    <div class="flex items-baseline gap-2 flex-wrap">
      <span class="line-dot shrink-0 self-center" aria-hidden="true" />
      <h2 class="font-bold text-[15px] text-slate-900">{{ board.title }}</h2>
      <span v-if="board.sparse" class="text-[11px] px-1.5 py-px rounded border border-accent-400 text-accent-700">
        資料量少 · 僅供參考
      </span>
    </div>
    <p class="text-xs text-slate-500 mt-1 mb-3 pl-[22px]">{{ board.subtitle }}</p>

    <!-- 雷達圖（全能王） -->
    <BaseCard v-if="board.variant === 'radar'" class="p-4">
      <div v-if="radarData" class="max-w-xs mx-auto">
        <Radar :data="radarData" :options="radarOptions" />
      </div>
      <div v-else class="py-6 text-xs text-slate-500 text-center">尚無足夠資料</div>
    </BaseCard>

    <!-- 排名（rank / score） -->
    <template v-else>
      <RankList v-if="board.rows.length" :rows="rankRows" :ranks="ranks">
        <template #detail="{ row, tone }">
          <span v-if="row.detail">{{ row.detail }}</span>
          <span v-if="row.breakdown" class="inline-flex flex-wrap gap-x-2" :class="row.detail ? 'ml-2' : ''">
            <span v-for="(v, k) in row.breakdown" :key="k">
              {{ k }} <span class="font-num" :class="tone === 'cover' ? 'text-white' : 'text-slate-700'">{{ v }}</span>
            </span>
          </span>
        </template>
      </RankList>
      <BaseCard v-else class="px-4 py-6 text-xs text-slate-500 text-center">
        尚無 {{ board.title }} 資料
      </BaseCard>

      <!-- highlight -->
      <div v-if="board.highlight" class="mt-2 px-3.5 py-3 rounded-xl border border-accent-200 bg-accent-50">
        <p class="text-xs text-accent-700">{{ board.highlight.label }}</p>
        <p class="text-sm text-slate-900 flex items-center justify-between mt-0.5">
          <span class="font-bold">{{ board.highlight.name }}</span>
          <span class="font-num text-[17px] font-semibold">{{ board.highlight.value_str }}</span>
        </p>
        <p v-if="board.highlight.note" class="text-xs text-slate-600 mt-0.5 truncate">
          {{ board.highlight.note }}
        </p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend,
} from 'chart.js'
import type { Board } from '@/api/client'
import BaseCard from '@/components/BaseCard.vue'
import RankList from '@/components/RankList.vue'
import { competitionRanks } from '@/utils/rank'
import { CHART_FONT, CHART_TEXT } from '@/constants/chartColors'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps<{ board: Board }>()

// 同分同名次（例：兩人都 9 次 → 都是第 1 名）
const ranks = computed(() => competitionRanks(props.board.rows, (r) => r.value))

const rankRows = computed(() => props.board.rows.map(u => ({
  ...u, id: u.user_id, name: u.name || u.user_id, value: u.value, valueStr: u.value_str,
})))

// 前三名：金、銀、銅
const RADAR_COLORS = ['#B8943A', '#8C938C', '#B07A48']

const radarData = computed(() => {
  const top = props.board.rows.filter(r => r.axes).slice(0, 3)
  if (!top.length) return null
  const labels = Object.keys(top[0].axes || {})
  return {
    labels,
    datasets: top.map((u, i) => ({
      label: u.name || u.user_id,
      data: labels.map(l => (u.axes || {})[l] ?? 0),
      backgroundColor: RADAR_COLORS[i] + '1A',
      borderColor: RADAR_COLORS[i],
      borderWidth: 2,
      pointBackgroundColor: RADAR_COLORS[i],
    })),
  }
})

const radarOptions = {
  responsive: true,
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: { display: false },
      pointLabels: { font: { size: 11, family: CHART_FONT }, color: CHART_TEXT },
    },
  },
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { font: { size: 11, family: CHART_FONT }, color: CHART_TEXT, boxWidth: 10, padding: 10 },
    },
  },
}
</script>
