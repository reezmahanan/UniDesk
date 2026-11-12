<template>
  <div class="min-h-screen flex items-center justify-center p-4 bg-cover bg-center relative bg-[url('/images/campus-auth-bg.jpg')]">
    <!-- Sophisticated Frosted Academic Backdrop Overlay -->
    <div class="absolute inset-0 bg-slate-950/45 backdrop-blur-[3px]"></div>

    <!-- Login Card (White surface with academic maroon border) -->
    <div class="bg-white/95 backdrop-blur-md w-full max-w-md p-8 rounded-3xl border-2 border-[#800020]/30 shadow-2xl relative z-10 text-slate-900 space-y-6">
      <!-- Brand Logo -->
      <div class="text-center space-y-2">
        <div class="w-14 h-14 rounded-2xl bg-[#800020] flex items-center justify-center mx-auto shadow-md shadow-[#800020]/25 text-white border-2 border-[#800020]">
          <Bot class="w-8 h-8" />
        </div>
        <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">Apex University Portal</h1>
        <p class="text-xs text-slate-600">AI University Help Desk & Ticketing Platform</p>
      </div>

      <!-- Error alert -->
      <div v-if="errorMessage" class="p-3.5 rounded-xl bg-rose-50 border border-rose-300 text-rose-800 text-xs flex items-center gap-2">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">University Email Address</label>
          <input 
            v-model="email"
            type="email"
            required
            placeholder="e.g. student@apex.edu.lk"
            class="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 placeholder-slate-400 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Password</label>
          <input 
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 placeholder-slate-400 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
          />
        </div>

        <button 
          type="submit"
          :disabled="isLoading"
          class="w-full py-3 rounded-xl bg-[#800020] hover:bg-[#600018] disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-[#800020]/20 transition flex items-center justify-center gap-2"
        >
          <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
          <span>{{ isLoading ? 'Authenticating...' : 'Sign In to Portal' }}</span>
        </button>
      </form>

      <!-- Quick Demo Users Panel -->
      <div class="pt-4 border-t border-[#800020]/15 space-y-2">
        <span class="text-[11px] font-semibold text-slate-600 block text-center">Development Quick Demo Profiles:</span>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <button 
            type="button"
            @click="quickLogin('student')"
            class="p-2 rounded-xl bg-slate-50 hover:bg-[#800020]/10 border border-[#800020]/20 text-slate-800 hover:text-[#800020] font-semibold transition text-center"
          >
            Kasun (Student)
          </button>
          <button 
            type="button"
            @click="quickLogin('student2')"
            class="p-2 rounded-xl bg-slate-50 hover:bg-[#800020]/10 border border-[#800020]/20 text-slate-800 hover:text-[#800020] font-semibold transition text-center"
          >
            Sanduni (Student)
          </button>
          <button 
            type="button"
            @click="quickLogin('staff')"
            class="p-2 rounded-xl bg-slate-50 hover:bg-[#800020]/10 border border-[#800020]/20 text-slate-800 hover:text-[#800020] font-semibold transition text-center"
          >
            Dr. Priyantha (Staff)
          </button>
          <button 
            type="button"
            @click="quickLogin('admin')"
            class="p-2 rounded-xl bg-slate-50 hover:bg-[#800020]/10 border border-[#800020]/20 text-slate-800 hover:text-[#800020] font-semibold transition text-center"
          >
            System Admin
          </button>
        </div>
      </div>

      <div class="text-center text-xs text-slate-600">
        New student at Apex? 
        <router-link to="/register" class="text-[#800020] hover:underline font-bold ml-1">Create Account</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Bot, AlertCircle, Loader2 } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

async function handleLogin() {
  errorMessage.value = ''
  isLoading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/dashboard')
  } catch (err: any) {
    errorMessage.value = err.message || 'Login failed.'
  } finally {
    isLoading.value = false
  }
}

async function quickLogin(role: any) {
  isLoading.value = true
  try {
    await authStore.quickSwitchDemo(role)
    router.push('/dashboard')
  } catch (err: any) {
    errorMessage.value = err.message
  } finally {
    isLoading.value = false
  }
}
</script>
