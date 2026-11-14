<template>
  <div>
    <PageSign title="榮譽排行榜" en="Class Honors" />

    <!-- Skeleton -->
    <div v-if="loading" class="bg-white rounded-xl border border-slate-200 px-4 divide-y divide-slate-100">
      <div v-for="i in 5" :key="i" class="flex items-center py-3 gap-3">
        <div class="skeleton w-7 h-7 rounded-md" />
        <div class="skeleton flex-1 h-4 rounded" />
        <div class="skeleton w-12 h-4 rounded" />
      </div>
    </div>

    <EmptyState
      v-else-if="error"
      title="無法載入資料"
      :description="error"
    />

    <div v-else-if="data">
      <!-- 徽章成就排行 -->
      <SectionHeader title="徽章成就榜" class="!mt-0">
        <template #action>
          <SegmentedControl
            v-model="badgeSortMode"
            :options="[
              { label: '加權積分', value: 'weighted' },
              { label: '總枚數', value: 'count' }
            ]"
          />
        </template>
      </SectionHeader>
      <p class="text-xs text-slate-500 mb-3 -mt-1" v-if="badgeSortMode === 'weighted'">
        計分規則：傳說 2.0 · 史詩 1.5 · 極稀有 1.0 · 稀有 0.8 · 普通 0.5
      </p>

      <RankList v-if="sortedBadgeRankings.length" :rows="badgeRows" :ranks="badgeRanks"
                :unit="badgeSortMode === 'weighted' ? '分' : '枚'">
        <template #detail="{ row, tone }">
          <span class="inline-flex flex-wrap gap-x-2 gap-y-0.5">
            <span v-for="r in RARITY_COUNTS" :key="r.key" v-show="row[r.key]" class="inline-flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full" :style="{ background: r.line }" aria-hidden="true" />
              {{ r.zh }} <span class="font-num" :class="tone === 'cover' ? 'text-white' : 'text-slate-800'">{{ row[r.key] }}</span>
            </span>
          </span>
        </template>
      </RankList>
      <BaseCard v-else class="px-4 py-8 text-sm text-slate-500 text-center">尚無徽章數據</BaseCard>

      <!-- 發言活躍排行 -->
      <SectionHeader title="發言活躍排行">
        <template #action>
          <SegmentedControl
            v-model="activeMessageFilter"
            :options="[
              { label: '全部', value: 'all' },
              { label: '文字', value: 'text' },
              { label: '貼圖', value: 'sticker' },
              { label: '圖片', value: 'image' }
            ]"
          />
        </template>
      </SectionHeader>

      <RankList v-if="sortedMessageRankings.length" :rows="msgRows" :ranks="msgRanks" unit="則">
        <template #detail="{ row }">
          <span v-if="msgTotal">佔 <span class="font-num">{{ (row.value / msgTotal * 100).toFixed(1) }}%</span></span>
          <template v-if="activeMessageFilter === 'all'">
            <span v-for="t in MSG_COUNTS" :key="t.key" v-show="row[t.key]" class="ml-2">{{ t.zh }} <span class="font-num">{{ row[t.key] }}</span></span>
          </template>
        </template>
      </RankList>
      <BaseCard v-else class="px-4 py-8 text-sm text-slate-500 text-center">尚無發言數據</BaseCard>

      <!-- 訊息類型圓餅圖 -->
      <SectionHeader title="訊息型態佔比" />
      <BaseCard class="p-4">
        <Pie :data="pieChartData" :options="pieOptions" style="max-height:200px" />
      </BaseCard>

      <!-- 夜貓子排行 -->
      <SectionHeader title="夜貓子排行榜" subtitle="0–4 點深夜發言" />
      <RankList v-if="data.night_owls.length" :rows="nightRows" :ranks="nightRanks" unit="則" />
      <BaseCard v-else class="px-4 py-8 text-sm text-slate-500 text-center">深夜無人發言，大家作息都很健康</BaseCard>

      <!-- 更多排行榜（資料驅動） -->
      <div v-if="boards.length">
        <SectionHeader title="更多自訂排行榜" />
        <!-- 手機也全部列出（換行），不做橫向捲動 -->
        <div class="flex flex-wrap gap-1.5 mb-5">
          <button
            v-for="b in boards"
            :key="b.id"
            @click="selectedId = b.id"
            class="px-3 py-1.5 rounded-md text-xs font-medium border btn-press whitespace-nowrap select-none"
            :class="selectedId === b.id
              ? 'bg-cloth text-white border-cloth'
              : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'"
            :aria-pressed="selectedId === b.id"
          >
            {{ b.title }}
          </button>
        </div>
        <BoardCard v-if="selectedBoard" id="board-detail" class="scroll-mt-4" :board="selectedBoard" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { competitionRanks } from '@/utils/rank'
import { RARITY } from '@/constants/rarity'
import PageSign from '@/components/PageSign.vue'
import RankList from '@/components/RankList.vue'
import { TYPE_COLORS, TYPE_LABELS } from '@/constants/chartColors'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { api, type Board } from '@/api/client'
import { useRefreshOnAnalysis } from '@/composables/useRefreshOnAnalysis'
import BoardCard from '@/components/BoardCard.vue'
import BaseCard from '@/components/BaseCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SectionHeader from '@/components/SectionHeader.vue'
import SegmentedControl from '@/components/SegmentedControl.vue'

ChartJS.register(ArcElement, Tooltip, Legend)

const data = ref<any>(null)
const loading = ref(true)
const error = ref('')
const badgeSortMode = ref<'weighted' | 'count'>('weighted')
const activeMessageFilter = ref<'all' | 'text' | 'sticker' | 'image'>('all')
const boards = ref<Board[]>([])
const route = useRoute()
const selectedId = ref('')
const selectedBoard = computed(() => boards.value.find(b => b.id === selectedId.value) || null)

const sortedBadgeRankings = computed(() => {
  const list = [...(data.value?.badge_rankings || [])]
  if (badgeSortMode.value === 'weighted') {
    return list.sort((a, b) => {
      if ((b.score ?? 0) !== (a.score ?? 0)) return (b.score ?? 0) - (a.score ?? 0)
      if ((b.legendary_count ?? 0) !== (a.legendary_count ?? 0)) return (b.legendary_count ?? 0) - (a.legendary_count ?? 0)
      return (b.badge_count ?? 0) - (a.badge_count ?? 0)
    })
  } else {
    return list.sort((a, b) => {
      if ((b.badge_count ?? 0) !== (a.badge_count ?? 0)) return (b.badge_count ?? 0) - (a.badge_count ?? 0)
      if ((b.legendary_count ?? 0) !== (a.legendary_count ?? 0)) return (b.legendary_count ?? 0) - (a.legendary_count ?? 0)
      return (b.score ?? 0) - (a.score ?? 0)
    })
  }
})

function displayCountOf(u: any): number {
  if (activeMessageFilter.value === 'text') return u.text_count ?? 0
  if (activeMessageFilter.value === 'sticker') return u.sticker_count ?? 0
  if (activeMessageFilter.value === 'image') return u.image_count ?? 0
  return u.total ?? 0
}

const filterUnitText = computed(() => {
  if (activeMessageFilter.value === 'text') return '文字'
  if (activeMessageFilter.value === 'sticker') return '貼圖'
  if (activeMessageFilter.value === 'image') return '圖片'
  return ''
})

// 同分同名次（與排序用的欄位一致）
const badgeRanks = computed(() => competitionRanks(sortedBadgeRankings.value,
  (u: any) => `${u.score ?? 0}|${u.legendary_count ?? 0}|${u.badge_count ?? 0}`))
const msgRanks = computed(() => competitionRanks(sortedMessageRankings.value, displayCountOf))
const nightRanks = computed(() => competitionRanks(data.value?.night_owls || [], (u: any) => u.night_count))

const sortedMessageRankings = computed(() => {
  const list = [...(data.value?.rankings || [])]
  return list.sort((a, b) => displayCountOf(b) - displayCountOf(a))
})

const RARITY_COUNTS = (['legendary', 'epic', 'super_rare', 'rare', 'common'] as const)
  .map(k => ({ key: `${k}_count`, zh: RARITY[k].zh, line: RARITY[k].line }))

const badgeRows = computed(() => sortedBadgeRankings.value.map((u: any) => {
  const v = badgeSortMode.value === 'weighted' ? u.score : u.badge_count
  return { ...u, id: u.user_id, name: u.user_name || u.user_id, value: v, valueStr: String(v) }
}))
const msgRows = computed(() => sortedMessageRankings.value.map((u: any) => {
  const v = displayCountOf(u)
  return { ...u, id: u.user_id, name: u.user_name || u.user_id, value: v, valueStr: v.toLocaleString() }
}))
const nightRows = computed(() => (data.value?.night_owls || []).map((u: any) => ({
  ...u, id: u.user_id, name: u.user_name || u.user_id, value: u.night_count, valueStr: String(u.night_count),
})))

const msgTotal = computed(() => sortedMessageRankings.value.reduce((n: number, u: any) => n + displayCountOf(u), 0))

const MSG_COUNTS = (['text', 'sticker', 'image', 'video'] as const)
  .map(t => ({ key: `${t}_count`, type: t, zh: TYPE_LABELS[t] }))

const pieChartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const dist = data.value.type_distribution
  return {
    labels: dist.map((d: any) => TYPE_LABELS[d.type] || d.type),
    datasets: [{
      data: dist.map((d: any) => d.count),
      backgroundColor: dist.map((d: any) => TYPE_COLORS[d.type] || '#8C938C'),
      borderWidth: 2,
      borderColor: '#fff',
    }],
  }
})

const pieOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        font: { size: 12, family: '"Noto Sans TC", sans-serif' },
        padding: 12,
        boxWidth: 10,
      },
    },
  },
}

async function loadLeaderboards() {
  try {
    const [lead, more] = await Promise.all([api.leaderboard(), api.leaderboards()])
    data.value = lead
    boards.value = more.boards || []
    // LINE 排行卡片會帶 ?board=<id>，直接選好那個排行榜
    const wanted = route.query.board as string | undefined
    if (wanted && boards.value.some(b => b.id === wanted)) selectedId.value = wanted
    if (boards.value.length && !selectedId.value) selectedId.value = boards.value[0].id
  }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
}

onMounted(async () => {
  await loadLeaderboards()
  // 從 LINE 卡片點進來：捲到指定的排行榜
  if (route.query.board && selectedBoard.value) {
    loading.value = false
    await nextTick()
    document.getElementById('board-detail')?.scrollIntoView({ block: 'start' })
  }
  loading.value = false
})
useRefreshOnAnalysis(loadLeaderboards)
</script>
