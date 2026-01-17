"""Canva image generation service (full implementation)

This module provides full Canva API integration for image generation.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
import httpx

from ai_writing.core.exceptions import ImageGenerationError
from ai_writing.services.image.base import BaseImageGenerator, ImageGenerationResult
from ai_writing.services.image.cache import ImageCache


class CanvaGenerator(BaseImageGenerator):
    """Canva image generator via Canva Designs API

    Generates images using Canva's Designs API with templates.

    Environment Variables:
        CANVA_API_KEY: Canva API key
        CANVA_TEMPLATE_ID: Default template ID
    """

    BASE_URL = "https://api.canva.com/rest/v1"

    def __init__(
        self,
        api_key: str | None = None,
        template_id: str | None = None,
        cache: ImageCache | None = None,
        **kwargs: Any,
    ):
        """Initialize Canva generator

        Args:
            api_key: Canva API key
            template_id: Default template ID
            cache: Image cache instance (optional)
            **kwargs: Additional parameters
        """
        super().__init__()

        # Load from environment if not provided
        self.api_key = api_key or os.getenv("CANVA_API_KEY")
        self.template_id = template_id or os.getenv("CANVA_TEMPLATE_ID")
        self.export_format = kwargs.get("export_format", "png")

        if not self.api_key:
            raise ImageGenerationError(
                "CANVA_API_KEY is required. Set it in .env or pass it.",
                suggestions=[
                    "1. Create a Canva account at https://www.canva.com",
                    "2. Go to https://www.canva.com/developers/api",
                    "3. Create an API key",
                    "4. Set CANVA_API_KEY in .env file",
                ],
            )

        self.cache = cache or ImageCache()
        self.timeout = kwargs.get("timeout", 60)  # 60 seconds default
        self.http_client: httpx.AsyncClient | None = None

    async def _get_headers(self) -> dict[str, str]:
        """Get authorization headers

        Returns:
            Headers with authorization token
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=self.timeout)

    async def _close_client(self) -> None:
        """Close HTTP client"""
        if self.http_client is not None:
            await self.http_client.aclose()
            self.http_client = None

    async def _create_design(
        self,
        prompt: str,
        template_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a new design from template

        Args:
            prompt: Design prompt
            template_id: Template ID (uses default if None)

        Returns:
            Design data

        Raises:
            ImageGenerationError: If creation fails
        """
        await self._ensure_client()

        if template_id is None:
            template_id = self.template_id

        if not template_id:
            raise ImageGenerationError(
                "Template ID is required. Set CANVA_TEMPLATE_ID or pass it.",
                provider="canva",
            )

        url = f"{self.BASE_URL}/designs"
        headers = await self._get_headers()

        try:
            # Canva Designs API request
            request_body = {
                "title": f"AI Generated: {prompt[:50]}",
                "type": "design",
                "template_id": template_id,
            }

            response = await self.http_client.post(url, json=request_body, headers=headers)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPError as e:
            raise ImageGenerationError(
                f"Failed to create Canva design: {e}",
                provider="canva",
                suggestions=[
                    "1. Check CANVA_API_KEY is valid",
                    "2. Verify template ID exists",
                    "3. Check API rate limits",
                ],
            ) from e

    async def _add_text_element(
        self,
        design_id: str,
        text: str,
    ) -> None:
        """Add text element to design

        Args:
            design_id: Design ID
            text: Text to add

        Raises:
            ImageGenerationError: If adding text fails
        """
        await self._ensure_client()

        url = f"{self.BASE_URL}/designs/{design_id}/text"
        headers = await self._get_headers()

        try:
            request_body = {
                "text": text,
                "position": {
                    "x": 100,
                    "y": 100,
                },
            }

            response = await self.http_client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as e:
            # Non-fatal: continue without text
            pass

    async def _export_design(
        self,
        design_id: str,
        format: str | None = None,
    ) -> str:
        """Export design as image

        Args:
            design_id: Design ID
            format: Export format (png, pdf, etc.)

        Returns:
            Export URL

        Raises:
            ImageGenerationError: If export fails
        """
        await self._ensure_client()

        format = format or self.export_format
        url = f"{self.BASE_URL}/designs/{design_id}/export"
        headers = await self._get_headers()

        try:
            request_body = {
                "format": format,
                "target": {
                    "type": "url",
                },
            }

            response = await self.http_client.post(url, json=request_body, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data.get("url")
        except httpx.HTTPError as e:
            raise ImageGenerationError(
                f"Failed to export Canva design: {e}",
                provider="canva",
            ) from e

    async def _download_image(self, url: str, filename: str) -> Path:
        """Download exported image

        Args:
            url: Image URL
            filename: Filename to save

        Returns:
            Local file path
        """
        await self._ensure_client()

        file_path = self.cache.cache_dir / filename

        if file_path.exists():
            return file_path

        async with self.http_client.stream("GET", url) as response:
            response.raise_for_status()
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in response.aiter_bytes(8192):
                    await f.write(chunk)

        return file_path

    async def generate(
        self,
        prompt: str,
        style: str = "natural",
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """Generate image with Canva

        Args:
            prompt: Image generation prompt
            style: Style parameter (not used in Canva)
            size: Image size (not used in Canva)
            **kwargs: Additional parameters (template_id, etc.)

        Returns:
            ImageGenerationResult

        Raises:
            ImageGenerationError: If generation fails
        """
        try:
            # Create design from template
            design_data = await self._create_design(prompt)
            design_id = design_data["id"]

            # Add text to design (optional)
            await self._add_text_element(design_id, prompt[:100])

            # Export design
            export_url = await self._export_design(design_id)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_part = "".join(c for c in prompt[:20] if c.isalnum())
            filename = f"canva_{timestamp}_{prompt_part}.{self.export_format}"

            # Download image
            local_path = await self._download_image(export_url, filename)

            return ImageGenerationResult(
                url=export_url,
                prompt=prompt,
                provider="canva",
                model="canva-designs-api",
                local_path=local_path,
                cached=False,
            )
        finally:
            await self._close_client()

    async def generate_with_cache(
        self,
        prompt: str,
        style: str = "natural",
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """Generate image with cache

        Args:
            prompt: Image generation prompt
            style: Style parameter
            size: Image size
            **kwargs: Additional parameters

        Returns:
            ImageGenerationResult
        """
        # Check cache first
        cached = self.cache.get(prompt, style, size, "canva", **kwargs)
        if cached:
            return cached

        # Generate new image
        result = await self.generate(prompt, style, size, **kwargs)

        # Save to cache
        self.cache.set(result, style=style, size=size, **kwargs)

        return result

    async def generate_from_template(
        self,
        prompt: str,
        template_id: str | None = None,
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """Generate image from Canva template

        Args:
            prompt: Image generation prompt
            template_id: Canva template ID (uses default if not provided)
            **kwargs: Additional parameters

        Returns:
            ImageGenerationResult

        Raises:
            ImageGenerationError: If generation fails
        """
        return await self.generate(
            prompt,
            template_id=template_id,
            **kwargs,
        )

    async def list_templates(self) -> list[dict[str, Any]]:
        """List available templates

        Returns:
            List of template data

        Raises:
            ImageGenerationError: If listing fails
        """
        await self._ensure_client()

        url = f"{self.BASE_URL}/templates"
        headers = await self._get_headers()

        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data.get("templates", [])
        except httpx.HTTPError as e:
            raise ImageGenerationError(
                f"Failed to list Canva templates: {e}",
                provider="canva",
            ) from e
        finally:
            await self._close_client()
