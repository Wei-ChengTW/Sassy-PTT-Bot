<template>
  <div v-if="rows.length">
    <!-- 第 1 名：班級之最 -->
    <div class="sign rounded-xl px-4 pt-3.5 pb-4 text-white relative overflow-hidden">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <p class="text-xs text-[#D6B872]">第 <span class="font-num">{{ ranks[0] }}</span> 名</p>
          <p class="font-display text-[24px] leading-tight font-black truncate mt-0.5">{{ rows[0].name }}</p>
          <div v-if="rows[0].sub || $slots.detail" class="text-xs text-[#C9D3CC] mt-1">
            <slot name="detail" :row="rows[0]" :tone="'cover'">{{ rows[0].sub }}</slot>
          </div>
        </div>
        <p class="font-num text-[34px] leading-none font-semibold text-[#E6D09A] shrink-0 pt-1">
          {{ rows[0].valueStr }}<span v-if="unit" class="font-sans text-xs font-normal text-[#C9D3CC] ml-1">{{ unit }}</span>
        </p>
      </div>
      <div class="foil-rule mt-3.5 opacity-70" aria-hidden="true" />
    </div>

    <!-- 第 2、3 名 -->
    <div v-if="rows.length > 1" class="grid grid-cols-2 gap-2 mt-2">
      <div v-for="(r, j) in rows.slice(1, 3)" :key="r.id"
           class="relative overflow-hidden rounded-xl border px-3.5 pt-3.5 pb-3 min-w-0"
           :class="j === 0 ? 'medal--silver' : 'medal--bronze'">
        <span class="medal-foil" aria-hidden="true" />
        <div class="flex items-center gap-2">
          <RankChip :rank="ranks[j + 1]" size="sm" />
          <p class="text-[15px] font-bold text-slate-900 truncate">{{ r.name }}</p>
        </div>
        <p class="font-num text-[22px] font-semibold text-slate-900 mt-2 leading-none">
          {{ r.valueStr }}<span v-if="unit" class="font-sans text-xs font-normal text-slate-500 ml-1">{{ unit }}</span>
        </p>
        <div v-if="r.sub || $slots.detail" class="text-[11px] text-slate-500 mt-1.5 truncate">
          <slot name="detail" :row="r" :tone="'page'">{{ r.sub }}</slot>
        </div>
      </div>
    </div>

    <!-- 第 4 名之後：比例條 -->
    <ol v-if="rows.length > 3" class="mt-2 bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
      <li v-for="(r, j) in rows.slice(3)" :key="r.id" class="px-3.5 py-2.5">
        <div class="flex items-start gap-3">
          <span class="font-num text-[15px] leading-5 font-semibold text-slate-500 w-5 text-right shrink-0">{{ ranks[j + 3] }}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline justify-between gap-2">
              <p class="text-sm leading-5 font-bold text-slate-900 truncate">{{ r.name }}</p>
              <p class="font-num text-[15px] font-semibold text-slate-900 shrink-0">
                {{ r.valueStr }}<span v-if="unit" class="font-sans text-[11px] font-normal text-slate-500 ml-0.5">{{ unit }}</span>
              </p>
            </div>
            <div class="h-1 mt-1.5 bg-slate-100 rounded-full overflow-hidden" aria-hidden="true">
              <div class="h-full bg-cloth rounded-full transition-[width] duration-700 ease-out-expo"
                   :style="{ width: ready ? `${ratio(r)}%` : '0%', transitionDelay: `${j * 45}ms` }" />
            </div>
            <div v-if="r.sub || $slots.detail" class="text-[11px] text-slate-500 mt-1 truncate">
              <slot name="detail" :row="r" :tone="'page'">{{ r.sub }}</slot>
            </div>
          </div>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import RankChip from '@/components/RankChip.vue'

export interface RankRow {
  id: string
  name: string
  value: number
  valueStr: string
  sub?: string | null
  [k: string]: any
}

// 班級之最：第 1 名封面塊、2–3 名並排、其餘附與第 1 名的比例條
// invert：數值越小越好（例如回覆分鐘數），比例條以最佳值為滿格
const props = defineProps<{ rows: RankRow[]; ranks: number[]; unit?: string; invert?: boolean }>()

const ready = ref(false)
onMounted(() => requestAnimationFrame(() => { ready.value = true }))

const top = computed(() => Math.max(...props.rows.map(r => Math.abs(r.value)), 0))
const best = computed(() => Math.min(...props.rows.map(r => Math.abs(r.value))))
function ratio(r: RankRow) {
  if (props.invert) return r.value ? Math.max(3, Math.round(best.value / Math.abs(r.value) * 100)) : 0
  if (!top.value) return 0
  return Math.max(3, Math.round(Math.abs(r.value) / top.value * 100))
}
</script>
