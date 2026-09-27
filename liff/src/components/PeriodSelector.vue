<template>
  <label class="flex items-center gap-2 text-white/90">
    <span class="text-xs shrink-0">期間</span>
    <select
      v-model="period" @change="onChange"
      class="min-w-0 max-w-[9.5rem] text-xs bg-white/10 border border-white/25 rounded-md pl-2 pr-6 py-1 text-white font-medium focus:outline-none focus:border-white cursor-pointer appearance-none bg-no-repeat"
      :style="{ backgroundImage: chevron, backgroundPosition: 'right 6px center', backgroundSize: '10px' }"
    >
      <option value="all" class="text-slate-900">全部時間</option>
      <optgroup v-if="years.length" label="歷年" class="text-slate-900">
        <option v-for="y in years" :key="y" :value="y">{{ y }} 年</option>
      </optgroup>
      <optgroup v-if="months.length" label="月份" class="text-slate-900">
        <option v-for="m in months" :key="m" :value="m">{{ formatMonth(m) }}</option>
      </optgroup>
    </select>
  </label>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api, setPeriod, getPeriod } from '@/api/client'

const router = useRouter()
const period = ref(getPeriod())
const years = ref<string[]>([])
const months = ref<string[]>([])

const chevron = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' fill='none' stroke='white' stroke-width='1.6'/%3E%3C/svg%3E")`

function formatMonth(m: string) {
  const [y, mo] = m.split('-')
  return `${y} 年 ${parseInt(mo)} 月`
}

function onChange() {
  setPeriod(period.value)
  router.go(0)
}

onMounted(async () => {
  try {
    const data = await api.periods()
    years.value = data.years || []
    months.value = data.months || []
    // 若已存的選擇不在清單中，回退全部
    const valid = period.value === 'all'
      || years.value.includes(period.value)
      || months.value.includes(period.value)
    if (!valid) { period.value = 'all'; setPeriod('all') }
  } catch {}
})
</script>
