<template>
  <header class="h-16 border-b-2 border-[#800020]/25 px-6 flex items-center justify-between z-20 bg-white shadow-sm">
    <!-- Left: Academic Portal Title -->
    <div class="flex items-center gap-3">
      <div class="hidden sm:flex flex-col">
        <span class="text-xs font-bold text-[#800020] uppercase tracking-wider">
          University of Sri Lanka • UniDesk Portal
        </span>
        <span class="text-sm font-bold text-slate-800">
          {{ authStore.currentUser ? authStore.currentUser.full_name : 'Guest Session' }}
        </span>
      </div>
    </div>

    <!-- Right Actions -->
    <div class="flex items-center gap-3.5">
      <!-- Demo Profile Switcher with Maroon Border -->
      <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-rose-50/70 border border-[#800020]/30 shadow-sm">
        <span class="text-[11px] font-bold text-[#800020]">Demo Role:</span>
        <select 
          class="bg-transparent text-xs text-slate-800 font-semibold focus:outline-none cursor-pointer"
          :value="currentDemoRole"
          @change="onDemoSwitch($event)"
        >
          <option value="student" class="bg-white text-slate-900">Kasun (Student • Computing)</option>
          <option value="student2" class="bg-white text-slate-900">Sanduni (Student • Business)</option>
          <option value="staff" class="bg-white text-slate-900">Dr. Priyantha (Staff • IT Dept)</option>
          <option value="admin" class="bg-white text-slate-900">System Admin (Full Admin)</option>
        </select>
      </div>

      <!-- Language Selector with Maroon Accent -->
      <div class="flex items-center bg-white border border-[#800020]/30 rounded-xl p-1 text-xs font-semibold shadow-sm">
        <button 
          @click="langStore.setLang('en')"
          class="px-2.5 py-1 rounded-lg transition"
          :class="langStore.currentLang === 'en' ? 'bg-[#800020] text-white shadow' : 'text-slate-600 hover:text-[#800020]'"
        >
          EN
        </button>
        <button 
          @click="langStore.setLang('si')"
          class="px-2.5 py-1 rounded-lg transition"
          :class="langStore.currentLang === 'si' ? 'bg-[#800020] text-white shadow' : 'text-slate-600 hover:text-[#800020]'"
        >
          සිං
        </button>
        <button 
          @click="langStore.setLang('ta')"
          class="px-2.5 py-1 rounded-lg transition"
          :class="langStore.currentLang === 'ta' ? 'bg-[#800020] text-white shadow' : 'text-slate-600 hover:text-[#800020]'"
        >
          தமிழ்
        </button>
      </div>

      <!-- User Role Pill -->
      <div 
        v-if="authStore.currentUser"
        class="px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 border border-[#800020]/30 bg-rose-50/80 text-[#800020]"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-[#800020]"></span>
        {{ authStore.currentUser.role }}
      </div>

      <!-- Logout Button -->
      <button 
        v-if="authStore.isAuthenticated"
        @click="handleLogout"
        class="p-2 rounded-xl text-slate-500 hover:text-[#800020] hover:bg-rose-50 transition border border-transparent hover:border-[#800020]/20"
        title="Sign Out"
      >
        <LogOut class="w-4 h-4" />
      </button>

      <router-link
        v-else
        to="/login"
        class="px-4 py-1.5 rounded-xl bg-[#800020] hover:bg-[#68001a] text-white text-xs font-bold shadow-md shadow-[#800020]/25 transition"
      >
        Sign In
      </router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import { LogOut } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const langStore = useLangStore()

const currentDemoRole = computed(() => {
  if (authStore.currentUser?.email === 'admin@apex.edu.lk') return 'admin'
  if (authStore.currentUser?.email === 'staff@apex.edu.lk') return 'staff'
  if (authStore.currentUser?.email === 'sanduni@apex.edu.lk') return 'student2'
  return 'student'
})

async function onDemoSwitch(e: Event) {
  const target = (e.target as HTMLSelectElement).value as any
  await authStore.quickSwitchDemo(target)
  router.push('/dashboard')
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>
