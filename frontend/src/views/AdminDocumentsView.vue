<template>
  <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 bg-academic-canvas">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-heading font-bold text-slate-900 tracking-tight">Knowledge Ingestion & Document Pipeline</h1>
        <p class="text-xs text-slate-600 mt-1">Upload approved university PDF/DOCX policies to extract, chunk, embed, and index for grounded AI retrieval.</p>
      </div>

      <button 
        @click="isUploadModalOpen = true"
        class="px-4 py-2.5 rounded-xl bg-[#800020] hover:bg-[#600018] text-white text-xs font-bold shadow-md shadow-[#800020]/20 flex items-center gap-2 transition shrink-0"
      >
        <UploadCloud class="w-4 h-4" />
        <span>Upload Document</span>
      </button>
    </div>

    <!-- Documents Table -->
    <div class="bg-white rounded-2xl border-2 border-[#800020]/20 shadow-sm overflow-hidden">
      <div class="p-4 border-b border-[#800020]/15 flex items-center justify-between text-xs bg-[#800020]/5">
        <span class="font-bold text-slate-900">Source Documents Repository ({{ documents.length }})</span>
      </div>

      <div v-if="documents.length === 0" class="p-12 text-center text-xs text-slate-500">
        No documents uploaded yet. Upload your first university policy file.
      </div>

      <div v-else class="divide-y divide-[#800020]/10">
        <div 
          v-for="doc in documents" 
          :key="doc.id"
          class="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-[#800020]/5 transition"
        >
          <div class="space-y-1 flex-1 min-w-0 pr-4">
            <div class="flex items-center gap-2.5">
              <span class="font-bold text-sm text-slate-900 truncate">{{ doc.title }}</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold" :class="doc.status === 'PUBLISHED' ? 'bg-emerald-50 text-emerald-800 border border-emerald-300' : 'bg-slate-100 text-slate-700 border border-slate-300'">
                {{ doc.status }}
              </span>
            </div>
            <div class="flex flex-wrap gap-4 text-xs text-slate-600">
              <span>File: <strong class="text-slate-800">{{ doc.original_filename }}</strong> ({{ (doc.file_size / 1024).toFixed(1) }} KB)</span>
              <span>Indexed Chunks: <strong class="text-[#800020] font-bold">{{ doc.chunks_count || 0 }}</strong></span>
              <span>Version: {{ doc.version }}</span>
            </div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <!-- Status toggle -->
            <button 
              @click="toggleStatus(doc)"
              class="px-3 py-1.5 rounded-xl text-xs font-semibold border transition"
              :class="doc.status === 'PUBLISHED' ? 'bg-amber-50 text-amber-800 border-amber-300 hover:bg-amber-100' : 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100'"
            >
              {{ doc.status === 'PUBLISHED' ? 'Archive Document' : 'Publish Document' }}
            </button>

            <!-- Download link -->
            <a 
              :href="`/api/documents/${doc.id}/download`" 
              target="_blank" 
              download
              class="p-2 rounded-xl bg-slate-100 hover:bg-[#800020] text-slate-700 hover:text-white transition"
              title="Download Source File"
            >
              <Download class="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="isUploadModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-lg rounded-2xl p-6 border-2 border-[#800020]/30 shadow-2xl relative text-slate-900">
        <button 
          @click="isUploadModalOpen = false"
          class="absolute top-4 right-4 text-slate-400 hover:text-slate-800 p-1 rounded-lg hover:bg-slate-100"
        >
          <X class="w-5 h-5" />
        </button>

        <h3 class="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <UploadCloud class="w-5 h-5 text-[#800020]" />
          <span>Upload Source Document</span>
        </h3>

        <form @submit.prevent="handleUpload" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Document Title</label>
            <input 
              v-model="newDocTitle"
              type="text"
              required
              placeholder="e.g. Mahapola Scholarship Circular 2026"
              class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Version</label>
              <input 
                v-model="newDocVersion"
                type="text"
                class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Language</label>
              <select 
                v-model="newDocLanguage"
                class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-[#800020]/25 text-slate-900 text-sm focus:border-[#800020] focus:ring-1 focus:ring-[#800020] focus:outline-none"
              >
                <option value="en">English (en)</option>
                <option value="si">Sinhala (si)</option>
                <option value="ta">Tamil (ta)</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Select File (PDF, DOCX, TXT up to 10MB):</label>
            <input 
              type="file"
              required
              @change="onFileSelect($event)"
              accept=".pdf,.docx,.txt"
              class="w-full text-xs text-slate-600 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-[#800020] file:text-white hover:file:bg-[#600018] cursor-pointer"
            />
          </div>

          <div class="pt-3 flex justify-end gap-3 border-t border-[#800020]/15">
            <button 
              type="button"
              @click="isUploadModalOpen = false"
              class="px-4 py-2 rounded-xl text-xs font-medium text-slate-700 hover:bg-slate-100 transition"
            >
              Cancel
            </button>
            <button 
              type="submit"
              :disabled="isUploading || !selectedFile"
              class="px-5 py-2.5 rounded-xl bg-[#800020] hover:bg-[#600018] disabled:opacity-50 text-white text-xs font-bold transition flex items-center gap-2 shadow-md shadow-[#800020]/20"
            >
              <UploadCloud class="w-4 h-4" />
              <span>{{ isUploading ? 'Extracting & Ingesting...' : 'Start Ingestion' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiRequest } from '../api/client'
import {
  UploadCloud,
  Download,
  X
} from 'lucide-vue-next'

const documents = ref<any[]>([])
const isUploadModalOpen = ref(false)
const newDocTitle = ref('')
const newDocVersion = ref('1.0')
const newDocLanguage = ref('en')
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)

onMounted(async () => {
  await loadDocs()
})

async function loadDocs() {
  documents.value = await apiRequest('/api/documents')
}

function onFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

async function handleUpload() {
  if (!selectedFile.value) return
  isUploading.value = true

  const formData = new FormData()
  formData.append('title', newDocTitle.value)
  formData.append('version', newDocVersion.value)
  formData.append('language', newDocLanguage.value)
  formData.append('file', selectedFile.value)

  try {
    await apiRequest('/api/documents', {
      method: 'POST',
      body: formData,
    })
    isUploadModalOpen.value = false
    newDocTitle.value = ''
    selectedFile.value = null
    await loadDocs()
  } catch (err: any) {
    alert(`Upload failed: ${err.message}`)
  } finally {
    isUploading.value = false
  }
}

async function toggleStatus(doc: any) {
  const target = doc.status === 'PUBLISHED' ? 'ARCHIVED' : 'PUBLISHED'
  try {
    await apiRequest(`/api/documents/${doc.id}/status?new_status=${target}`, {
      method: 'PATCH',
    })
    await loadDocs()
  } catch (err: any) {
    alert(err.message)
  }
}
</script>
