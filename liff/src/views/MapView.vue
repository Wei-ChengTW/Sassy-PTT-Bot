<template>
  <div>
    <PageSign title="足跡探索地圖" en="Footprints" line="trip">
      <template #action>
        <button
          @click="fitBounds"
          class="text-xs font-bold px-3 py-2 rounded-md bg-white text-cloth hover:bg-slate-100 btn-press inline-flex items-center gap-1"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" /></svg>
          全景視角
        </button>
      </template>
      <span class="font-num">{{ places.length }}</span> 個地點、<span class="font-num">{{ mappedTrips.length }}</span> 個回憶
    </PageSign>

    <!-- 地圖容器 -->
    <div class="relative rounded-xl overflow-hidden border border-slate-200 bg-slate-100 h-[calc(100vh-330px)] min-h-[340px]">
      <div id="footprint-map" class="w-full h-full z-10" />
      <div v-if="error" class="absolute inset-0 z-20 bg-white/95 flex items-center justify-center px-6 text-center">
        <p class="text-sm text-slate-700 font-bold">載入足跡失敗：{{ error }}</p>
      </div>
      <div v-if="loading" class="absolute inset-0 z-20 bg-white/80 flex items-center justify-center">
        <p class="text-sm text-slate-600 font-bold">載入足跡地圖中...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { api } from '@/api/client'
import { resolveLocationCoords } from '@/constants/locations'
import { rarityOf } from '@/constants/rarity'
import PageSign from '@/components/PageSign.vue'
import { labelFor } from '@/constants/tripTypes'
import { tripPhase } from '@/constants/tripStatus'

const trips = ref<any[]>([])
const loading = ref(true)
const error = ref('')
let map: L.Map | null = null
let markerLayer: L.LayerGroup | null = null

const mappedTrips = computed(() => {
  return trips.value
    .map((t) => {
      const coords = resolveLocationCoords(t.location, t.title)
      return coords ? { ...t, coords } : null
    })
    .filter(Boolean) as (any & { coords: [number, number] })[]
})

function initMap() {
  const container = document.getElementById('footprint-map')
  if (!container) return

  // 預設中心為台灣
  map = L.map('footprint-map', {
    center: [23.9756, 120.9738],
    zoom: 7,
    zoomControl: false,
  })

  L.control.zoom({ position: 'bottomright' }).addTo(map)

  // CARTO 免費圖磚已改成需要 API key（只回「API KEY REQUIRED」浮水印），改用 OpenStreetMap
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19,
  }).addTo(map)

  markerLayer = L.layerGroup().addTo(map)
  renderMarkers()
}

// 名稱等文字插進 Leaflet 的 HTML 前先跳脫
function esc(text: unknown): string {
  return String(text ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!))
}

function tripDate(t: any): string {
  return t.start_date ? new Date(t.start_date * 1000).toLocaleDateString('zh-TW') : ''
}

// 同一組座標的旅程合成一個圖釘（台北、內湖高中各有十幾趟，分開放會完全疊在一起）
const places = computed(() => {
  const byKey = new Map<string, { coords: [number, number]; trips: any[] }>()
  for (const t of mappedTrips.value) {
    const key = t.coords.join(',')
    if (!byKey.has(key)) byKey.set(key, { coords: t.coords, trips: [] })
    byKey.get(key)!.trips.push(t)
  }
  return [...byKey.values()].map((p) => ({
    ...p,
    trips: [...p.trips].sort((a, b) => (b.start_date || 0) - (a.start_date || 0)),
  }))
})

function singlePopup(t: any): string {
  const emoji = esc(t.custom_emoji || t.badge_emoji || '🎒')
  const tagsHtml = (t.trip_types || [])
    .map((ty: string) => esc(labelFor(ty)))
    .join('、')
  const upcoming = tripPhase(t) === 'upcoming' ? ' · <span class="text-accent-700 font-bold">規劃中</span>' : ''
  return `
    <div class="max-w-[220px] font-sans">
      <div class="flex items-center gap-2">
        <span class="text-xl" aria-hidden="true">${emoji}</span>
        <p class="font-bold text-sm text-slate-900 leading-tight">${esc(t.title)}</p>
      </div>
      <p class="text-xs text-slate-600 mt-1.5">${esc(t.location || '群組回憶')}</p>
      <p class="text-xs text-slate-500 font-num mt-0.5">${tripDate(t)}${upcoming}</p>
      ${tagsHtml ? `<p class="text-xs text-slate-600 mt-1">${tagsHtml}</p>` : ''}
      <a href="/trips/${encodeURIComponent(t.id)}" class="mt-2.5 block w-full text-center bg-brand-500 hover:bg-brand-600 !text-white rounded-md py-2 text-xs font-bold no-underline">
        查看事件詳情
      </a>
    </div>
  `
}

function listPopup(trips: any[]): string {
  const items = trips.map((t) => `
    <a href="/trips/${encodeURIComponent(t.id)}" class="flex items-center gap-2 px-2 py-2 rounded hover:bg-slate-50 no-underline">
      <span class="text-base" aria-hidden="true">${esc(t.custom_emoji || t.badge_emoji || '🎒')}</span>
      <span class="flex-1 min-w-0">
        <span class="block text-xs font-bold text-slate-900 truncate">${esc(t.title)}</span>
        <span class="block text-[11px] text-slate-500 font-num">${tripDate(t)}${tripPhase(t) === 'upcoming' ? ' · 規劃中' : ''}</span>
      </span>
    </a>`).join('')
  return `
    <div class="font-sans w-[220px]">
      <p class="text-xs font-bold text-slate-900 px-2 pb-1.5 border-b border-slate-100 mb-1">${esc(trips[0].location || '群組回憶')} · ${trips.length} 個回憶</p>
      <div class="max-h-60 overflow-y-auto">${items}</div>
    </div>
  `
}

function renderMarkers() {
  if (!map || !markerLayer) return
  markerLayer.clearLayers()
  const bounds: L.LatLngBounds = L.latLngBounds([])

  places.value.forEach(({ coords, trips }) => {
    const top = trips[0]                       // 最新的一趟決定圖釘外觀
    const rarity = rarityOf(top.rarity)
    const emoji = esc(top.custom_emoji || top.badge_emoji || '🎒')
    const countBadge = trips.length > 1
      ? `<span class="absolute -top-1.5 -right-1.5 min-w-5 h-5 px-1 rounded-sm bg-cloth text-white text-[11px] font-num font-semibold flex items-center justify-center">${trips.length}</span>`
      : ''
    const icon = L.divIcon({
      className: 'custom-map-pin',
      html: `
        <div class="relative flex items-center justify-center w-11 h-11 rounded-full bg-white border-[3px] cursor-pointer" style="border-color:${rarity.line}; box-shadow: 0 2px 6px -2px rgba(25,29,26,.4)">
          <span class="text-2xl leading-none">${emoji}</span>
          ${countBadge}
        </div>
      `,
      iconSize: [44, 44],
      iconAnchor: [22, 22],
      popupAnchor: [0, -24],
    })
    const marker = L.marker(coords, { icon })
    marker.bindPopup(trips.length > 1 ? listPopup(trips) : singlePopup(top), { closeButton: false, minWidth: 170 })
    markerLayer!.addLayer(marker)
    bounds.extend(coords)
  })

  if (places.value.length && bounds.isValid()) {
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 })
  }
}

function fitBounds() {
  if (!map || !mappedTrips.value.length) return
  const bounds = L.latLngBounds(mappedTrips.value.map((t) => t.coords))
  if (bounds.isValid()) {
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 })
  }
}

onMounted(async () => {
  try {
    trips.value = await api.trips()
    await nextTick()
    initMap()
  } catch (e: any) {
    error.value = e?.message || '請求失敗'
    console.error(e)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style>
.custom-map-pin {
  background: transparent;
  border: none;
}
.leaflet-popup-content-wrapper {
  border-radius: 4px;
  box-shadow: 0 8px 20px -8px rgba(25, 29, 26, 0.35);
  border: 1px solid #DDE1DC;
  padding: 2px;
}
.leaflet-popup-tip {
  box-shadow: none;
  border: 1px solid #DDE1DC;
}
.leaflet-popup-content {
  margin: 10px 12px;
}
</style>
