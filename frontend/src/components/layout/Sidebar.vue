<template>
  <aside 
    :class="[
      'bg-white flex flex-col h-screen transition-all duration-300 z-30 shrink-0 border-r-2 border-[#800020]/25 shadow-sm',
      isCollapsed ? 'w-20' : 'w-72'
    ]"
  >
    <!-- Header / Logo with Maroon Border -->
    <div class="p-5 border-b border-[#800020]/20 flex items-center justify-between bg-white">
      <div class="flex items-center gap-3 overflow-hidden">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#800020] to-[#9b1c3a] flex items-center justify-center shadow-md shadow-[#800020]/20 text-white shrink-0">
          <Bot class="w-6 h-6" />
        </div>
        <div v-if="!isCollapsed" class="flex flex-col">
          <span class="font-heading font-bold text-xl tracking-tight text-[#800020]">
            Apex
          </span>
          <span class="text-xs text-slate-500 font-medium tracking-wide">University Help Desk</span>
        </div>
      </div>
      <button 
        @click="isCollapsed = !isCollapsed" 
        class="text-slate-500 hover:text-[#800020] transition p-1.5 rounded-lg hover:bg-[#800020]/5"
        title="Toggle Sidebar"
      >
        <ChevronLeft v-if="!isCollapsed" class="w-4 h-4" />
        <ChevronRight v-else class="w-4 h-4" />
      </button>
    </div>

    <!-- Navigation Links -->
    <nav class="flex-1 overflow-y-auto px-4 py-5 space-y-1.5 bg-white">
      <!-- Dashboard -->
      <router-link
        to="/dashboard"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition group"
        :class="isActive('/dashboard') ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shadow-sm' : 'text-slate-700 hover:bg-[#800020]/5 hover:text-[#800020]'"
      >
        <LayoutDashboard class="w-4 h-4 shrink-0" :class="isActive('/dashboard') ? 'text-[#800020]' : 'text-slate-500 group-hover:text-[#800020]'" />
        <span v-if="!isCollapsed">{{ langStore.t('nav.dashboard') }}</span>
      </router-link>

      <!-- Chat -->
      <router-link
        to="/chat"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition group"
        :class="isActive('/chat') ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shadow-sm' : 'text-slate-700 hover:bg-[#800020]/5 hover:text-[#800020]'"
      >
        <MessageSquareText class="w-4 h-4 shrink-0" :class="isActive('/chat') ? 'text-[#800020]' : 'text-slate-500 group-hover:text-[#800020]'" />
        <span v-if="!isCollapsed">{{ langStore.t('nav.chat') }}</span>
      </router-link>

      <!-- Tickets -->
      <router-link
        to="/tickets"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition group"
        :class="isActive('/tickets') ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shadow-sm' : 'text-slate-700 hover:bg-[#800020]/5 hover:text-[#800020]'"
      >
        <Ticket class="w-4 h-4 shrink-0" :class="isActive('/tickets') ? 'text-[#800020]' : 'text-slate-500 group-hover:text-[#800020]'" />
        <span v-if="!isCollapsed">{{ authStore.isStaff ? langStore.t('nav.staffTickets') : langStore.t('nav.tickets') }}</span>
      </router-link>

      <!-- FAQs -->
      <router-link
        to="/faqs"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition group"
        :class="isActive('/faqs') ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shadow-sm' : 'text-slate-700 hover:bg-[#800020]/5 hover:text-[#800020]'"
      >
        <HelpCircle class="w-4 h-4 shrink-0" :class="isActive('/faqs') ? 'text-[#800020]' : 'text-slate-500 group-hover:text-[#800020]'" />
        <span v-if="!isCollapsed">{{ langStore.t('nav.faqs') }}</span>
      </router-link>

      <!-- Notices -->
      <router-link
        to="/notices"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition group"
        :class="isActive('/notices') ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shadow-sm' : 'text-slate-700 hover:bg-[#800020]/5 hover:text-[#800020]'"
      >
        <Bell class="w-4 h-4 shrink-0" :class="isActive('/notices') ? 'text-[#800020]' : 'text-slate-500 group-hover:text-[#800020]'" />
        <span v-if="!isCollapsed">{{ langStore.t('nav.notices') }}</span>
      </router-link>

      <!-- Services -->
      <router-link
        to="/services"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition group"
        :class="isActive('/services') ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shadow-sm' : 'text-slate-700 hover:bg-[#800020]/5 hover:text-[#800020]'"
      >
        <Compass class="w-4 h-4 shrink-0" :class="isActive('/services') ? 'text-[#800020]' : 'text-slate-500 group-hover:text-[#800020]'" />
        <span v-if="!isCollapsed">{{ langStore.t('nav.services') }}</span>
      </router-link>

      <!-- Administration Section -->
      <div v-if="authStore.isAdmin" class="pt-4 border-t border-[#800020]/15 my-2">
        <p v-if="!isCollapsed" class="px-3 text-[11px] font-bold text-[#800020] uppercase tracking-wider mb-2">
          Administration
        </p>
        <router-link
          to="/admin/documents"
          class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition group"
          :class="isActive('/admin/documents') ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shadow-sm' : 'text-slate-700 hover:bg-[#800020]/5 hover:text-[#800020]'"
        >
          <FileText class="w-4 h-4 shrink-0" :class="isActive('/admin/documents') ? 'text-[#800020]' : 'text-slate-500 group-hover:text-[#800020]'" />
          <span v-if="!isCollapsed">{{ langStore.t('nav.documents') }}</span>
        </router-link>
        <router-link
          to="/admin/users"
          class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition group"
          :class="isActive('/admin/users') ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shadow-sm' : 'text-slate-700 hover:bg-[#800020]/5 hover:text-[#800020]'"
        >
          <Users class="w-4 h-4 shrink-0" :class="isActive('/admin/users') ? 'text-[#800020]' : 'text-slate-500 group-hover:text-[#800020]'" />
          <span v-if="!isCollapsed">{{ langStore.t('nav.users') }}</span>
        </router-link>
      </div>
    </nav>

    <!-- Support Hours Badge with Maroon Frame -->
    <div v-if="!isCollapsed" class="p-3.5 mx-4 mb-3 rounded-xl bg-rose-50/60 border border-[#800020]/25">
      <div class="flex items-center gap-2 text-xs font-bold text-[#800020] mb-1">
        <Clock class="w-3.5 h-3.5" />
        <span>University Support Hours</span>
      </div>
      <p class="text-[11px] text-slate-600 font-medium">
        Mon–Fri: 8am–8pm | Sat: 10am–4pm
      </p>
    </div>

    <!-- Sidebar Footer with Maroon Border -->
    <div class="p-4 border-t border-[#800020]/20 space-y-2 bg-white">
      <!-- Voice synthesis toggle -->
      <button 
        @click="langStore.toggleSpeech()"
        class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition"
        :class="langStore.speechEnabled ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30' : 'text-slate-600 hover:bg-[#800020]/5'"
        :title="langStore.t('nav.speechEnabled')"
      >
        <div class="flex items-center gap-2">
          <Volume2 v-if="langStore.speechEnabled" class="w-4 h-4 text-[#800020]" />
          <VolumeX v-else class="w-4 h-4 text-slate-400" />
          <span v-if="!isCollapsed">Voice Audio (TTS)</span>
        </div>
        <span v-if="!isCollapsed" class="text-[10px] px-1.5 py-0.5 rounded font-bold" :class="langStore.speechEnabled ? 'bg-[#800020] text-white' : 'bg-slate-200 text-slate-700'">
          {{ langStore.speechEnabled ? 'ON' : 'OFF' }}
        </span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import {
  Bot,
  LayoutDashboard,
  MessageSquareText,
  Ticket,
  HelpCircle,
  Bell,
  Compass,
  FileText,
  Users,
  ChevronLeft,
  ChevronRight,
  Clock,
  Volume2,
  VolumeX
} from 'lucide-vue-next'

const route = useRoute()
const authStore = useAuthStore()
const langStore = useLangStore()

const isCollapsed = ref<boolean>(false)

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(`${path}/`)
}
</script>
