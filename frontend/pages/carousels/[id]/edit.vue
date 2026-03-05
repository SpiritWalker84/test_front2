<script setup lang="ts">
definePageMeta({ layout: 'default' })
const route = useRoute()
const router = useRouter()
const id = route.params.id as string
const { get, post, patch } = useApi()

const carousel = ref<{ title: string; status: string; slides_count: number } | null>(null)
const slides = ref<Array<{ id: string; order: number; title: string; body: string; footer?: string }>>([])
const design = ref<Record<string, any> | null>(null)
/** Состояние, которое отображается в превью; обновляется по кнопке «Применить» */
const previewDesign = ref<Record<string, any> | null>(null)
const currentIndex = ref(0)
const loading = ref(true)
const genStatus = ref<string | null>(null)
const genError = ref<string | null>(null)
const exportStatus = ref<string | null>(null)
const exportZipUrl = ref<string | null>(null)
type PanelTab = 'content' | 'template' | 'background' | 'text' | 'layout' | 'extra'
const panelTab = ref<PanelTab>('content')

async function load() {
  try {
    carousel.value = await get(`/carousels/${id}`)
    slides.value = await get(`/carousels/${id}/slides`)
    try {
      design.value = await get(`/carousels/${id}/design`)
      previewDesign.value = design.value ? { ...design.value } : null
    } catch { design.value = null; previewDesign.value = null }
  } finally {
    loading.value = false
  }
}

onMounted(load)

const currentSlide = computed(() => slides.value[currentIndex.value])

const previewCardStyle = computed(() => {
  const d = previewDesign.value
  const padding = Math.round((d?.padding ?? 32) * 0.25)
  const bgColor = (d?.bg_color && String(d.bg_color).trim()) || '#ffffff'
  if (d?.bg_type === 'image' && d?.bg_image_url) {
    return {
      padding: `${padding}px`,
      backgroundImage: `url(${d.bg_image_url})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundColor: '#f0f0f0',
    }
  }
  return {
    padding: `${padding}px`,
    backgroundColor: bgColor,
  }
})

const previewContentStyle = computed(() => {
  const d = previewDesign.value
  const justify = d?.align_vertical === 'top' ? 'flex-start' : d?.align_vertical === 'bottom' ? 'flex-end' : 'center'
  const align = d?.align_horizontal === 'left' ? 'flex-start' : d?.align_horizontal === 'right' ? 'flex-end' : 'center'
  return {
    justifyContent: justify,
    alignItems: align,
    textAlign: d?.align_horizontal || 'center',
  }
})

const previewTitleStyle = computed(() => {
  const d = previewDesign.value
  const size = d?.title_font_size ?? 32
  const color = d?.highlight_color || '#111111'
  return {
    fontSize: `${size}px`,
    color,
  }
})

const previewBodyStyle = computed(() => {
  const d = previewDesign.value
  const size = d?.body_font_size ?? 18
  return {
    fontSize: `${size}px`,
  }
})

async function saveSlide(field: 'title' | 'body' | 'footer', value: string) {
  if (!currentSlide.value) return
  await patch(`/carousels/${id}/slides/${currentSlide.value.id}`, { [field]: value })
  if (field === 'title') currentSlide.value.title = value
  if (field === 'body') currentSlide.value.body = value
  if (field === 'footer') currentSlide.value.footer = value
}

async function startGeneration() {
  genStatus.value = 'running'
  genError.value = null
  try {
    const g = await post<{ id: string; status: string; error_message?: string }>('/generations', { carousel_id: id })
    genStatus.value = g.status
    genError.value = g.error_message || null
    if (g.status === 'done') {
      await load()
      router.push(`/carousels/${id}/preview`)
    }
  } catch (e: any) {
    genStatus.value = 'failed'
    genError.value = e?.data?.detail || e?.message || 'Ошибка запроса'
  }
}

let exportPollTimer: ReturnType<typeof setInterval> | null = null
async function startExport() {
  exportStatus.value = 'queued'
  exportZipUrl.value = null
  const e = await post<{ id: string }>('/exports', { carousel_id: id })
  exportPollTimer = setInterval(async () => {
    const r = await get<{ status: string; zip_url?: string }>(`/exports/${e.id}`)
    exportStatus.value = r.status
    if (r.status === 'done' && r.zip_url) {
      exportZipUrl.value = r.zip_url
      if (exportPollTimer) clearInterval(exportPollTimer)
    }
    if (r.status === 'failed') {
      if (exportPollTimer) clearInterval(exportPollTimer)
    }
  }, 2000)
}

function updateDesign(updates: Record<string, any>) {
  if (design.value) Object.assign(design.value, updates)
}

function applyTemplateDefaults(template: string) {
  if (!design.value) return
  const base: Record<string, any> = { template }
  if (template === 'classic') {
    base.title_font_size = 32
    base.body_font_size = 18
    base.highlight_color = '#111111'
    base.padding = 32
    base.bg_type = design.value.bg_type || 'color'
    if (base.bg_type === 'color' && !design.value.bg_color) base.bg_color = '#ffffff'
  } else if (template === 'bold') {
    base.title_font_size = 36
    base.body_font_size = 20
    base.highlight_color = '#111827'
    base.padding = 32
    base.bg_type = 'color'
    base.bg_color = '#f97316'
  } else if (template === 'minimal') {
    base.title_font_size = 28
    base.body_font_size = 16
    base.highlight_color = '#111111'
    base.padding = 24
    base.bg_type = 'color'
    base.bg_color = '#f3f4f6'
  }
  updateDesign(base)
}

const applyingDesign = ref(false)
const DESIGN_FIELDS = ['template', 'bg_type', 'bg_color', 'bg_image_url', 'bg_dim_amount', 'padding', 'align_horizontal', 'align_vertical', 'title_font_size', 'body_font_size', 'highlight_color', 'show_header', 'header_text', 'show_footer', 'footer_text'] as const
async function applyDesign() {
  if (!design.value) return
  applyingDesign.value = true
  try {
    previewDesign.value = { ...design.value }
    const payload: Record<string, any> = {}
    for (const key of DESIGN_FIELDS) {
      if (design.value[key] !== undefined) payload[key] = design.value[key]
    }
    await patch(`/carousels/${id}/design`, payload)
  } finally {
    applyingDesign.value = false
  }
}

onUnmounted(() => {
  if (exportPollTimer) clearInterval(exportPollTimer)
})
</script>

<template>
  <div class="container editor">
    <h1 class="page-title">{{ carousel?.title || 'Редактор' }}</h1>
    <p v-if="loading">Загрузка...</p>
    <div v-else class="editor-grid">
      <div class="preview-area card">
        <p class="preview-label">Превью карточки (как в экспорте)</p>
        <div
          class="slide-preview-card"
          :style="previewCardStyle"
        >
          <div v-if="previewDesign?.bg_dim_amount > 0" class="slide-preview-dim" :style="{ background: `rgba(0,0,0,${previewDesign.bg_dim_amount})` }" />
          <div class="slide-preview-content" :style="previewContentStyle">
            <div v-if="previewDesign?.show_header && previewDesign?.header_text" class="slide-preview-header">{{ previewDesign.header_text }}</div>
            <h1 class="slide-preview-title" :style="previewTitleStyle">{{ currentSlide?.title || 'Заголовок' }}</h1>
            <div class="slide-preview-body" :style="previewBodyStyle">{{ currentSlide?.body || 'Текст слайда' }}</div>
            <div v-if="currentSlide?.footer" class="slide-preview-footer">{{ currentSlide.footer }}</div>
            <div v-if="previewDesign?.show_footer && previewDesign?.footer_text" class="slide-preview-footer">{{ previewDesign.footer_text }}</div>
          </div>
        </div>
        <div class="slide-nav">
          <button type="button" class="btn btn-secondary" :disabled="currentIndex === 0" @click="currentIndex--">←</button>
          <span>{{ currentIndex + 1 }} / {{ slides.length }}</span>
          <button type="button" class="btn btn-secondary" :disabled="currentIndex >= slides.length - 1" @click="currentIndex++">→</button>
        </div>
      </div>
      <div class="panel card">
        <div class="tabs">
          <button
            type="button"
            :class="['tab', { active: panelTab === 'content' }]"
            @click="panelTab = 'content'"
          >
            Текст
          </button>
          <button
            type="button"
            :class="['tab', { active: panelTab === 'template' }]"
            @click="panelTab = 'template'"
          >
            Шаблон
          </button>
          <button
            type="button"
            :class="['tab', { active: panelTab === 'background' }]"
          @click="panelTab = 'background'"
          >
            Фон
          </button>
          <button
            type="button"
            :class="['tab', { active: panelTab === 'text' }]"
            @click="panelTab = 'text'"
          >
            Текст (стиль)
          </button>
          <button
            type="button"
            :class="['tab', { active: panelTab === 'layout' }]"
            @click="panelTab = 'layout'"
          >
            Макет
          </button>
          <button
            type="button"
            :class="['tab', { active: panelTab === 'extra' }]"
            @click="panelTab = 'extra'"
          >
            Дополнительно
          </button>
        </div>
        <!-- Редактирование текста слайда -->
        <template v-if="panelTab === 'content' && currentSlide">
          <label>Заголовок</label>
          <input :value="currentSlide.title" @input="saveSlide('title', ($event.target as HTMLInputElement).value)" />
          <label>Текст</label>
          <textarea :value="currentSlide.body" @input="saveSlide('body', ($event.target as HTMLTextAreaElement).value)" />
          <label>Подвал (опционально)</label>
          <input :value="currentSlide.footer || ''" @input="saveSlide('footer', ($event.target as HTMLInputElement).value)" />
        </template>
        <!-- Шаблон -->
        <template v-else-if="panelTab === 'template' && design">
          <p class="section-hint">Выберите шаблон оформления — он задаёт начальные размеры текста, акцентный цвет и фон.</p>
          <label>Шаблон</label>
          <select :value="design.template" @change="applyTemplateDefaults(($event.target as HTMLSelectElement).value)">
            <option value="classic">Classic</option>
            <option value="bold">Bold</option>
            <option value="minimal">Minimal</option>
          </select>
        </template>

        <!-- Фон -->
        <template v-else-if="panelTab === 'background' && design">
          <label>Тип фона</label>
          <div class="radio-row">
            <label><input type="radio" value="color" :checked="design.bg_type === 'color'" @change="updateDesign({ bg_type: 'color' })" /> Цвет</label>
            <label><input type="radio" value="image" :checked="design.bg_type === 'image'" @change="updateDesign({ bg_type: 'image' })" /> Фото</label>
          </div>

          <label v-if="design.bg_type === 'color'">Цвет фона карточки</label>
          <div v-if="design.bg_type === 'color'" class="color-row">
            <input
              type="color"
              :value="design.bg_color || '#ffffff'"
              @input="updateDesign({ bg_color: ($event.target as HTMLInputElement).value })"
              class="color-picker"
            />
            <input type="text" :value="design.bg_color || '#ffffff'" class="color-hex" readonly />
          </div>

          <template v-else>
            <label>Фоновое изображение (URL)</label>
            <input
              :value="design.bg_image_url || ''"
              placeholder="https://..."
              @input="updateDesign({ bg_image_url: ($event.target as HTMLInputElement).value })"
            />
          </template>

          <label>Затемнение (0–1)</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            :value="design.bg_dim_amount ?? 0"
            @input="updateDesign({ bg_dim_amount: +($event.target as HTMLInputElement).value })"
          />
        </template>

        <!-- Текст (стиль) -->
        <template v-else-if="panelTab === 'text' && design">
          <label>Размер заголовка (px)</label>
          <input
            type="number"
            :value="design.title_font_size ?? 32"
            min="16"
            max="72"
            @input="updateDesign({ title_font_size: +($event.target as HTMLInputElement).value })"
          />

          <label>Размер текста (px)</label>
          <input
            type="number"
            :value="design.body_font_size ?? 18"
            min="12"
            max="48"
            @input="updateDesign({ body_font_size: +($event.target as HTMLInputElement).value })"
          />

          <label>Цвет выделения (заголовок)</label>
          <div class="color-row">
            <input
              type="color"
              :value="design.highlight_color || '#111111'"
              @input="updateDesign({ highlight_color: ($event.target as HTMLInputElement).value })"
              class="color-picker"
            />
            <input type="text" :value="design.highlight_color || '#111111'" class="color-hex" readonly />
          </div>
        </template>

        <!-- Макет -->
        <template v-else-if="panelTab === 'layout' && design">
          <label>Отступы контента</label>
          <input
            type="number"
            :value="design.padding"
            min="0"
            max="200"
            @input="updateDesign({ padding: +($event.target as HTMLInputElement).value })"
          />

          <label>Выравнивание по горизонтали</label>
          <select :value="design.align_horizontal || 'center'" @change="updateDesign({ align_horizontal: ($event.target as HTMLSelectElement).value })">
            <option value="left">Слева</option>
            <option value="center">По центру</option>
            <option value="right">Справа</option>
          </select>

          <label>Выравнивание по вертикали</label>
          <select :value="design.align_vertical || 'center'" @change="updateDesign({ align_vertical: ($event.target as HTMLSelectElement).value })">
            <option value="top">Сверху</option>
            <option value="center">По центру</option>
            <option value="bottom">Снизу</option>
          </select>
        </template>

        <!-- Дополнительно -->
        <template v-else-if="panelTab === 'extra' && design">
          <label>Шапка</label>
          <div class="checkbox-row">
            <label>
              <input
                type="checkbox"
                :checked="design.show_header"
                @change="updateDesign({ show_header: ($event.target as HTMLInputElement).checked })"
              />
              Показывать шапку
            </label>
          </div>
          <input
            v-if="design.show_header"
            :value="design.header_text"
            placeholder="Текст шапки"
            @input="updateDesign({ header_text: ($event.target as HTMLInputElement).value })"
          />

          <label>Подвал</label>
          <div class="checkbox-row">
            <label>
              <input
                type="checkbox"
                :checked="design.show_footer"
                @change="updateDesign({ show_footer: ($event.target as HTMLInputElement).checked })"
              />
              Показывать подвал
            </label>
          </div>
          <input
            v-if="design.show_footer"
            :value="design.footer_text"
            placeholder="Текст подвала"
            @input="updateDesign({ footer_text: ($event.target as HTMLInputElement).value })"
          />
        </template>

        <template v-else-if="panelTab !== 'content' && !design">
          <p class="design-load-msg">Дизайн не загружен. Обновите страницу или откройте карусель снова.</p>
        </template>

        <div v-if="panelTab !== 'content' && design" class="apply-row">
          <button type="button" class="btn btn-primary" :disabled="applyingDesign" @click="applyDesign">
            {{ applyingDesign ? 'Сохранение…' : 'Применить к превью и сохранить' }}
          </button>
        </div>
      </div>
    </div>
    <div class="actions card">
      <div v-if="carousel?.status === 'draft' || carousel?.status === 'failed'" class="action-block">
        <p>Запустить генерацию (примерно ~2000 токенов)</p>
        <button type="button" class="btn btn-primary" :disabled="genStatus === 'running' || genStatus === 'queued'" @click="startGeneration">
          Сгенерировать
        </button>
        <span v-if="genStatus" class="status">Статус: {{ genStatus }}</span>
        <p v-if="genError" class="error-msg">{{ genError }}</p>
      </div>
      <div v-else class="action-block">
        <button
          type="button"
          class="btn btn-primary"
          @click="router.push(`/carousels/${id}/export`)"
        >
          Экспорт
        </button>
        <span class="status">Перейдите на экран экспорта, чтобы скачать все слайды.</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title { margin-bottom: 1rem; }
.editor-grid { display: grid; gap: 1rem; }
@media (min-width: 768px) { .editor-grid { grid-template-columns: 1fr 1fr; } }
.preview-area { min-width: 0; }
.preview-label { font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem; }
.slide-preview-card {
  position: relative;
  width: 100%;
  height: 320px;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  border: 2px solid #e5e7eb;
  /* фон только из :style (previewCardStyle), иначе белый */
  background-color: #ffffff;
}
.slide-preview-dim {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}
.slide-preview-content {
  position: relative;
  z-index: 2;
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 12px;
  overflow: auto;
  min-height: 0;
}
.slide-preview-header { font-size: 12px; color: #666; margin-bottom: 6px; }
.slide-preview-title { font-size: 18px; margin-bottom: 8px; line-height: 1.2; font-weight: 700; }
.slide-preview-body { font-size: 14px; line-height: 1.5; flex: 1; white-space: pre-wrap; overflow-wrap: break-word; }
.slide-preview-footer { font-size: 12px; color: #666; margin-top: 6px; }
.slide-nav { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1rem; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.tab { padding: 0.5rem 1rem; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; }
.tab.active { background: #2563eb; color: #fff; border-color: #2563eb; }
.actions { margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 1rem; }
.action-block { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.status { font-size: 0.875rem; color: #6b7280; }
.error-msg { font-size: 0.875rem; color: #dc2626; margin-top: 0.5rem; max-width: 480px; }
.color-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }
.color-picker { width: 48px; height: 36px; padding: 2px; cursor: pointer; }
.color-hex { flex: 1; font-size: 0.875rem; color: #6b7280; }
.apply-row { margin-top: 1rem; }
.design-load-msg { color: #6b7280; font-size: 0.875rem; }
.section-hint { font-size: 0.85rem; color: #6b7280; margin-bottom: 0.5rem; }
.radio-row { display: flex; gap: 1.5rem; margin-bottom: 0.75rem; font-size: 0.875rem; color: #374151; }
.checkbox-row { margin-bottom: 0.5rem; font-size: 0.875rem; color: #374151; }
</style>
