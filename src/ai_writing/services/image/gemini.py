"""Gemini Imagen Image Generator"""

from typing import Any

import httpx
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ai_writing.services.image.base import BaseImageGenerator, ImageGenerationResult
from ai_writing.services.image.cache import ImageCache


class GeminiGenerator(BaseImageGenerator):
    """Gemini Imagen 画像生成クラス"""

    SUPPORTED_SIZES = ["1024x1024", "512x512"]
    SUPPORTED_STYLES = ["natural"]

    def __init__(
        self,
        api_key: str,
        cache: ImageCache | None = None,
        model: str = "imagen-3.0-generate-001",
        max_retries: int = 3,
        **kwargs: Any,
    ):
        """Gemini Generatorを初期化

        Args:
            api_key: Google APIキー
            cache: キャッシュインスタンス（オプション）
            model: 使用するモデル（デフォルト: imagen-3.0-generate-001）
            max_retries: 最大リトライ回数
            **kwargs: 追加パラメータ
        """
        self.api_key = api_key
        self.cache = cache or ImageCache()
        self.model = model
        self.max_retries = max_retries
        genai.configure(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError)),
        reraise=True,
    )
    async def generate(
        self,
        prompt: str,
        style: str = "natural",
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """画像を生成する

        Args:
            prompt: 生成プロンプト
            style: スタイル（naturalのみ）
            size: 画像サイズ
            **kwargs: 追加パラメータ

        Returns:
            画像生成結果

        Raises:
            ValueError: 不正なスタイルまたはサイズ
            genai.APIError: Gemini APIエラー
        """
        if style not in self.SUPPORTED_STYLES:
            raise ValueError(f"Unsupported style: {style}. Supported: {self.SUPPORTED_STYLES}")

        if size not in self.SUPPORTED_SIZES:
            raise ValueError(f"Unsupported size: {size}. Supported: {self.SUPPORTED_SIZES}")

        try:
            model = genai.GenerativeModel(self.model)

            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
            )

            image_url = response.generated_images[0].image_bytes

            result = ImageGenerationResult(
                url=image_url,
                prompt=prompt,
                provider="gemini",
                model=self.model,
            )

            return result

        except Exception as e:
            raise

    async def generate_with_cache(
        self,
        prompt: str,
        style: str = "natural",
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """キャッシュを考慮して画像を生成する

        Args:
            prompt: 生成プロンプト
            style: スタイル
            size: 画像サイズ
            **kwargs: 追加パラメータ

        Returns:
            画像生成結果（キャッシュから取得した場合cached=True）
        """
        cached = self.cache.get(prompt, style, size, "gemini", **kwargs)
        if cached:
            return cached

        result = await self.generate(prompt, style, size, **kwargs)

        self.cache.set(result, style=style, size=size, **kwargs)

        return result
