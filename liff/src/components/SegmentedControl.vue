<template>
  <div class="inline-flex rounded-md border border-slate-300 bg-white overflow-hidden">
    <button
      v-for="(opt, i) in options"
      :key="opt.value"
      type="button"
      @click="$emit('update:modelValue', opt.value)"
      class="px-3 py-1.5 text-xs font-medium transition-colors"
      :class="[
        modelValue === opt.value ? 'bg-cloth text-white' : 'text-slate-600 hover:bg-slate-50',
        i > 0 ? 'border-l border-slate-300' : '',
      ]"
      :aria-pressed="modelValue === opt.value"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
export interface SegmentOption {
  value: string
  label: string
}

defineProps<{
  modelValue: string
  options: SegmentOption[]
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>
