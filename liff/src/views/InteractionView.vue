<template>
  <div>
    <PageSign title="群組互動關係網絡" en="Interactions" />

    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-32 rounded-xl" />
      <div class="skeleton h-64 rounded-xl" />
    </div>

    <EmptyState
      v-else-if="error"
      title="無法載入互動資料"
      :description="error"
    />

    <div v-else-if="data">
      <!-- 最佳拍檔 -->
      <div>
        <SectionHeader title="群組最佳拍檔" subtitle="依雙向回覆次數" class="!mt-0" />
        <BaseCard class="overflow-hidden">
          <div v-if="!data.best_pairs.length" class="px-4 py-8 text-sm text-slate-500 text-center">
            尚無回覆互動資料
          </div>
          <div v-else class="divide-y divide-slate-100">
            <div
              v-for="(pair, i) in data.best_pairs"
              :key="i"
              class="flex items-center px-3.5 py-3 gap-3"
            :class="pairRanks[i] === 1 ? 'bg-accent-50' : ''"
            >
              <RankChip :rank="pairRanks[i]" size="sm" />
              <span class="flex-1 min-w-0 text-sm font-bold text-slate-900 flex items-center gap-1.5">
                <span class="truncate">{{ pair.user1_name || pair.user1_id }}</span>
                <svg class="w-6 h-2.5 shrink-0" viewBox="0 0 24 10" aria-label="與"><line x1="4" y1="5" x2="20" y2="5" stroke="#2346A0" stroke-width="3" /><circle cx="4" cy="5" r="3" fill="#fff" stroke="#2346A0" stroke-width="2" /><circle cx="20" cy="5" r="3" fill="#fff" stroke="#2346A0" stroke-width="2" /></svg>
                <span class="truncate">{{ pair.user2_name || pair.user2_id }}</span>
              </span>
              <span class="font-num text-[17px] font-semibold text-slate-900 shrink-0">
                {{ pair.count }}<span class="font-sans text-xs font-normal text-slate-500 ml-1">次回覆</span>
              </span>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- 社交網絡圖 -->
      <div>
        <SectionHeader title="社交引力網絡圖" />
        <BaseCard class="p-4 flex flex-col items-center min-h-[300px] justify-center">
          <svg
            v-show="data.network_edges && data.network_edges.length"
            ref="svgRef"
            :width="svgW"
            :height="svgH"
            class="w-full max-w-[340px]"
          />
          <p v-if="!data.network_edges || !data.network_edges.length" class="text-center text-xs text-slate-500 py-6">
            互動數據尚不足以繪製網絡圖
          </p>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { competitionRanks } from '@/utils/rank'
import PageSign from '@/components/PageSign.vue'
import RankChip from '@/components/RankChip.vue'
import * as d3 from 'd3'
import { api } from '@/api/client'
import { useRefreshOnAnalysis } from '@/composables/useRefreshOnAnalysis'
import BaseCard from '@/components/BaseCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SectionHeader from '@/components/SectionHeader.vue'

const data = ref<any>(null)
// 同分同名次
const pairRanks = computed(() => competitionRanks(data.value?.best_pairs || [], (p: any) => p.count))
const loading = ref(true)
const error = ref('')
const svgRef = ref<SVGSVGElement | null>(null)
const simRef = ref<any>(null)
const svgW = 340
const svgH = 280

function drawGraph() {
  if (!svgRef.value || !data.value?.network_edges?.length) return

  const nodes: any[] = (data.value.network_nodes || []).map((n: any) => ({ ...n }))
  const links: any[] = (data.value.network_edges || []).map((e: any) => ({
    source: e.source, target: e.target, weight: e.weight,
  }))

  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  const maxMsg = Math.max(...nodes.map((n: any) => n.message_count), 1)
  const rScale = d3.scaleSqrt().domain([0, maxMsg]).range([10, 24])
  const maxW = Math.max(...links.map((l: any) => l.weight), 1)
  const strokeScale = d3.scaleLinear().domain([0, maxW]).range([1.5, 6])

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id((d: any) => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-120))
    .force('center', d3.forceCenter(svgW / 2, svgH / 2))
    .force('collision', d3.forceCollide().radius((d: any) => rScale(d.message_count) + 5))
  simRef.value = sim

  const link = svg.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', '#1E3A2F')
    .attr('stroke-opacity', 0.55)
    .attr('stroke-linecap', 'round')
    .attr('stroke-width', (d: any) => strokeScale(d.weight))

  const node = svg.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .call(d3.drag<any, any>()
      .on('start', (event, d) => {
        if (!event.active) sim.alphaTarget(0.3).restart()
        d.fx = d.x; d.fy = d.y
      })
      .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y })
      .on('end', (event, d) => {
        if (!event.active) sim.alphaTarget(0)
        d.fx = null; d.fy = null
      }))

  node.append('circle')
    .attr('r', (d: any) => rScale(d.message_count))
    .attr('fill', '#ffffff')
    .attr('stroke', '#1E3A2F')
    .attr('stroke-width', 3)
    .attr('class', 'cursor-grab active:cursor-grabbing')

  node.append('text')
    .text((d: any) => (d.name || d.id).slice(0, 4))
    .attr('text-anchor', 'middle')
    .attr('dy', (d: any) => rScale(d.message_count) + 12)
    .attr('font-size', 11)
    .attr('font-family', '"Noto Sans TC", sans-serif')
    .attr('font-weight', '700')
    .attr('fill', '#191D1A')
    .attr('paint-order', 'stroke')
    .attr('stroke', '#ffffff')
    .attr('stroke-width', 3)
    .attr('pointer-events', 'none')

  sim.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y)
    node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
  })
}

onUnmounted(() => {
  if (simRef.value) simRef.value.stop()
})

async function loadInteractions() {
  try {
    loading.value = true
    data.value = await api.interactions()
  } catch (e: any) {
    error.value = e?.message || '請求失敗'
    console.error(e)
  } finally {
    loading.value = false
    await nextTick()
    setTimeout(() => {
      drawGraph()
    }, 50)
  }
}

onMounted(async () => {
  await loadInteractions()
})

watch(() => data.value, () => {
  nextTick(() => drawGraph())
})

useRefreshOnAnalysis(loadInteractions)
</script>
