<template>
  <div>
    <PageSign title="本週稱號" en="Nicknames" line="people" />

    <!-- 說明 -->
    <BaseCard variant="subtle" class="p-4">
      <p class="text-sm font-bold text-slate-900 mb-2">這是什麼？</p>
      <ul class="text-[13px] text-slate-600 leading-relaxed space-y-1 list-disc pl-4 marker:text-slate-400">
        <li>機器人每週日凌晨看一次大家最近的發言，幫每個人取一個暫時稱號。</li>
        <li>最近 7 天講超過 30 句就看 7 天；不夠就看 30 天；再不夠就跳過。</li>
        <li>每人最多留 {{ data?.max_per_member ?? 3 }} 個，新的進來就把最舊的擠掉。</li>
        <li>不會在群組公布，機器人聊天時會默默拿來叫你，而且比一般外號更常用。</li>
      </ul>
    </BaseCard>

    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-28 rounded-xl" />
      <div class="skeleton h-28 rounded-xl" />
    </div>

    <EmptyState
      v-else-if="error"
      title="無法載入稱號"
      :description="error"
    />

    <EmptyState
      v-else-if="!data?.members.length"
      title="還沒有稱號"
      description="機器人還沒幫大家取過稱號，等這週日凌晨再來看看。"
    />

    <div v-else>
      <SectionHeader title="成員稱號" :subtitle="`${data.members.length} 人`" />
      <div class="space-y-3">
        <article v-for="m in data.members" :key="m.name" class="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <!-- 個人簡介：照片 + 名字 + 本週稱號 -->
          <div class="flex gap-4 p-4">
            <div class="w-[76px] h-[92px] shrink-0 rounded-md overflow-hidden bg-slate-100 border border-slate-200 flex items-center justify-center">
              <img v-if="m.picture_url" :src="m.picture_url" :alt="m.name" class="w-full h-full object-cover" loading="lazy" />
              <svg v-else class="w-9 h-9 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.5 20.1a7.5 7.5 0 0115 0" /></svg>
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-[17px] font-black text-slate-900 truncate">{{ m.name }}</p>
              <p v-if="m.aliases.length" class="text-xs text-slate-500 truncate mt-0.5">
                又稱 {{ m.aliases.slice(0, 3).join('、') }}
              </p>
              <template v-if="m.auto_aliases[0]">
                <p class="text-xs text-accent-700 mt-2.5">本週稱號</p>
                <p class="font-hand text-[22px] leading-tight font-bold text-cloth mt-0.5 break-words">{{ m.auto_aliases[0].name }}</p>
                <div class="foil-rule w-10 mt-1.5" aria-hidden="true" />
              </template>
            </div>
          </div>
          <div v-if="m.auto_aliases[0]" class="px-4 pb-3.5 -mt-1">
            <p class="text-[13px] text-slate-700 leading-relaxed">{{ m.auto_aliases[0].reason }}</p>
            <p class="text-[11px] text-slate-500 mt-1 font-num">{{ m.auto_aliases[0].created }} · 看 {{ m.auto_aliases[0].window_days }} 天</p>
          </div>
          <!-- 過去稱號 -->
          <div v-if="m.auto_aliases.length > 1" class="border-t border-slate-100 bg-slate-50 px-4 py-2.5">
            <p class="text-[11px] text-slate-500 mb-1">過去稱號</p>
            <ul class="space-y-1.5">
              <li v-for="a in m.auto_aliases.slice(1)" :key="a.name + a.created" class="text-xs">
                <span class="font-hand text-[14px] font-bold text-slate-800">{{ a.name }}</span>
                <span class="text-slate-500 font-num ml-1.5">{{ a.created }}</span>
                <p class="text-slate-600 leading-relaxed">{{ a.reason }}</p>
              </li>
            </ul>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import { ref, onMounted } from 'vue'
import { api, type NicknamesData } from '@/api/client'
import BaseCard from '@/components/BaseCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SectionHeader from '@/components/SectionHeader.vue'

const data = ref<NicknamesData | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try { data.value = await api.nicknames() }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
  loading.value = false
})
</script>
