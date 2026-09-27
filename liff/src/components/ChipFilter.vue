<template>
  <div :class="scroll ? 'scroll-row' : 'flex flex-wrap gap-1.5'">
    <button
      v-if="showAll"
      type="button"
      @click="$emit('update:modelValue', '')"
      class="rounded-md px-3 py-1.5 text-xs font-medium border btn-press whitespace-nowrap shrink-0"
      :class="modelValue === '' ? activeCls : idleCls"
      :aria-pressed="modelValue === ''"
    >
      {{ allLabel }}
    </button>
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      @click="(e) => { $emit('update:modelValue', opt.value); reveal(e) }"
      class="rounded-md px-3 py-1.5 text-xs font-medium border btn-press inline-flex items-center gap-1 whitespace-nowrap shrink-0"
      :class="modelValue === opt.value ? activeCls : idleCls"
      :aria-pressed="modelValue === opt.value"
    >
      <span>{{ opt.label }}</span>
      <span v-if="opt.count !== undefined" class="font-num text-[11px] opacity-70">{{ opt.count }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
export interface ChipOption {
  value: string
  label: string
  emoji?: string
  count?: number
}

const activeCls = 'bg-cloth text-white border-cloth'
const idleCls = 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'

withDefaults(
  defineProps<{
    modelValue: string
    options: ChipOption[]
    showAll?: boolean
    allLabel?: string
    scroll?: boolean
  }>(),
  {
    showAll: true,
    allLabel: '全部',
  }
)

// 選取時把按鈕完整捲進可視範圍
function reveal(e: MouseEvent) {
  (e.currentTarget as HTMLElement).scrollIntoView({ behavior: 'smooth', inline: 'nearest', block: 'nearest' })
}

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>
