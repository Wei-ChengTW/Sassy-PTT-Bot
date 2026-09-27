<template>
  <div class="flex items-center justify-between gap-3 mb-3 mt-8">
    <div class="flex items-baseline gap-2 min-w-0">
      <span class="chapter-mark shrink-0 self-center" aria-hidden="true" />
      <h2 class="font-bold text-[15px] text-slate-900 truncate">
        {{ title }}
      </h2>
      <span v-if="subtitle" class="text-xs text-slate-500 truncate">
        {{ subtitle }}
      </span>
    </div>
    <div v-if="$slots.action" class="flex items-center gap-1.5 shrink-0">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>
