<template>
  <div>
    <PageSign title="群組話題與情緒" en="Topics &amp; Mood">
      <template v-if="auth.role === 'admin'" #action>
        <!-- 管理員觸發重新分析按鈕 -->
        <button
          @click="triggerReanalyze"
          :disabled="analyzing"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold bg-white text-slate-900 hover:bg-slate-100 disabled:opacity-60 btn-press"
        >
          <svg class="w-3.5 h-3.5" :class="analyzing ? 'animate-spin' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11a8 8 0 10-2.3 5.7M20 4v7h-7" /></svg>
          <span>{{ analyzing ? 'LLM 分析中...' : '重新分析' }}</span>
        </button>
      </template>
      <template v-if="data?.last_analyzed_at">
        最後分析：<span class="font-num">{{ formatAnalyzedTime(data.last_analyzed_at) }}</span>
      </template>
    </PageSign>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-48 rounded-xl" />
      <div class="skeleton h-40 rounded-xl" />
    </div>

    <EmptyState
      v-else-if="error"
      title="無法載入話題資料"
      :description="error"
    />

    <div v-else-if="data">
      <!-- 熱門關鍵字文字雲 -->
      <template v-if="data.top_keywords && data.top_keywords.length">
        <div>
          <SectionHeader title="熱門話題關鍵字雲" class="!mt-0" />
          <BaseCard class="p-3 overflow-hidden">
            <WordCloud :words="cloudWords" />
          </BaseCard>
        </div>
      </template>

      <!-- 熱門話題 -->
      <div>
        <SectionHeader title="熱門話題 Top 10" />
        <BaseCard class="p-4">
          <Bar :data="topicBarData" :options="barOptions" style="max-height:220px" />
        </BaseCard>
      </div>

      <!-- 情緒分佈 -->
      <template v-if="data.sentiment_distribution && data.sentiment_distribution.length">
        <div>
          <SectionHeader title="發言情緒佔比" />
          <BaseCard class="p-4">
            <Doughnut :data="sentimentDistData" :options="doughnutOptions" style="max-height:220px" />
          </BaseCard>
        </div>
      </template>

      <!-- 話題情緒 -->
      <template v-if="data.topic_sentiment && data.topic_sentiment.length">
        <div>
          <SectionHeader title="各話題平均情緒指標" />
          <BaseCard class="overflow-hidden">
            <div class="divide-y divide-slate-100">
              <div v-for="t in data.topic_sentiment" :key="t.topic" class="flex items-center px-4 py-3 gap-3">
                <span class="w-20 text-sm font-bold text-slate-900 truncate">{{ t.topic }}</span>
                <div class="flex-1 h-1 bg-slate-200 relative">
                  <div class="absolute left-1/2 -top-1 -bottom-1 w-px bg-slate-400" aria-hidden="true" />
                  <div class="absolute top-0 bottom-0"
                       :style="sentimentBarStyle(t.avg_sentiment)" />
                </div>
                <span class="font-num text-[15px] font-semibold w-12 text-right"
                      :class="t.avg_sentiment >= 0 ? 'text-success-700' : 'text-danger-600'">
                  {{ t.avg_sentiment > 0 ? '+' : '' }}{{ t.avg_sentiment.toFixed(2) }}
                </span>
              </div>
            </div>
          </BaseCard>
        </div>
      </template>

      <!-- 情緒曲線 -->
      <div>
        <SectionHeader title="情緒波動趨勢曲線" />
        <BaseCard class="p-4">
          <Line :data="sentimentLineData" :options="lineOptions" style="max-height:180px" />
        </BaseCard>
      </div>

      <!-- 熱門地點 -->
      <template v-if="data.hot_locations && data.hot_locations.length">
        <div>
          <SectionHeader title="熱門提及地點" />
          <BaseCard class="p-4 flex flex-wrap gap-2">
            <span
              v-for="l in data.hot_locations"
              :key="l.location"
              class="inline-flex items-center gap-1.5 rounded-md border border-slate-300 px-2.5 py-1 text-xs text-slate-800"
            >
              <span class="w-2 h-2 rounded-full border-2 border-trip-500" aria-hidden="true" />
              <span class="font-bold">{{ l.location }}</span>
              <span class="font-num text-slate-500">{{ l.count }}</span>
            </span>
          </BaseCard>
        </div>
      </template>

      <!-- 精選語錄 -->
      <template v-if="data.highlight_quotes && data.highlight_quotes.length">
        <div>
          <SectionHeader title="精選金句語錄" subtitle="AI 評審每日選出" />
          <div class="space-y-2">
            <figure
              v-for="(q, i) in data.highlight_quotes"
              :key="i"
              class="rounded-xl border border-brand-100 px-4 py-3.5 bg-brand-50"
              style="background-image: repeating-linear-gradient(transparent 0 27px, rgba(35,70,160,0.10) 27px 28px); background-position: 0 10px"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700">
                  <span class="w-2 h-2 rounded-full" :class="q.tone === 'positive' ? 'bg-success-500' : 'bg-danger-500'" aria-hidden="true" />
                  {{ q.label || (q.tone === 'positive' ? '滿滿正能量' : '吐槽代表') }}
                </span>
                <span class="flex items-center gap-1">
                  <span class="text-xs font-num text-slate-500">{{ quoteDate(q.timestamp) }}</span>
                  <button
                    type="button"
                    @click="onShareQuote(q, i)"
                    :disabled="sharingQuote !== null"
                    class="-my-2 -mr-2 w-10 h-10 flex items-center justify-center rounded-md text-brand-600 hover:bg-brand-100 disabled:opacity-40 btn-press"
                    aria-label="分享這句到 LINE"
                  >
                    <svg v-if="sharingQuote !== i" class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12v7a1 1 0 001 1h14a1 1 0 001-1v-7M16 6l-4-4-4 4M12 2v14" /></svg>
                    <svg v-else class="w-[18px] h-[18px] animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" stroke-opacity="0.3" /><path d="M21 12a9 9 0 00-9-9" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
                  </button>
                </span>
              </div>
              <blockquote class="font-hand text-[18px] font-bold text-brand-700 leading-[28px]">「{{ q.content }}」</blockquote>
              <figcaption class="flex items-center justify-between mt-2 text-xs text-slate-500">
                <span>
                  <template v-if="q.laughs"><span class="font-num text-slate-700">{{ q.laughs }}</span> 人笑</template>
                  <template v-if="q.laughs && q.replies"> · </template>
                  <template v-if="q.replies"><span class="font-num text-slate-700">{{ q.replies }}</span> 則回覆</template>
                </span>
                <span class="font-hand font-bold text-brand-600 text-[15px]">— {{ q.user_name }}</span>
              </figcaption>
            </figure>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Bar, Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, ArcElement,
  BarElement, PointElement, LineElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { useRefreshOnAnalysis } from '@/composables/useRefreshOnAnalysis'
import WordCloud from '@/components/WordCloud.vue'
import BaseCard from '@/components/BaseCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SectionHeader from '@/components/SectionHeader.vue'
import PageSign from '@/components/PageSign.vue'
import { peakColors } from '@/constants/chartColors'
import { shareFlexMessage } from '@/utils/liffShare'
import { buildQuoteFlex } from '@/utils/flexQuoteCard'

ChartJS.register(CategoryScale, LinearScale, ArcElement, BarElement, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const auth = useAuthStore()
const toast = useToast()
const data = ref<any>(null)
const loading = ref(true)
const analyzing = ref(false)
const error = ref('')
const sharingQuote = ref<number | null>(null)

async function onShareQuote(q: any, i: number) {
  if (sharingQuote.value !== null) return
  sharingQuote.value = i
  try {
    const res = await shareFlexMessage(buildQuoteFlex(q))
    if (res.success) toast.success('已分享金句')
    else if (res.mode === 'picker') toast.error('已取消分享')
  } catch (e: any) {
    toast.error(e?.message || '分享失敗，請稍後再試')
  } finally {
    sharingQuote.value = null
  }
}

async function loadTopics() {
  try { data.value = await api.topics() }
  catch (e: any) { error.value = e?.message || '請求失敗' }
}

function formatAnalyzedTime(ts: number) {
  if (!ts) return ''
  const d = new Date(ts * 1000)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function quoteDate(ts: number) {
  const d = new Date(ts)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

async function triggerReanalyze() {
  if (analyzing.value) return
  analyzing.value = true
  try {
    const res = await api.adminAnalyzeTopics()
    const minutes = Math.max(1, Math.ceil(res.pending / 1000))
    if (!res.started) toast.success(`已經在分析中了，約 ${minutes} 分鐘後重新整理看看 ⏳`)
    else if (!res.pending) toast.success('最近一個月都分析過了，只補情緒分數')
    else toast.success(`背景分析最近一個月 ${res.pending} 則訊息，約 ${minutes} 分鐘後重新整理 ⏳`)
  } catch (e: any) {
    toast.error(e?.message || '分析失敗，請稍後再試')
  } finally {
    analyzing.value = false
  }
}

const topicBarData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const top10 = data.value.top_topics.slice(0, 10)
  return {
    labels: top10.map((t: any) => t.topic),
    datasets: [{
      label: '提及次數',
      data: top10.map((t: any) => t.count),
      backgroundColor: peakColors(top10.map((t: any) => t.count)),
      borderRadius: 2,
    }],
  }
})

const barOptions = {
  responsive: true,
  indexAxis: 'y' as const,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: '#EEF0ED' } },
    y: { grid: { display: false } },
  },
}

const sentimentLineData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const rows = data.value.daily_sentiment.slice(-30)
  return {
    labels: rows.map((r: any) => r.date),
    datasets: [{
      label: '情緒值',
      data: rows.map((r: any) => r.avg_sentiment),
      borderColor: '#2E7D4F',
      backgroundColor: 'rgba(46,125,79,0.08)',
      fill: true,
      tension: 0,
      borderWidth: 2.5,
    }],
  }
})

const lineOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    y: { min: -1, max: 1, grid: { color: '#EEF0ED' } },
    x: { grid: { display: false } },
  },
}

const SENT_COLORS: Record<string, string> = {
  非常正面: '#2E7D4F', 正面: '#A1CCB2', 中性: '#C5CAC4',
  負面: '#E8A69F', 非常負面: '#B8332A',
}

const sentimentDistData = computed(() => {
  if (!data.value?.sentiment_distribution) return { labels: [], datasets: [] }
  const rows = data.value.sentiment_distribution
  return {
    labels: rows.map((r: any) => `${r.category} ${r.percentage}%`),
    datasets: [{
      data: rows.map((r: any) => r.count),
      backgroundColor: rows.map((r: any) => SENT_COLORS[r.category] || '#8C938C'),
      borderWidth: 0,
    }],
  }
})

const doughnutOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { boxWidth: 12, font: { size: 11, family: '"Noto Sans TC", sans-serif' }, padding: 12 },
    },
  },
}

const cloudWords = computed(() =>
  (data.value?.top_keywords || []).map((k: any) => ({ text: k.keyword, count: k.count })),
)

function sentimentBarStyle(v: number) {
  const pct = Math.min(Math.abs(v), 1) * 50
  if (v >= 0) {
    return { left: '50%', width: `${pct}%`, background: '#2E7D4F' }
  }
  return { right: '50%', width: `${pct}%`, background: '#B8332A' }
}

onMounted(async () => {
  await loadTopics()
  loading.value = false
})
useRefreshOnAnalysis(loadTopics)
</script>
