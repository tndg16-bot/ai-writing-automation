"""Test Image Generation Stage"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from ai_writing.core.context import GenerationContext, Section
from ai_writing.core.config import Config
from ai_writing.stages.image_generation import ImageGenerationStage


@pytest.fixture
def mock_config():
    """モック設定"""
    return Config(
        llm={"provider": "openai", "model": "gpt-4", "temperature": 0.7, "max_tokens": 4096},
        prompts_folder="./prompts",
    )


@pytest.fixture
def image_config():
    """画像生成が有効なクライアント設定"""
    return {
        "image_generation": {
            "enabled": True,
            "style": "natural",
            "size": "1024x1024",
            "insertion_rules": {"after_h2": True, "after_lead": True},
            "generator": {"provider": "dalle", "model": "dall-e-3"},
        }
    }


@pytest.fixture
def mock_context(image_config):
    """モックコンテキスト"""
    return GenerationContext(
        keyword="AI副業",
        content_type="blog",
        persona="副業を検討している20代社会人",
        sections=[
            Section(heading="はじめに", content="AI副業の基本について説明します。"),
            Section(heading="AI副業の種類", content="代表的なAI副業を紹介します。"),
        ],
        client_config=image_config,
    )


@pytest.mark.asyncio
async def test_image_generation_stage_disabled(mock_context, mock_config):
    """画像生成が無効の場合のテスト"""
    mock_context.client_config = {"image_generation": {"enabled": False}}

    stage = ImageGenerationStage(mock_config)
    result = await stage.execute(mock_context)

    assert len(result.images) == 0
    assert all(s.image_path is None for s in result.sections)


@pytest.mark.asyncio
@patch("ai_writing.services.llm.base.LLMFactory.create")
async def test_image_generation_stage_calculates_positions(mock_llm_factory, mock_context, mock_config):
    """挿入位置計算のテスト"""
    stage = ImageGenerationStage(mock_config)

    positions = stage._calculate_insertion_positions(
        mock_context.sections,
        mock_context.client_config["image_generation"],
    )

    assert len(positions) > 0


@pytest.mark.asyncio
@patch("ai_writing.services.image.base.ImageGeneratorFactory.create")
@patch("ai_writing.services.llm.base.LLMFactory.create")
async def test_image_generation_stage_generates_images(
    mock_llm_factory,
    mock_image_factory,
    mock_context,
    mock_config,
):
    """画像生成のテスト"""
    # モック設定
    mock_llm_instance = AsyncMock()
    mock_llm_instance.generate.return_value = "自然な写真風で、AI副業の概念図"
    mock_llm_factory.return_value = mock_llm_instance

    mock_image_instance = AsyncMock()
    mock_result = MagicMock()
    mock_result.url = "https://example.com/image.png"
    mock_result.provider = "dalle"
    mock_result.model = "dall-e-3"
    mock_result.cached = False
    mock_image_instance.generate_with_cache.return_value = mock_result
    mock_image_factory.return_value = mock_image_instance

    # ステージ実行
    stage = ImageGenerationStage(mock_config)
    result = await stage.execute(mock_context)

    # 検証
    assert len(result.images) > 0
    assert mock_llm_instance.generate.call_count > 0
    assert mock_image_instance.generate_with_cache.call_count > 0
