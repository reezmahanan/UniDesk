<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 bg-academic-canvas">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">Frequently Asked Questions</h1>
        <p class="text-xs text-slate-600 mt-1">Verified answers on Sri Lankan higher education rules, admissions, and financial aid.</p>
      </div>
    </div>

    <!-- Search & Category Filters -->
    <div class="bg-white p-4 rounded-2xl border-2 border-[#800020]/20 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
      <div class="relative flex-1 min-w-[200px]">
        <input 
          v-model="searchQuery"
          type="text"
          placeholder="Search FAQs by keywords (e.g. Mahapola, A/L requirements, WiFi)..."
          class="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#800020] focus:ring-1 focus:ring-[#800020]"
        />
        <Search class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
      </div>

      <div class="flex flex-wrap gap-1.5">
        <button 
          v-for="cat in ['ALL', 'admissions', 'mahapola', 'it_support', 'library']"
          :key="cat"
          @click="selectedCategory = cat"
          class="px-3 py-1.5 rounded-lg font-medium transition"
          :class="selectedCategory === cat ? 'bg-[#800020] text-white shadow font-semibold' : 'text-slate-700 hover:bg-[#800020]/10 hover:text-[#800020]'"
        >
          {{ cat === 'ALL' ? 'All Topics' : cat.replace(/_/g, ' ') }}
        </button>
      </div>
    </div>

    <!-- Accordion FAQ List -->
    <div class="space-y-3">
      <div 
        v-for="faq in filteredFaqs" 
        :key="faq.id"
        class="bg-white rounded-2xl border-2 border-[#800020]/20 shadow-sm overflow-hidden transition"
      >
        <button 
          @click="toggleFaq(faq.id)"
          class="w-full p-5 text-left flex items-center justify-between gap-4 hover:bg-[#800020]/5 transition"
        >
          <div class="space-y-1">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#800020]/10 text-[#800020] border border-[#800020]/30 capitalize">
              {{ faq.category.replace(/_/g, ' ') }}
            </span>
            <h3 class="text-sm font-bold text-slate-900">{{ faq.question }}</h3>
          </div>
          <div 
            class="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 shrink-0 transition-transform duration-200"
            :class="openFaqIds.includes(faq.id) ? 'rotate-180 text-[#800020] bg-[#800020]/10' : ''"
          >
            <ChevronDown class="w-4 h-4" />
          </div>
        </button>

        <!-- Accordion Body -->
        <div 
          v-if="openFaqIds.includes(faq.id)"
          class="px-5 pb-5 pt-3 text-xs text-slate-700 leading-relaxed border-t border-[#800020]/15 bg-slate-50/50 space-y-2"
        >
          <p class="whitespace-pre-wrap">{{ faq.answer }}</p>
          <div v-if="faq.source_reference" class="pt-2 text-[11px] text-[#800020] font-semibold flex items-center gap-1.5 border-t border-slate-200">
            <BookOpen class="w-3.5 h-3.5" />
            <span>Official Policy Reference: {{ faq.source_reference }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { apiRequest } from '../api/client'
import { Search, ChevronDown, BookOpen } from 'lucide-vue-next'

const faqs = ref<any[]>([])
const openFaqIds = ref<number[]>([])
const searchQuery = ref('')
const selectedCategory = ref('ALL')

onMounted(async () => {
  faqs.value = await apiRequest('/api/knowledge/faqs')
  if (faqs.value.length > 0) {
    openFaqIds.value.push(faqs.value[0].id)
  }
})

function toggleFaq(id: number) {
  if (openFaqIds.value.includes(id)) {
    openFaqIds.value = openFaqIds.value.filter(item => item !== id)
  } else {
    openFaqIds.value.push(id)
  }
}

const filteredFaqs = computed(() => {
  return faqs.value.filter(f => {
    const matchesCat = selectedCategory.value === 'ALL' || f.category === selectedCategory.value
    const matchesSearch = !searchQuery.value.trim() || 
      f.question.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      f.answer.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCat && matchesSearch
  })
})
</script>
