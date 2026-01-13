"""Image generation base classes"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ImageGenerationResult:
    """画像生成結果

    Attributes:
        url: 画像URL
        local_path: ローカル保存パス（保存した場合）
        prompt: 使用したプロンプト
        provider: プロバイダー名
        model: モデル名
        cached: キャッシュから取得したかどうか
    """

    def __init__(
        self,
        url: str,
        prompt: str,
        provider: str,
        model: str,
        local_path: Path | None = None,
        cached: bool = False,
    ):
        self.url = url
        self.local_path = local_path
        self.prompt = prompt
        self.provider = provider
        self.model = model
        self.cached = cached


class BaseImageGenerator(ABC):
    """画像生成サービスの基底クラス"""

    @abstractmethod
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
            style: スタイル（natural, vivid, etc.）
            size: 画像サイズ
            **kwargs: 追加パラメータ

        Returns:
            画像生成結果
        """
        pass

    @abstractmethod
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
        pass


class ImageGeneratorFactory:
    """画像生成サービスのファクトリ"""

    @staticmethod
    def create(provider: str, **config: Any) -> BaseImageGenerator:
        """プロバイダー名から画像生成インスタンスを作成

        Args:
            provider: プロバイダー名（dalle, gemini, midjourney, canva）
            **config: 設定パラメータ

        Returns:
            画像生成インスタンス

        Raises:
            ValueError: 不明なプロバイダー
        """
        if provider == "dalle":
            from ai_writing.services.image.dalle import DALLEGenerator

            return DALLEGenerator(**config)
        elif provider == "gemini":
            from ai_writing.services.image.gemini import GeminiGenerator

            return GeminiGenerator(**config)
        elif provider == "midjourney":
            from ai_writing.services.image.midjourney import MidjourneyGenerator

            return MidjourneyGenerator(**config)
        elif provider == "canva":
            from ai_writing.services.image.canva import CanvaGenerator

            return CanvaGenerator(**config)
        else:
            raise ValueError(f"Unknown image generation provider: {provider}")
