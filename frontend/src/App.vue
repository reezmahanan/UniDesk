<template>
  <div class="h-screen w-screen overflow-hidden flex flex-col font-sans text-slate-800 bg-white">
    <!-- Auth Pages (Login/Register) rendered standalone -->
    <template v-if="isAuthRoute">
      <router-view />
    </template>

    <!-- Main Application Shell -->
    <div v-else class="flex h-screen w-screen overflow-hidden bg-white">
      <Sidebar />
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#fafafa]">
        <Topbar />
        <main class="flex-1 overflow-hidden flex flex-col bg-academic-canvas">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from './stores/theme'
import { useLangStore } from './stores/lang'
import Sidebar from './components/layout/Sidebar.vue'
import Topbar from './components/layout/Topbar.vue'

const route = useRoute()
const themeStore = useThemeStore()
const langStore = useLangStore()

const isAuthRoute = computed(() => {
  return route.name === 'Login' || route.name === 'Register'
})

onMounted(() => {
  themeStore.initTheme()
  langStore.initLang()
})
</script>
