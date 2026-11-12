import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiRequest } from '../api/client'

export interface Attachment {
  id: number
  original_filename: string
  file_size: number
  mime_type: string
  created_at: string
}

export interface TicketReply {
  id: number
  ticket_id: number
  user_id: number
  user: {
    id: number
    full_name: string
    role: string
    student_index?: string
  }
  message: string
  is_solution: boolean
  created_at: string
  attachments?: Attachment[]
}

export interface TicketInternalNote {
  id: number
  ticket_id: number
  staff_id: number
  staff: {
    id: number
    full_name: string
    role: string
  }
  note: string
  created_at: string
}

export interface TicketEvent {
  id: number
  event_type: string
  old_value?: string
  new_value?: string
  comment?: string
  created_at: string
}

export interface Ticket {
  id: number
  ticket_number: string
  student_id: number
  student: {
    id: number
    full_name: string
    email: string
    student_index?: string
    faculty?: string
  }
  department_id: number
  assigned_staff_id?: number
  assigned_staff?: {
    id: number
    full_name: string
    email: string
  }
  subject: string
  description: string
  category: string
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'
  status: 'OPEN' | 'IN_PROGRESS' | 'WAITING_FOR_STUDENT' | 'RESOLVED' | 'CLOSED'
  transcript_excerpt?: string
  created_at: string
  updated_at: string
  resolved_at?: string
  closed_at?: string
  replies?: TicketReply[]
  internal_notes?: TicketInternalNote[]
  events?: TicketEvent[]
  attachments?: Attachment[]
}

export const useTicketsStore = defineStore('tickets', () => {
  const tickets = ref<Ticket[]>([])
  const currentTicket = ref<Ticket | null>(null)
  const isLoading = ref<boolean>(false)
  const aiSummary = ref<{ summary: string; key_facts: string[]; missing_information: string[] } | null>(null)
  const aiDraftReply = ref<{ suggested_reply: string; relevant_sources: string[] } | null>(null)

  async function loadTickets(filters?: { status?: string; category?: string; department_id?: number }) {
    isLoading.value = true
    try {
      const queryParams = new URLSearchParams()
      if (filters?.status) queryParams.set('status_filter', filters.status)
      if (filters?.category) queryParams.set('category_filter', filters.category)
      if (filters?.department_id) queryParams.set('department_id', String(filters.department_id))

      const url = `/api/tickets${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
      tickets.value = await apiRequest<Ticket[]>(url)
    } finally {
      isLoading.value = false
    }
  }

  async function loadTicketDetails(ticketId: number) {
    isLoading.value = true
    try {
      currentTicket.value = await apiRequest<Ticket>(`/api/tickets/${ticketId}`)
      aiSummary.value = null
      aiDraftReply.value = null
    } finally {
      isLoading.value = false
    }
  }

  async function createTicket(payload: {
    subject: string
    description: string
    category: string
    department_id?: number
    priority?: string
    transcript_excerpt?: string
  }): Promise<Ticket> {
    const ticket = await apiRequest<Ticket>('/api/tickets', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    tickets.value.unshift(ticket)
    return ticket
  }

  async function addReply(ticketId: number, message: string, is_solution: boolean = false) {
    const reply = await apiRequest<TicketReply>(`/api/tickets/${ticketId}/replies`, {
      method: 'POST',
      body: JSON.stringify({ message, is_solution }),
    })
    if (currentTicket.value && currentTicket.value.id === ticketId) {
      if (!currentTicket.value.replies) currentTicket.value.replies = []
      currentTicket.value.replies.push(reply)
      if (is_solution) currentTicket.value.status = 'RESOLVED'
    }
    return reply
  }

  async function addInternalNote(ticketId: number, note: string) {
    const internalNote = await apiRequest<TicketInternalNote>(`/api/tickets/${ticketId}/internal-notes`, {
      method: 'POST',
      body: JSON.stringify({ note }),
    })
    if (currentTicket.value && currentTicket.value.id === ticketId) {
      if (!currentTicket.value.internal_notes) currentTicket.value.internal_notes = []
      currentTicket.value.internal_notes.push(internalNote)
    }
    return internalNote
  }

  async function updateStatus(ticketId: number, status: string, comment?: string) {
    const updated = await apiRequest<Ticket>(`/api/tickets/${ticketId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, comment }),
    })
    if (currentTicket.value && currentTicket.value.id === ticketId) {
      currentTicket.value.status = updated.status
    }
    const idx = tickets.value.findIndex(t => t.id === ticketId)
    if (idx !== -1) tickets.value[idx].status = updated.status
    return updated
  }

  async function assignStaff(ticketId: number, staffId: number | null, departmentId?: number, comment?: string) {
    const updated = await apiRequest<Ticket>(`/api/tickets/${ticketId}/assign`, {
      method: 'PATCH',
      body: JSON.stringify({ assigned_staff_id: staffId, department_id: departmentId, comment }),
    })
    if (currentTicket.value && currentTicket.value.id === ticketId) {
      currentTicket.value.assigned_staff_id = updated.assigned_staff_id
      currentTicket.value.assigned_staff = updated.assigned_staff
    }
    return updated
  }

  async function fetchAiSummary(ticketId: number) {
    try {
      aiSummary.value = await apiRequest(`/api/tickets/${ticketId}/ai-summary`)
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchAiDraftReply(ticketId: number) {
    try {
      aiDraftReply.value = await apiRequest(`/api/tickets/${ticketId}/ai-draft-reply`)
    } catch (e) {
      console.error(e)
    }
  }

  return {
    tickets,
    currentTicket,
    isLoading,
    aiSummary,
    aiDraftReply,
    loadTickets,
    loadTicketDetails,
    createTicket,
    addReply,
    addInternalNote,
    updateStatus,
    assignStaff,
    fetchAiSummary,
    fetchAiDraftReply,
  }
})
