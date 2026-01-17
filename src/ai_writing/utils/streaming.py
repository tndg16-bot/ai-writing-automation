"""Streaming response utilities for AI Writing Automation

This module provides streaming response support for LLM APIs.
"""

import asyncio
from typing import Any, AsyncGenerator, Callable


class StreamingLLM:
    """LLM with streaming response support

    Wraps an LLM instance to provide streaming responses.
    """

    def __init__(self, base_llm: Any):
        """Initialize streaming LLM

        Args:
            base_llm: Base LLM instance
        """
        self.base_llm = base_llm

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        on_chunk: Callable[[str], None] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Generate text with streaming

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            on_chunk: Callback for each chunk
            **kwargs: Additional parameters

        Yields:
            Generated text chunks
        """
        # Check if base LLM supports streaming
        if hasattr(self.base_llm, "generate_stream"):
            async for chunk in self.base_llm.generate_stream(
                prompt, system_prompt=system_prompt, **kwargs
            ):
                if on_chunk:
                    on_chunk(chunk)
                yield chunk
        else:
            # Fallback: generate normally and yield as single chunk
            text = await self.base_llm.generate(prompt, system_prompt=system_prompt, **kwargs)
            if on_chunk:
                on_chunk(text)
            yield text

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text (non-streaming fallback)

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        # Generate with streaming and concatenate
        chunks = []
        async for chunk in self.generate_stream(prompt, system_prompt, **kwargs):
            chunks.append(chunk)

        return "".join(chunks)


class ProgressReporter:
    """Progress reporter for streaming responses

    Reports progress of long-running generation tasks.
    """

    def __init__(self, total_steps: int = 100):
        """Initialize progress reporter

        Args:
            total_steps: Total number of steps
        """
        self.total_steps = total_steps
        self.current_step = 0

    def update(self, progress: float) -> None:
        """Update progress

        Args:
            progress: Progress percentage (0-100)
        """
        percentage = int(progress)
        if percentage != self.current_step:
            self.current_step = percentage
            self._report(percentage)

    def increment(self, delta: int = 1) -> None:
        """Increment progress

        Args:
            delta: Number of steps to increment
        """
        new_step = min(self.current_step + delta, self.total_steps)
        self.current_step = new_step
        self._report(new_step)

    def _report(self, step: int) -> None:
        """Report progress (override for custom reporting)"""
        pass


class ConsoleProgressReporter(ProgressReporter):
    """Console-based progress reporter"""

    def _report(self, step: int) -> None:
        """Report progress to console"""
        # This would use Rich progress bar in production
        # For now, just skip implementation
        pass


async def generate_with_progress(
    llm: Any,
    prompt: str,
    system_prompt: str | None = None,
    reporter: ProgressReporter | None = None,
    **kwargs: Any,
) -> str:
    """Generate with progress reporting

    Args:
        llm: LLM instance
        prompt: User prompt
        system_prompt: System prompt (optional)
        reporter: Progress reporter (optional)
        **kwargs: Additional parameters

    Returns:
        Generated text
    """
    if reporter is None:
        reporter = ProgressReporter()

    # Use streaming if available
    streaming_llm = StreamingLLM(llm)

    # Track total tokens for progress estimation
    total_estimated_tokens = kwargs.get("max_tokens", 1000)
    tokens_generated = 0

    def on_chunk(chunk: str) -> None:
        nonlocal tokens_generated
        # Rough estimate: 1 token ≈ 4 characters
        tokens_generated += len(chunk) // 4
        progress = (tokens_generated / total_estimated_tokens) * 100
        reporter.update(min(progress, 100))

    result = await streaming_llm.generate(
        prompt, system_prompt=system_prompt, on_chunk=on_chunk, **kwargs
    )

    return result
