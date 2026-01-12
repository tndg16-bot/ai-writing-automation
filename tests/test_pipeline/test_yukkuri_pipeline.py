"""Test Yukkuri pipeline"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_writing.core.context import GenerationContext


@pytest.mark.asyncio
async def test_yukkuri_pipeline_initialization():
    """Test Yukkuri pipeline initialization"""
    from ai_writing.pipeline.yukkuri import YukkuriPipeline

    config = MagicMock()
    config.llm = MagicMock()

    pipeline = YukkuriPipeline(config)
    assert pipeline.content_type == "yukkuri"
    assert len(pipeline.stages) == 4  # SearchIntent, Structure, YukkuriScript, DocsOutput


@pytest.mark.asyncio
async def test_yukkuri_pipeline_build_stages_order():
    """Test that Yukkuri pipeline stages are in correct order"""
    from ai_writing.pipeline.yukkuri import YukkuriPipeline
    from ai_writing.stages.search_intent import SearchIntentStage
    from ai_writing.stages.structure import StructureStage
    from ai_writing.stages.yukkuri_script import YukkuriScriptStage
    from ai_writing.stages.docs_output import DocsOutputStage

    config = MagicMock()
    config.llm = MagicMock()

    pipeline = YukkuriPipeline(config)
    assert isinstance(pipeline.stages[0], SearchIntentStage)
    assert isinstance(pipeline.stages[1], StructureStage)
    assert isinstance(pipeline.stages[2], YukkuriScriptStage)
    assert isinstance(pipeline.stages[3], DocsOutputStage)


@pytest.mark.asyncio
async def test_yukkuri_pipeline_full_execution():
    """Test full Yukkuri pipeline execution with mocked stages"""
    from ai_writing.pipeline.yukkuri import YukkuriPipeline
    from ai_writing.core.context import GenerationContext

    config = MagicMock()
    config.llm = MagicMock()

    pipeline = YukkuriPipeline(config)

    # 各ステージをモック
    with patch.object(pipeline.stages[0], "execute", new_callable=AsyncMock) as mock_search:
        with patch.object(pipeline.stages[1], "execute", new_callable=AsyncMock) as mock_structure:
            with patch.object(pipeline.stages[2], "execute", new_callable=AsyncMock) as mock_script:
                with patch.object(pipeline.stages[3], "execute", new_callable=AsyncMock) as mock_docs:
                    # Setup context
                    base_context = GenerationContext(
                        keyword="test keyword",
                        content_type="yukkuri"
                    )

                    # Mock return values
                    mock_search.return_value = base_context
                    mock_structure.return_value = base_context
                    mock_script.return_value = base_context
                    mock_docs.return_value = base_context

                    # Run pipeline
                    result = await pipeline.run("test keyword")

                    assert result.keyword == "test keyword"
                    assert result.content_type == "yukkuri"


@pytest.mark.asyncio
async def test_yukkuri_script_stage_execution():
    """Test YukkuriScriptStage execution"""
    from ai_writing.stages.yukkuri_script import YukkuriScriptStage
    from ai_writing.core.context import GenerationContext

    config = MagicMock()
    config.llm = MagicMock()
    config.prompts_folder = MagicMock()

    with patch("ai_writing.stages.yukkuri_script.PromptLoader") as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = {
            "system": "システムプロンプト",
            "user": "ユーザープロンプト {{keyword}}"
        }
        mock_loader.return_value = mock_loader_instance

        with patch("ai_writing.services.llm.base.LLMFactory") as mock_llm_factory:
            mock_llm = AsyncMock()
            mock_llm.generate_json = AsyncMock(return_value={
                "sections": [
                    {
                        "heading": "トピック1",
                        "reimu": "霊夢の台本",
                        "marisa": "魔理沙の台本"
                    }
                ]
            })
            mock_llm_config = {"model": "gpt-4", "api_key": "test"}
            mock_llm_factory.create = MagicMock(return_value=mock_llm)

            stage = YukkuriScriptStage(config)
            context = GenerationContext(
                keyword="test keyword",
                content_type="yukkuri",
                structure=[
                    {
                        "topic": "トピック1",
                        "reimu_role": "霊夢の役割",
                        "marisa_role": "魔理沙の役割"
                    }
                ]
            )

            result = await stage.execute(context)

            assert len(result.sections) == 1
            assert result.sections[0].heading == "トピック1"
            assert "霊夢" in result.sections[0].content
            assert "魔理沙" in result.sections[0].content
