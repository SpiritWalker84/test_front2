from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/config-check")
async def config_check():
    """Проверка: подхватились ли LLM-переменные (ключ не показываем)."""
    s = get_settings()
    return {
        "llm_base_url": s.llm_base_url or "(не задан)",
        "llm_api_key_set": bool(s.llm_api_key and s.llm_api_key.strip()),
        "llm_model": s.llm_model,
    }


@router.get("/config-check/test-request")
async def test_llm_request():
    """Минимальный запрос к LLM API; при ошибке возвращает ответ сервера."""
    import httpx
    s = get_settings()
    key = (s.llm_api_key or "").strip()
    base = (s.llm_base_url or "").strip().rstrip("/")
    if not base or not key:
        return {"ok": False, "error": "LLM_API_KEY или LLM_BASE_URL не заданы"}
    url = f"{base}/chat/completions"
    payload = {
        "model": s.llm_model or "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Say OK"}],
        "max_tokens": 10,
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
            )
        if r.status_code == 200:
            return {"ok": True, "message": "Запрос к API успешен"}
        return {
            "ok": False,
            "status_code": r.status_code,
            "response_body": r.text[:1000],
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
