# Carousel MVP — Генерация + Редактор

Минимальный end-to-end продукт: создание каруселей из текста/видео, настройка формата, генерация через LLM, редактор, экспорт в PNG/ZIP.

## Стек

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2 (async), PostgreSQL, MinIO (S3), LLM (OpenAI-совместимый API), Playwright (экспорт в PNG).
- **Frontend:** Nuxt 3 (Vue), адаптивный UI.

## Запуск

### 1. Переменные окружения

```bash
cp .env.example .env
# Отредактируйте .env: LLM_API_KEY, при необходимости DATABASE_URL и S3_*.
```

### 2. Docker Compose (все сервисы одной командой)

```bash
cp .env.example .env
# Заполните LLM_API_KEY в .env

docker-compose up -d
# Первый запуск: миграции выполняются при старте web (create_all). Либо вручную:
#   docker-compose exec web alembic upgrade head
```

- **Фронт:** http://localhost:3000  
- **API:** http://localhost:8000  
- **Документация API:** http://localhost:8000/docs  
- **MinIO:** http://localhost:9001  

### 3. Локально без Docker

```bash
# PostgreSQL и MinIO должны быть запущены, в .env указаны DATABASE_URL и S3_ENDPOINT_URL
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Примеры запросов (curl)

```bash
# Создать карусель
curl -X POST http://localhost:8000/api/v1/carousels \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","source_type":"text","source_payload":{"text":"Текст поста для карусели"},"format":{"slides_count":8,"language":"ru"}}'

# Список каруселей
curl "http://localhost:8000/api/v1/carousels"

# Запуск генерации (подставить CAROUSEL_ID)
curl -X POST http://localhost:8000/api/v1/generations \
  -H "Content-Type: application/json" \
  -d '{"carousel_id":"CAROUSEL_ID"}'

# Статус генерации
curl "http://localhost:8000/api/v1/generations/GENERATION_ID"

# Слайды карусели
curl "http://localhost:8000/api/v1/carousels/CAROUSEL_ID/slides"

# Обновить дизайн
curl -X PATCH "http://localhost:8000/api/v1/carousels/CAROUSEL_ID/design" \
  -H "Content-Type: application/json" \
  -d '{"template":"bold","bg_color":"#f0f0f0"}'

# Экспорт (подставить CAROUSEL_ID)
curl -X POST "http://localhost:8000/api/v1/exports" \
  -H "Content-Type: application/json" \
  -d '{"carousel_id":"CAROUSEL_ID"}'

# Статус экспорта и ссылка на ZIP
curl "http://localhost:8000/api/v1/exports/EXPORT_ID"

# Дублировать карусель (создать из существующей)
curl -X POST "http://localhost:8000/api/v1/carousels/CAROUSEL_ID/duplicate" \
  -H "Content-Type: application/json" \
  -d '{}'

# Загрузка файла (фон/ресурс), пример для S3/MinIO
curl -X POST "http://localhost:8000/api/v1/assets/upload" \
  -F "file=@background.png"
```

## Упрощения MVP

- Авторизация не реализована.
- Источник «из видео»: URL сохраняется и передаётся в LLM как контекст, транскрипция не выполняется.
- Экспорт: полный ZIP всех слайдов 1080×1350 через Playwright; при отсутствии Playwright/Chromium в контейнере экспорт может завершиться с ошибкой (см. Dockerfile).
- «Списание токенов»: только оценка на фронте (текст «~N токенов»), без учёта в БД.
- Экспорт на фронте: отдельный экран с прогрессом и одной кнопкой «Скачать все слайды (ZIP)» без галереи PNG по одному слайду.
- Режим «Создать из карусели» реализован через дублирование существующей карусели (копируются текст слайдов и дизайн, без истории генераций/экспортов).

## Миграции и существующая база

- Если база **чистая** (новый проект), достаточно:

```bash
docker compose exec web alembic upgrade head
```

- Если таблицы уже были созданы до Alembic (через `create_all`), нужно один раз пометить начальную миграцию применённой и затем накатить остальные:

```bash
docker compose exec web alembic stamp 001
docker compose exec web alembic upgrade head
```

## Структура проекта

```
backend/
  app/
    api/v1/       — роутеры
    core/         — config, database
    models/       — SQLAlchemy
    schemas/      — Pydantic
    services/    — бизнес-логика
    storage/      — S3/MinIO
    tasks/        — фоновые задачи (генерация, экспорт)
    templates/    — Jinja2 для рендера слайдов
  alembic/
frontend/         — Nuxt (если добавлен)
```

## Отчёт

- **Затраченное время (реально)**: ~2–2.5 часа чистой работы (не считая времени на техническую проблему с провайдером, из-за которой не открывался сайт Figma).
- **Инструменты вайбкодинга**: Cursor, ChatGPT.
- **Модель / провайдер**: GPT‑5.1 (через инфраструктуру Cursor/ChatGPT).
- **Оценка расхода токенов / $ на задачу**: порядка 4.5 млн токенов суммарно по сессии.
