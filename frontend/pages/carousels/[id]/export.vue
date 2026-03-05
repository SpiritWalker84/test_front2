<script setup lang="ts">
definePageMeta({ layout: 'default' })

const route = useRoute()
const router = useRouter()
const id = route.params.id as string
const { get, post } = useApi()

type ExportStatus = 'queued' | 'running' | 'done' | 'failed'
type ExportRead = { id: string; status: ExportStatus; zip_url?: string; error_message?: string | null }

const loading = ref(true)
const error = ref('')
const exportId = ref<string | null>(null)
const status = ref<ExportStatus | null>(null)
const zipUrl = ref<string | null>(null)
const pollTimer = ref<ReturnType<typeof setInterval> | null>(null)

async function startOrLoadExport() {
  loading.value = true
  error.value = ''
  try {
    // Стартуем новый экспорт для карусели
    const exp = await post<ExportRead>('/exports', { carousel_id: id })
    exportId.value = exp.id
    status.value = exp.status
    zipUrl.value = exp.zip_url || null
    if (exp.status !== 'done') {
      beginPolling()
    } else if (exp.zip_url) {
      zipUrl.value = exp.zip_url
    }
  } catch (e: any) {
    error.value = e?.data?.detail || e?.message || 'Не удалось запустить экспорт'
  } finally {
    loading.value = false
  }
}

async function pollOnce() {
  if (!exportId.value) return
  try {
    const exp = await get<ExportRead>(`/exports/${exportId.value}`)
    status.value = exp.status
    zipUrl.value = exp.zip_url || null
    if (exp.status === 'done' || exp.status === 'failed') {
      if (pollTimer.value) clearInterval(pollTimer.value)
      pollTimer.value = null
    }
  } catch (e: any) {
    if (pollTimer.value) clearInterval(pollTimer.value)
    pollTimer.value = null
    error.value = e?.data?.detail || e?.message || 'Ошибка запроса экспорта'
  }
}

function beginPolling() {
  if (pollTimer.value) return
  pollTimer.value = setInterval(pollOnce, 2000)
}

function backToEditor() {
  router.push(`/carousels/${id}/edit`)
}

onMounted(startOrLoadExport)

onUnmounted(() => {
  if (pollTimer.value) clearInterval(pollTimer.value)
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">Экспорт карусели</h1>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading">Подготовка экспорта…</p>

    <div v-if="!loading && !error" class="card export-card">
      <p class="hint">
        Готовим изображения слайдов. После завершения вы сможете скачать архив со всеми картинками.
      </p>
      <p class="status-text" v-if="status">
        Статус экспорта:
        <strong>
          <span v-if="status === 'queued'">в очереди</span>
          <span v-else-if="status === 'running'">идёт экспорт…</span>
          <span v-else-if="status === 'done'">готово</span>
          <span v-else-if="status === 'failed'">ошибка</span>
        </strong>
      </p>

      <div class="actions">
        <button type="button" class="btn btn-secondary" @click="backToEditor">
          Назад в редактор
        </button>
        <a
          v-if="zipUrl && status === 'done'"
          :href="zipUrl"
          class="btn btn-primary"
          target="_blank"
          rel="noopener"
        >
          Скачать все слайды (ZIP)
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title { margin-bottom: 0.5rem; }
.error { color: #dc2626; margin-bottom: 0.75rem; }
.export-card { max-width: 640px; }
.hint { font-size: 0.9rem; color: #4b5563; margin-bottom: 0.5rem; }
.status-text { font-size: 0.9rem; color: #374151; margin-bottom: 1rem; }
.actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}
</style>

