<template>
  <div>
    <PageSign :title="detail?.trip.title || '管理旅行'" en="Manage Trip" back="返回">
      <template v-if="detail && !isEditing" #action>
        <button
          @click="startEdit"
          class="text-xs font-bold px-3 py-2 rounded-md bg-white text-cloth hover:bg-slate-100 btn-press inline-flex items-center gap-1"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16.9 4.1l3 3L8 19H5v-3L16.9 4.1z" /></svg>
          編輯資訊
        </button>
      </template>
    </PageSign>

    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-32 rounded-xl" />
      <div class="skeleton h-48 rounded-xl" />
    </div>

    <div v-else-if="detail" class="space-y-4">
      <!-- 資訊卡片 -->
      <BaseCard class="p-5">
        <!-- 檢視模式 -->
        <div v-if="!isEditing">
          <p class="text-sm font-bold text-slate-900">{{ detail.trip.location || '無指定地點' }}</p>
          
          <div v-if="detail.trip.trip_types && detail.trip.trip_types.length" class="flex flex-wrap gap-1.5 mt-3">
            <span
              v-for="ty in detail.trip.trip_types"
              :key="ty"
              class="inline-flex items-center rounded border border-slate-300 px-1.5 py-px text-xs text-slate-700"
            >
              {{ labelFor(ty) }}
            </span>
          </div>

          <div class="flex items-center gap-2 text-xs mt-3 pt-3 border-t border-slate-100">
            <span class="font-medium text-slate-600">
              狀態：
              <span :class="{ ended: 'text-slate-500', upcoming: 'text-accent-700 font-bold', ongoing: 'text-success-700 font-bold' }[tripPhase(detail.trip)]">
                {{ { ended: '已結束', upcoming: '規劃中', ongoing: '進行中' }[tripPhase(detail.trip)] }}
              </span>
            </span>
            <span
              v-if="detail.trip.rarity"
              class="inline-flex items-center gap-1 px-1.5 py-px rounded font-bold"
              :class="rarity.pill"
            >
              {{ rarity.zh }}
            </span>
          </div>
        </div>

        <!-- 編輯模式 -->
        <div v-else class="space-y-4">
          <div class="flex gap-3 items-start">
            <div class="w-18 shrink-0">
              <label class="block text-[13px] font-bold text-slate-700 mb-1.5">Emoji</label>
              <input
                v-model="editForm.custom_emoji"
                class="w-full bg-white border border-slate-300 rounded-md px-2 py-2 text-center text-xl focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                placeholder="🎒"
              />
            </div>
            <div class="flex-1 min-w-0">
              <label class="block text-[13px] font-bold text-slate-700 mb-1.5">旅行名稱 *</label>
              <input
                v-model="editForm.title"
                class="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                placeholder="例如：墾丁三日遊"
              />
            </div>
          </div>

          <div>
            <label class="block text-[13px] font-bold text-slate-700 mb-1.5">地點</label>
            <input
              v-model="editForm.location"
              class="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              placeholder="例如：墾丁"
            />
          </div>

          <!-- 日期編輯 -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[13px] font-bold text-slate-700 mb-1.5">開始日期 *</label>
              <input
                v-model="editForm.startDate"
                type="date"
                required
                class="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <div>
              <label class="flex items-center gap-1 text-[13px] font-bold text-slate-700 mb-1.5">
                結束日期
                <span class="text-[11px] text-slate-500 font-normal">（留空=當天）</span>
              </label>
              <input
                v-model="editForm.endDate"
                type="date"
                :min="editForm.startDate || undefined"
                class="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-sm font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              />
            </div>
          </div>

          <div v-if="tripKindLabel" class="text-xs text-slate-500">
            目前分類：<span :class="tripKindLabel.color">{{ tripKindLabel.text }}</span>
          </div>

          <div>
            <label class="block text-[13px] font-bold text-slate-700 mb-2">類型標籤（可複選）</label>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="t in TRIP_TYPES"
                :key="t.value"
                type="button"
                @click="toggleType(t.value)"
                class="rounded-md px-3 py-1.5 text-xs font-medium border transition-all duration-150 btn-press"
                :class="editForm.types.includes(t.value) ? 'bg-cloth text-white border-cloth'
                  : 'bg-white text-slate-700 border-slate-300 hover:border-slate-400'"
              >
                {{ t.label }}
              </button>
            </div>
          </div>

          <div>
            <label class="block text-[13px] font-bold text-slate-700 mb-2">稀有度等級</label>
            <div class="grid grid-cols-5 gap-1.5">
              <button
                v-for="r in rarityOptions"
                :key="r.key"
                type="button"
                @click="editForm.rarity = r.key"
                class="py-1.5 text-xs rounded-md border-2 font-bold transition-colors"
                :class="editForm.rarity === r.key ? 'bg-slate-900 text-white' : 'bg-white text-slate-700 hover:bg-slate-50'"
                :style="{ borderColor: r.line }"
                :aria-pressed="editForm.rarity === r.key"
              >
                {{ r.zh }}
              </button>
            </div>
          </div>

          <div class="flex items-center gap-2 pt-2 border-t border-slate-100">
            <button
              @click="saveEdit"
              :disabled="saving || !editForm.title.trim()"
              class="flex-1 bg-brand-500 hover:bg-brand-600 text-white text-sm py-2.5 rounded-md font-bold disabled:opacity-60 btn-press"
            >
              {{ saving ? '儲存中...' : '儲存變更' }}
            </button>
            <button
              @click="isEditing = false"
              class="px-4 py-2.5 border border-slate-300 text-sm font-medium rounded-md text-slate-700 hover:bg-slate-50 btn-press"
            >
              取消
            </button>
          </div>
        </div>
      </BaseCard>

      <!-- 參與人勾選卡片 -->
      <BaseCard class="p-5">
        <SectionHeader
          title="參與人員名單"
          :subtitle="`已選 ${selected.size} 人`"
          class="!mt-0 !mb-3"
        />

        <div v-if="membersLoading" class="text-xs text-slate-500 py-3">載入群組成員中...</div>
        <div v-else class="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto no-scrollbar pr-1">
          <label
            v-for="m in members"
            :key="m.user_id"
            class="flex items-center gap-2 rounded-md border px-3 py-2.5 text-[13px] cursor-pointer select-none transition-colors"
            :class="selected.has(m.user_id) ? 'border-brand-500 bg-brand-50 text-slate-900 font-bold' : 'border-slate-200 hover:bg-slate-50 text-slate-700'"
          >
            <input
              type="checkbox"
              :checked="selected.has(m.user_id)"
              @change="toggle(m.user_id)"
              class="accent-brand-500 w-4 h-4"
            />
            <span class="truncate" :class="m.resolved ? '' : 'text-slate-500'">
              {{ m.display_name }}
              <span v-if="!m.resolved" class="text-[11px]">（待接回）</span>
            </span>
          </label>
        </div>

        <button
          v-if="detail.trip.status !== 'ended'"
          @click="saveParticipants"
          :disabled="actionLoading"
          class="mt-4 w-full border border-slate-300 bg-white hover:bg-slate-50 text-slate-900 rounded-md py-3 text-sm font-bold disabled:opacity-60 btn-press"
        >
          僅儲存名單（活動繼續進行）
        </button>
        <button
          v-if="detail.trip.status !== 'ended'"
          @click="saveAndAward"
          :disabled="actionLoading || selected.size === 0"
          class="mt-2 w-full bg-brand-500 hover:bg-brand-600 text-white rounded-md py-3 text-sm font-bold disabled:opacity-60 btn-press"
        >
          儲存名單並結束活動、發放徽章
        </button>
        <button
          v-else
          @click="saveParticipants"
          :disabled="actionLoading"
          class="mt-4 w-full bg-brand-500 hover:bg-brand-600 text-white rounded-md py-3 text-sm font-bold disabled:opacity-60 btn-press"
        >
          更新參與名單
        </button>
      </BaseCard>

      <!-- 手動操作 -->
      <div class="space-y-2.5">
        <button
          v-if="detail.trip.status !== 'ended'"
          @click="endTrip"
          :disabled="actionLoading"
          class="w-full border border-slate-300 bg-white hover:bg-slate-50 text-slate-900 rounded-md py-3 text-sm font-bold disabled:opacity-60 btn-press"
        >
          僅結束旅行（不發徽章）
        </button>
        <button
          v-if="detail.trip.status === 'ended'"
          @click="awardBadges"
          :disabled="actionLoading"
          class="w-full border border-slate-300 bg-white hover:bg-slate-50 text-slate-900 rounded-md py-3 text-sm font-bold disabled:opacity-60 btn-press"
        >
          重新發放徽章
        </button>
      </div>

      <p v-if="message" class="text-center mt-3 text-sm font-bold text-success-700" role="status">{{ message }}</p>
      <p v-if="error" class="text-center mt-3 text-sm font-bold text-danger-600" role="alert">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import { RARITY } from '@/constants/rarity'
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'
import { rarityOf } from '@/constants/rarity'
import { TRIP_TYPES, emojiFor, labelFor } from '@/constants/tripTypes'
import BaseCard from '@/components/BaseCard.vue'
import SectionHeader from '@/components/SectionHeader.vue'
import { tripPhase } from '@/constants/tripStatus'

const route = useRoute()
const tripId = route.params.id as string

const detail = ref<any>(null)
const loading = ref(true)
const membersLoading = ref(true)
const actionLoading = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const editForm = ref({
  title: '',
  location: '',
  rarity: 'common',
  types: [] as string[],
  custom_emoji: '',
  startDate: '',
  endDate: '',
})
const members = ref<{ user_id: string; display_name: string; resolved: number }[]>([])
const selected = ref<Set<string>>(new Set())
const message = ref('')
const error = ref('')

const rarity = computed(() => rarityOf(detail.value?.trip?.rarity))

const tripKindLabel = computed(() => {
  const sd = editForm.value.startDate
  const ed = editForm.value.endDate
  if (!sd) return null
  if (ed && ed !== sd) return { text: '多日旅行', color: 'text-slate-900 font-bold' }
  return { text: '當天事件', color: 'text-slate-900 font-bold' }
})

const rarityOptions = Object.values(RARITY).map(r => ({ key: r.key, zh: r.zh, line: r.line }))

function toDateInput(ts: number | null | undefined) {
  if (!ts) return ''
  const d = new Date(ts * 1000)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function toggleType(typeVal: string) {
  const i = editForm.value.types.indexOf(typeVal)
  if (i >= 0) editForm.value.types.splice(i, 1)
  else editForm.value.types.push(typeVal)
}

function startEdit() {
  const t = detail.value?.trip || {}
  editForm.value = {
    title: t.title || '',
    location: t.location || '',
    rarity: t.rarity || 'common',
    types: [...(t.trip_types || [])],
    custom_emoji: t.custom_emoji || t.badge_emoji || '',
    startDate: toDateInput(t.start_date),
    endDate: toDateInput(t.end_date),
  }
  isEditing.value = true
}

async function saveEdit() {
  if (!editForm.value.title.trim() || saving.value) return
  saving.value = true
  message.value = ''; error.value = ''
  try {
    const startTs = editForm.value.startDate
      ? Math.floor(new Date(editForm.value.startDate).getTime() / 1000)
      : null
    const endTs = editForm.value.endDate
      ? Math.floor(new Date(editForm.value.endDate).getTime() / 1000)
      : null
    await api.adminUpdateTrip(tripId, {
      title: editForm.value.title.trim(),
      location: editForm.value.location.trim(),
      rarity: editForm.value.rarity,
      types: editForm.value.types,
      custom_emoji: editForm.value.custom_emoji.trim(),
      start_date: startTs,
      end_date: endTs,
    })
    await load()
    isEditing.value = false
    message.value = '旅行資訊修改成功'
  } catch (e: any) {
    error.value = e.message || '修改失敗'
  } finally {
    saving.value = false
  }
}

function toggle(userId: string) {
  const s = new Set(selected.value)
  s.has(userId) ? s.delete(userId) : s.add(userId)
  selected.value = s
}

async function load() {
  loading.value = true
  try {
    detail.value = await api.tripDetail(tripId)
    selected.value = new Set((detail.value?.participants || []).map((p: any) => p.user_id))
  } finally { loading.value = false }
}

async function loadMembers() {
  membersLoading.value = true
  try { members.value = await api.adminMembers() }
  catch (e: any) { error.value = e.message }
  finally { membersLoading.value = false }
}

async function saveParticipants() {
  actionLoading.value = true
  message.value = ''; error.value = ''
  try {
    const res = await api.adminAddParticipants(tripId, [...selected.value], true)
    await load()
    message.value = `名單已儲存（${res.total} 人，新增 ${res.added}、移除 ${res.removed}）`
  } catch (e: any) { error.value = e.message }
  finally { actionLoading.value = false }
}

async function saveAndAward() {
  if (!confirm('儲存參與人並結束事件、發放徽章？')) return
  actionLoading.value = true
  message.value = ''; error.value = ''
  try {
    await api.adminAddParticipants(tripId, [...selected.value], true)
    await api.adminEndTrip(tripId)
    const res = await api.adminAwardBadges(tripId)
    await load()
    message.value = `已結束並發放 ${res.awarded.length} 枚徽章`
  } catch (e: any) { error.value = e.message }
  finally { actionLoading.value = false }
}

async function endTrip() {
  if (!confirm('確定只結束旅行（不發徽章）？')) return
  actionLoading.value = true
  message.value = ''; error.value = ''
  try {
    await api.adminEndTrip(tripId)
    await load()
    message.value = '旅行已結束'
  } catch (e: any) { error.value = e.message }
  finally { actionLoading.value = false }
}

async function awardBadges() {
  actionLoading.value = true
  message.value = ''; error.value = ''
  try {
    const res = await api.adminAwardBadges(tripId)
    message.value = `已發放 ${res.awarded.length} 枚徽章`
  } catch (e: any) { error.value = e.message }
  finally { actionLoading.value = false }
}

onMounted(() => { load(); loadMembers() })
</script>
