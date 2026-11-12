import { defineStore } from 'pinia'
import { ref } from 'vue'
import en from '../locales/en'
import si from '../locales/si'
import ta from '../locales/ta'

export type SupportedLang = 'en' | 'si' | 'ta'

export const useLangStore = defineStore('lang', () => {
  const currentLang = ref<SupportedLang>('en')
  const speechEnabled = ref<boolean>(false)
  const isSpeaking = ref<boolean>(false)

  const messages: Record<SupportedLang, any> = { en, si, ta }

  function initLang() {
    const savedLang = localStorage.getItem('apex_lang') as SupportedLang
    if (savedLang && ['en', 'si', 'ta'].includes(savedLang)) {
      currentLang.value = savedLang
    }
    const savedSpeech = localStorage.getItem('apex_speech')
    if (savedSpeech) {
      speechEnabled.value = savedSpeech === 'true'
    }
  }

  function setLang(lang: SupportedLang) {
    currentLang.value = lang
    localStorage.setItem('apex_lang', lang)
  }

  function toggleSpeech() {
    speechEnabled.value = !speechEnabled.value
    localStorage.setItem('apex_speech', String(speechEnabled.value))
    if (!speechEnabled.value) {
      stopSpeech()
    }
  }

  function t(path: string, params?: Record<string, string>): string {
    const keys = path.split('.')
    let current = messages[currentLang.value]
    for (const k of keys) {
      if (current && current[k] !== undefined) {
        current = current[k]
      } else {
        // Fallback to english
        let fallback = messages['en']
        for (const fk of keys) {
          if (fallback && fallback[fk] !== undefined) {
            fallback = fallback[fk]
          } else {
            return path
          }
        }
        return formatString(String(fallback), params)
      }
    }
    return formatString(String(current), params)
  }

  function formatString(str: string, params?: Record<string, string>): string {
    if (!params) return str
    let res = str
    for (const [key, val] of Object.entries(params)) {
      res = res.replace(new RegExp(`\\{${key}\\}`, 'g'), val)
    }
    return res
  }

  function speak(text: string) {
    if (!speechEnabled.value || !('speechSynthesis' in window)) return
    stopSpeech()

    const cleanText = text.replace(/<[^>]*>/g, '').replace(/[*_#`~]/g, '')
    const utterance = new SpeechSynthesisUtterance(cleanText)
    
    // Choose appropriate voice or rate
    const voices = window.speechSynthesis.getVoices()
    if (currentLang.value === 'si') {
      utterance.lang = 'si-LK'
    } else if (currentLang.value === 'ta') {
      utterance.lang = 'ta-LK'
    } else {
      utterance.lang = 'en-US'
    }

    const matchedVoice = voices.find(v => v.lang.startsWith(utterance.lang.slice(0, 2)))
    if (matchedVoice) {
      utterance.voice = matchedVoice
    }
    utterance.rate = 1.0

    utterance.onstart = () => { isSpeaking.value = true }
    utterance.onend = () => { isSpeaking.value = false }
    utterance.onerror = () => { isSpeaking.value = false }

    window.speechSynthesis.speak(utterance)
  }

  function stopSpeech() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      isSpeaking.value = false
    }
  }

  return {
    currentLang,
    speechEnabled,
    isSpeaking,
    initLang,
    setLang,
    toggleSpeech,
    t,
    speak,
    stopSpeech,
  }
})
