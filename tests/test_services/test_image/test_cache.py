"""Test ImageCache class"""

import pytest

from ai_writing.services.image.cache import ImageCache
from ai_writing.services.image.base import ImageGenerationResult


@pytest.fixture
def cache(tmp_path):
    """テスト用キャッシュインスタンス"""
    cache_dir = tmp_path / "images"
    return ImageCache(cache_dir=cache_dir)


@pytest.fixture
def sample_result():
    """サンプル画像生成結果"""
    return ImageGenerationResult(
        url="https://example.com/image.png",
        prompt="a beautiful sunset",
        provider="test",
        model="test-model",
    )


def test_cache_initialization(cache):
    """キャッシュの初期化テスト"""
    assert cache.cache_dir.exists()
    assert cache.cache is not None


def test_cache_set_and_get(cache, sample_result):
    """キャッシュの保存と取得テスト"""
    style = "natural"
    size = "1024x1024"

    cache.set(sample_result, style=style, size=size)

    retrieved = cache.get(sample_result.prompt, style, size, sample_result.provider)

    assert retrieved is not None
    assert retrieved.url == sample_result.url
    assert retrieved.prompt == sample_result.prompt
    assert retrieved.cached is True


def test_cache_miss(cache):
    """キャッシュミステスト"""
    result = cache.get("nonexistent prompt", "natural", "1024x1024", "test")
    assert result is None


def test_cache_stats(cache):
    """キャッシュ統計テスト"""
    stats = cache.get_stats()

    assert "size" in stats
    assert "volume" in stats
    assert "directory" in stats
    assert stats["size"] == 0


def test_cache_clear(cache, sample_result):
    """キャッシュクリアテスト"""
    style = "natural"
    size = "1024x1024"

    cache.set(sample_result, style=style, size=size)
    retrieved = cache.get(sample_result.prompt, style, size, sample_result.provider)
    assert retrieved is not None

    cache.clear()
    retrieved = cache.get(sample_result.prompt, style, size, sample_result.provider)
    assert retrieved is None
