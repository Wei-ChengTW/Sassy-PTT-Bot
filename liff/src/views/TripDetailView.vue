<template>
  <div>
    <PageSign :title="detail?.trip.title || '旅程'" en="Trip Record" line="trip" back="返回列表">
      <template v-if="detail" #action>
        <RaritySeal :rarity="detail.trip.rarity" :emoji="detail.trip.custom_emoji || detail.trip.badge_emoji" :size="68" />
      </template>
      <template v-if="detail?.trip.rarity">
        <span class="inline-flex items-center px-1.5 py-px rounded text-[11px] font-bold bg-white" :class="rarity.pill">{{ rarity.zh }}</span>
      </template>
    </PageSign>

    <div v-if="loading" class="space-y-3">
      <div class="skeleton h-36 rounded-xl" />
      <div class="skeleton h-24 rounded-xl" />
    </div>

    <EmptyState
      v-else-if="!detail"
      title="找不到這趟旅程"
      :description="error || '可能已被刪除，或網址打錯了'"
    />
    <div v-else>
      <!-- 旅程資料 -->
      <dl class="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100 text-sm">
        <div v-if="detail.trip.location" class="flex px-4 py-3 gap-4">
          <dt class="w-12 shrink-0 text-slate-500">地點</dt>
          <dd class="font-bold text-slate-900">{{ detail.trip.location }}</dd>
        </div>
        <div v-if="dateRange" class="flex px-4 py-3 gap-4">
          <dt class="w-12 shrink-0 text-slate-500">日期</dt>
          <dd class="font-num text-[15px] font-semibold text-slate-900">{{ dateRange }}</dd>
        </div>
        <div v-if="detail.trip.trip_types && detail.trip.trip_types.length" class="flex px-4 py-3 gap-4">
          <dt class="w-12 shrink-0 text-slate-500">類型</dt>
          <dd class="text-slate-900">{{ detail.trip.trip_types.map(labelFor).join('、') }}</dd>
        </div>
        <div class="flex px-4 py-3 gap-4">
          <dt class="w-12 shrink-0 text-slate-500">狀態</dt>
          <dd class="font-bold text-slate-900">
            {{ { ended: '已圓滿結束', upcoming: '規劃中', ongoing: '進行中' }[tripPhase(detail.trip)] }}
            <span v-if="tripAgo(detail.trip)" class="ml-1.5 text-sm font-bold text-accent-700">· {{ tripAgo(detail.trip) }}</span>
            <span v-else-if="daysUntil(detail.trip) !== null" class="ml-1.5 text-sm font-bold text-accent-700">· 還有 <span class="font-num">{{ daysUntil(detail.trip) }}</span> 天</span>
          </dd>
        </div>
        <div class="flex px-4 py-3 gap-4">
          <dt class="w-12 shrink-0 text-slate-500">訊息</dt>
          <dd class="text-slate-900"><span class="font-num text-[15px] font-semibold">{{ detail.stats.message_count }}</span> 則</dd>
        </div>
      </dl>

      <!-- 參與者列表 -->
      <SectionHeader title="活動參與者" :subtitle="`共 ${detail.participants.length} 人`" />
      <BaseCard class="overflow-hidden">
        <ul v-if="detail.participants.length" class="divide-y divide-slate-100">
          <li
            v-for="p in detail.participants"
            :key="p.user_id"
            class="px-3.5 py-2.5 text-sm flex items-center gap-3"
          >
            <span class="flex-1 font-bold text-slate-900 truncate">{{ p.user_name || p.user_id }}</span>
            <span class="text-xs text-slate-500">{{ p.role || '成員' }}</span>
          </li>
        </ul>
        <div v-else class="px-4 py-8 text-sm text-slate-500 text-center">
          尚未指定參與者
        </div>
      </BaseCard>

      <!-- Action buttons -->
      <div class="space-y-2 mt-6">
        <button
          @click="onShare"
          :disabled="sharing"
          class="w-full bg-brand-500 hover:bg-brand-600 text-white rounded-md py-3.5 font-bold disabled:opacity-60 btn-press flex items-center justify-center gap-2"
        >
          <svg v-if="!sharing" class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12v7a1 1 0 001 1h14a1 1 0 001-1v-7M16 6l-4-4-4 4M12 2v14" /></svg>
          <svg v-else class="w-[18px] h-[18px] animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" stroke-opacity="0.3" /><path d="M21 12a9 9 0 00-9-9" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
          <span>{{ sharing ? '小卡發送中…' : '分享回顧小卡到 LINE 群組' }}</span>
        </button>

        <router-link
          v-if="auth.role === 'admin'"
          :to="`/admin/trips/${route.params.id}`"
          class="block w-full text-center bg-white border border-slate-300 hover:border-slate-400 text-slate-900 rounded-md py-3 font-bold btn-press"
        >
          管理參與名單 / 發放勳章
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'
import { labelFor } from '@/constants/tripTypes'
import PageSign from '@/components/PageSign.vue'
import { tripAgo } from '@/utils/ago'
import RaritySeal from '@/components/RaritySeal.vue'
import { rarityOf } from '@/constants/rarity'
import { useAuthStore } from '@/stores/auth'
import { buildTripFlex } from '@/utils/flexTripCard'
import { shareFlexMessage } from '@/utils/liffShare'
import { useToast } from '@/composables/useToast'
import BaseCard from '@/components/BaseCard.vue'
import SectionHeader from '@/components/SectionHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { tripPhase } from '@/constants/tripStatus'

const route = useRoute()
const auth = useAuthStore()
const toast = useToast()
const detail = ref<any>(null)
const loading = ref(true)
const error = ref('')
const sharing = ref(false)

async function onShare() {
  if (!detail.value || sharing.value) return
  sharing.value = true
  try {
    const res = await shareFlexMessage(buildTripFlex(detail.value))
    if (res.success) toast.success('已分享回顧小卡')
    else if (res.mode === 'picker') toast.error('已取消分享')
  } catch (e: any) {
    toast.error(e?.message || '分享失敗，請稍後再試')
  } finally {
    sharing.value = false
  }
}

const rarity = computed(() => rarityOf(detail.value?.trip?.rarity))

const dateRange = computed(() => {
  const t = detail.value?.trip
  if (!t?.start_date) return ''
  const fmt = (ts: number) => {
    const d = new Date(ts * 1000)
    return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
  }
  const start = fmt(t.start_date)
  if (!t.end_date || t.end_date === t.start_date) return start
  return `${start} – ${fmt(t.end_date)}`
})

onMounted(async () => {
  try { detail.value = await api.tripDetail(route.params.id as string) }
  catch (e: any) {
    // 404 屬於正常的「找不到」，其他錯誤才顯示訊息
    if (!String(e?.message).startsWith('404')) error.value = e?.message || '請求失敗'
    console.error(e)
  }
  finally { loading.value = false }
})

function daysUntil(t: any): number | null {
  if (tripPhase(t) !== 'upcoming' || !t.start_date) return null
  return Math.max(1, Math.ceil((t.start_date * 1000 - Date.now()) / 86400000))
}
</script>
