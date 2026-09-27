<template>
  <div>
    <PageSign title="建立旅行與事件" en="New Trip" back="返回" />

    <BaseCard class="p-5">
      <form @submit.prevent="submit" class="space-y-5">
        <!-- 類型切換：單日事件 vs 多日旅行 -->
        <div>
          <label class="block text-[13px] font-bold text-slate-700 mb-2">活動形式</label>
          <div class="grid grid-cols-2 border border-slate-300 rounded-md overflow-hidden">
            <button
              type="button"
              @click="mode = 'event'"
              class="py-2.5 text-xs font-bold transition-colors"
              :class="mode === 'event' ? 'bg-cloth text-white' : 'bg-white text-slate-600 hover:bg-slate-50'"
              :aria-pressed="mode === 'event'"
            >
              單日事件（當天）
            </button>
            <button
              type="button"
              @click="mode = 'trip'"
              class="py-2.5 text-xs font-bold transition-colors border-l border-slate-300"
              :class="mode === 'trip' ? 'bg-cloth text-white' : 'bg-white text-slate-600 hover:bg-slate-50'"
              :aria-pressed="mode === 'trip'"
            >
              多日旅行（跨日）
            </button>
          </div>
        </div>

        <!-- 標題與自訂 Emoji -->
        <div class="flex gap-3 items-start">
          <div class="w-18 shrink-0">
            <label class="block text-[13px] font-bold text-slate-700 mb-1.5">Emoji</label>
            <input
              v-model="form.custom_emoji"
              class="w-full bg-white border border-slate-300 rounded-md px-2 py-2.5 text-center text-xl focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              placeholder="🎒"
            />
          </div>
          <div class="flex-1 min-w-0">
            <label class="block text-[13px] font-bold text-slate-700 mb-1.5">名稱 / 標題 *</label>
            <input
              v-model="form.title"
              required
              class="w-full bg-white border border-slate-300 rounded-md px-3.5 py-2.5 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              :placeholder="mode === 'event' ? '例如：聚餐吃火鍋、夜唱' : '例如：花東三日遊、宜蘭包棟'"
            />
          </div>
        </div>

        <div>
          <label class="block text-[13px] font-bold text-slate-700 mb-1.5">活動地點 *</label>
          <input
            v-model="form.location"
            required
            class="w-full bg-white border border-slate-300 rounded-md px-3.5 py-2.5 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
            placeholder="例如：墾丁、內湖高中、宜蘭礁溪"
          />
        </div>

        <!-- 日期選擇 -->
        <div v-if="mode === 'event'">
          <label class="block text-[13px] font-bold text-slate-700 mb-1.5">發生日期 *</label>
          <input
            v-model="form.startDate"
            type="date"
            required
            class="w-full bg-white border border-slate-300 rounded-md px-3.5 py-2.5 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <div v-else class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-[13px] font-bold text-slate-700 mb-1.5">開始日期 *</label>
            <input
              v-model="form.startDate"
              type="date"
              required
              class="w-full bg-white border border-slate-300 rounded-md px-3.5 py-2.5 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label class="block text-[13px] font-bold text-slate-700 mb-1.5">結束日期 *</label>
            <input
              v-model="form.endDate"
              type="date"
              required
              :min="form.startDate"
              class="w-full bg-white border border-slate-300 rounded-md px-3.5 py-2.5 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
            />
          </div>
        </div>

        <!-- 類型標籤 -->
        <div>
          <label class="block text-[13px] font-bold text-slate-700 mb-2">類型標籤（可複選）</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="t in TRIP_TYPES"
              :key="t.value"
              type="button"
              @click="toggleType(t.value)"
              class="rounded-md px-3 py-1.5 text-xs font-medium border transition-all duration-150 btn-press"
              :class="form.types.includes(t.value) ? 'bg-cloth text-white border-cloth'
                : 'bg-white text-slate-700 border-slate-300 hover:border-slate-400'"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <div class="flex gap-3 pt-3 border-t border-slate-100">
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 bg-brand-500 hover:bg-brand-600 text-white rounded-md py-3 text-sm font-bold disabled:opacity-50 transition-all btn-press"
          >
            {{ loading ? '建立中...' : (mode === 'event' ? '建立事件' : '建立旅行') }}
          </button>
          <button
            type="button"
            @click="$router.back()"
            class="px-5 border border-slate-300 rounded-md py-3 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-all btn-press"
          >
            取消
          </button>
        </div>
        <p v-if="error" class="text-danger-600 text-xs font-semibold text-center mt-2">{{ error }}</p>
      </form>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'
import { TRIP_TYPES } from '@/constants/tripTypes'
import BaseCard from '@/components/BaseCard.vue'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const mode = ref<'event' | 'trip'>('event')
const form = ref({
  title: '',
  location: '',
  startDate: '',
  endDate: '',
  custom_emoji: '',
  types: [] as string[],
})

function toggleType(value: string) {
  const i = form.value.types.indexOf(value)
  if (i >= 0) form.value.types.splice(i, 1)
  else form.value.types.push(value)
}

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const startDate = Math.floor(new Date(form.value.startDate).getTime() / 1000)
    let endDate: number | undefined = undefined
    if (mode.value === 'trip' && form.value.endDate) {
      endDate = Math.floor(new Date(form.value.endDate).getTime() / 1000)
    }
    if (!startDate) { error.value = '請選擇開始日期'; return }
    if (endDate !== undefined && endDate < startDate) { error.value = '結束日期不能早於開始日期'; return }
    const res = await api.adminCreateTrip({
      title: form.value.title.trim(),
      location: form.value.location.trim(),
      start_date: startDate,
      end_date: endDate,
      types: form.value.types,
      custom_emoji: form.value.custom_emoji.trim() || undefined,
    })
    router.push(`/admin/trips/${res.trip_id}`)
  } catch (e: any) {
    error.value = e.message || '建立失敗'
  } finally {
    loading.value = false
  }
}
</script>
