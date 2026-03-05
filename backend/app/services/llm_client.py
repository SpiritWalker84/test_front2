"""LLM client abstraction for generation."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Call LLM and return parsed JSON."""
        ...


def _build_messages(system: str, user: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
