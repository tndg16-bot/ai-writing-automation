"""Test BaseImageGenerator and ImageGenerationResult"""

import pytest

from ai_writing.services.image.base import (
    BaseImageGenerator,
    ImageGenerationResult,
    ImageGeneratorFactory,
)


def test_image_generation_result_creation():
    """ImageGenerationResultの作成テスト"""
    result = ImageGenerationResult(
        url="https://example.com/image.png",
        prompt="a beautiful sunset",
        provider="test",
        model="test-model",
    )

    assert result.url == "https://example.com/image.png"
    assert result.prompt == "a beautiful sunset"
    assert result.provider == "test"
    assert result.model == "test-model"
    assert result.local_path is None
    assert result.cached is False


def test_image_generation_result_with_local_path():
    """ローカルパス付きImageGenerationResultテスト"""
    from pathlib import Path

    result = ImageGenerationResult(
        url="https://example.com/image.png",
        prompt="test",
        provider="test",
        model="test-model",
        local_path=Path("/tmp/image.png"),
    )

    assert result.local_path == Path("/tmp/image.png")


def test_image_generation_result_cached():
    """キャッシュ済みImageGenerationResultテスト"""
    result = ImageGenerationResult(
        url="https://example.com/image.png",
        prompt="test",
        provider="test",
        model="test-model",
        cached=True,
    )

    assert result.cached is True


def test_base_image_generator_abstract():
    """BaseImageGeneratorの抽象クラステスト"""
    with pytest.raises(TypeError):
        BaseImageGenerator()


def test_image_generator_factory_invalid_provider():
    """無効なプロバイダーに対するテスト"""
    with pytest.raises(ValueError, match="Unknown image generation provider"):
        ImageGeneratorFactory.create("invalid_provider")
