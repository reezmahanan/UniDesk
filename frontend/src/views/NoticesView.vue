<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 bg-academic-canvas">
    <div>
      <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">University Notices & Announcements</h1>
      <p class="text-xs text-slate-600 mt-1">Official bulletins from the registrar, student welfare division, and faculties.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="notice in notices" 
        :key="notice.id"
        class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm flex flex-col justify-between space-y-4 hover:border-[#800020]/60 hover:shadow-md transition group"
      >
        <div class="space-y-2.5">
          <div class="flex items-center justify-between text-xs">
            <span 
              class="px-2.5 py-0.5 rounded-full font-bold text-[11px]"
              :class="notice.tag === 'Urgent' ? 'bg-rose-50 text-rose-700 border border-rose-300' : 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30'"
            >
              {{ notice.tag }}
            </span>
            <span class="text-slate-500">{{ formatDate(notice.publish_date) }}</span>
          </div>

          <h3 class="text-base font-bold text-slate-900 group-hover:text-[#800020] transition">{{ notice.title }}</h3>
          <p class="text-xs text-slate-700 leading-relaxed">{{ notice.content }}</p>
        </div>

        <div class="pt-3 border-t border-[#800020]/15 flex items-center justify-between text-[11px] text-slate-500">
          <span>Target: <strong class="text-slate-700">{{ notice.audience }}</strong></span>
          <span class="text-[#800020] font-semibold">Official Dispatch ✓</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiRequest } from '../api/client'

const notices = ref<any[]>([])

onMounted(async () => {
  notices.value = await apiRequest('/api/notices')
})

function formatDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
