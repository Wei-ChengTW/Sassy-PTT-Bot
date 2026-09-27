<template>
  <Transition name="toast">
    <div v-if="toast.state.visible"
         class="fixed z-[60] bottom-24 inset-x-0 flex justify-center px-4 pointer-events-none">
      <div class="max-w-sm w-fit bg-slate-800 text-white text-sm font-medium rounded-md shadow-pop pl-3 pr-4 py-2.5 flex items-center gap-2.5"
           role="status" aria-live="polite">
        <span class="w-2.5 h-2.5 rounded-full shrink-0"
              :class="toast.state.type === 'success' ? 'bg-success-400' : 'bg-danger-400'" aria-hidden="true" />
        <span>{{ toast.state.message }}</span>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const toast = useToast()
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.18s ease, transform 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
@media (prefers-reduced-motion: reduce) {
  .toast-enter-active,
  .toast-leave-active {
    transition: opacity 0.1s linear;
    transform: none !important;
  }
}
</style>
