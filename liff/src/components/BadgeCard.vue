<template>
  <FoilCard :rarity="badge.badge_rarity" :delay="delay"
            class="rounded-xl border bg-white p-3.5 flex items-center gap-3.5 select-none touch-pan-y" :class="rarityStyle.card">
    <RaritySeal :rarity="badge.badge_rarity" :emoji="badge.badge_emoji" :image="badge.badge_image_url" :size="56" />

    <div class="flex-1 min-w-0 relative z-[3]">
      <p class="font-bold text-sm truncate" :class="rarityStyle.name">
        {{ badge.badge_name }}
      </p>
      <div class="flex items-center gap-2 mt-1.5">
        <span class="inline-flex items-center px-1.5 py-px rounded text-[11px] font-bold" :class="rarityStyle.pill">
          {{ rarityStyle.zh }}
        </span>
        <p v-if="displayDate" class="font-num text-xs" :class="rarityStyle.date">
          {{ displayDate }}
        </p>
      </div>
    </div>
  </FoilCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { rarityOf } from '@/constants/rarity'
import FoilCard from '@/components/FoilCard.vue'
import RaritySeal from '@/components/RaritySeal.vue'

const props = withDefaults(defineProps<{ badge: any; delay?: number }>(), { delay: 0.4 })

const rarityStyle = computed(() => rarityOf(props.badge.badge_rarity))
const displayDate = computed(() => {
  const ts = props.badge.start_date || props.badge.earned_at
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleDateString('zh-TW')
})
</script>
