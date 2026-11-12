<template>
  <div class="flex-1 flex overflow-hidden bg-white">
    <!-- Chat Sessions Sub-sidebar with Maroon Border -->
    <div class="hidden md:flex flex-col w-64 border-r-2 border-[#800020]/25 bg-white p-4 space-y-3 shadow-sm">
      <button 
        @click="chatStore.startNewSession()"
        class="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[#800020] hover:bg-[#68001a] text-white text-xs font-bold shadow-md shadow-[#800020]/25 transition"
      >
        <Plus class="w-4 h-4" />
        {{ langStore.t('nav.resetChat') }}
      </button>

      <div class="text-[11px] font-bold text-[#800020] uppercase tracking-wider px-1">
        Recent Inquiries
      </div>

      <div class="flex-1 overflow-y-auto space-y-1.5">
        <div 
          v-for="s in chatStore.sessions"
          :key="s.id"
          class="flex items-center justify-between p-2.5 rounded-xl text-xs font-semibold cursor-pointer transition group"
          :class="chatStore.currentSessionId === s.id ? 'bg-[#800020]/10 text-[#800020] border border-[#800020]/35 shadow-sm' : 'text-slate-700 hover:bg-rose-50/70 hover:text-[#800020]'"
          @click="chatStore.selectSession(s.id)"
        >
          <div class="truncate flex items-center gap-2">
            <MessageSquare class="w-3.5 h-3.5 shrink-0 text-slate-400 group-hover:text-[#800020]" />
            <span class="truncate">{{ s.title }}</span>
          </div>
          <button 
            @click.stop="chatStore.deleteSession(s.id)"
            class="opacity-0 group-hover:opacity-100 hover:text-rose-600 p-1"
            title="Delete Session"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Main Chat Feed Area -->
    <div class="flex-1 flex flex-col overflow-hidden bg-[#fdfdfd]">
      <!-- AI Grounded Header Banner with Maroon Border -->
      <div class="px-6 py-3 border-b-2 border-[#800020]/20 bg-rose-50/40 flex items-center justify-between text-xs text-slate-700">
        <div class="flex items-center gap-2">
          <ShieldCheck class="w-4 h-4 text-[#800020] shrink-0" />
          <span class="font-medium">{{ langStore.t('chat.disclaimer') }}</span>
        </div>
        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#800020]/10 text-[#800020] border border-[#800020]/30 shrink-0">
          Grounded University RAG
        </span>
      </div>

      <!-- Messages Stream with Academic Pattern -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6 bg-academic-canvas" ref="messagesContainer">
        <!-- Initial Welcome if empty with University Seal Watermark -->
        <div v-if="chatStore.messages.length === 0" class="max-w-2xl mx-auto text-center py-12 space-y-4 bg-seal-watermark">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-[#800020] to-[#a81c3e] flex items-center justify-center mx-auto shadow-lg shadow-[#800020]/25 text-white">
            <Bot class="w-8 h-8" />
          </div>
          <h2 class="text-xl font-heading font-bold text-slate-900">
            Ayubowan! I'm Apex, your University Help Desk Assistant.
          </h2>
          <p class="text-xs text-slate-600 leading-relaxed max-w-lg mx-auto font-medium">
            I search approved university documents and policies to provide grounded answers for admissions, Mahapola bursaries, IT accounts, and campus regulations.
          </p>

          <!-- Quick Decision Tree Prompt Pills with Maroon Border -->
          <div class="pt-4 flex flex-wrap justify-center gap-2">
            <button 
              v-for="prompt in quickPrompts" 
              :key="prompt"
              @click="submitPrompt(prompt)"
              class="px-4 py-2 rounded-xl text-xs font-semibold bg-white hover:bg-rose-50 border-2 border-[#800020]/25 text-[#800020] shadow-sm transition hover:border-[#800020]"
            >
              {{ prompt }}
            </button>
          </div>
        </div>

        <!-- Chat Bubbles -->
        <div 
          v-for="msg in chatStore.messages" 
          :key="msg.id"
          class="flex gap-3.5 max-w-3xl"
          :class="msg.sender_role === 'USER' ? 'ml-auto flex-row-reverse' : 'mr-auto'"
        >
          <!-- Avatar -->
          <div 
            class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 text-white font-bold text-xs shadow-md"
            :class="msg.sender_role === 'USER' ? 'bg-gradient-to-tr from-slate-700 to-slate-900' : 'bg-gradient-to-tr from-[#800020] to-[#a81c3e] border border-[#800020]/40'"
          >
            <UserIcon v-if="msg.sender_role === 'USER'" class="w-4 h-4" />
            <Bot v-else class="w-4 h-4 text-white" />
          </div>

          <!-- Message Body -->
          <div class="space-y-2">
            <div 
              class="p-4 rounded-2xl text-sm leading-relaxed"
              :class="msg.sender_role === 'USER' ? 'bg-gradient-to-tr from-[#800020] to-[#9b1c3a] text-white shadow-md rounded-tr-none' : 'bg-white text-slate-800 rounded-tl-none border-2 border-[#800020]/20 shadow-sm'"
            >
              <div class="whitespace-pre-wrap">{{ msg.content }}</div>

              <!-- Citations Badges on Assistant Messages -->
              <div v-if="msg.citations && msg.citations.length > 0" class="pt-3 border-t border-[#800020]/15 mt-3 space-y-1.5">
                <span class="text-[11px] font-bold text-[#800020] block">Verified University Sources:</span>
                <div class="flex flex-wrap gap-1.5">
                  <button 
                    v-for="c in msg.citations" 
                    :key="c.chunk_id"
                    @click="openSourceModal(c)"
                    class="px-3 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 border border-[#800020]/30 text-[11px] text-[#800020] flex items-center gap-1.5 transition font-semibold"
                    title="View Source Citation"
                  >
                    <BookOpen class="w-3 h-3 text-[#800020]" />
                    <span>{{ c.document_title }} (P.{{ c.page_number || 1 }})</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Assistant Actions: TTS, Feedback, Create Ticket -->
            <div v-if="msg.sender_role === 'ASSISTANT'" class="flex items-center gap-3 px-1 text-xs text-slate-500">
              <!-- Voice Playback -->
              <button 
                @click="langStore.speak(msg.content)"
                class="hover:text-[#800020] flex items-center gap-1 font-semibold transition"
                title="Read aloud"
              >
                <Volume2 class="w-3.5 h-3.5 text-[#800020]" />
                <span>Audio</span>
              </button>

              <!-- Helpful / Unhelpful -->
              <div class="flex items-center gap-1 border-l border-slate-300 pl-3">
                <button 
                  @click="chatStore.submitFeedback(msg.id, true)"
                  class="p-1 rounded hover:text-emerald-600 transition"
                  :class="msg.feedback?.is_helpful === true ? 'text-emerald-600' : ''"
                  title="Helpful answer"
                >
                  <ThumbsUp class="w-3.5 h-3.5" />
                </button>
                <button 
                  @click="chatStore.submitFeedback(msg.id, false)"
                  class="p-1 rounded hover:text-rose-600 transition"
                  :class="msg.feedback?.is_helpful === false ? 'text-rose-600' : ''"
                  title="Needs improvement"
                >
                  <ThumbsDown class="w-3.5 h-3.5" />
                </button>
              </div>

              <!-- Create Ticket Handoff Action -->
              <button 
                @click="chatStore.requestHandoffDraft()"
                class="border-l border-slate-300 pl-3 text-[#800020] hover:underline flex items-center gap-1 font-bold transition"
              >
                <TicketPlus class="w-3.5 h-3.5" />
                <span>Create Support Ticket</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Generating indicator -->
        <div v-if="chatStore.isGenerating" class="flex gap-3 max-w-md">
          <div class="w-9 h-9 rounded-xl bg-rose-50 border border-[#800020]/30 flex items-center justify-center text-[#800020]">
            <Bot class="w-4 h-4 animate-pulse" />
          </div>
          <div class="bg-white p-3.5 rounded-2xl rounded-tl-none text-xs text-slate-700 border-2 border-[#800020]/20 flex items-center gap-2 shadow-sm">
            <Loader2 class="w-3.5 h-3.5 animate-spin text-[#800020]" />
            <span class="font-medium">Searching approved university documents & formulating grounded response...</span>
          </div>
        </div>
      </div>

      <!-- Chat Input Form with Maroon Accents -->
      <div class="p-4 border-t-2 border-[#800020]/20 bg-white shadow-sm">
        <form @submit.prevent="handleSend" class="flex items-center gap-2.5 max-w-4xl mx-auto">
          <div class="flex-1 relative">
            <input 
              v-model="inputQuery"
              type="text"
              :placeholder="langStore.t('chat.inputPlaceholder')"
              :disabled="chatStore.isGenerating"
              class="w-full px-4 py-3 rounded-xl bg-white border-2 border-[#800020]/25 text-slate-900 placeholder-slate-400 text-sm focus:border-[#800020] focus:outline-none shadow-sm"
            />
          </div>
          <button 
            type="submit"
            :disabled="!inputQuery.trim() || chatStore.isGenerating"
            class="px-5 py-3 rounded-xl bg-[#800020] hover:bg-[#68001a] disabled:opacity-40 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-[#800020]/25 transition"
          >
            <Send class="w-4 h-4" />
            <span>{{ langStore.t('chat.send') }}</span>
          </button>
        </form>
      </div>
    </div>

    <!-- Modals -->
    <SourceReferenceModal 
      :is-open="isSourceModalOpen"
      :citation="activeCitation"
      @close="isSourceModalOpen = false"
    />

    <ChatTicketHandoffModal 
      :is-open="chatStore.isHandoffModalOpen"
      :draft="chatStore.ticketDraft"
      @close="chatStore.isHandoffModalOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useChatStore, type Citation } from '../stores/chat'
import { useLangStore } from '../stores/lang'
import SourceReferenceModal from '../components/chat/SourceReferenceModal.vue'
import ChatTicketHandoffModal from '../components/chat/ChatTicketHandoffModal.vue'
import {
  Bot,
  User as UserIcon,
  Send,
  Plus,
  Trash2,
  BookOpen,
  Volume2,
  ThumbsUp,
  ThumbsDown,
  TicketPlus,
  Loader2,
  ShieldCheck,
  MessageSquare
} from 'lucide-vue-next'

const chatStore = useChatStore()
const langStore = useLangStore()

const inputQuery = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const activeCitation = ref<Citation | null>(null)
const isSourceModalOpen = ref(false)

const quickPrompts = [
  'How do I apply for the Mahapola Scholarship?',
  'What are the minimum Z-score requirements for Computing?',
  'How do I reset my university LMS password?',
  'How do I access past examination papers in the Library?'
]

onMounted(async () => {
  await chatStore.loadSessions()
  if (chatStore.sessions.length > 0) {
    await chatStore.selectSession(chatStore.sessions[0].id)
  }
})

async function submitPrompt(text: string) {
  inputQuery.value = text
  await handleSend()
}

async function handleSend() {
  if (!inputQuery.value.trim() || chatStore.isGenerating) return
  const q = inputQuery.value
  inputQuery.value = ''
  await chatStore.sendMessage(q)
  await nextTick()
  scrollToBottom()
}

function openSourceModal(c: Citation) {
  activeCitation.value = c
  isSourceModalOpen.value = true
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>
