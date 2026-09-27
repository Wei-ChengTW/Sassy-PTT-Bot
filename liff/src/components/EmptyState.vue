<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <!-- 路線終點符號 -->
    <svg class="mb-4" width="72" height="16" viewBox="0 0 72 16" aria-hidden="true">
      <line x1="0" y1="8" x2="56" y2="8" stroke="#C5CAC4" stroke-width="4" stroke-dasharray="6 5" />
      <circle cx="62" cy="8" r="6" fill="#fff" stroke="#8C938C" stroke-width="3" />
    </svg>
    <h3 class="text-base font-bold text-slate-900">{{ title }}</h3>
    <p v-if="description" class="text-[13px] text-slate-500 mt-1 max-w-xs leading-relaxed">
      {{ description }}
    </p>
    <div v-if="$slots.action" class="mt-4">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>
