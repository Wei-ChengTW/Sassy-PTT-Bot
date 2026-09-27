<template>
  <div
    ref="el"
    class="foil-card"
    :class="{ 'is-active': active }"
    :style="{ '--sheen-delay': `${delay}s` }"
    @pointermove="onMove"
    @pointerenter="onMove"
    @pointerleave="reset"
    @pointercancel="reset"
  >
    <slot />
    <template v-if="tier >= 3">
      <span class="foil-layer foil-glare" aria-hidden="true" />
    </template>
    <span v-if="tier >= 4" class="foil-layer foil-sheen" aria-hidden="true" />
    <span v-if="tier >= 5" class="foil-layer foil-holo" aria-hidden="true" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { rarityOf } from '@/constants/rarity'

// 箔面卡片：光源位置（--mx/--my）由指標驅動；傳說等級另外會 3D 傾斜。
const props = withDefaults(defineProps<{ rarity?: string | null; delay?: number }>(), { delay: 0.4 })

const el = ref<HTMLElement | null>(null)
const active = ref(false)
const tier = computed(() => rarityOf(props.rarity).order)
const reduced = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

function onMove(e: PointerEvent) {
  if (tier.value < 3 || reduced || !el.value) return
  const r = el.value.getBoundingClientRect()
  const x = Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1)
  const y = Math.min(Math.max((e.clientY - r.top) / r.height, 0), 1)
  const s = el.value.style
  active.value = true
  s.setProperty('--mx', `${x * 100}%`)
  s.setProperty('--my', `${y * 100}%`)
  s.setProperty('--glare', '1')
  s.setProperty('--sheen-x', `${120 - x * 140}%`)
  if (tier.value >= 5) {
    s.setProperty('--rx', `${(0.5 - y) * 10}deg`)
    s.setProperty('--ry', `${(x - 0.5) * 12}deg`)
  }
}

function reset() {
  active.value = false
  const s = el.value?.style
  if (!s) return
  s.setProperty('--glare', '0')
  s.setProperty('--rx', '0deg')
  s.setProperty('--ry', '0deg')
  s.removeProperty('--sheen-x')
}
</script>
