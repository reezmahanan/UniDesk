<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 bg-academic-canvas">
    <div>
      <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">University Users & Permissions</h1>
      <p class="text-xs text-slate-600 mt-1">Manage student accounts, staff department affiliations, and system administrator privileges.</p>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-2xl border-2 border-[#800020]/20 shadow-sm overflow-hidden">
      <div class="p-4 border-b border-[#800020]/15 bg-[#800020]/5 flex items-center justify-between text-xs">
        <span class="font-bold text-slate-900">Registered Users ({{ users.length }})</span>
      </div>

      <div class="divide-y divide-[#800020]/10">
        <div 
          v-for="u in users" 
          :key="u.id"
          class="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-[#800020]/5 transition"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2.5">
              <span class="font-bold text-sm text-slate-900">{{ u.full_name }}</span>
              <span 
                class="px-2 py-0.5 rounded text-[10px] font-bold"
                :class="{
                  'bg-slate-100 text-slate-700 border border-slate-300': u.role === 'STUDENT',
                  'bg-blue-50 text-blue-800 border border-blue-200': u.role === 'STAFF',
                  'bg-[#800020]/10 text-[#800020] border border-[#800020]/30': u.role === 'ADMIN',
                }"
              >
                {{ u.role }}
              </span>
            </div>
            <p class="text-xs text-slate-600">{{ u.email }} • Index: <span class="font-mono text-slate-800 font-semibold">{{ u.student_index || 'Staff/Admin' }}</span></p>
          </div>

          <!-- Role selection & Actions -->
          <div class="flex items-center gap-3">
            <select 
              :value="u.role"
              @change="onRoleChange(u, $event)"
              class="px-3 py-1.5 rounded-xl bg-white border-2 border-[#800020]/30 text-xs font-semibold text-slate-900 focus:outline-none focus:border-[#800020] cursor-pointer"
            >
              <option value="STUDENT">STUDENT</option>
              <option value="STAFF">STAFF</option>
              <option value="ADMIN">ADMIN</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiRequest } from '../api/client'

const users = ref<any[]>([])

onMounted(async () => {
  await loadUsers()
})

async function loadUsers() {
  users.value = await apiRequest('/api/users')
}

async function onRoleChange(user: any, e: Event) {
  const newRole = (e.target as HTMLSelectElement).value
  try {
    await apiRequest(`/api/users/${user.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ role: newRole }),
    })
    await loadUsers()
  } catch (err: any) {
    alert(err.message)
  }
}
</script>
