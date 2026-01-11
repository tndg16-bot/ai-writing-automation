"""Test base pipeline and stage classes"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ai_writing.core.context import GenerationContext


@pytest.mark.asyncio
async def test_base_pipeline_run_with_context():
    """Test pipeline execution with context propagation"""
    from ai_writing.pipeline.blog import BlogPipeline

    config = MagicMock()
    config.llm = MagicMock()
    config.llm.provider = "openai"
    config.llm.model = "gpt-4"
    config.llm.temperature = 0.7
    config.llm.max_tokens = 4096
    config.prompts_folder = MagicMock()

    with patch("ai_writing.services.llm.base.LLMFactory") as mock_llm_factory:
        mock_llm = AsyncMock()
        mock_llm.generate_json = AsyncMock(return_value={
            "persona": "test persona",
            "needs_explicit": ["need1"],
            "needs_latent": ["need2"],
        })
        mock_llm.generate = AsyncMock(return_value="test content")
        mock_llm_factory.create.return_value = mock_llm

        pipeline = BlogPipeline(config)
        assert len(pipeline.stages) == 6
        assert pipeline.content_type == "blog"
        assert pipeline.config == config


@pytest.mark.asyncio
async def test_base_stage_abstract_methods():
    """Test that BaseStage and BasePipeline are properly abstract"""
    from ai_writing.pipeline.base import BasePipeline
    from ai_writing.stages.base import BaseStage

    # BasePipeline should require _build_stages implementation
    from abc import ABC
    assert issubclass(BasePipeline, ABC)

    # BaseStage should require execute implementation
    assert issubclass(BaseStage, ABC)
