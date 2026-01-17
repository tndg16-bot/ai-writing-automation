"""LLM response caching for AI Writing Automation

This module provides caching for LLM API responses to reduce costs and latency.
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from diskcache import Cache


class LLMCache:
    """LLM response cache with disk persistence

    Caches LLM API responses based on prompt hash to reduce API calls.
    Supports TTL (Time To Live) for cache expiration.
    """

    def __init__(self, cache_dir: str | Path = "./cache/llm", default_ttl: int = 86400):
        """Initialize LLM cache

        Args:
            cache_dir: Cache directory path
            default_ttl: Default TTL in seconds (default: 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache = Cache(str(self.cache_dir))
        self.default_ttl = default_ttl

        # Statistics
        self.hits = 0
        self.misses = 0

    def _generate_cache_key(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        **params: Any,
    ) -> str:
        """Generate cache key from parameters

        Args:
            prompt: User prompt
            model: Model name
            system_prompt: System prompt (optional)
            **params: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            MD5 hash cache key
        """
        key_data = f"{prompt}|{model}|{system_prompt or ''}"

        # Add sorted parameters to ensure consistent hashing
        for k, v in sorted(params.items()):
            key_data += f"|{k}:{json.dumps(v) if isinstance(v, (dict, list)) else v}"

        return hashlib.md5(key_data.encode("utf-8")).hexdigest()

    def get(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        **params: Any,
    ) -> Optional[str]:
        """Get cached response

        Args:
            prompt: User prompt
            model: Model name
            system_prompt: System prompt (optional)
            **params: Additional parameters

        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_cache_key(prompt, model, system_prompt, **params)
        cached = self.cache.get(key)

        if cached:
            # Check if expired
            if "expires_at" in cached:
                expires_at = datetime.fromisoformat(cached["expires_at"])
                if datetime.now() > expires_at:
                    self.misses += 1
                    return None

            self.hits += 1
            return cached["response"]

        self.misses += 1
        return None

    def set(
        self,
        prompt: str,
        response: str,
        model: str,
        system_prompt: str | None = None,
        ttl: Optional[int] = None,
        **params: Any,
    ) -> None:
        """Cache response

        Args:
            prompt: User prompt
            response: LLM response
            model: Model name
            system_prompt: System prompt (optional)
            ttl: TTL in seconds (default: default_ttl)
            **params: Additional parameters
        """
        key = self._generate_cache_key(prompt, model, system_prompt, **params)

        # Calculate expiration
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)

        cache_data = {
            "response": response,
            "prompt": prompt,
            "model": model,
            "system_prompt": system_prompt,
            "params": params,
            "cached_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
        }

        self.cache.set(key, cache_data, expire=ttl)

    def invalidate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        **params: Any,
    ) -> bool:
        """Invalidate specific cache entry

        Args:
            prompt: User prompt
            model: Model name
            system_prompt: System prompt (optional)
            **params: Additional parameters

        Returns:
            True if entry was invalidated, False otherwise
        """
        key = self._generate_cache_key(prompt, model, system_prompt, **params)
        try:
            self.cache.delete(key)
            return True
        except KeyError:
            return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics

        Returns:
            Statistics dictionary
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests) if total_requests > 0 else 0.0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "cache_size": self.cache.size,
            "cache_volume": self.cache.volume,
            "cache_dir": str(self.cache_dir),
        }

    def get_expired(self, limit: int = 100) -> list[str]:
        """Get expired cache keys

        Args:
            limit: Maximum number of keys to return

        Returns:
            List of expired keys
        """
        expired_keys = []
        now = datetime.now()

        for key in list(self.cache)[:limit]:
            try:
                cached = self.cache.get(key)
                if cached and "expires_at" in cached:
                    expires_at = datetime.fromisoformat(cached["expires_at"])
                    if now > expires_at:
                        expired_keys.append(key)
            except Exception:
                continue

        return expired_keys

    def cleanup_expired(self) -> int:
        """Remove expired cache entries

        Returns:
            Number of entries removed
        """
        expired_keys = self.get_expired(limit=10000)
        for key in expired_keys:
            self.cache.delete(key)

        return len(expired_keys)

    def set_ttl(
        self,
        prompt: str,
        model: str,
        ttl: int,
        system_prompt: str | None = None,
        **params: Any,
    ) -> bool:
        """Update TTL for existing cache entry

        Args:
            prompt: User prompt
            model: Model name
            ttl: New TTL in seconds
            system_prompt: System prompt (optional)
            **params: Additional parameters

        Returns:
            True if TTL was updated, False otherwise
        """
        key = self._generate_cache_key(prompt, model, system_prompt, **params)
        cached = self.cache.get(key)

        if cached:
            expires_at = datetime.now() + timedelta(seconds=ttl)
            cached["expires_at"] = expires_at.isoformat()
            self.cache.set(key, cached, expire=ttl)
            return True

        return False

    def get_all_keys(self) -> list[str]:
        """Get all cache keys

        Returns:
            List of cache keys
        """
        return list(self.cache.keys())

    def get_entries_by_model(self, model: str) -> list[dict[str, Any]]:
        """Get all cache entries for a specific model

        Args:
            model: Model name

        Returns:
            List of cache entries
        """
        entries = []

        for key in self.cache.keys():
            try:
                cached = self.cache.get(key)
                if cached and cached.get("model") == model:
                    entries.append(
                        {
                            "key": key,
                            "response": cached["response"],
                            "prompt": cached["prompt"],
                            "cached_at": cached["cached_at"],
                            "expires_at": cached["expires_at"],
                        }
                    )
            except Exception:
                continue

        return entries

    def export(self, filepath: str | Path) -> None:
        """Export cache to JSON file

        Args:
            filepath: Export file path
        """
        data = {}

        for key in self.cache.keys():
            try:
                cached = self.cache.get(key)
                if cached:
                    data[key] = cached
            except Exception:
                continue

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_cache(self, filepath: str | Path) -> int:
        """Import cache from JSON file

        Args:
            filepath: Import file path

        Returns:
            Number of entries imported
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for key, cached_data in data.items():
            try:
                if "expires_at" in cached_data:
                    expires_at = datetime.fromisoformat(cached_data["expires_at"])
                    if datetime.now() > expires_at:
                        continue  # Skip expired entries

                    ttl = (expires_at - datetime.now()).total_seconds()
                    ttl = int(max(0, ttl))
                else:
                    ttl = self.default_ttl

                self.cache.set(key, cached_data, expire=ttl)
                count += 1
            except Exception:
                continue

        return count
