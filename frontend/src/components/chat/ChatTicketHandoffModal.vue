<template>
  <div v-if="isOpen && draft" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-white w-full max-w-xl rounded-2xl p-6 border-2 border-[#800020]/30 shadow-2xl relative text-slate-900 max-h-[90vh] overflow-y-auto">
      <button 
        @click="$emit('close')"
        class="absolute top-4 right-4 text-slate-400 hover:text-slate-800 p-1 rounded-lg hover:bg-slate-100"
      >
        <X class="w-5 h-5" />
      </button>

      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-xl bg-[#800020] flex items-center justify-center text-white shadow-md shadow-[#800020]/20 border-2 border-[#800020]">
          <TicketPlus class="w-5 h-5" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-slate-900">Create Support Ticket from Chat</h3>
          <p class="text-xs text-slate-600">Review and edit the AI-drafted ticket before submitting to department officers.</p>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Subject -->
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Subject</label>
          <input 
            v-model="editableSubject"
            type="text"
            required
            class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
          />
        </div>

        <!-- Category & Priority -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Support Category</label>
            <select 
              v-model="editableCategory"
              class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:outline-none"
            >
              <option value="it_support">IT & LMS Support</option>
              <option value="mahapola">Mahapola & Welfare</option>
              <option value="admissions">Admissions & UGC</option>
              <option value="academics">Examinations & Course Reg</option>
              <option value="library">Library Services</option>
              <option value="general">General Campus Affairs</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Priority</label>
            <select 
              v-model="editablePriority"
              class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:outline-none"
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="URGENT">Urgent</option>
            </select>
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Issue Description</label>
          <textarea 
            v-model="editableDescription"
            rows="4"
            required
            class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
          ></textarea>
        </div>

        <!-- Explicit transcript choice checkbox -->
        <div class="p-3.5 rounded-xl bg-[#800020]/5 border border-[#800020]/20 flex items-start gap-3">
          <input 
            type="checkbox" 
            id="includeTranscript"
            v-model="includeTranscript"
            class="mt-1 w-4 h-4 rounded text-[#800020] focus:ring-[#800020] border-slate-300"
          />
          <label for="includeTranscript" class="text-xs text-slate-800 cursor-pointer">
            <span class="font-bold text-[#800020]">Attach recent chat transcript excerpt:</span>
            <p class="text-slate-600 mt-0.5">Allow department staff to review the AI dialogue for additional context.</p>
          </label>
        </div>

        <div v-if="includeTranscript && draft.transcript_excerpt" class="p-3 rounded-lg bg-slate-50 border border-[#800020]/20 text-[11px] text-slate-700 font-mono max-h-24 overflow-y-auto">
          {{ draft.transcript_excerpt }}
        </div>

        <!-- Buttons -->
        <div class="pt-3 flex justify-end gap-3 border-t border-[#800020]/15">
          <button 
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 rounded-xl text-xs font-medium text-slate-700 hover:bg-slate-100 transition"
          >
            Cancel
          </button>
          <button 
            type="submit"
            :disabled="isSubmitting"
            class="px-5 py-2.5 rounded-xl bg-[#800020] hover:bg-[#600018] disabled:opacity-50 text-white text-xs font-bold shadow-md shadow-[#800020]/20 flex items-center gap-2 transition"
          >
            <Check class="w-4 h-4" />
            <span>{{ isSubmitting ? 'Submitting...' : 'Confirm & Submit Ticket' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { TicketPlus, X, Check } from 'lucide-vue-next'
import { useTicketsStore } from '../../stores/tickets'
import type { TicketDraft } from '../../stores/chat'

const props = defineProps<{
  isOpen: boolean
  draft: TicketDraft | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const router = useRouter()
const ticketsStore = useTicketsStore()

const editableSubject = ref('')
const editableDescription = ref('')
const editableCategory = ref('general')
const editablePriority = ref('MEDIUM')
const includeTranscript = ref(true)
const isSubmitting = ref(false)

watch(() => props.draft, (newDraft) => {
  if (newDraft) {
    editableSubject.value = newDraft.suggested_subject
    editableDescription.value = newDraft.suggested_description
    editableCategory.value = newDraft.suggested_category || 'general'
  }
}, { immediate: true })

async function handleSubmit() {
  if (!props.draft) return
  isSubmitting.value = true
  try {
    const ticket = await ticketsStore.createTicket({
      subject: editableSubject.value,
      description: editableDescription.value,
      category: editableCategory.value,
      department_id: props.draft.suggested_department_id,
      priority: editablePriority.value as any,
      transcript_excerpt: includeTranscript.value ? props.draft.transcript_excerpt : undefined,
    })
    emit('close')
    router.push(`/tickets/${ticket.id}`)
  } catch (err: any) {
    alert(`Failed to create ticket: ${err.message}`)
  } finally {
    isSubmitting.value = false
  }
}
</script>
