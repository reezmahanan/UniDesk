<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 bg-academic-canvas">
    <!-- Back button & Ticket Number Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <router-link to="/tickets" class="p-2 rounded-xl text-slate-500 hover:text-[#800020] hover:bg-[#800020]/10 transition">
          <ArrowLeft class="w-5 h-5" />
        </router-link>
        <div>
          <div class="flex items-center gap-2">
            <span class="font-mono text-base font-bold text-[#800020]">{{ ticket?.ticket_number }}</span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold border" :class="getStatusClass(ticket?.status || 'OPEN')">
              {{ ticket?.status?.replace(/_/g, ' ') }}
            </span>
          </div>
          <h1 class="text-xl font-heading font-bold text-slate-900 mt-1">{{ ticket?.subject }}</h1>
        </div>
      </div>

      <!-- Student Resolution Actions -->
      <div v-if="authStore.isStudent && ticket?.status === 'RESOLVED'" class="flex items-center gap-2">
        <button 
          @click="updateStatus('IN_PROGRESS', 'Student requested ticket reopening')"
          class="px-3.5 py-2 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300 text-xs font-bold transition flex items-center gap-1.5"
        >
          <RotateCcw class="w-4 h-4" />
          <span>Reopen Ticket</span>
        </button>
        <button 
          @click="updateStatus('CLOSED', 'Student confirmed resolution')"
          class="px-4 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold shadow-md shadow-emerald-700/20 transition flex items-center gap-1.5"
        >
          <CheckCircle2 class="w-4 h-4" />
          <span>Confirm Resolution</span>
        </button>
      </div>

      <!-- Staff Status / Assign Controls -->
      <div v-if="authStore.isStaff" class="flex flex-wrap items-center gap-2">
        <select 
          :value="ticket?.status"
          @change="onStaffStatusChange($event)"
          class="px-3 py-1.5 rounded-xl bg-white border-2 border-[#800020]/30 text-xs font-semibold text-slate-800 focus:outline-none focus:border-[#800020] cursor-pointer"
        >
          <option value="OPEN">Set: OPEN</option>
          <option value="IN_PROGRESS">Set: IN PROGRESS</option>
          <option value="WAITING_FOR_STUDENT">Set: WAITING FOR STUDENT</option>
          <option value="RESOLVED">Set: RESOLVED</option>
          <option value="CLOSED">Set: CLOSED</option>
        </select>
      </div>
    </div>

    <!-- Main Grid: Conversation + Details Sidebar -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left 2 Cols: Description, Replies & Notes -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Original Description Card -->
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-3">
          <div class="flex items-center justify-between text-xs text-slate-500">
            <span class="font-semibold text-slate-700">Initial Issue Description</span>
            <span>{{ formatDate(ticket?.created_at) }}</span>
          </div>
          <p class="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">{{ ticket?.description }}</p>

          <!-- Transcript Excerpt if Student opted in -->
          <div v-if="ticket?.transcript_excerpt" class="pt-3 border-t border-[#800020]/15 mt-3 space-y-1.5">
            <span class="text-xs font-semibold text-[#800020] flex items-center gap-1.5">
              <MessageSquareQuote class="w-4 h-4" />
              <span>Attached Chat Transcript Excerpt</span>
            </span>
            <div class="p-3 rounded-xl bg-slate-50 border border-[#800020]/20 text-xs text-slate-700 font-mono leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
              {{ ticket.transcript_excerpt }}
            </div>
          </div>
        </div>

        <!-- Staff AI Assistant Tools Card -->
        <div v-if="authStore.isStaff" class="bg-rose-50/50 p-5 rounded-2xl border-2 border-[#800020]/25 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 text-xs font-bold text-[#800020]">
              <Sparkles class="w-4 h-4 text-[#800020]" />
              <span>Staff AI Assistance (Grounded in University Knowledge)</span>
            </div>
            <div class="flex gap-2">
              <button 
                @click="loadAiSummary"
                class="px-3 py-1.5 rounded-lg bg-[#800020] hover:bg-[#600018] text-white text-xs font-bold transition flex items-center gap-1 shadow-sm"
              >
                <span>Summarize Issue</span>
              </button>
              <button 
                @click="loadAiDraftReply"
                class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold transition flex items-center gap-1 shadow-sm"
              >
                <span>Draft Reply</span>
              </button>
            </div>
          </div>

          <!-- Summary Box -->
          <div v-if="ticketsStore.aiSummary" class="p-4 rounded-xl bg-white border border-[#800020]/20 text-xs space-y-2 shadow-sm">
            <p class="text-slate-800 leading-relaxed">{{ ticketsStore.aiSummary.summary }}</p>
            <div class="space-y-1">
              <span class="font-bold text-[#800020]">Key Facts:</span>
              <ul class="list-disc list-inside text-slate-600 pl-1 space-y-0.5">
                <li v-for="f in ticketsStore.aiSummary.key_facts" :key="f">{{ f }}</li>
              </ul>
            </div>
          </div>

          <!-- Draft Reply Box -->
          <div v-if="ticketsStore.aiDraftReply" class="p-4 rounded-xl bg-white border border-[#800020]/20 text-xs space-y-2 shadow-sm">
            <div class="flex items-center justify-between">
              <span class="font-bold text-[#800020]">AI Suggested Response:</span>
              <button 
                @click="useDraftReply(ticketsStore.aiDraftReply.suggested_reply)"
                class="text-xs text-[#800020] hover:underline font-bold"
              >
                Insert into Reply Box →
              </button>
            </div>
            <p class="text-slate-800 whitespace-pre-wrap font-mono bg-slate-50 p-3 rounded-lg border border-slate-200">{{ ticketsStore.aiDraftReply.suggested_reply }}</p>
          </div>
        </div>

        <!-- Replies Thread -->
        <div class="space-y-4">
          <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <MessagesSquare class="w-4 h-4 text-[#800020]" />
            <span>Public Conversation ({{ ticket?.replies?.length || 0 }})</span>
          </h3>

          <div v-if="!ticket?.replies || ticket.replies.length === 0" class="text-xs text-slate-500 p-6 bg-white rounded-2xl border-2 border-[#800020]/15 text-center shadow-sm">
            No public replies yet. Use the message box below to respond.
          </div>

          <div 
            v-for="r in ticket?.replies" 
            :key="r.id"
            class="bg-white p-5 rounded-2xl border-2 shadow-sm space-y-2"
            :class="r.user.role === 'STAFF' || r.user.role === 'ADMIN' ? 'border-[#800020]/30 bg-[#800020]/5' : 'border-[#800020]/15'"
          >
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="font-bold text-slate-900">{{ r.user.full_name }}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold" :class="r.user.role === 'STUDENT' ? 'bg-slate-100 text-slate-700 border border-slate-200' : 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30'">
                  {{ r.user.role }}
                </span>
                <span v-if="r.is_solution" class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px] border border-emerald-300">
                  Official Solution ✓
                </span>
              </div>
              <span class="text-slate-500">{{ formatDate(r.created_at) }}</span>
            </div>
            <p class="text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">{{ r.message }}</p>
          </div>
        </div>

        <!-- Staff Internal Notes (Strictly hidden from students) -->
        <div v-if="authStore.isStaff" class="space-y-4 pt-4 border-t-2 border-[#800020]/15">
          <h3 class="text-sm font-bold text-amber-900 flex items-center gap-2">
            <Lock class="w-4 h-4 text-amber-700" />
            <span>Staff Internal Notes (Confidential)</span>
          </h3>

          <div v-if="ticket?.internal_notes?.length === 0" class="text-xs text-slate-500 p-4 rounded-xl bg-amber-50/60 border border-amber-200 text-center">
            No internal notes recorded yet.
          </div>

          <div 
            v-for="n in ticket?.internal_notes" 
            :key="n.id"
            class="p-4 rounded-xl bg-amber-50/70 border border-amber-300 space-y-1.5 text-xs shadow-sm"
          >
            <div class="flex items-center justify-between text-amber-900 font-bold">
              <span>{{ n.staff.full_name }} (Staff Note)</span>
              <span class="text-slate-500 font-normal text-[11px]">{{ formatDate(n.created_at) }}</span>
            </div>
            <p class="text-slate-800 leading-relaxed whitespace-pre-wrap">{{ n.note }}</p>
          </div>

          <!-- Add Note Form -->
          <form @submit.prevent="handleAddNote" class="space-y-2">
            <textarea 
              v-model="internalNoteText"
              rows="2"
              placeholder="Add confidential internal note for department staff only..."
              class="w-full px-3.5 py-2.5 rounded-xl bg-white border border-amber-300 text-slate-900 text-xs focus:border-amber-600 focus:outline-none"
            ></textarea>
            <div class="flex justify-end">
              <button 
                type="submit"
                :disabled="!internalNoteText.trim()"
                class="px-4 py-2 rounded-xl bg-amber-700 hover:bg-amber-800 disabled:opacity-40 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-sm"
              >
                <Lock class="w-3.5 h-3.5" />
                <span>Save Internal Note</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Reply Form -->
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-3">
          <h4 class="text-xs font-bold text-slate-900 uppercase tracking-wider">Send Reply</h4>
          <form @submit.prevent="handleSendReply" class="space-y-3">
            <textarea 
              v-model="replyText"
              rows="3"
              placeholder="Type your reply here..."
              required
              class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-xs focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
            ></textarea>

            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div v-if="authStore.isStaff" class="flex items-center gap-2 text-xs text-slate-700">
                <input 
                  type="checkbox" 
                  id="markSolution" 
                  v-model="isMarkSolution"
                  class="w-4 h-4 rounded text-[#800020] border-slate-300 focus:ring-[#800020]"
                />
                <label for="markSolution" class="cursor-pointer font-medium">Mark as Resolution & Resolve Ticket</label>
              </div>
              <div v-else></div>

              <button 
                type="submit"
                :disabled="!replyText.trim() || isSubmittingReply"
                class="px-5 py-2.5 rounded-xl bg-[#800020] hover:bg-[#600018] disabled:opacity-40 text-white text-xs font-bold shadow-md shadow-[#800020]/20 transition flex items-center justify-center gap-2 shrink-0"
              >
                <Send class="w-4 h-4" />
                <span>Send Reply</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Right Column: Metadata & Audit Timeline -->
      <div class="space-y-6">
        <!-- Metadata Details Card -->
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-4 text-xs">
          <h3 class="font-bold text-slate-900 text-sm border-b border-[#800020]/15 pb-2">Ticket Properties</h3>

          <div class="space-y-2.5 divide-y divide-[#800020]/10">
            <div class="pt-2 flex justify-between">
              <span class="text-slate-500">Student Owner:</span>
              <span class="font-bold text-slate-900">{{ ticket?.student?.full_name }}</span>
            </div>
            <div class="pt-2 flex justify-between">
              <span class="text-slate-500">Student Index:</span>
              <span class="font-mono text-[#800020] font-bold">{{ ticket?.student?.student_index || 'N/A' }}</span>
            </div>
            <div class="pt-2 flex justify-between">
              <span class="text-slate-500">Faculty:</span>
              <span class="text-slate-800">{{ ticket?.student?.faculty || 'Faculty of Computing' }}</span>
            </div>
            <div class="pt-2 flex justify-between">
              <span class="text-slate-500">Category:</span>
              <span class="font-semibold text-slate-800 capitalize">{{ ticket?.category?.replace(/_/g, ' ') }}</span>
            </div>
            <div class="pt-2 flex justify-between">
              <span class="text-slate-500">Priority:</span>
              <span class="font-bold" :class="ticket?.priority === 'URGENT' ? 'text-rose-600' : 'text-[#800020]'">
                {{ ticket?.priority }}
              </span>
            </div>
            <div class="pt-2 flex justify-between">
              <span class="text-slate-500">Assigned Staff:</span>
              <span class="font-semibold text-slate-800">{{ ticket?.assigned_staff?.full_name || 'Unassigned' }}</span>
            </div>
            <div class="pt-2 flex justify-between">
              <span class="text-slate-500">Created:</span>
              <span class="text-slate-700">{{ formatDate(ticket?.created_at) }}</span>
            </div>
            <div class="pt-2 flex justify-between">
              <span class="text-slate-500">Last Activity:</span>
              <span class="text-slate-700">{{ formatDate(ticket?.updated_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Attachments Card -->
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-4 text-xs">
          <div class="flex items-center justify-between border-b border-[#800020]/15 pb-2">
            <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2">
              <Paperclip class="w-4 h-4 text-[#800020]" />
              <span>Attachments ({{ ticket?.attachments?.length || 0 }})</span>
            </h3>
          </div>

          <div v-if="!ticket?.attachments || ticket.attachments.length === 0" class="text-slate-500 text-center py-2">
            No files attached.
          </div>

          <div v-else class="space-y-2">
            <div 
              v-for="att in ticket.attachments" 
              :key="att.id"
              class="p-2.5 rounded-xl bg-slate-50 border border-[#800020]/20 flex items-center justify-between"
            >
              <div class="truncate mr-2">
                <span class="font-semibold text-slate-800 block truncate">{{ att.original_filename }}</span>
                <span class="text-[10px] text-slate-500">{{ (att.file_size / 1024).toFixed(1) }} KB</span>
              </div>
              <a 
                :href="`/api/tickets/${ticket.id}/attachments/${att.id}/download`"
                target="_blank"
                download
                class="p-1.5 rounded-lg bg-[#800020]/10 hover:bg-[#800020] text-[#800020] hover:text-white transition shrink-0"
                title="Download"
              >
                <Download class="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          <!-- Upload form -->
          <div class="pt-2 border-t border-[#800020]/15">
            <label class="block text-slate-600 mb-1.5 font-semibold">Upload Document (PDF, DOCX, PNG, JPG up to 10MB):</label>
            <input 
              type="file" 
              @change="handleFileUpload($event)"
              class="text-xs text-slate-600 file:mr-2 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-[#800020]/10 file:text-[#800020] hover:file:bg-[#800020] hover:file:text-white cursor-pointer"
            />
          </div>
        </div>

        <!-- Audit Timeline Card -->
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-3 text-xs">
          <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2 border-b border-[#800020]/15 pb-2">
            <History class="w-4 h-4 text-[#800020]" />
            <span>Activity History</span>
          </h3>

          <div class="space-y-3 pt-2">
            <div v-for="ev in ticket?.events" :key="ev.id" class="flex items-start gap-2.5">
              <div class="w-2 h-2 rounded-full bg-[#800020] mt-1.5 shrink-0"></div>
              <div>
                <span class="font-bold text-slate-800 block">{{ ev.event_type }}</span>
                <p class="text-slate-600 text-[11px]">{{ ev.comment }}</p>
                <span class="text-[10px] text-slate-400">{{ formatDate(ev.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTicketsStore } from '../stores/tickets'
import { apiRequest } from '../api/client'
import {
  ArrowLeft,
  RotateCcw,
  CheckCircle2,
  Sparkles,
  MessagesSquare,
  Lock,
  Send,
  Paperclip,
  Download,
  History,
  MessageSquareQuote
} from 'lucide-vue-next'

const route = useRoute()
const authStore = useAuthStore()
const ticketsStore = useTicketsStore()

const replyText = ref('')
const internalNoteText = ref('')
const isMarkSolution = ref(false)
const isSubmittingReply = ref(false)

const ticketId = computed(() => Number(route.params.id))
const ticket = computed(() => ticketsStore.currentTicket)

onMounted(async () => {
  await ticketsStore.loadTicketDetails(ticketId.value)
})

async function updateStatus(st: string, comment?: string) {
  try {
    await ticketsStore.updateStatus(ticketId.value, st, comment)
    await ticketsStore.loadTicketDetails(ticketId.value)
  } catch (err: any) {
    alert(err.message)
  }
}

async function onStaffStatusChange(e: Event) {
  const target = (e.target as HTMLSelectElement).value
  await updateStatus(target, `Staff updated status to ${target}`)
}

async function handleSendReply() {
  if (!replyText.value.trim()) return
  isSubmittingReply.value = true
  try {
    await ticketsStore.addReply(ticketId.value, replyText.value, isMarkSolution.value)
    replyText.value = ''
    isMarkSolution.value = false
    await ticketsStore.loadTicketDetails(ticketId.value)
  } catch (err: any) {
    alert(err.message)
  } finally {
    isSubmittingReply.value = false
  }
}

async function handleAddNote() {
  if (!internalNoteText.value.trim()) return
  try {
    await ticketsStore.addInternalNote(ticketId.value, internalNoteText.value)
    internalNoteText.value = ''
    await ticketsStore.loadTicketDetails(ticketId.value)
  } catch (err: any) {
    alert(err.message)
  }
}

async function handleFileUpload(e: Event) {
  const target = e.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  const formData = new FormData()
  formData.append('file', target.files[0])

  try {
    await apiRequest(`/api/tickets/${ticketId.value}/attachments`, {
      method: 'POST',
      body: formData,
    })
    target.value = ''
    await ticketsStore.loadTicketDetails(ticketId.value)
  } catch (err: any) {
    alert(`Upload failed: ${err.message}`)
  }
}

async function loadAiSummary() {
  await ticketsStore.fetchAiSummary(ticketId.value)
}

async function loadAiDraftReply() {
  await ticketsStore.fetchAiDraftReply(ticketId.value)
}

function useDraftReply(text: string) {
  replyText.value = text
}

function formatDate(iso?: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getStatusClass(s: string): string {
  if (s === 'OPEN') return 'bg-blue-50 text-blue-700 border-blue-200'
  if (s === 'IN_PROGRESS') return 'bg-amber-50 text-amber-800 border-amber-300'
  if (s === 'WAITING_FOR_STUDENT') return 'bg-orange-50 text-orange-800 border-orange-300'
  if (s === 'RESOLVED') return 'bg-emerald-50 text-emerald-800 border-emerald-300'
  return 'bg-slate-100 text-slate-700 border-slate-300'
}
</script>
