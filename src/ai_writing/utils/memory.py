"""Memory optimization utilities for AI Writing Automation

This module provides utilities for optimizing memory usage.
"""

import gc
import sys
from typing import Any, Generator, List
from functools import lru_cache


class ChunkedTextProcessor:
    """Process large texts in chunks to reduce memory usage

    Processes large texts in smaller chunks to avoid loading entire
    text into memory at once.
    """

    def __init__(self, chunk_size: int = 4000):
        """Initialize chunked processor

        Args:
            chunk_size: Maximum size of each chunk (in characters)
        """
        self.chunk_size = chunk_size

    def chunk_text(self, text: str) -> Generator[str, None, None]:
        """Split text into chunks

        Args:
            text: Text to chunk

        Yields:
            Text chunks
        """
        for i in range(0, len(text), self.chunk_size):
            yield text[i : i + self.chunk_size]

    def process_in_chunks(
        self,
        text: str,
        processor: callable,
        **kwargs: Any,
    ) -> Any:
        """Process text in chunks

        Args:
            text: Text to process
            processor: Function to process each chunk
            **kwargs: Additional arguments for processor

        Returns:
            Combined results from all chunks
        """
        results = []

        for chunk in self.chunk_text(text):
            result = processor(chunk, **kwargs)
            results.append(result)

            # Explicitly free memory
            del chunk
            gc.collect()

        return results


class MemoryMonitor:
    """Monitor memory usage"""

    @staticmethod
    def get_memory_usage() -> dict[str, Any]:
        """Get current memory usage

        Returns:
            Dictionary with memory statistics
        """
        # For Python, we can use psutil if available
        try:
            import psutil

            process = psutil.Process()
            return {
                "rss_mb": process.memory_info().rss / 1024 / 1024,
                "vms_mb": process.memory_info().vms / 1024 / 1024,
                "percent": process.memory_percent(),
            }
        except ImportError:
            # Fallback: use sys
            return {
                "object_count": len(gc.get_objects()),
                "garbage_count": len(gc.garbage),
            }

    @staticmethod
    def optimize_memory() -> None:
        """Optimize memory usage"""
        # Force garbage collection
        gc.collect()

        # Clear any caches
        try:
            # Clear LRU caches
            for func in gc.get_objects():
                if hasattr(func, "cache_clear"):
                    func.cache_clear()
        except Exception:
            pass


class LRUCacheWithSize:
    """LRU cache with size limit in bytes

    Similar to functools.lru_cache but tracks memory usage.
    """

    def __init__(self, max_size_bytes: int = 10 * 1024 * 1024):
        """Initialize size-limited LRU cache

        Args:
            max_size_bytes: Maximum cache size in bytes
        """
        self.max_size_bytes = max_size_bytes
        self.current_size = 0
        self.cache = {}

    def get(self, key: Any) -> Any | None:
        """Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        return self.cache.get(key)

    def set(self, key: Any, value: Any, size_bytes: int | None = None) -> None:
        """Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            size_bytes: Estimated size (None = estimate)
        """
        if size_bytes is None:
            # Rough estimate
            size_bytes = len(str(key)) + len(str(value))

        # Evict old entries if necessary
        while self.current_size + size_bytes > self.max_size_bytes:
            if not self.cache:
                break
            oldest_key = next(iter(self.cache))
            self._remove(oldest_key)

        self.cache[key] = value
        self.current_size += size_bytes

    def _remove(self, key: Any) -> None:
        """Remove entry from cache

        Args:
            key: Cache key
        """
        if key in self.cache:
            # Estimate size
            size_bytes = len(str(key)) + len(str(self.cache[key]))
            del self.cache[key]
            self.current_size -= size_bytes

    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
        self.current_size = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics

        Returns:
            Statistics dictionary
        """
        return {
            "entries": len(self.cache),
            "size_bytes": self.current_size,
            "size_mb": self.current_size / 1024 / 1024,
            "max_size_bytes": self.max_size_bytes,
            "usage_percent": (self.current_size / self.max_size_bytes) * 100,
        }


def optimize_large_generation(
    generator: callable,
    prompt: str,
    max_tokens: int = 4000,
    **kwargs: Any,
) -> str:
    """Optimize generation of large text

    Args:
        generator: Generation function
        prompt: Generation prompt
        max_tokens: Maximum tokens to generate
        **kwargs: Additional arguments

    Returns:
            Generated text
    """
    # Process in smaller chunks if needed
    chunk_processor = ChunkedTextProcessor(chunk_size=2000)

    # Generate text
    text = generator(prompt, max_tokens=max_tokens, **kwargs)

    # Process in chunks if large
    if len(text) > 10000:
        return "".join(chunk_processor.chunk_text(text))

    return text


def with_memory_cleanup(func: callable) -> callable:
    """Decorator that cleans up memory after function execution

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Force garbage collection
            gc.collect()

    return wrapper
