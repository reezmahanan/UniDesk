<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 bg-academic-canvas">
    <div>
      <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">Student Digital Portals & Services</h1>
      <p class="text-xs text-slate-600 mt-1">Official access links to university learning systems, student mailboxes, and campus resources.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div 
        v-for="serv in services" 
        :key="serv.id"
        class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm flex flex-col justify-between space-y-4 hover:border-[#800020]/60 hover:-translate-y-1 hover:shadow-md transition duration-200"
      >
        <div class="space-y-3">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center text-white shadow-md shadow-[#800020]/25 bg-[#800020]">
            <component :is="getIconComponent(serv.icon_name)" class="w-6 h-6" />
          </div>

          <h3 class="text-base font-bold text-slate-900">{{ serv.title }}</h3>
          <p class="text-xs text-slate-600 leading-relaxed">{{ serv.description }}</p>
        </div>

        <a 
          :href="serv.url" 
          target="_blank" 
          rel="noopener"
          class="w-full py-2.5 rounded-xl bg-[#800020]/10 hover:bg-[#800020] hover:text-white border border-[#800020]/30 text-center text-xs font-bold text-[#800020] transition flex items-center justify-center gap-1.5 shadow-sm"
        >
          <span>Launch Service</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiRequest } from '../api/client'
import {
  ExternalLink,
  BookOpen,
  Mail,
  Search,
  MapPin,
  Laptop
} from 'lucide-vue-next'

const services = ref<any[]>([])

onMounted(async () => {
  services.value = await apiRequest('/api/knowledge/services')
})

function getIconComponent(name: string) {
  if (name === 'book-open') return BookOpen
  if (name === 'mail') return Mail
  if (name === 'search') return Search
  if (name === 'map-pin') return MapPin
  return Laptop
}
</script>
