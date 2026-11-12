import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // Only default white theme is used
  const isDark = ref<boolean>(false)

  function initTheme() {
    isDark.value = false
    localStorage.removeItem('apex_theme')
    document.body.classList.remove('dark-theme')
    document.body.classList.add('light-theme')
    document.documentElement.classList.remove('dark')
  }

  function applyTheme() {
    isDark.value = false
    document.body.classList.remove('dark-theme')
    document.body.classList.add('light-theme')
    document.documentElement.classList.remove('dark')
  }

  return {
    isDark,
    initTheme,
    applyTheme,
  }
})
