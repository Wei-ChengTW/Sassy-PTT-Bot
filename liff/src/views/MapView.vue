<template>
  <div class="flex flex-col h-[calc(100vh-145px)] space-y-3">
    <!-- 頂部資訊與過濾 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
          <span>🌍 足跡探索地圖</span>
        </h1>
        <p class="text-xs text-slate-400 mt-0.5 font-medium">
          <span class="font-bold font-mono text-brand-600">{{ places.length }}</span> 個地點、
          <span class="font-bold font-mono text-brand-600">{{ mappedTrips.length }}</span> 個回憶
        </p>
      </div>
      <button
        @click="fitBounds"
        class="text-xs px-3 py-1.5 bg-white border border-slate-200 rounded-xl shadow-xs font-bold text-slate-600 hover:text-brand-600 hover:border-brand-200 active:scale-95 transition-all btn-press inline-flex items-center gap-1"
      >
        <span>🎯</span>
        <span>全景視角</span>
      </button>
    </div>

    <!-- 地圖容器 -->
    <div class="flex-1 relative rounded-2xl overflow-hidden shadow-card border border-slate-200/80 bg-slate-100 min-h-[350px]">
      <div id="footprint-map" class="w-full h-full z-10" />
      <div v-if="error" class="absolute inset-0 z-20 bg-white/90 flex items-center justify-center px-6 text-center">
        <div>
          <p class="text-3xl">⚠️</p>
          <p class="text-xs text-slate-500 font-bold mt-2">載入足跡失敗：{{ error }}</p>
        </div>
      </div>
      <div v-if="loading" class="absolute inset-0 z-20 bg-white/70 backdrop-blur-xs flex items-center justify-center">
        <div class="text-center">
          <p class="text-3xl animate-bounce">🌍</p>
          <p class="text-xs text-slate-500 font-bold mt-2">載入足跡地圖中...</p>
        </div>
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
import { emojiFor, labelFor } from '@/constants/tripTypes'
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
    .map((ty: string) => `<span class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-brand-50 text-[10px] text-brand-700 font-semibold border border-brand-100">${emojiFor(ty)} ${esc(labelFor(ty))}</span>`)
    .join(' ')
  const upcoming = tripPhase(t) === 'upcoming' ? ' · <span class="text-amber-600 font-bold">規劃中</span>' : ''
  return `
    <div class="p-1 max-w-[210px] font-sans">
      <div class="flex items-center gap-1.5">
        <span class="text-xl">${emoji}</span>
        <p class="font-bold text-sm text-slate-900 leading-tight">${esc(t.title)}</p>
      </div>
      <p class="text-[11px] text-slate-500 font-medium mt-1">📍 ${esc(t.location || '群組回憶')}</p>
      <p class="text-[10px] text-slate-400 font-mono mt-0.5">🗓️ ${tripDate(t)}${upcoming}</p>
      <div class="mt-2 flex flex-wrap gap-1">${tagsHtml}</div>
      <a href="/trips/${encodeURIComponent(t.id)}" class="mt-2.5 block w-full text-center bg-brand-600 hover:bg-brand-700 text-white rounded-xl py-1.5 text-xs font-bold no-underline transition-colors shadow-xs">
        查看事件詳情 →
      </a>
    </div>
  `
}

function listPopup(trips: any[]): string {
  const items = trips.map((t) => `
    <a href="/trips/${encodeURIComponent(t.id)}" class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-50 no-underline">
      <span class="text-base">${esc(t.custom_emoji || t.badge_emoji || '🎒')}</span>
      <span class="flex-1 min-w-0">
        <span class="block text-xs font-bold text-slate-800 truncate">${esc(t.title)}</span>
        <span class="block text-[10px] text-slate-400 font-mono">${tripDate(t)}${tripPhase(t) === 'upcoming' ? ' · 規劃中' : ''}</span>
      </span>
    </a>`).join('')
  return `
    <div class="font-sans w-[220px]">
      <p class="text-xs font-bold text-slate-600 px-2 pb-1.5">📍 ${esc(trips[0].location || '群組回憶')} · ${trips.length} 個回憶</p>
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
      ? `<span class="absolute -top-1.5 -right-1.5 min-w-5 h-5 px-1 rounded-full bg-slate-900 text-white text-[10px] font-bold flex items-center justify-center border-2 border-white">${trips.length}</span>`
      : `<span class="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full border-2 border-white ${rarity.dot}"></span>`
    const icon = L.divIcon({
      className: 'custom-map-pin',
      html: `
        <div class="relative flex items-center justify-center w-11 h-11 rounded-2xl shadow-lift border-2 border-white transition-all hover:scale-115 active:scale-95 cursor-pointer ${rarity.card}">
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
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -12px rgba(15, 23, 42, 0.2);
  border: 1px solid rgba(226, 232, 240, 0.8);
  padding: 4px;
}
.leaflet-popup-content {
  margin: 10px 12px;
}
</style>
