<template>
  <div>
    <PageSign title="活動與旅行後台" en="Trip Admin">
      <template #action>
        <router-link
          to="/admin/trips/new"
          class="text-xs font-bold px-3 py-2 rounded-md bg-white text-cloth hover:bg-slate-100 btn-press inline-flex items-center gap-1"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>
          新增旅行
        </router-link>
      </template>
    </PageSign>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-2">
      <div v-for="i in 3" :key="i" class="skeleton h-16 rounded-xl" />
    </div>

    <EmptyState
      v-else-if="error"
      title="載入失敗"
      :description="error"
    />
    <EmptyState
      v-else-if="trips.length === 0"
      title="尚無旅行資料"
      description="目前沒有建立任何群組旅行紀錄"
    />

    <div v-else class="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
      <router-link
        v-for="t in trips"
        :key="t.id"
        :to="`/admin/trips/${t.id}`"
        class="flex items-center gap-3.5 px-3.5 py-3 hover:bg-slate-50 active:bg-slate-100 transition-colors"
      >
        <RaritySeal :rarity="t.rarity" :emoji="t.custom_emoji || t.badge_emoji" :size="44" />
        <div class="flex-1 min-w-0">
          <p class="font-bold text-[15px] truncate text-slate-900">{{ t.title }}</p>
          <p class="text-xs mt-0.5 truncate text-slate-600">{{ t.location || '群組回憶' }}</p>
        </div>
        <div class="text-right shrink-0">
          <span class="block text-[11px] px-1.5 py-px rounded font-bold" :class="rarityOf(t.rarity).pill">{{ rarityOf(t.rarity).zh }}</span>
          <span class="block text-[11px] font-bold mt-1" :class="phaseClass(t)">{{ PHASE_LABEL[tripPhase(t)] }}</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import RaritySeal from '@/components/RaritySeal.vue'
import { ref, onMounted } from 'vue'
import { api } from '@/api/client'
import { rarityOf } from '@/constants/rarity'
import EmptyState from '@/components/EmptyState.vue'
import { tripPhase, PHASE_LABEL } from '@/constants/tripStatus'

const trips = ref<any[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try { trips.value = await api.trips() }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
  finally { loading.value = false }
})
// 規劃中（還沒出發）與進行中分開顯示
function phaseClass(t: any) {
  const p = tripPhase(t)
  return p === 'ended' ? 'text-slate-500'
    : p === 'upcoming' ? 'text-accent-700' : 'text-success-700'
}
</script>
