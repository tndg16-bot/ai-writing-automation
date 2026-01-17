"""Parallel execution utilities for AI Writing Automation

This module provides utilities for parallel execution of independent tasks.
"""

import asyncio
from typing import Any, Callable, Coroutine
from functools import wraps


class ParallelExecutor:
    """Executor for parallel execution of tasks

    Handles concurrent execution of independent tasks with error handling.
    """

    def __init__(self, max_concurrency: int | None = None):
        """Initialize parallel executor

        Args:
            max_concurrency: Maximum number of concurrent tasks (None = no limit)
        """
        self.max_concurrency = max_concurrency

    async def execute_parallel(
        self,
        tasks: list[Coroutine[Any, Any, Any]],
        show_progress: bool = False,
    ) -> list[Any]:
        """Execute tasks in parallel

        Args:
            tasks: List of async tasks/coroutines
            show_progress: Whether to show progress

        Returns:
            List of results in same order as tasks

        Raises:
            Exception: If any task fails
        """
        if not tasks:
            return []

        if self.max_concurrency:
            # Use semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.max_concurrency)

            async def run_with_semaphore(task: Coroutine[Any, Any, Any]) -> Any:
                async with semaphore:
                    return await task

            tasks = [run_with_semaphore(task) for task in tasks]

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise RuntimeError(f"Task {i} failed: {result}") from result

        return results


class ParallelStageRunner:
    """Runner for parallel execution of pipeline stages

    Allows parallel execution of independent stages within a pipeline.
    """

    def __init__(self, max_concurrency: int = 5):
        """Initialize parallel stage runner

        Args:
            max_concurrency: Maximum number of concurrent stages
        """
        self.executor = ParallelExecutor(max_concurrency)

    async def run_parallel(
        self,
        stages: list[Any],
        context: Any,
    ) -> Any:
        """Run stages in parallel on same context

        Args:
            stages: List of stage instances
            context: Shared context

        Returns:
            Updated context
        """
        # Create tasks for each stage
        tasks = [stage.execute(context) for stage in stages]

        # Execute in parallel
        results = await self.executor.execute_parallel(tasks)

        # Merge results (last result wins for now)
        # In a more sophisticated implementation, we'd merge intelligently
        return results[-1] if results else context


async def parallel_generate(
    llm: Any,
    prompts: list[str],
    system_prompt: str | None = None,
    **kwargs: Any,
) -> list[str]:
    """Generate multiple prompts in parallel

    Args:
        llm: LLM instance
        prompts: List of prompts to generate
        system_prompt: System prompt (optional)
        **kwargs: Additional parameters

    Returns:
        List of generated responses
    """
    tasks = [llm.generate(prompt, system_prompt=system_prompt, **kwargs) for prompt in prompts]

    return await asyncio.gather(*tasks)


async def parallel_generate_json(
    llm: Any,
    prompts: list[str],
    system_prompt: str | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Generate multiple JSON responses in parallel

    Args:
        llm: LLM instance
        prompts: List of prompts to generate
        system_prompt: System prompt (optional)
        **kwargs: Additional parameters

    Returns:
        List of generated JSON objects
    """
    tasks = [llm.generate_json(prompt, system_prompt=system_prompt, **kwargs) for prompt in prompts]

    return await asyncio.gather(*tasks)


def with_semaphore(max_concurrency: int):
    """Decorator to limit concurrency of async function

    Args:
        max_concurrency: Maximum number of concurrent calls

    Returns:
        Decorated function
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


async def batch_process(
    items: list[Any],
    processor: Callable[[Any], Coroutine[Any, Any, Any]],
    batch_size: int = 10,
) -> list[Any]:
    """Process items in batches

    Args:
        items: List of items to process
        processor: Async function to process each item
        batch_size: Number of items to process in each batch

    Returns:
        List of processed results
    """
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]

        # Process batch in parallel
        batch_results = await asyncio.gather(
            *[processor(item) for item in batch],
            return_exceptions=True,
        )

        # Check for exceptions
        for result in batch_results:
            if isinstance(result, Exception):
                raise result

        results.extend(batch_results)

    return results
