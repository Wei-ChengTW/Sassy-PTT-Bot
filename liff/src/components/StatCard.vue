<template>
  <div class="px-4 py-3.5 min-w-0" :class="tone === 'cover' ? 'bg-cloth' : 'bg-white'">
    <p class="font-num text-[30px] leading-none font-semibold" :class="tone === 'cover' ? 'text-white' : 'text-slate-900'">
      <CountUp v-if="typeof value === 'number'" :value="value" :duration="600" />
      <span v-else>{{ value }}</span>
    </p>
    <p class="text-xs mt-1.5 truncate" :class="tone === 'cover' ? 'text-[#D6B872]' : 'text-slate-500'">{{ label }}</p>
    <div v-if="subtext || $slots.subtext" class="mt-1 text-[11px] text-slate-500 flex items-center gap-1">
      <slot name="subtext">{{ subtext }}</slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import CountUp from '@/components/CountUp.vue'

// 數字格：放在 gap-px 格線容器裡組成一條紀錄表；tone="cover" 用於印在封面布上。
withDefaults(defineProps<{
  label: string
  value: number | string
  subtext?: string
  tone?: 'page' | 'cover'
}>(), { tone: 'page' })
</script>
