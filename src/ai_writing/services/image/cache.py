"""Image caching with diskcache"""

import hashlib
from pathlib import Path
from typing import Any

import aiofiles
import httpx
from diskcache import Cache

from ai_writing.services.image.base import ImageGenerationResult


class ImageCache:
    """画像生成結果の永続キャッシュ

    プロンプトとパラメータをキーにして画像生成結果をキャッシュする。
    ディスクキャッシュを使用し、プロセス再起動後もキャッシュが維持される。
    """

    def __init__(self, cache_dir: str | Path = "./cache/images"):
        """キャッシュを初期化

        Args:
            cache_dir: キャッシュディレクトリのパス
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache = Cache(str(self.cache_dir))

    def _generate_cache_key(
        self,
        prompt: str,
        style: str,
        size: str,
        provider: str,
        **kwargs: Any,
    ) -> str:
        """キャッシュキーを生成

        Args:
            prompt: 生成プロンプト
            style: スタイル
            size: サイズ
            provider: プロバイダー
            **kwargs: 追加パラメータ

        Returns:
            MD5ハッシュのキャッシュキー
        """
        key_data = f"{prompt}|{style}|{size}|{provider}"
        for k, v in sorted(kwargs.items()):
            key_data += f"|{k}:{v}"

        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, prompt: str, style: str, size: str, provider: str, **kwargs: Any) -> ImageGenerationResult | None:
        """キャッシュから画像生成結果を取得

        Args:
            prompt: 生成プロンプト
            style: スタイル
            size: サイズ
            provider: プロバイダー
            **kwargs: 追加パラメータ

        Returns:
            キャッシュされた結果（存在しない場合はNone）
        """
        key = self._generate_cache_key(prompt, style, size, provider, **kwargs)
        cached = self.cache.get(key)

        if cached:
            result_dict = cached

            local_path = Path(result_dict["local_path"]) if result_dict.get("local_path") else None

            return ImageGenerationResult(
                url=result_dict["url"],
                prompt=result_dict["prompt"],
                provider=result_dict["provider"],
                model=result_dict["model"],
                local_path=local_path,
                cached=True,
            )

        return None

    def set(self, result: ImageGenerationResult, style: str, size: str, **kwargs: Any) -> None:
        """画像生成結果をキャッシュに保存

        Args:
            result: 画像生成結果
            style: スタイル
            size: サイズ
            **kwargs: 追加パラメータ
        """
        key = self._generate_cache_key(result.prompt, style, size, result.provider, **kwargs)

        result_dict = {
            "url": result.url,
            "prompt": result.prompt,
            "provider": result.provider,
            "model": result.model,
            "local_path": str(result.local_path) if result.local_path else None,
        }

        self.cache.set(key, result_dict)

    async def download_and_save(self, url: str, filename: str) -> Path:
        """画像をダウンロードしてローカルに保存

        Args:
            url: 画像URL
            filename: 保存するファイル名

        Returns:
            保存先のパス
        """
        file_path = self.cache_dir / filename

        if file_path.exists():
            return file_path

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(response.content)

        return file_path

    def clear(self) -> None:
        """キャッシュをクリア"""
        self.cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """キャッシュ統計を取得

        Returns:
            キャッシュ統計情報
        """
        return {
            "size": self.cache.size,
            "volume": self.cache.volume,
            "directory": str(self.cache_dir),
        }
