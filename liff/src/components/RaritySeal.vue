<template>
  <span
    class="seal"
    :class="`seal--${rarityKey}`"
    :style="{ width: `${size}px`, height: `${size}px`, fontSize: `${Math.round(size * 0.46)}px` }"
    :title="rarityOf(rarityKey).zh"
  >
    <img v-if="image" :src="image" alt="" class="rounded-full object-cover" :style="{ width: `${size - 14}px`, height: `${size - 14}px` }" />
    <span v-else aria-hidden="true">{{ emoji }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { rarityOf } from '@/constants/rarity'

// 紀念章：邊框加工依稀有度而不同（平印 / 壓紋 / 燙綠箔 / 燙金 / 鐳射箔）
const props = withDefaults(defineProps<{
  rarity?: string | null
  emoji?: string | null
  image?: string | null
  size?: number
}>(), { size: 48 })

const rarityKey = computed(() => rarityOf(props.rarity).key)
</script>
