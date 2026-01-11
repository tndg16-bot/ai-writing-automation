"""DALL-E 3 Image Generator"""

from typing import Any

import httpx
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ai_writing.services.image.base import BaseImageGenerator, ImageGenerationResult
from ai_writing.services.image.cache import ImageCache


class DALLEGenerator(BaseImageGenerator):
    """DALL-E 3 画像生成クラス"""

    SUPPORTED_SIZES = ["1024x1024", "1792x1024", "1024x1792"]
    SUPPORTED_STYLES = ["natural", "vivid"]

    def __init__(
        self,
        api_key: str,
        cache: ImageCache | None = None,
        model: str = "dall-e-3",
        max_retries: int = 3,
        **kwargs: Any,
    ):
        """DALL-E Generatorを初期化

        Args:
            api_key: OpenAI APIキー
            cache: キャッシュインスタンス（オプション）
            model: 使用するモデル（デフォルト: dall-e-3）
            max_retries: 最大リトライ回数
            **kwargs: 追加パラメータ
        """
        self.api_key = api_key
        self.cache = cache or ImageCache()
        self.model = model
        self.max_retries = max_retries
        self.client = AsyncOpenAI(api_key=api_key)

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
            style: スタイル（natural, vivid）
            size: 画像サイズ
            **kwargs: 追加パラメータ

        Returns:
            画像生成結果

        Raises:
            ValueError: 不正なスタイルまたはサイズ
            httpx.HTTPStatusError: APIエラー
        """
        if style not in self.SUPPORTED_STYLES:
            raise ValueError(f"Unsupported style: {style}. Supported: {self.SUPPORTED_STYLES}")

        if size not in self.SUPPORTED_SIZES:
            raise ValueError(f"Unsupported size: {size}. Supported: {self.SUPPORTED_SIZES}")

        try:
            response = await self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                style=style,
                n=1,
                response_format="url",
            )

            image_url = response.data[0].url

            result = ImageGenerationResult(
                url=image_url,
                prompt=prompt,
                provider="dalle",
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
        cached = self.cache.get(prompt, style, size, "dalle", **kwargs)
        if cached:
            return cached

        result = await self.generate(prompt, style, size, **kwargs)

        self.cache.set(result, style=style, size=size, **kwargs)

        return result
