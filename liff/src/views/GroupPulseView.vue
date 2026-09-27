<template>
  <div>
    <PageSign title="群組動態脈搏" en="Group Pulse" />

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-32 rounded-xl" />
      <div class="skeleton h-36 rounded-xl" />
    </div>

    <EmptyState
      v-else-if="error"
      title="無法載入動態資料"
      :description="error"
    />

    <div v-else-if="data">
      <!-- 回應速度 -->
      <SectionHeader title="群組回應速度" class="!mt-0" />
      <BaseCard class="px-4 py-4 flex items-baseline gap-2">
        <span class="font-num text-[44px] leading-none font-semibold text-slate-900">
          {{ data.response_speed.avg_minutes !== null ? data.response_speed.avg_minutes : '—' }}
        </span>
        <span class="text-sm text-slate-500">分鐘 · 平均回覆時效</span>
      </BaseCard>

      <SectionHeader title="閃電神回手" subtitle="平均回覆越快排越前面" />
      <RankList v-if="responderRows.length" :rows="responderRows" :ranks="responderRows.map((_: any, i: number) => i + 1)"
                unit="分鐘" invert />
      <BaseCard v-else class="px-4 py-6 text-xs text-slate-500 text-center">
        目前還沒有足夠的回覆資料
      </BaseCard>

      <!-- 訊息爆發 -->
      <SectionHeader title="熱門話題爆發時段" :subtitle="`平均每小時 ${data.avg_hourly} 則`" />
      <BaseCard class="overflow-hidden">
        <div v-if="!data.bursts.length" class="px-4 py-8 text-center text-xs text-slate-500">
          尚無明顯爆發時段
        </div>
        <ol v-else class="divide-y divide-slate-100">
          <li
            v-for="(b, i) in data.bursts"
            :key="b.hour"
            class="flex items-center px-3.5 py-3 gap-3"
            :class="i === 0 ? 'bg-accent-50' : ''"
          >
            <RankChip :rank="i + 1" size="sm" />
            <div class="flex-1 min-w-0">
              <p class="font-num text-[15px] font-semibold text-slate-900">
                {{ burstTime(b.hour).time }}
                <span class="font-sans text-xs font-normal text-slate-500 ml-1">{{ burstTime(b.hour).date }}</span>
              </p>
              <p class="text-xs text-slate-500 mt-0.5">
                平均的 <span class="font-num font-semibold text-accent-700">{{ burstRatio(b) }}</span> 倍
              </p>
            </div>
            <span class="font-num text-[17px] font-semibold text-slate-900 shrink-0">{{ b.count }}<span class="font-sans text-xs font-normal text-slate-500 ml-1">則</span></span>
          </li>
        </ol>
      </BaseCard>

      <!-- 潛水員 -->
      <div>
        <SectionHeader title="群組潛水員偵測" />
        <BaseCard class="overflow-hidden">
          <div v-if="!data.lurkers.length" class="px-4 py-8 text-center text-sm font-bold text-success-700">
            沒有人潛水，全員活躍熱絡中
          </div>
          <div v-else class="divide-y divide-slate-100">
            <div
              v-for="u in data.lurkers"
              :key="u.user_id"
              class="flex items-center px-4 py-3 gap-3"
            >
              <span class="w-3 h-3 rounded-full border-[3px] border-slate-300 bg-white shrink-0" aria-hidden="true" />
              <span class="flex-1 text-sm font-bold text-slate-900 truncate">{{ u.name }}</span>
              <span class="text-xs text-slate-500">
                {{ u.days_inactive !== null ? `${Math.floor(u.days_inactive)} 天未發言` : '從未發言' }}
              </span>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import RankChip from '@/components/RankChip.vue'
import PageSign from '@/components/PageSign.vue'
import RankList from '@/components/RankList.vue'
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api/client'
import { useRefreshOnAnalysis } from '@/composables/useRefreshOnAnalysis'
import BaseCard from '@/components/BaseCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SectionHeader from '@/components/SectionHeader.vue'

const data = ref<any>(null)
const loading = ref(true)
const error = ref('')

async function loadPulse() {
  try { data.value = await api.pulse() }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
}

onMounted(async () => {
  await loadPulse()
  loading.value = false
})
useRefreshOnAnalysis(loadPulse)

const responderRows = computed(() => (data.value?.response_speed?.fastest_responders || []).map((u: any) => ({
  ...u, id: u.user_id, name: u.name, value: u.avg_minutes, valueStr: String(u.avg_minutes),
})))

const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']
// b.hour 形如「2025-07-16 00」或「14」→ 拆成時間與日期（含星期）
function burstTime(h: string | number) {
  const str = String(h)
  const [d, hr] = str.includes(' ') ? str.split(' ') : ['', str]
  const time = `${hr.padStart(2, '0')}:00`
  if (!d) return { time, date: '' }
  const dt = new Date(`${d}T00:00:00`)
  const date = isNaN(dt.getTime()) ? d : `${d.replace(/-/g, '/')}（${WEEKDAYS[dt.getDay()]}）`
  return { time, date }
}

function burstRatio(b: any) {
  const r = b.ratio ?? (data.value?.avg_hourly ? b.count / data.value.avg_hourly : 0)
  return r >= 10 ? Math.round(r) : Number(r).toFixed(1)
}
</script>
