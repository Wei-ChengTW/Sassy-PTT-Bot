<template>
  <div>
    <PageSign title="成員互動對比" en="Compare" />

    <!-- 成員選擇 -->
    <div class="grid grid-cols-2 gap-2 mb-5">
      <select
        v-model="userA"
        @change="loadCompare"
        class="text-sm bg-white border-2 border-cloth rounded-md px-3 py-2 text-slate-900 font-bold focus:outline-none"
      >
        <option value="" disabled>選擇成員 A</option>
        <option v-for="u in members" :key="u.user_id" :value="u.user_id">{{ u.name }}</option>
      </select>
      <select
        v-model="userB"
        @change="loadCompare"
        class="text-sm bg-white border-2 border-danger-500 rounded-md px-3 py-2 text-slate-900 font-bold focus:outline-none"
      >
        <option value="" disabled>選擇成員 B</option>
        <option v-for="u in members" :key="u.user_id" :value="u.user_id">{{ u.name }}</option>
      </select>
    </div>

    <div v-if="membersLoading" class="skeleton rounded-xl h-48" />
    <EmptyState
      v-else-if="membersError"
      title="無法載入成員名單"
      :description="membersError"
    />

    <template v-else>
      <EmptyState
        v-if="!userA || !userB"
        title="請選擇兩位成員"
        description="從上方下拉選單挑選兩位群組好友，比較彼此的發言習慣與默契。"
      />
      <EmptyState
        v-else-if="userA === userB"
        title="請選擇兩位不同的成員"
        description="自己跟自己比較相似度一定是 100% 啦！"
      />

      <div v-else-if="loading" class="skeleton rounded-xl h-48" />
      <EmptyState
        v-else-if="error"
        title="對比資料載入失敗"
        :description="error"
      />

      <div v-else-if="cmp" class="space-y-3">
        <!-- 相似度 -->
        <BaseCard class="p-5 flex items-end justify-between gap-4">
          <div>
            <p class="text-xs text-slate-500">默契相似度</p>
            <p class="text-sm font-bold text-slate-900 mt-0.5">{{ similarityLabel }}</p>
          </div>
          <p class="font-num text-[52px] leading-none font-semibold text-slate-900">
            <CountUp :value="cmp.similarity" :duration="600" :format="(v) => `${v}%`" />
          </p>
        </BaseCard>

        <!-- 對比列：A 深綠、B 印章紅 -->
        <BaseCard class="overflow-hidden">
          <div class="grid grid-cols-[1fr_auto_1fr] gap-3 px-4 py-2.5 border-b border-slate-200 text-sm font-bold">
            <span class="truncate flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cloth shrink-0" />{{ cmp.a.name }}</span>
            <span class="text-slate-400 font-normal text-xs self-center">VS</span>
            <span class="truncate flex items-center gap-1.5 justify-end">{{ cmp.b.name }}<span class="w-2.5 h-2.5 rounded-full bg-danger-500 shrink-0" /></span>
          </div>
          <div
            v-for="row in rows"
            :key="row.label"
            class="grid grid-cols-[1fr_auto_1fr] gap-3 px-4 py-3 items-center border-t border-slate-100 first:border-t-0"
          >
            <span class="font-num text-[17px]" :class="row.aWin ? 'font-bold text-cloth' : 'font-medium text-slate-500'">
              {{ row.a }}
            </span>
            <span class="text-center text-xs text-slate-600">
              {{ row.label }}
            </span>
            <span class="font-num text-[17px] text-right" :class="row.bWin ? 'font-bold text-danger-700' : 'font-medium text-slate-500'">
              {{ row.b }}
            </span>
          </div>
        </BaseCard>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api/client'
import { useRefreshOnAnalysis } from '@/composables/useRefreshOnAnalysis'
import BaseCard from '@/components/BaseCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import CountUp from '@/components/CountUp.vue'

const members = ref<{ user_id: string; name: string }[]>([])
const membersLoading = ref(true)
const membersError = ref('')
const userA = ref('')
const userB = ref('')

const cmp = ref<any>(null)
const loading = ref(false)
const error = ref('')

const SLOT_LABELS: Record<string, string> = {
  night: '深夜', morning: '清晨', daytime: '白天', evening: '晚上',
}

const rows = computed(() => {
  if (!cmp.value) return []
  const a = cmp.value.a, b = cmp.value.b
  const num = (label: string, av: number, bv: number, fmt = (x: number) => `${x}`) => ({
    label, a: fmt(av), b: fmt(bv), aWin: av > bv, bWin: bv > av,
  })
  const sentA = a.avg_sentiment, sentB = b.avg_sentiment
  const sentFmt = (x: number | null) => (x === null || x === undefined ? '—' : x.toFixed(2))
  return [
    num('總訊息量', a.total, b.total),
    num('活躍天數', a.active_days, b.active_days),
    num('平均日發言', a.avg_per_day, b.avg_per_day),
    num('文字比例', a.text_ratio, b.text_ratio, (x) => `${x}%`),
    num('貼圖比例', a.sticker_ratio, b.sticker_ratio, (x) => `${x}%`),
    {
      label: '情緒指數', a: sentFmt(sentA), b: sentFmt(sentB),
      aWin: (sentA ?? -2) > (sentB ?? -2), bWin: (sentB ?? -2) > (sentA ?? -2),
    },
    {
      label: '活躍時段',
      a: SLOT_LABELS[a.top_slot] || '—', b: SLOT_LABELS[b.top_slot] || '—',
      aWin: false, bWin: false,
    },
  ]
})

const similarityLabel = computed(() => {
  const s = cmp.value?.similarity ?? 0
  if (s >= 80) return '超級麻吉'
  if (s >= 60) return '頗有默契'
  if (s >= 40) return '各有風格'
  return '互補型夥伴'
})

async function loadCompare() {
  if (!userA.value || !userB.value || userA.value === userB.value) { cmp.value = null; return }
  loading.value = true
  error.value = ''
  try { cmp.value = await api.compare(userA.value, userB.value) }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
  finally { loading.value = false }
}

async function loadMembers() {
  try {
    const dash = await api.dashboard()
    members.value = (dash.top_users || []).map((u: any) => ({
      user_id: u.user_id, name: u.user_name || u.user_id,
    }))
  } catch (e: any) { membersError.value = e?.message || '請求失敗'; console.error(e) }
}

onMounted(async () => {
  await loadMembers()
  membersLoading.value = false
})
useRefreshOnAnalysis(loadMembers)
</script>
