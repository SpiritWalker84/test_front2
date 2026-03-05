<script setup lang="ts">
definePageMeta({ layout: 'default' })
const { get, del } = useApi()
const carousels = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const deletingId = ref<string | null>(null)

onMounted(async () => {
  try {
    carousels.value = await get('/carousels?include_first_slide=true')
  } catch (e: any) {
    error.value = e?.data?.detail || e?.message || 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
})

async function removeCarousel(c: { id: string; title: string }) {
  if (!confirm(`Удалить карусель «${c.title || 'Без названия'}»? Это действие нельзя отменить.`)) return
  deletingId.value = c.id
  try {
    await del(`/carousels/${c.id}`)
    carousels.value = carousels.value.filter((x) => x.id !== c.id)
  } catch (e: any) {
    alert(e?.data?.detail || e?.message || 'Не удалось удалить')
  } finally {
    deletingId.value = null
  }
}

function statusBadge(s: string) {
  const map: Record<string, string> = { draft: 'badge-draft', generating: 'badge-generating', ready: 'badge-ready', failed: 'badge-failed' }
  return map[s] || 'badge-draft'
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div class="container">
    <h1 class="page-title">Мои карусели</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading">Загрузка...</p>
    <div v-else class="grid">
      <div v-for="c in carousels" :key="c.id" class="card">
        <div class="card-preview">
          <div v-if="c.first_slide_title || c.first_slide_body" class="card-preview-text">
            <strong>{{ c.first_slide_title || 'Первый слайд' }}</strong>
            <span>{{ (c.first_slide_body || '').slice(0, 100) }}{{ (c.first_slide_body && c.first_slide_body.length > 100) ? '…' : '' }}</span>
          </div>
          <div v-else class="card-preview-placeholder">Нет контента</div>
        </div>
        <h3 class="card-title">{{ c.title || 'Без названия' }}</h3>
        <p class="card-meta">{{ formatDate(c.created_at) }} · {{ c.slides_count }} слайдов · {{ c.language }}</p>
        <span :class="['badge', statusBadge(c.status)]">{{ c.status }}</span>
        <div class="card-actions">
          <NuxtLink :to="`/carousels/${c.id}/edit`" class="btn btn-primary">{{ c.status === 'ready' ? 'Редактор' : 'Продолжить' }}</NuxtLink>
          <button type="button" class="btn btn-danger" :disabled="deletingId === c.id" @click="removeCarousel(c)">
            {{ deletingId === c.id ? 'Удаление…' : 'Удалить' }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="!loading && !error && carousels.length === 0" class="empty">
      <p>Каруселей пока нет.</p>
      <NuxtLink to="/carousels/new" class="btn btn-primary">Создать карусель</NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.page-title { margin-bottom: 1rem; font-size: 1.5rem; }
.error { color: #dc2626; margin-bottom: 1rem; }
.card-title { font-size: 1.1rem; margin-bottom: 0.25rem; }
.card-meta { font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem; }
.card-preview { min-height: 100px; background: #f3f4f6; border-radius: 8px; margin-bottom: 0.75rem; padding: 0.75rem; display: flex; flex-direction: column; justify-content: center; }
.card-preview-text { font-size: 0.8rem; color: #374151; display: flex; flex-direction: column; gap: 0.25rem; }
.card-preview-text strong { color: #111; }
.card-preview-placeholder { font-size: 0.8rem; color: #9ca3af; }
.card-actions { margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem; }
.btn-danger { background: #dc2626; color: #fff; border: none; padding: 0.5rem 0.75rem; border-radius: 6px; cursor: pointer; font-size: 0.875rem; }
.btn-danger:hover:not(:disabled) { background: #b91c1c; }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }
.empty { text-align: center; padding: 2rem; }
</style>
