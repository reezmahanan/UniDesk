<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 bg-academic-canvas">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">
          {{ authStore.isStaff ? 'Department Ticket Workspace' : 'My Support Tickets' }}
        </h1>
        <p class="text-xs text-slate-600 mt-1">
          Track official inquiries submitted to university departments and staff officers.
        </p>
      </div>

      <button 
        @click="isCreateModalOpen = true"
        class="px-4 py-2.5 rounded-xl bg-[#800020] hover:bg-[#600018] text-white text-xs font-bold shadow-md shadow-[#800020]/20 border border-[#800020] flex items-center gap-2 transition shrink-0"
      >
        <Plus class="w-4 h-4" />
        <span>New Support Ticket</span>
      </button>
    </div>

    <!-- Filters Bar -->
    <div class="bg-white p-4 rounded-2xl border-2 border-[#800020]/20 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
      <!-- Status Tabs -->
      <div class="flex flex-wrap gap-1.5">
        <button 
          v-for="st in ['ALL', 'OPEN', 'IN_PROGRESS', 'WAITING_FOR_STUDENT', 'RESOLVED', 'CLOSED']"
          :key="st"
          @click="setStatusFilter(st)"
          class="px-3 py-1.5 rounded-lg font-medium transition"
          :class="selectedStatus === st ? 'bg-[#800020] text-white shadow font-semibold' : 'text-slate-700 hover:bg-[#800020]/10 hover:text-[#800020]'"
        >
          {{ st === 'ALL' ? 'All Tickets' : st.replace(/_/g, ' ') }}
        </button>
      </div>

      <!-- Category Filter -->
      <div class="flex items-center gap-2">
        <span class="text-slate-600 font-medium">Category:</span>
        <select 
          v-model="selectedCategory"
          @change="onCategoryChange"
          class="px-3 py-1.5 rounded-lg bg-white border border-[#800020]/30 text-slate-800 focus:outline-none focus:border-[#800020] cursor-pointer"
        >
          <option value="">All Categories</option>
          <option value="it_support">IT & LMS Support</option>
          <option value="mahapola">Mahapola & Welfare</option>
          <option value="admissions">Admissions & UGC</option>
          <option value="academics">Examinations & Academics</option>
          <option value="library">Library Services</option>
          <option value="general">General Student Affairs</option>
        </select>
      </div>
    </div>

    <!-- Tickets List -->
    <div class="bg-white rounded-2xl border-2 border-[#800020]/20 shadow-sm overflow-hidden">
      <div v-if="ticketsStore.isLoading" class="p-8 text-center text-xs text-slate-600 flex items-center justify-center gap-2">
        <Loader2 class="w-4 h-4 animate-spin text-[#800020]" />
        <span>Loading ticket records...</span>
      </div>

      <div v-else-if="ticketsStore.tickets.length === 0" class="p-12 text-center text-xs text-slate-500 space-y-2">
        <TicketIcon class="w-8 h-8 text-slate-400 mx-auto" />
        <p class="font-medium text-slate-800">No support tickets found.</p>
        <p>Submit an inquiry using the button above or start a conversation with the AI assistant.</p>
      </div>

      <div v-else class="divide-y divide-[#800020]/10">
        <div 
          v-for="t in ticketsStore.tickets" 
          :key="t.id"
          @click="$router.push(`/tickets/${t.id}`)"
          class="p-4 md:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-[#800020]/5 cursor-pointer transition"
        >
          <div class="space-y-1.5 flex-1 min-w-0 pr-4">
            <div class="flex items-center gap-2.5">
              <span class="text-xs font-mono font-bold text-[#800020]">{{ t.ticket_number }}</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider" :class="getPriorityClass(t.priority)">
                {{ t.priority }}
              </span>
              <span class="text-[11px] text-slate-500 capitalize">• {{ t.category.replace(/_/g, ' ') }}</span>
            </div>
            <h3 class="text-sm font-bold text-slate-900 truncate">{{ t.subject }}</h3>
            <p class="text-xs text-slate-600 line-clamp-1">{{ t.description }}</p>
          </div>

          <div class="flex items-center gap-4 shrink-0">
            <div class="text-right hidden md:block text-xs">
              <span class="text-slate-500 block">Student</span>
              <span class="text-slate-800 font-medium">{{ t.student?.full_name }}</span>
            </div>

            <!-- Status Badge -->
            <div 
              class="px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 border"
              :class="getStatusClass(t.status)"
            >
              <span class="w-1.5 h-1.5 rounded-full" :class="getStatusDotClass(t.status)"></span>
              <span>{{ t.status.replace(/_/g, ' ') }}</span>
            </div>

            <ChevronRight class="w-4 h-4 text-slate-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- Create Ticket Modal -->
    <div v-if="isCreateModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-lg rounded-2xl p-6 border-2 border-[#800020]/30 shadow-2xl relative text-slate-900">
        <button 
          @click="isCreateModalOpen = false"
          class="absolute top-4 right-4 text-slate-400 hover:text-slate-800 p-1 rounded-lg hover:bg-slate-100"
        >
          <X class="w-5 h-5" />
        </button>

        <h3 class="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <TicketIcon class="w-5 h-5 text-[#800020]" />
          <span>Create New Support Ticket</span>
        </h3>

        <form @submit.prevent="handleCreateTicket" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Subject</label>
            <input 
              v-model="newTicket.subject" 
              type="text" 
              required
              placeholder="Brief summary of your inquiry"
              class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Category</label>
              <select 
                v-model="newTicket.category"
                class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:outline-none"
              >
                <option value="it_support">IT & LMS Support</option>
                <option value="mahapola">Mahapola & Welfare</option>
                <option value="admissions">Admissions & UGC</option>
                <option value="academics">Examinations & Academics</option>
                <option value="library">Library Services</option>
                <option value="general">General Student Affairs</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Priority</label>
              <select 
                v-model="newTicket.priority"
                class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:outline-none"
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="URGENT">Urgent</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Issue Details</label>
            <textarea 
              v-model="newTicket.description" 
              rows="4" 
              required
              placeholder="Provide complete details so department officers can assist you..."
              class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
            ></textarea>
          </div>

          <div class="pt-2 flex justify-end gap-3 border-t border-[#800020]/15">
            <button 
              type="button" 
              @click="isCreateModalOpen = false"
              class="px-4 py-2 rounded-xl text-xs font-medium text-slate-700 hover:bg-slate-100 transition"
            >
              Cancel
            </button>
            <button 
              type="submit"
              class="px-5 py-2.5 rounded-xl bg-[#800020] hover:bg-[#600018] text-white text-xs font-bold shadow-md shadow-[#800020]/20 transition"
            >
              Submit Ticket
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useTicketsStore } from '../stores/tickets'
import {
  Plus,
  Ticket as TicketIcon,
  ChevronRight,
  Loader2,
  X
} from 'lucide-vue-next'

const authStore = useAuthStore()
const ticketsStore = useTicketsStore()

const selectedStatus = ref('ALL')
const selectedCategory = ref('')
const isCreateModalOpen = ref(false)

const newTicket = ref({
  subject: '',
  description: '',
  category: 'it_support',
  priority: 'MEDIUM',
})

onMounted(async () => {
  await ticketsStore.loadTickets()
})

async function setStatusFilter(st: string) {
  selectedStatus.value = st
  await ticketsStore.loadTickets({
    status: st === 'ALL' ? undefined : st,
    category: selectedCategory.value || undefined,
  })
}

async function onCategoryChange() {
  await ticketsStore.loadTickets({
    status: selectedStatus.value === 'ALL' ? undefined : selectedStatus.value,
    category: selectedCategory.value || undefined,
  })
}

async function handleCreateTicket() {
  try {
    await ticketsStore.createTicket(newTicket.value)
    isCreateModalOpen.value = false
    newTicket.value = { subject: '', description: '', category: 'it_support', priority: 'MEDIUM' }
    await ticketsStore.loadTickets()
  } catch (err: any) {
    alert(`Failed to create ticket: ${err.message}`)
  }
}

function getPriorityClass(p: string): string {
  if (p === 'URGENT') return 'bg-rose-50 text-rose-700 border border-rose-200'
  if (p === 'HIGH') return 'bg-amber-50 text-amber-700 border border-amber-200'
  if (p === 'MEDIUM') return 'bg-[#800020]/10 text-[#800020] border border-[#800020]/30'
  return 'bg-slate-100 text-slate-700 border border-slate-200'
}

function getStatusClass(s: string): string {
  if (s === 'OPEN') return 'bg-blue-50 text-blue-700 border-blue-200'
  if (s === 'IN_PROGRESS') return 'bg-amber-50 text-amber-800 border-amber-300'
  if (s === 'WAITING_FOR_STUDENT') return 'bg-orange-50 text-orange-800 border-orange-300'
  if (s === 'RESOLVED') return 'bg-emerald-50 text-emerald-800 border-emerald-300'
  return 'bg-slate-100 text-slate-700 border-slate-300'
}

function getStatusDotClass(s: string): string {
  if (s === 'OPEN') return 'bg-blue-500'
  if (s === 'IN_PROGRESS') return 'bg-amber-500'
  if (s === 'WAITING_FOR_STUDENT') return 'bg-orange-500'
  if (s === 'RESOLVED') return 'bg-emerald-500'
  return 'bg-slate-500'
}
</script>
