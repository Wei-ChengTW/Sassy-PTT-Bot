<template>
  <div
    class="rounded-xl border"
    :class="[
      variantClasses,
      interactive ? 'btn-press cursor-pointer hover:border-slate-300' : '',
    ]"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'surface' | 'brand' | 'subtle' | 'elevated'
    interactive?: boolean
  }>(),
  {
    variant: 'surface',
    interactive: false,
  }
)

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'brand':
      return 'bg-brand-50 border-brand-100'
    case 'subtle':
      return 'bg-slate-50 border-slate-200'
    case 'elevated':
    case 'surface':
    default:
      return 'bg-white border-slate-200'
  }
})
</script>
