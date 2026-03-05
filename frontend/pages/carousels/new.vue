<script setup lang="ts">
definePageMeta({ layout: 'default' })
const router = useRouter()
const { get, post } = useApi()

type CreationMode = 'choice' | 'text' | 'video' | 'fromCarousel'

const creationMode = ref<CreationMode>('choice')
const sourceType = ref<'text' | 'video'>('text')
const title = ref('')
const sourceText = ref('')
const videoUrl = ref('')
const slidesCount = ref(8)
const language = ref('ru')
const styleHint = ref('')
const loading = ref(false)
const error = ref('')
const existingCarousels = ref<any[]>([])
const listLoading = ref(false)
const listError = ref('')

function pickMode(mode: CreationMode) {
  if (mode === 'fromCarousel') {
    creationMode.value = 'fromCarousel'
    loadExistingCarousels()
    return
  }
  creationMode.value = mode
  if (mode === 'text') sourceType.value = 'text'
  if (mode === 'video') sourceType.value = 'video'
}

function goBackToChoice() {
  if (loading.value) return
  creationMode.value = 'choice'
}

async function loadExistingCarousels() {
  listError.value = ''
  listLoading.value = true
  try {
    existingCarousels.value = await get('/carousels?include_first_slide=true')
  } catch (e: any) {
    listError.value = e?.data?.detail || e?.message || 'Не удалось загрузить список каруселей'
  } finally {
    listLoading.value = false
  }
}

async function duplicateFromCarousel(c: { id: string }) {
  loading.value = true
  error.value = ''
  try {
    const carousel = await post<{ id: string }>(`/carousels/${c.id}/duplicate`, {})
    await router.push(`/carousels/${carousel.id}/edit`)
  } catch (e: any) {
    error.value = e?.data?.detail || e?.message || 'Не удалось создать из карусели'
  } finally {
    loading.value = false
  }
}

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const sourcePayload: Record<string, string> = {}
    if (sourceType.value === 'text') sourcePayload.text = sourceText.value
    else sourcePayload.video_url = videoUrl.value
    const carousel = await post<{ id: string }>('/carousels', {
      title: title.value || 'Untitled',
      source_type: sourceType.value,
      source_payload: sourcePayload,
      format: { slides_count: slidesCount.value, language: language.value, style_hint: styleHint.value || undefined },
    })
    await router.push(`/carousels/${carousel.id}/edit`)
  } catch (e: any) {
    error.value = e?.data?.detail || e?.message || 'Ошибка создания'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container">
    <h1 class="page-title">Новая карусель</h1>

    <div v-if="creationMode === 'choice'" class="card choice-card">
      <p class="choice-title">Выберите способ создания карусели</p>
      <div class="choice-grid">
        <button type="button" class="choice-item" @click="pickMode('text')">
          <h2>Свой текст</h2>
          <p>Вставьте текст поста — мы разобьём его на слайды и подготовим карусель.</p>
        </button>
        <button type="button" class="choice-item" @click="pickMode('fromCarousel')">
          <h2>Создать из карусели</h2>
          <p>Переделать уже существующую карусель на основе текста и дизайна.</p>
        </button>
        <button type="button" class="choice-item" @click="pickMode('video')">
          <h2>По ссылке на видео</h2>
          <p>Укажете ссылку на ролик — мы проанализируем и предложим карусель.</p>
        </button>
      </div>
    </div>

    <div v-else-if="creationMode === 'fromCarousel'" class="card form-card">
      <div class="breadcrumbs">
        <button type="button" class="link-back" :disabled="loading" @click="goBackToChoice">← Назад</button>
        <span class="crumb-sep">/</span>
        <span>Новая карусель</span>
        <span class="crumb-sep">/</span>
        <span>Создать из карусели</span>
      </div>

      <p class="hint">Выберите существующую карусель — мы создадим её копию и откроем в редакторе.</p>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="listError" class="error">{{ listError }}</p>
      <p v-if="listLoading">Загрузка списка каруселей…</p>

      <div v-if="!listLoading && existingCarousels.length === 0" class="empty-list">
        Пока нет каруселей, из которых можно сделать копию.
      </div>

      <div v-else class="existing-list">
        <div
          v-for="c in existingCarousels"
          :key="c.id"
          class="existing-item"
        >
          <div class="existing-main">
            <div class="existing-title">
              {{ c.title || 'Без названия' }}
            </div>
            <div class="existing-meta">
              {{ c.slides_count }} слайдов · {{ c.language }} · {{ new Date(c.created_at).toLocaleDateString('ru-RU') }}
            </div>
            <div v-if="c.first_slide_title || c.first_slide_body" class="existing-preview">
              <strong>{{ c.first_slide_title || 'Первый слайд' }}</strong>
              <span>
                {{ (c.first_slide_body || '').slice(0, 80) }}<span v-if="c.first_slide_body && c.first_slide_body.length > 80">…</span>
              </span>
            </div>
          </div>
          <div class="existing-actions">
            <button
              type="button"
              class="btn btn-primary"
              :disabled="loading"
              @click="duplicateFromCarousel(c)"
            >
              Использовать
            </button>
          </div>
        </div>
      </div>
    </div>

    <form v-else class="card form-card" @submit.prevent="submit">
      <div class="breadcrumbs">
        <button type="button" class="link-back" :disabled="loading" @click="goBackToChoice">← Назад</button>
        <span class="crumb-sep">/</span>
        <span>Новая карусель</span>
        <span class="crumb-sep">/</span>
        <span v-if="creationMode === 'text'">Свой текст</span>
        <span v-else-if="creationMode === 'video'">По ссылке на видео</span>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <label>Название</label>
      <input v-model="title" type="text" placeholder="Название карусели" />

      <template v-if="creationMode === 'text'">
        <label>Текст поста</label>
        <textarea v-model="sourceText" placeholder="Вставьте текст..." required />
      </template>
      <template v-else-if="creationMode === 'video'">
        <label>Ссылка на видео</label>
        <input v-model="videoUrl" type="url" placeholder="https://..." required />
      </template>

      <label>Слайдов (6–10)</label>
      <input v-model.number="slidesCount" type="number" min="6" max="10" />

      <label>Язык</label>
      <select v-model="language">
        <option value="ru">RU</option>
        <option value="en">EN</option>
      </select>

      <label>Стиль (пример)</label>
      <textarea v-model="styleHint" placeholder="Пример поста..." />

      <button type="submit" class="btn btn-primary" :disabled="loading">
        {{ loading ? 'Создание...' : 'Создать черновик' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.page-title { margin-bottom: 1rem; }
.choice-card { max-width: 720px; }
.choice-title { margin-bottom: 1rem; font-size: 1rem; color: #4b5563; }
.choice-grid { display: grid; gap: 0.75rem; }
@media (min-width: 768px) {
  .choice-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
.choice-item {
  text-align: left;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  transition: background 0.15s ease, box-shadow 0.15s ease, transform 0.05s ease;
}
.choice-item h2 { font-size: 0.95rem; margin: 0; }
.choice-item p { font-size: 0.85rem; color: #4b5563; margin: 0; }
.choice-item:hover:not(:disabled) {
  background: #eef2ff;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.06);
  transform: translateY(-1px);
}
.choice-item:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
.form-card { max-width: 560px; }
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
}
.link-back {
  border: none;
  background: transparent;
  color: #2563eb;
  cursor: pointer;
  padding: 0;
  font-size: 0.85rem;
}
.link-back:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.crumb-sep { opacity: 0.7; }
.error { color: #dc2626; margin-bottom: 0.5rem; }
.hint { font-size: 0.9rem; color: #4b5563; margin-bottom: 0.75rem; }
.existing-list { display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem; }
.existing-item {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
}
.existing-main { flex: 1; min-width: 0; }
.existing-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 0.25rem; }
.existing-meta { font-size: 0.8rem; color: #6b7280; margin-bottom: 0.25rem; }
.existing-preview {
  font-size: 0.8rem;
  color: #374151;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}
.existing-preview strong { font-weight: 600; }
.existing-actions { display: flex; align-items: center; }
.empty-list { font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem; }
</style>
