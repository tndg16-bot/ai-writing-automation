"""LLM Service with Retry and Rate Limiting

This module provides LLM service with automatic retry and rate limit handling.
"""

import asyncio
from typing import Any, Optional

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from ai_writing.core.exceptions import AIWritingError
from ai_writing.services.llm.base import BaseLLM
from ai_writing.services.llm.openai import OpenAILLM


class RateLimitedError(Exception):
    """Rate limit error"""


class LLMWithRetry(BaseLLM):
    """LLM service with automatic retry and rate limit handling

    Wraps any BaseLLM implementation with retry logic and rate limit handling.
    """

    def __init__(self, base_llm: BaseLLM, max_retries: int = 3):
        """Initialize LLM with retry

        Args:
            base_llm: Base LLM instance
            max_retries: Maximum number of retries
        """
        self.base_llm = base_llm
        self.max_retries = max_retries

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text with automatic retry

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Additional parameters

        Returns:
            Generated text

        Raises:
            AIWritingError: If all retries fail
        """
        try:
            return await self._generate_with_retry(prompt, system_prompt=system_prompt, **kwargs)
        except Exception as e:
            raise AIWritingError(
                f"Failed to generate text after {self.max_retries} retries: {e}",
                suggestions=[
                    "1. Check your API key is valid",
                    "2. Verify you have available API quota",
                    "3. Try reducing the complexity of the prompt",
                    "4. Increase max_retries parameter if needed",
                ],
            ) from e

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate JSON with automatic retry

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Additional parameters

        Returns:
            Parsed JSON object

        Raises:
            AIWritingError: If all retries fail
        """
        try:
            return await self._generate_json_with_retry(
                prompt, system_prompt=system_prompt, **kwargs
            )
        except Exception as e:
            raise AIWritingError(
                f"Failed to generate JSON after {self.max_retries} retries: {e}",
                suggestions=[
                    "1. Check your API key is valid",
                    "2. Verify the JSON schema is valid",
                    "3. Try reducing the complexity of the prompt",
                ],
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((RateLimitedError, asyncio.TimeoutError)),
    )
    async def _generate_with_retry(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text with retry logic

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        return await self.base_llm.generate(prompt, system_prompt=system_prompt, **kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((RateLimitedError, asyncio.TimeoutError)),
    )
    async def _generate_json_with_retry(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate JSON with retry logic

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Additional parameters

        Returns:
            Parsed JSON object
        """
        return await self.base_llm.generate_json(prompt, system_prompt=system_prompt, **kwargs)


class LLMFactoryWithRetry:
    """Factory for creating LLM instances with retry logic

    Extends LLMFactory to automatically wrap instances with retry logic.
    """

    @staticmethod
    def create(
        provider: str,
        **config: Any,
    ) -> BaseLLM:
        """Create LLM with retry logic

        Args:
            provider: Provider name (openai, ollama)
            **config: Configuration parameters

        Returns:
            LLM instance with retry logic
        """
        from ai_writing.services.llm.base import LLMFactory

        # Create base LLM
        base_llm = LLMFactory.create(provider, **config)

        # Wrap with retry logic
        max_retries = config.get("max_retries", 3)
        return LLMWithRetry(base_llm, max_retries=max_retries)
