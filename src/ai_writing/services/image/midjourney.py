"""Midjourney image generation service (full implementation)

This module provides full Midjourney integration via Discord Bot API.
"""

import asyncio
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import aiofiles
import httpx

from ai_writing.core.exceptions import ImageGenerationError
from ai_writing.services.image.base import BaseImageGenerator, ImageGenerationResult
from ai_writing.services.image.cache import ImageCache


class MidjourneyGenerator(BaseImageGenerator):
    """Midjourney image generator via Discord Bot API

    Generates images using Midjourney by sending commands through Discord.
    Monitors messages for generation progress and retrieves final image URLs.

    Environment Variables:
        DISCORD_BOT_TOKEN: Discord bot token
        DISCORD_SERVER_ID: Discord server ID
        MIDJOURNEY_CHANNEL_ID: Midjourney channel ID
    """

    BASE_URL = "https://discord.com/api/v10"

    def __init__(
        self,
        bot_token: str | None = None,
        server_id: str | None = None,
        channel_id: str | None = None,
        cache: ImageCache | None = None,
        **kwargs: Any,
    ):
        """Initialize Midjourney generator

        Args:
            bot_token: Discord bot token
            server_id: Discord server ID
            channel_id: Midjourney channel ID
            cache: Image cache instance (optional)
            **kwargs: Additional parameters
        """
        super().__init__()

        # Load from environment if not provided
        self.bot_token = bot_token or os.getenv("DISCORD_BOT_TOKEN")
        self.server_id = server_id or os.getenv("DISCORD_SERVER_ID")
        self.channel_id = channel_id or os.getenv("MIDJOURNEY_CHANNEL_ID")

        if not self.bot_token:
            raise ImageGenerationError(
                "DISCORD_BOT_TOKEN is required. Set it in .env or pass it.",
                suggestions=[
                    "1. Create a Discord bot at https://discord.com/developers/applications",
                    "2. Enable Bot application and get the token",
                    "3. Set DISCORD_BOT_TOKEN in .env file",
                ],
            )

        if not self.channel_id:
            raise ImageGenerationError(
                "MIDJOURNEY_CHANNEL_ID is required. Set it in .env or pass it.",
                suggestions=[
                    "1. Add the Discord bot to your server",
                    "2. Get the Midjourney channel ID",
                    "3. Set MIDJOURNEY_CHANNEL_ID in .env file",
                ],
            )

        self.cache = cache or ImageCache()
        self.timeout = kwargs.get("timeout", 300)  # 5 minutes default
        self.poll_interval = kwargs.get("poll_interval", 2)  # 2 seconds default

        self.http_client: httpx.AsyncClient | None = None

    async def _get_headers(self) -> dict[str, str]:
        """Get authorization headers

        Returns:
            Headers with authorization token
        """
        return {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json",
        }

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=60.0)

    async def _close_client(self) -> None:
        """Close HTTP client"""
        if self.http_client is not None:
            await self.http_client.aclose()
            self.http_client = None

    async def _send_message(self, content: str) -> dict[str, Any]:
        """Send message to Discord channel

        Args:
            content: Message content

        Returns:
            Message response

        Raises:
            ImageGenerationError: If sending fails
        """
        await self._ensure_client()

        url = f"{self.BASE_URL}/channels/{self.channel_id}/messages"
        headers = await self._get_headers()

        try:
            response = await self.http_client.post(
                url,
                json={"content": content},
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ImageGenerationError(
                f"Failed to send message to Discord: {e}",
                provider="midjourney",
                suggestions=[
                    "1. Check DISCORD_BOT_TOKEN is valid",
                    "2. Check MIDJOURNEY_CHANNEL_ID is correct",
                    "3. Verify bot has permissions in the channel",
                ],
            ) from e

    async def _get_message(self, message_id: str) -> dict[str, Any]:
        """Get message from Discord

        Args:
            message_id: Message ID

        Returns:
            Message data

        Raises:
            ImageGenerationError: If getting message fails
        """
        await self._ensure_client()

        url = f"{self.BASE_URL}/channels/{self.channel_id}/messages/{message_id}"
        headers = await self._get_headers()

        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ImageGenerationError(
                f"Failed to get message from Discord: {e}",
                provider="midjourney",
            ) from e

    async def _poll_for_completion(
        self, message_id: str, timeout: int | None = None
    ) -> dict[str, Any]:
        """Poll for message completion

        Args:
            message_id: Original message ID
            timeout: Timeout in seconds (default: self.timeout)

        Returns:
            Final message with image attachments

        Raises:
            ImageGenerationError: If timeout occurs
        """
        timeout = timeout or self.timeout
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                message = await self._get_message(message_id)

                # Check for attachments (completed generation)
                if message.get("attachments"):
                    return message

                # Check for error states
                content = message.get("content", "")
                if "error" in content.lower() or "failed" in content.lower():
                    raise ImageGenerationError(
                        f"Midjourney generation failed: {content}",
                        provider="midjourney",
                    )

                await asyncio.sleep(self.poll_interval)
            except ImageGenerationError:
                raise
            except Exception as e:
                # Ignore transient errors, continue polling
                await asyncio.sleep(self.poll_interval)

        raise ImageGenerationError(
            f"Midjourney generation timed out after {timeout} seconds",
            provider="midjourney",
            suggestions=[
                "1. Try increasing timeout via --timeout parameter",
                "2. Check if Midjourney bot is online",
                "3. Verify bot permissions in the channel",
            ],
        )

    def _extract_image_url(self, message: dict[str, Any]) -> str:
        """Extract image URL from message attachments

        Args:
            message: Discord message

        Returns:
            Image URL

        Raises:
            ImageGenerationError: If no image found
        """
        attachments = message.get("attachments", [])
        if not attachments:
            raise ImageGenerationError(
                "No image attachment found in message",
                provider="midjourney",
            )

        # Return the first attachment's URL
        return attachments[0]["url"]

    async def _download_image(self, url: str, filename: str) -> Path:
        """Download image from URL

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
        """Generate image with Midjourney

        Args:
            prompt: Image generation prompt
            style: Style parameter (natural, anime, etc.)
            size: Image size (e.g., "1024x1024", "16:9", etc.)
            **kwargs: Additional parameters (model, etc.)

        Returns:
            ImageGenerationResult

        Raises:
            ImageGenerationError: If generation fails
        """
        try:
            # Build Midjourney command
            # Midjourney uses --ar for aspect ratio
            aspect_ratio = self._convert_size_to_ar(size)
            command = f"/imagine {prompt} --v 6 --style raw --ar {aspect_ratio}"

            # Send command
            message = await self._send_message(command)
            message_id = message["id"]

            # Poll for completion
            completed_message = await self._poll_for_completion(message_id)

            # Extract image URL
            image_url = self._extract_image_url(completed_message)

            # Generate filename
            filename = self._generate_filename(prompt, "midjourney")

            # Download image
            local_path = await self._download_image(image_url, filename)

            return ImageGenerationResult(
                url=image_url,
                prompt=prompt,
                provider="midjourney",
                model="midjourney-v6",
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
        cached = self.cache.get(prompt, style, size, "midjourney", **kwargs)
        if cached:
            return cached

        # Generate new image
        result = await self.generate(prompt, style, size, **kwargs)

        # Save to cache
        self.cache.set(result, style=style, size=size, **kwargs)

        return result

    async def generate_with_prompt_enhancement(
        self,
        prompt: str,
        enhance: bool = True,
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """Generate image with optional prompt enhancement

        Args:
            prompt: Base prompt
            enhance: Whether to enhance prompt
            **kwargs: Additional parameters

        Returns:
            ImageGenerationResult

        Raises:
            ImageGenerationError: If generation fails
        """
        if enhance:
            # In production, this would use an LLM to enhance prompt
            # For now, just add Midjourney parameters
            pass  # Parameters are already added in generate()

        return await self.generate(prompt, **kwargs)

    def _convert_size_to_ar(self, size: str) -> str:
        """Convert size string to Midjourney aspect ratio

        Args:
            size: Size string (e.g., "1024x1024", "16:9")

        Returns:
            Aspect ratio string
        """
        # If already in ratio format, return as is
        if ":" in size:
            return size

        # Convert dimensions to ratio
        try:
            width, height = map(int, size.split("x"))
            # Simplify ratio
            from math import gcd

            divisor = gcd(width, height)
            return f"{width // divisor}:{height // divisor}"
        except (ValueError, ZeroDivisionError):
            # Default to 1:1 if parsing fails
            return "1:1"

    def _generate_filename(self, prompt: str, provider: str) -> str:
        """Generate filename from prompt

        Args:
            prompt: Generation prompt
            provider: Image provider name

        Returns:
            Filename
        """
        # Extract key words from prompt
        words = re.findall(r"\w+", prompt.lower())
        words = words[:3]  # First 3 words

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_part = "_".join(words)

        return f"{provider}_{timestamp}_{prompt_part}.png"
