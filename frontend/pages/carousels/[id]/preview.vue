<script setup lang="ts">
definePageMeta({ layout: 'default' })

const route = useRoute()
const router = useRouter()
const id = route.params.id as string
const { get } = useApi()

type Slide = { id: string; order: number; title: string; body: string; footer?: string }
type Carousel = { id: string; title: string; status: string; slides_count: number; language: string; created_at: string }

const loading = ref(true)
const error = ref('')
const carousel = ref<Carousel | null>(null)
const slides = ref<Slide[]>([])

async function load() {
  loading.value = true
  error.value = ''
  try {
    // Берём карусель со слайдами, чтобы соответствовать экрану предпросмотра из PDF
    carousel.value = await get(`/carousels/${id}?include_slides=true`)
    // если API не вернул слайды внутри, подстрахуемся отдельным запросом
    try {
      slides.value = await get(`/carousels/${id}/slides`)
    } catch {
      slides.value = []
    }
  } catch (e: any) {
    error.value = e?.data?.detail || e?.message || 'Не удалось загрузить карусель'
  } finally {
    loading.value = false
  }
}

onMounted(load)

function goToEditor() {
  router.push(`/carousels/${id}/edit`)
}
</script>

<template>
  <div class="container">
    <h1 class="page-title">Предпросмотр карусели</h1>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading">Загрузка...</p>

    <div v-if="!loading && !error && carousel" class="card preview-card">
      <p class="subtitle">
        Карусель: <strong>{{ carousel.title || 'Без названия' }}</strong> ·
        {{ slides.length || carousel.slides_count }} слайдов · {{ carousel.language }}
      </p>
      <p class="hint">
        Предпросмотр карусели. Нажмите «В редактор» для создания дизайна и редактирования текста.
      </p>

      <ol class="slides-list">
        <li v-for="s in slides" :key="s.id" class="slide-item">
          <div class="slide-order">#{{ s.order }}</div>
          <div class="slide-content">
            <p class="slide-title">
              {{ s.title || 'Без заголовка' }}
            </p>
            <p class="slide-body">
              {{ (s.body || '').slice(0, 180) }}<span v-if="s.body && s.body.length > 180">…</span>
            </p>
            <p v-if="s.footer" class="slide-footer">
              {{ s.footer }}
            </p>
          </div>
        </li>
      </ol>

      <div class="actions">
        <button type="button" class="btn btn-secondary" @click="goToEditor">
          В редактор
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title { margin-bottom: 0.5rem; }
.error { color: #dc2626; margin-bottom: 0.75rem; }
.preview-card { max-width: 760px; }
.subtitle { font-size: 0.9rem; color: #4b5563; margin-bottom: 0.25rem; }
.hint { font-size: 0.85rem; color: #6b7280; margin-bottom: 1rem; }
.slides-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.slide-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
}
.slide-order {
  font-weight: 600;
  font-size: 0.9rem;
  color: #4b5563;
  min-width: 2.5rem;
}
.slide-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.slide-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
}
.slide-body {
  font-size: 0.85rem;
  color: #374151;
  margin: 0;
}
.slide-footer {
  font-size: 0.8rem;
  color: #6b7280;
  margin: 0;
}
.actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
}
</style>

