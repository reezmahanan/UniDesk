import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiRequest } from '../api/client'
import { useLangStore } from './lang'

export interface Citation {
  chunk_id: number
  document_id: number
  document_title: string
  page_number?: number
  section_heading?: string
  snippet?: string
}

export interface ChatMessage {
  id: number
  session_id: number
  sender_role: 'USER' | 'ASSISTANT' | 'SYSTEM'
  content: string
  citations: Citation[]
  confidence_score?: number
  created_at: string
  feedback?: { is_helpful: boolean; comment?: string }
}

export interface ChatSession {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface TicketDraft {
  suggested_subject: string
  suggested_description: string
  suggested_category: string
  suggested_department_id?: number
  transcript_excerpt: string
}

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<number | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isGenerating = ref<boolean>(false)
  const ticketDraft = ref<TicketDraft | null>(null)
  const isHandoffModalOpen = ref<boolean>(false)

  async function loadSessions() {
    try {
      sessions.value = await apiRequest<ChatSession[]>('/api/chat/sessions')
      if (sessions.value.length > 0 && !currentSessionId.value) {
        await selectSession(sessions.value[0].id)
      }
    } catch {
      sessions.value = []
    }
  }

  async function selectSession(sessionId: number) {
    currentSessionId.value = sessionId
    try {
      const res = await apiRequest<{ messages: ChatMessage[] }>(`/api/chat/sessions/${sessionId}`)
      messages.value = res.messages || []
    } catch {
      messages.value = []
    }
  }

  async function startNewSession() {
    try {
      const newSession = await apiRequest<ChatSession>('/api/chat/sessions', {
        method: 'POST',
      })
      sessions.value.unshift(newSession)
      currentSessionId.value = newSession.id
      messages.value = []
    } catch (e) {
      console.error(e)
    }
  }

  async function deleteSession(sessionId: number) {
    try {
      await apiRequest(`/api/chat/sessions/${sessionId}`, { method: 'DELETE' })
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (currentSessionId.value === sessionId) {
        if (sessions.value.length > 0) {
          await selectSession(sessions.value[0].id)
        } else {
          currentSessionId.value = null
          messages.value = []
        }
      }
    } catch (e) {
      console.error(e)
    }
  }

  async function sendMessage(content: string) {
    if (!content.trim()) return
    isGenerating.value = true

    // Optimistically add user message
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      session_id: currentSessionId.value || 0,
      sender_role: 'USER',
      content: content.trim(),
      citations: [],
      created_at: new Date().toISOString(),
    }
    messages.value.push(tempUserMsg)

    try {
      const resMsg = await apiRequest<ChatMessage>('/api/chat/message', {
        method: 'POST',
        body: JSON.stringify({
          content: content.trim(),
          session_id: currentSessionId.value,
        }),
      })

      // Update session if it was created
      if (!currentSessionId.value) {
        currentSessionId.value = resMsg.session_id
        await loadSessions()
      }

      // Replace or append assistant message
      messages.value.push(resMsg)

      // Automatic text-to-speech if enabled
      const langStore = useLangStore()
      if (langStore.speechEnabled) {
        langStore.speak(resMsg.content)
      }
    } catch (err: any) {
      messages.value.push({
        id: Date.now() + 1,
        session_id: currentSessionId.value || 0,
        sender_role: 'ASSISTANT',
        content: `Error: ${err.message || 'Unable to retrieve grounded university information.'}`,
        citations: [],
        created_at: new Date().toISOString(),
      })
    } finally {
      isGenerating.value = false
    }
  }

  async function submitFeedback(messageId: number, isHelpful: boolean, comment?: string) {
    try {
      await apiRequest('/api/chat/feedback', {
        method: 'POST',
        body: JSON.stringify({ message_id: messageId, is_helpful: isHelpful, comment }),
      })
      const target = messages.value.find(m => m.id === messageId)
      if (target) {
        target.feedback = { is_helpful: isHelpful, comment }
      }
    } catch (e) {
      console.error(e)
    }
  }

  async function requestHandoffDraft() {
    if (!currentSessionId.value) return
    try {
      ticketDraft.value = await apiRequest<TicketDraft>('/api/chat/hand-off-draft', {
        method: 'POST',
        body: JSON.stringify({ session_id: currentSessionId.value }),
      })
      isHandoffModalOpen.value = true
    } catch (e) {
      console.error(e)
    }
  }

  return {
    sessions,
    currentSessionId,
    messages,
    isGenerating,
    ticketDraft,
    isHandoffModalOpen,
    loadSessions,
    selectSession,
    startNewSession,
    deleteSession,
    sendMessage,
    submitFeedback,
    requestHandoffDraft,
  }
})
