<template>
  <header class="sign -mx-4 px-4 pt-5 pb-5 mb-6">
    <button v-if="back" type="button" @click="$router.back()"
            class="-ml-2 -mt-2 mb-2 px-2 py-1.5 text-xs text-[#C9D3CC] hover:text-white inline-flex items-center gap-1">
      <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M15 6l-6 6 6 6" /></svg>
      {{ back }}
    </button>
    <div class="flex items-end justify-between gap-3">
      <div class="min-w-0">
        <h1 class="font-display text-[28px] leading-[1.2] font-black break-words">
          <slot name="title">{{ title }}</slot>
        </h1>
        <p v-if="en" class="sign-en text-[13px] mt-1">{{ en }}</p>
      </div>
      <div v-if="$slots.action" class="shrink-0 pb-0.5">
        <slot name="action" />
      </div>
    </div>
    <div class="foil-rule mt-4 w-12" aria-hidden="true" />
    <div v-if="$slots.default" class="mt-2.5 text-xs text-[#C9D3CC]">
      <slot />
    </div>
    <div v-if="$slots.figures" class="mt-5">
      <slot name="figures" />
    </div>
  </header>
</template>

<script setup lang="ts">
import type { LineKey } from '@/constants/lines'

withDefaults(defineProps<{ title?: string; en?: string; line?: LineKey; back?: string }>(), { line: 'data' })
</script>
