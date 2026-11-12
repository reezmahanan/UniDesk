<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-8 bg-[#fafafa]">
    <!-- Campus Hero Banner with University Architecture Background -->
    <div class="relative overflow-hidden rounded-3xl border-2 border-[#800020]/25 shadow-sm bg-cover bg-center p-6 md:p-8 bg-[url('/images/campus-hero.jpg')]">
      <!-- Gradient overlay preserving white clarity and contrast -->
      <div class="absolute inset-0 bg-gradient-to-r from-white via-white/95 to-white/70"></div>
      
      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#800020]/10 border border-[#800020]/30 text-[#800020] text-xs font-bold mb-2.5">
            <span class="w-2 h-2 rounded-full bg-[#800020] animate-pulse"></span>
            <span>University of Sri Lanka • Official Help Desk</span>
          </div>
          <h1 class="text-2xl md:text-3xl font-heading font-bold text-slate-900 tracking-tight">
            {{ langStore.t('dashboard.welcome', { name: authStore.currentUser?.full_name || 'Student' }) }}
          </h1>
          <p class="text-xs md:text-sm text-slate-600 mt-1 max-w-2xl font-medium">
            {{ getSubtitle() }}
          </p>
        </div>

        <!-- Quick Action Buttons -->
        <div class="flex items-center gap-3 shrink-0">
          <router-link 
            to="/chat"
            class="px-5 py-2.5 rounded-xl bg-[#800020] hover:bg-[#68001a] text-white text-xs font-bold shadow-md shadow-[#800020]/25 flex items-center gap-2 transition"
          >
            <Bot class="w-4 h-4" />
            <span>Ask AI Assistant</span>
          </router-link>
          <router-link 
            to="/tickets"
            class="px-5 py-2.5 rounded-xl bg-white hover:bg-rose-50 border-2 border-[#800020]/30 text-[#800020] text-xs font-bold flex items-center gap-2 shadow-sm transition"
          >
            <TicketPlus class="w-4 h-4 text-[#800020]" />
            <span>{{ authStore.isStaff ? 'Ticket Workspace' : 'New Ticket' }}</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Role Views Switcher if Staff / Admin -->
    <div v-if="authStore.isStaff" class="flex border-b-2 border-[#800020]/20 gap-4 text-xs font-bold">
      <button 
        @click="activeViewTab = 'student'"
        class="pb-2.5 transition"
        :class="activeViewTab === 'student' ? 'text-[#800020] border-b-2 border-[#800020]' : 'text-slate-500 hover:text-[#800020]'"
      >
        Student Services View
      </button>
      <button 
        @click="activeViewTab = 'staff'"
        class="pb-2.5 transition"
        :class="activeViewTab === 'staff' ? 'text-[#800020] border-b-2 border-[#800020]' : 'text-slate-500 hover:text-[#800020]'"
      >
        Department Staff Workspace
      </button>
      <button 
        v-if="authStore.isAdmin"
        @click="activeViewTab = 'admin'"
        class="pb-2.5 transition"
        :class="activeViewTab === 'admin' ? 'text-[#800020] border-b-2 border-[#800020]' : 'text-slate-500 hover:text-[#800020]'"
      >
        System Admin Metrics
      </button>
    </div>

    <!-- 1. STUDENT VIEW -->
    <div v-if="activeViewTab === 'student'" class="space-y-8">
      <!-- 3 Metrics Cards (White surface with Maroon borders) -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm flex items-center justify-between">
          <div>
            <span class="text-xs text-slate-500 font-semibold block">Open Support Tickets</span>
            <span class="text-2xl font-bold text-slate-900 mt-1 block">{{ studentMetrics.open_tickets_count }}</span>
          </div>
          <div class="w-11 h-11 rounded-xl bg-rose-50 text-[#800020] border border-[#800020]/30 flex items-center justify-center">
            <Ticket class="w-5 h-5" />
          </div>
        </div>

        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm flex items-center justify-between">
          <div>
            <span class="text-xs text-slate-500 font-semibold block">Resolved Tickets</span>
            <span class="text-2xl font-bold text-slate-900 mt-1 block">{{ studentMetrics.resolved_tickets_count }}</span>
          </div>
          <div class="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-600/30 flex items-center justify-center">
            <CheckCircle2 class="w-5 h-5" />
          </div>
        </div>

        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm flex items-center justify-between">
          <div>
            <span class="text-xs text-slate-500 font-semibold block">Awaiting Your Reply</span>
            <span class="text-2xl font-bold text-slate-900 mt-1 block">{{ studentMetrics.awaiting_student_reply_count }}</span>
          </div>
          <div class="w-11 h-11 rounded-xl bg-amber-50 text-amber-700 border border-amber-600/30 flex items-center justify-center">
            <Clock class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Grid: Profile + Mahapola/Bursary Checklist -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Student Profile Card -->
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-4">
          <div class="flex items-center gap-3.5">
            <div class="w-12 h-12 rounded-xl bg-[#800020] flex items-center justify-center text-white text-lg font-bold shadow-md shadow-[#800020]/20">
              {{ authStore.currentUser?.full_name?.charAt(0) || 'S' }}
            </div>
            <div>
              <h3 class="text-base font-bold text-slate-900">{{ authStore.currentUser?.full_name }}</h3>
              <p class="text-xs text-slate-600 font-medium">
                {{ authStore.currentUser?.faculty || 'Faculty of Computing' }} • Index: {{ authStore.currentUser?.student_index || '2026/SE/048' }}
              </p>
              <span class="text-xs text-[#800020] font-semibold">{{ authStore.currentUser?.email }}</span>
            </div>
          </div>

          <div class="pt-3 border-t border-[#800020]/15 grid grid-cols-2 gap-3 text-xs">
            <div class="p-3 rounded-xl bg-rose-50/50 border border-[#800020]/15">
              <span class="text-slate-500 block mb-0.5">Academic Status</span>
              <span class="font-bold text-emerald-700">Good Standing</span>
            </div>
            <div class="p-3 rounded-xl bg-rose-50/50 border border-[#800020]/15">
              <span class="text-slate-500 block mb-0.5">Faculty Registration</span>
              <span class="font-bold text-[#800020]">2026 Active</span>
            </div>
          </div>
        </div>

        <!-- Mahapola / Bursary Verification Checklist -->
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
              <GraduationCap class="w-4 h-4 text-[#800020]" />
              <span>Mahapola & Bursary Checklist</span>
            </h3>
            <span class="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-rose-50 text-[#800020] border border-[#800020]/30">Official Aid</span>
          </div>

          <ul class="space-y-2.5">
            <li 
              v-for="item in studentMetrics.bursary_checklist"
              :key="item.title"
              class="p-3 rounded-xl bg-rose-50/30 border border-[#800020]/15 flex items-center justify-between text-xs"
            >
              <div class="flex items-center gap-2.5">
                <span 
                  class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0"
                  :class="item.completed ? 'bg-emerald-100 text-emerald-700 border border-emerald-500/30' : 'bg-rose-100 text-[#800020] border border-[#800020]/30'"
                >
                  {{ item.completed ? '✓' : '!' }}
                </span>
                <span class="text-slate-800 font-semibold">{{ item.title }}</span>
              </div>
              <span 
                class="px-2.5 py-0.5 rounded text-[10px] font-bold shrink-0"
                :class="item.completed ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-[#800020]'"
              >
                {{ item.badge }}
              </span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Recent Announcements & Inquiries -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Announcements -->
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Bell class="w-4 h-4 text-[#800020]" />
              <span>Latest Official Notices</span>
            </h3>
            <router-link to="/notices" class="text-xs text-[#800020] hover:underline font-bold">View all →</router-link>
          </div>

          <div class="space-y-3">
            <div 
              v-for="n in studentMetrics.latest_notices" 
              :key="n.id"
              class="p-3.5 rounded-xl bg-rose-50/30 border border-[#800020]/15 space-y-1.5"
            >
              <div class="flex items-center justify-between text-[11px]">
                <span class="px-2 py-0.5 rounded font-bold" :class="n.tag === 'Urgent' ? 'bg-rose-100 text-rose-800' : 'bg-rose-50 text-[#800020] border border-[#800020]/20'">
                  {{ n.tag }}
                </span>
                <span class="text-slate-500 font-medium">{{ n.date }}</span>
              </div>
              <h4 class="text-xs font-bold text-slate-900">{{ n.title }}</h4>
              <p class="text-xs text-slate-600 line-clamp-2 leading-relaxed">{{ n.content }}</p>
            </div>
          </div>
        </div>

        <!-- Recent Chat Inquiries -->
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
              <MessageSquare class="w-4 h-4 text-[#800020]" />
              <span>Recent AI Consultations</span>
            </h3>
            <router-link to="/chat" class="text-xs text-[#800020] hover:underline font-bold">Open chat →</router-link>
          </div>

          <div v-if="studentMetrics.recent_inquiries.length === 0" class="text-xs text-slate-500 py-8 text-center font-medium">
            No recent AI inquiries. Ask your first question anytime!
          </div>

          <div v-else class="space-y-2">
            <router-link 
              v-for="inq in studentMetrics.recent_inquiries" 
              :key="inq.id"
              to="/chat"
              class="p-3 rounded-xl bg-rose-50/20 hover:bg-rose-50/60 border border-[#800020]/15 flex items-center justify-between text-xs text-slate-700 transition block font-medium"
            >
              <span class="truncate mr-2">{{ inq.title }}</span>
              <span class="text-[11px] text-slate-500 shrink-0">{{ inq.date }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. STAFF VIEW TAB -->
    <div v-else-if="activeViewTab === 'staff'" class="space-y-8">
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm">
          <span class="text-xs text-slate-500 font-semibold block">Unassigned Dept Tickets</span>
          <span class="text-2xl font-bold text-[#800020] mt-1 block">{{ staffMetrics.unassigned_department_tickets_count }}</span>
        </div>
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm">
          <span class="text-xs text-slate-500 font-semibold block">My Assigned Workload</span>
          <span class="text-2xl font-bold text-slate-900 mt-1 block">{{ staffMetrics.assigned_workload_count }}</span>
        </div>
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm">
          <span class="text-xs text-slate-500 font-semibold block">High Priority Tickets</span>
          <span class="text-2xl font-bold text-rose-700 mt-1 block">{{ staffMetrics.high_priority_count }}</span>
        </div>
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm">
          <span class="text-xs text-slate-500 font-semibold block">Total Resolved</span>
          <span class="text-2xl font-bold text-emerald-700 mt-1 block">{{ staffMetrics.total_resolved_count }}</span>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm flex items-center justify-between">
        <div>
          <h3 class="text-sm font-bold text-slate-900">Department Queue Operations ({{ staffMetrics.department_code }})</h3>
          <p class="text-xs text-slate-500 mt-1">Review unassigned tickets, assign officers, and write internal notes.</p>
        </div>
        <router-link to="/tickets" class="px-5 py-2.5 rounded-xl bg-[#800020] hover:bg-[#68001a] text-white text-xs font-bold transition shadow-md shadow-[#800020]/20">
          Go to Ticket Workspace →
        </router-link>
      </div>
    </div>

    <!-- 3. ADMIN VIEW TAB -->
    <div v-else-if="activeViewTab === 'admin'" class="space-y-8">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm">
          <span class="text-xs text-slate-500 font-semibold block">Total Registered Users</span>
          <span class="text-2xl font-bold text-slate-900 mt-1 block">{{ adminMetrics.total_users_count }}</span>
        </div>
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm">
          <span class="text-xs text-slate-500 font-semibold block">Published Source Documents</span>
          <span class="text-2xl font-bold text-[#800020] mt-1 block">{{ adminMetrics.total_published_documents }}</span>
        </div>
        <div class="bg-white p-5 rounded-2xl border-2 border-[#800020]/20 shadow-sm">
          <span class="text-xs text-slate-500 font-semibold block">Helpful Answer Ratings</span>
          <span class="text-2xl font-bold text-emerald-700 mt-1 block">{{ adminMetrics.helpful_feedback_count }}</span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-3">
          <h3 class="text-sm font-bold text-slate-900">Tickets by Department</h3>
          <div class="space-y-2 text-xs">
            <div v-for="(count, dept) in adminMetrics.tickets_by_department" :key="dept" class="flex justify-between p-2.5 rounded-lg bg-rose-50/40 border border-[#800020]/10">
              <span class="text-slate-800 font-medium">{{ dept }}</span>
              <span class="font-bold text-[#800020]">{{ count }}</span>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-2xl border-2 border-[#800020]/20 shadow-sm space-y-3">
          <h3 class="text-sm font-bold text-slate-900">Tickets by Status</h3>
          <div class="space-y-2 text-xs">
            <div v-for="(count, stat) in adminMetrics.tickets_by_status" :key="stat" class="flex justify-between p-2.5 rounded-lg bg-rose-50/40 border border-[#800020]/10">
              <span class="text-slate-800 font-medium">{{ stat }}</span>
              <span class="font-bold text-[#800020]">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLangStore } from '../stores/lang'
import { apiRequest } from '../api/client'
import {
  Bot,
  TicketPlus,
  Ticket,
  CheckCircle2,
  Clock,
  GraduationCap,
  Bell,
  MessageSquare
} from 'lucide-vue-next'

const authStore = useAuthStore()
const langStore = useLangStore()

const activeViewTab = ref<'student' | 'staff' | 'admin'>('student')

const studentMetrics = ref({
  open_tickets_count: 0,
  resolved_tickets_count: 0,
  awaiting_student_reply_count: 0,
  recent_inquiries: [] as any[],
  latest_notices: [] as any[],
  bursary_checklist: [] as any[],
})

const staffMetrics = ref({
  unassigned_department_tickets_count: 0,
  assigned_workload_count: 0,
  high_priority_count: 0,
  total_resolved_count: 0,
  department_code: 'ALL',
})

const adminMetrics = ref({
  total_users_count: 0,
  total_published_documents: 0,
  helpful_feedback_count: 0,
  tickets_by_department: {} as Record<string, number>,
  tickets_by_status: {} as Record<string, number>,
})

onMounted(async () => {
  if (authStore.isStaff && !authStore.isStudent) {
    activeViewTab.value = 'staff'
  }
  await loadDashboardData()
})

async function loadDashboardData() {
  try {
    studentMetrics.value = await apiRequest('/api/dashboard/student')
    if (authStore.isStaff) {
      staffMetrics.value = await apiRequest('/api/dashboard/staff')
    }
    if (authStore.isAdmin) {
      adminMetrics.value = await apiRequest('/api/dashboard/admin')
    }
  } catch (e) {
    console.error(e)
  }
}

function getSubtitle(): string {
  if (authStore.isAdmin) return langStore.t('dashboard.adminSubtitle')
  if (authStore.isStaff) return langStore.t('dashboard.staffSubtitle')
  return langStore.t('dashboard.studentSubtitle')
}
</script>
