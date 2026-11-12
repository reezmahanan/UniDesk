<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 max-w-4xl mx-auto bg-academic-canvas">
    <div>
      <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">Account Profile & Preferences</h1>
      <p class="text-xs text-slate-600 mt-1">Manage your identity, language settings, and voice accessibility preferences.</p>
    </div>

    <!-- Identity Card -->
    <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-4">
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 rounded-2xl bg-[#800020] flex items-center justify-center text-white text-2xl font-bold shadow-md shadow-[#800020]/20 border-2 border-[#800020]">
          {{ authStore.currentUser?.full_name?.charAt(0) || 'U' }}
        </div>
        <div>
          <h2 class="text-lg font-bold text-slate-900">{{ authStore.currentUser?.full_name }}</h2>
          <p class="text-xs text-slate-600">{{ authStore.currentUser?.email }}</p>
          <span class="inline-block mt-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#800020]/10 text-[#800020] border border-[#800020]/30">
            {{ authStore.currentUser?.role }} Account
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-[#800020]/15 text-xs">
        <div class="p-3.5 rounded-xl bg-slate-50 border border-[#800020]/15 space-y-1">
          <span class="text-slate-500 font-medium">Student Index Number</span>
          <p class="font-bold text-slate-900 font-mono">{{ authStore.currentUser?.student_index || 'Staff Member' }}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-50 border border-[#800020]/15 space-y-1">
          <span class="text-slate-500 font-medium">Faculty / Department</span>
          <p class="font-bold text-slate-900">{{ authStore.currentUser?.faculty || 'Administrative' }}</p>
        </div>
      </div>
    </div>

    <!-- Accessibility & Preferences -->
    <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-4">
      <h3 class="text-sm font-bold text-slate-900 border-b border-[#800020]/15 pb-2">Accessibility & Language Preferences</h3>

      <div class="space-y-4 text-xs">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-50 border border-[#800020]/15">
          <div>
            <span class="font-bold text-slate-900 block">Portal Language</span>
            <span class="text-slate-600">Select language for interface and AI translations</span>
          </div>
          <div class="flex gap-2">
            <button 
              @click="langStore.setLang('en')"
              class="px-3.5 py-1.5 rounded-lg font-bold transition text-xs"
              :class="langStore.currentLang === 'en' ? 'bg-[#800020] text-white shadow-sm' : 'bg-white text-slate-700 border border-slate-200 hover:bg-[#800020]/10 hover:text-[#800020]'"
            >
              English
            </button>
            <button 
              @click="langStore.setLang('si')"
              class="px-3.5 py-1.5 rounded-lg font-bold transition text-xs"
              :class="langStore.currentLang === 'si' ? 'bg-[#800020] text-white shadow-sm' : 'bg-white text-slate-700 border border-slate-200 hover:bg-[#800020]/10 hover:text-[#800020]'"
            >
              සිංහල
            </button>
            <button 
              @click="langStore.setLang('ta')"
              class="px-3.5 py-1.5 rounded-lg font-bold transition text-xs"
              :class="langStore.currentLang === 'ta' ? 'bg-[#800020] text-white shadow-sm' : 'bg-white text-slate-700 border border-slate-200 hover:bg-[#800020]/10 hover:text-[#800020]'"
            >
              தமிழ்
            </button>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-50 border border-[#800020]/15">
          <div>
            <span class="font-bold text-slate-900 block">Text-to-Speech (TTS) Voice Readout</span>
            <span class="text-slate-600">Speak bot responses aloud using native browser speech synthesis</span>
          </div>
          <button 
            @click="langStore.toggleSpeech()"
            class="px-4 py-2 rounded-xl text-xs font-bold transition self-start sm:self-auto"
            :class="langStore.speechEnabled ? 'bg-[#800020] text-white shadow-sm' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'"
          >
            {{ langStore.speechEnabled ? 'Enabled' : 'Disabled' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import { useLangStore } from '../stores/lang'

const authStore = useAuthStore()
const langStore = useLangStore()
</script>
