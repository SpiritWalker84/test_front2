import json
import re
from typing import Any

from app.core.config import get_settings
from app.services.llm_client import BaseLLMClient, _build_messages

settings = get_settings()

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None


class OpenAIClient(BaseLLMClient):
    """OpenAI-compatible API client (OpenAI, Azure, local)."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        s = get_settings()
        self._api_key = (api_key or s.llm_api_key or "").strip()
        self._base_url = (base_url or s.llm_base_url or "").strip() or None
        self._model = (model or s.llm_model or "").strip()
        self._client = None

    def _get_client(self) -> "AsyncOpenAI":
        if AsyncOpenAI is None:
            raise RuntimeError("openai package required. pip install openai")
        if self._client is None:
            kwargs = {"api_key": self._api_key}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = AsyncOpenAI(**kwargs)
        return self._client

    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        client = self._get_client()
        messages = _build_messages(system_prompt, user_prompt)
        response = await client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.5,
        )
        content = response.choices[0].message.content or "{}"
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
        return json.loads(content)
