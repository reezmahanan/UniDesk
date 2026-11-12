<template>
  <div class="min-h-screen flex items-center justify-center p-4 bg-cover bg-center relative bg-[url('/images/campus-auth-bg.jpg')]">
    <!-- Sophisticated Frosted Academic Backdrop Overlay -->
    <div class="absolute inset-0 bg-slate-950/45 backdrop-blur-[3px]"></div>

    <!-- Register Card (White surface with academic maroon border) -->
    <div class="bg-white/95 backdrop-blur-md w-full max-w-md p-8 rounded-3xl border-2 border-[#800020]/30 shadow-2xl relative z-10 text-slate-900 space-y-6">
      <div class="text-center space-y-2">
        <div class="w-14 h-14 rounded-2xl bg-[#800020] flex items-center justify-center mx-auto shadow-md shadow-[#800020]/25 text-white border-2 border-[#800020]">
          <Bot class="w-8 h-8" />
        </div>
        <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">Student Registration</h1>
        <p class="text-xs text-slate-600">Join the UniDesk AI University Help Desk & Ticketing Platform</p>
      </div>

      <div v-if="errorMessage" class="p-3.5 rounded-xl bg-rose-50 border border-rose-300 text-rose-800 text-xs flex items-center gap-2">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Full Legal Name</label>
          <input 
            v-model="fullName"
            type="text"
            required
            placeholder="e.g. Kasun Jayasundara"
            class="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 placeholder-slate-400 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">University Email Address</label>
          <input 
            v-model="email"
            type="email"
            required
            placeholder="e.g. kasun.j@student.apex.edu.lk"
            class="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 placeholder-slate-400 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Student Index</label>
            <input 
              v-model="studentIndex"
              type="text"
              placeholder="e.g. 2026/SE/048"
              class="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 placeholder-slate-400 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Faculty</label>
            <select 
              v-model="faculty"
              class="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:outline-none"
            >
              <option value="Faculty of Computing">Computing</option>
              <option value="Faculty of Business">Business</option>
              <option value="Faculty of Engineering">Engineering</option>
              <option value="Faculty of Humanities">Humanities</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Password</label>
          <input 
            v-model="password"
            type="password"
            required
            minlength="6"
            placeholder="Minimum 6 characters"
            class="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 placeholder-slate-400 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
          />
        </div>

        <button 
          type="submit"
          :disabled="isLoading"
          class="w-full py-3 rounded-xl bg-[#800020] hover:bg-[#600018] disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-[#800020]/20 transition flex items-center justify-center gap-2"
        >
          <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
          <span>{{ isLoading ? 'Creating Account...' : 'Complete Registration' }}</span>
        </button>
      </form>

      <div class="text-center text-xs text-slate-600">
        Already have an account? 
        <router-link to="/login" class="text-[#800020] hover:underline font-bold ml-1">Sign In</router-link>
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

const fullName = ref('')
const email = ref('')
const studentIndex = ref('')
const faculty = ref('Faculty of Computing')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

async function handleRegister() {
  errorMessage.value = ''
  isLoading.value = true
  try {
    await authStore.register({
      full_name: fullName.value,
      email: email.value,
      password: password.value,
      student_index: studentIndex.value || undefined,
      faculty: faculty.value,
    })
    router.push('/dashboard')
  } catch (err: any) {
    errorMessage.value = err.message || 'Registration failed.'
  } finally {
    isLoading.value = false
  }
}
</script>
