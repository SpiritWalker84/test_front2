from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_db
from app.api.v1 import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # shutdown if needed


app = FastAPI(
    title="Carousel API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/config-check")
async def config_check():
    """Проверка: подхватились ли LLM-переменные (ключ не показываем)."""
    s = get_settings()
    return {
        "llm_base_url": s.llm_base_url or "(не задан)",
        "llm_api_key_set": bool(s.llm_api_key and s.llm_api_key.strip()),
        "llm_model": s.llm_model,
    }
