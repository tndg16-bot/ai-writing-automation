"""Fallback strategy for image generation providers

This module implements fallback strategies for multiple image providers.
"""

from typing import Any, List

from ai_writing.core.exceptions import ImageGenerationError
from ai_writing.services.image.base import BaseImageGenerator, ImageGenerationResult


class FallbackImageGenerator:
    """Image generator with automatic fallback

    Tries multiple providers in order until one succeeds.
    """

    def __init__(
        self,
        providers: list[BaseImageGenerator],
        fallback_chain: list[str] | None = None,
    ):
        """Initialize fallback generator

        Args:
            providers: Dictionary of provider name to generator instance
            fallback_chain: List of provider names to try in order
        """
        self.providers = providers

        # Default fallback chain: use enabled providers
        if fallback_chain is None:
            self.fallback_chain = [p for p in providers]
        else:
            self.fallback_chain = fallback_chain

    async def generate(
        self,
        prompt: str,
        style: str = "natural",
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """Generate image with fallback

        Args:
            prompt: Image generation prompt
            style: Style parameter
            size: Image size
            **kwargs: Additional parameters

        Returns:
            ImageGenerationResult

        Raises:
            ImageGenerationError: If all providers fail
        """
        last_error = None

        for provider_name in self.fallback_chain:
            provider = self.providers.get(provider_name)

            if provider is None:
                continue

            try:
                result = await provider.generate(prompt, style=style, size=size, **kwargs)
                return result
            except ImageGenerationError as e:
                last_error = e
                # Continue to next provider
                continue

        # All providers failed
        raise ImageGenerationError(
            f"All image providers failed. Last error: {last_error}",
            suggestions=[
                "1. Check your API keys are valid",
                "2. Verify providers are enabled in config",
                "3. Try reducing prompt complexity",
                "4. Check network connectivity",
            ],
        )

    async def generate_with_cache(
        self,
        prompt: str,
        style: str = "natural",
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """Generate image with fallback (with cache)

        Args:
            prompt: Image generation prompt
            style: Style parameter
            size: Image size
            **kwargs: Additional parameters

        Returns:
            ImageGenerationResult
        """
        # Check cache first (using first provider's cache)
        first_provider = self.providers.get(self.fallback_chain[0])

        if first_provider and hasattr(first_provider, "cache"):
            cached = first_provider.cache.get(prompt, style, size, "fallback", **kwargs)
            if cached:
                return cached

        # Generate with fallback
        result = await self.generate(prompt, style, size, **kwargs)

        # Save to cache
        if first_provider and hasattr(first_provider, "cache"):
            first_provider.cache.set(result, style=style, size=size, **kwargs)

        return result


def create_fallback_generator(
    providers: dict[str, BaseImageGenerator],
    config: dict[str, Any],
) -> FallbackImageGenerator:
    """Create fallback generator from configuration

    Args:
        providers: Dictionary of provider instances
        config: Configuration dictionary

    Returns:
        FallbackImageGenerator instance
    """
    fallback_chain = config.get("fallback_chain", list(providers.keys()))

    return FallbackImageGenerator(
        providers,
        fallback_chain=fallback_chain,
    )


class WeightedFallbackGenerator:
    """Fallback generator with weighted provider selection

    Distributes load across providers based on weights.
    """

    def __init__(
        self,
        providers: dict[str, BaseImageGenerator],
        weights: dict[str, int] | None = None,
    ):
        """Initialize weighted fallback generator

        Args:
            providers: Dictionary of provider instances
            weights: Dictionary of provider weights (higher = more likely)
        """
        self.providers = providers

        # Default weights: all equal
        if weights is None:
            self.weights = {p: 1 for p in providers}
        else:
            self.weights = weights

    def select_provider(self) -> str:
        """Select a provider based on weights

        Returns:
            Selected provider name
        """
        import random

        providers = list(self.providers.keys())
        weights = [self.weights.get(p, 1) for p in providers]

        # Weighted random selection
        return random.choices(providers, weights=weights, k=1)[0]

    async def generate(
        self,
        prompt: str,
        style: str = "natural",
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """Generate image with weighted selection and fallback

        Args:
            prompt: Image generation prompt
            style: Style parameter
            size: Image size
            **kwargs: Additional parameters

        Returns:
            ImageGenerationResult

        Raises:
            ImageGenerationError: If all providers fail
        """
        # Try selected provider first, then fallback
        selected = self.select_provider()

        # Build fallback chain: selected -> others
        others = [p for p in self.providers if p != selected]
        fallback_chain = [selected] + others

        fallback_gen = FallbackImageGenerator(self.providers, fallback_chain)
        return await fallback_gen.generate(prompt, style, size, **kwargs)
