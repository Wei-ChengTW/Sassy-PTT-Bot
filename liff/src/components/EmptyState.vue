<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <!-- 空白的相片格：紀念冊還沒貼上照片的那一頁 -->
    <svg class="mb-4" width="48" height="58" viewBox="0 0 48 58" aria-hidden="true">
      <rect x="1" y="1" width="46" height="46" rx="2" fill="#F7F8F6" stroke="#C5CAC4" stroke-width="2" stroke-dasharray="5 4" />
      <circle cx="24" cy="19" r="6" fill="none" stroke="#C5CAC4" stroke-width="2" />
      <path d="M12 40a12 10 0 0124 0" fill="none" stroke="#C5CAC4" stroke-width="2" />
      <rect x="14" y="54" width="20" height="1.5" fill="#B8943A" />
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
