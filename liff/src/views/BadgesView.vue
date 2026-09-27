<template>
  <div>
    <PageSign title="我的成就勳章" en="Awards" line="people">
      <template v-if="badges.length" #action>
        <span class="text-sm text-slate-300">已解鎖 <span class="font-num text-xl font-semibold text-white">{{ badges.length }}</span> 枚</span>
      </template>
    </PageSign>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i"
           class="rounded-xl border border-slate-100 bg-white p-4 flex items-center gap-4">
        <div class="skeleton w-14 h-14 rounded-full shrink-0" />
        <div class="flex-1 space-y-2">
          <div class="skeleton h-4 rounded-full w-2/3" />
          <div class="skeleton h-3 rounded-full w-1/3" />
        </div>
      </div>
    </div>

    <EmptyState
      v-else-if="error"
      title="載入失敗"
      :description="error"
    />
    <EmptyState
      v-else-if="badges.length === 0"
      title="尚未獲得任何勳章"
      description="參與群組旅行與活動，即可解鎖各式專屬稀有勳章！"
    />

    <div v-else class="space-y-2">
      <BadgeCard v-for="b in badges" :key="b.badge_id" :badge="b" class="" />
    </div>
  </div>
</template>

<script setup lang="ts">
import PageSign from '@/components/PageSign.vue'
import { ref, onMounted } from 'vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import BadgeCard from '@/components/BadgeCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const auth = useAuthStore()
const badges = ref<any[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try { badges.value = await api.badges(auth.userId) }
  catch (e: any) { error.value = e?.message || '請求失敗'; console.error(e) }
  finally { loading.value = false }
})
</script>
