<template>
  <div v-if="isOpen && citation" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-white w-full max-w-lg rounded-2xl p-6 border-2 border-[#800020]/30 shadow-2xl relative text-slate-900">
      <!-- Close button -->
      <button 
        @click="$emit('close')"
        class="absolute top-4 right-4 text-slate-400 hover:text-slate-800 p-1 rounded-lg hover:bg-slate-100"
      >
        <X class="w-5 h-5" />
      </button>

      <!-- Modal Header -->
      <div class="flex items-center gap-3 mb-4">
        <div class="w-9 h-9 rounded-xl bg-[#800020]/10 text-[#800020] flex items-center justify-center border border-[#800020]/30">
          <BookOpen class="w-5 h-5" />
        </div>
        <div>
          <h3 class="text-base font-bold text-slate-900 leading-tight">Verified Source Citation</h3>
          <span class="text-xs text-[#800020] font-semibold">Official University Document</span>
        </div>
      </div>

      <!-- Citation Info -->
      <div class="space-y-4">
        <div class="p-3.5 rounded-xl bg-slate-50 border border-[#800020]/20 space-y-1.5">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-500 font-medium">Document Title:</span>
            <span class="font-bold text-slate-900">{{ citation.document_title }}</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-500 font-medium">Section:</span>
            <span class="text-slate-800 font-medium">{{ citation.section_heading || 'General' }}</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-500 font-medium">Page Reference:</span>
            <span class="px-2 py-0.5 rounded bg-[#800020]/10 text-[#800020] font-bold border border-[#800020]/25">
              Page {{ citation.page_number || 1 }}
            </span>
          </div>
        </div>

        <div>
          <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">Extracted Document Snippet</h4>
          <p class="text-xs text-slate-800 p-3.5 rounded-xl bg-slate-50 border border-slate-200 leading-relaxed font-mono">
            {{ citation.snippet || 'Referenced official university regulations context.' }}
          </p>
        </div>

        <!-- Action / Download link -->
        <div class="pt-2 flex justify-end gap-2.5 border-t border-[#800020]/15">
          <button 
            @click="$emit('close')"
            class="px-4 py-2 rounded-xl text-xs font-medium text-slate-700 hover:bg-slate-100 transition"
          >
            Close
          </button>
          <a
            :href="`/api/documents/${citation.document_id}/download`"
            target="_blank"
            download
            class="px-4 py-2 rounded-xl bg-[#800020] hover:bg-[#600018] text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-[#800020]/20 transition"
          >
            <Download class="w-3.5 h-3.5" />
            <span>Download Source Document</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { BookOpen, Download, X } from 'lucide-vue-next'
import type { Citation } from '../../stores/chat'

defineProps<{
  isOpen: boolean
  citation: Citation | null
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>
