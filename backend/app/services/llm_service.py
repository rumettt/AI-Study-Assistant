import json
from collections.abc import Iterable

from openai import OpenAI

from app.core.config import settings


class LlmService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for AI generation")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def text(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def json_object(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        response = self.client.chat.completions.create(
            model=settings.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def json_array(self, system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
        parsed = self.json_object(system_prompt, f"{user_prompt}\nWrap the array in an object as {{\"items\": [...]}}.")
        items = parsed.get("items", [])
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict)]

    def stream_text(self, system_prompt: str, user_prompt: str) -> Iterable[str]:
        stream = self.client.chat.completions.create(
            model=settings.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            stream=True,
        )
        for event in stream:
            delta = event.choices[0].delta.content
            if delta:
                yield delta
