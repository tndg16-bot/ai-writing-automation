"""OpenAI LLM サービス"""

import json
import os
from typing import Any

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ai_writing.core.exceptions import LLMError, LLMRateLimitError, LLMResponseError
from ai_writing.services.llm.base import BaseLLM


class OpenAILLM(BaseLLM):
    """OpenAI API を使用した LLM サービス"""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY") or "dummy",
            base_url=base_url
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(LLMRateLimitError),
        reraise=True,
    )
    async def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """テキストを生成する"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            content = response.choices[0].message.content
            if content is None:
                raise LLMResponseError("Empty response from OpenAI")

            return content

        except Exception as e:
            error_message = str(e).lower()
            if "rate_limit" in error_message or "429" in error_message:
                raise LLMRateLimitError(f"Rate limit exceeded: {e}") from e
            raise LLMError(f"OpenAI API error: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(LLMRateLimitError),
        reraise=True,
    )
    async def generate_json(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """JSON形式でテキストを生成する"""
        messages = []

        # システムプロンプトにJSON指示を追加
        base_system = system_prompt or ""
        json_instruction = "\n\nYou must respond with valid JSON only. No additional text."
        messages.append({"role": "system", "content": base_system + json_instruction})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if content is None:
                raise LLMResponseError("Empty response from OpenAI")

            # JSONをパース
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                raise LLMResponseError(f"Failed to parse JSON response: {e}") from e

        except LLMResponseError:
            raise
        except Exception as e:
            error_message = str(e).lower()
            if "rate_limit" in error_message or "429" in error_message:
                raise LLMRateLimitError(f"Rate limit exceeded: {e}") from e
            raise LLMError(f"OpenAI API error: {e}") from e


async def test_openai_connection() -> bool:
    """OpenAI API接続テスト"""
    try:
        llm = OpenAILLM(model="gpt-4o-mini")
        response = await llm.generate("Say 'Hello' in one word.")
        return "hello" in response.lower()
    except Exception:
        return False
