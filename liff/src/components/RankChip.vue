<template>
  <span
    class="seat-chip shrink-0"
    :class="[rank <= 3 ? 'seat-chip--solid' : '', size === 'sm' ? '!min-w-[1.625rem] !h-[1.625rem] !text-[0.85rem]' : '']"
    :style="{ '--line': lineColor }"
    :aria-label="`第 ${rank} 名`"
  >{{ rank }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ rank: number; size?: 'sm' | 'md' }>(), { size: 'md' })

// 座號格：第 1 名金、第 2 名銀、第 3 名銅（實心），其餘灰框
const lineColor = computed(() =>
  props.rank === 1 ? '#C6A252' : props.rank === 2 ? '#BFC7C5' : props.rank === 3 ? '#C8956A' : '#C5CAC4',
)
</script>
