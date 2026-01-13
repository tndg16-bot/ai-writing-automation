"""Test YouTube pipeline"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_writing.core.context import GenerationContext


@pytest.mark.asyncio
async def test_youtube_pipeline_initialization():
    """Test YouTube pipeline initialization"""
    from ai_writing.pipeline.youtube import YouTubePipeline

    config = MagicMock()
    config.llm = MagicMock()

    pipeline = YouTubePipeline(config)
    assert pipeline.content_type == "youtube"
    assert len(pipeline.stages) == 5  # SearchIntent, Structure, IntroEnding, YouTubeBody, DocsOutput


@pytest.mark.asyncio
async def test_youtube_pipeline_build_stages_order():
    """Test that YouTube pipeline stages are in correct order"""
    from ai_writing.pipeline.youtube import YouTubePipeline
    from ai_writing.stages.search_intent import SearchIntentStage
    from ai_writing.stages.structure import StructureStage
    from ai_writing.stages.intro_ending import IntroEndingStage
    from ai_writing.stages.youtube_body import YouTubeBodyStage
    from ai_writing.stages.docs_output import DocsOutputStage

    config = MagicMock()
    config.llm = MagicMock()

    pipeline = YouTubePipeline(config)
    assert isinstance(pipeline.stages[0], SearchIntentStage)
    assert isinstance(pipeline.stages[1], StructureStage)
    assert isinstance(pipeline.stages[2], IntroEndingStage)
    assert isinstance(pipeline.stages[3], YouTubeBodyStage)
    assert isinstance(pipeline.stages[4], DocsOutputStage)


@pytest.mark.asyncio
async def test_youtube_pipeline_full_execution():
    """Test full YouTube pipeline execution with mocked stages"""
    from ai_writing.pipeline.youtube import YouTubePipeline
    from ai_writing.core.context import GenerationContext

    config = MagicMock()
    config.llm = MagicMock()

    pipeline = YouTubePipeline(config)

    # 各ステージをモック
    with patch.object(pipeline.stages[0], "execute", new_callable=AsyncMock) as mock_search:
        with patch.object(pipeline.stages[1], "execute", new_callable=AsyncMock) as mock_structure:
            with patch.object(pipeline.stages[2], "execute", new_callable=AsyncMock) as mock_intro:
                with patch.object(pipeline.stages[3], "execute", new_callable=AsyncMock) as mock_body:
                    with patch.object(pipeline.stages[4], "execute", new_callable=AsyncMock) as mock_docs:
                        # Setup context
                        base_context = GenerationContext(
                            keyword="test keyword",
                            content_type="youtube"
                        )

                        # Mock return values
                        mock_search.return_value = base_context
                        mock_structure.return_value = base_context
                        mock_intro.return_value = base_context
                        mock_body.return_value = base_context
                        mock_docs.return_value = base_context

                        # Run pipeline
                        result = await pipeline.run("test keyword")

                        assert result.keyword == "test keyword"
                        assert result.content_type == "youtube"


@pytest.mark.asyncio
async def test_intro_ending_stage_execution():
    """Test IntroEndingStage execution"""
    from ai_writing.stages.intro_ending import IntroEndingStage
    from ai_writing.core.context import GenerationContext

    config = MagicMock()
    config.llm = MagicMock()
    config.prompts_folder = MagicMock()

    with patch("ai_writing.stages.intro_ending.PromptLoader") as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = {
            "system": "システムプロンプト",
            "user": "ユーザープロンプト {{keyword}}"
        }
        mock_loader.return_value = mock_loader_instance

        with patch("ai_writing.services.llm.base.LLMFactory") as mock_llm_factory:
            mock_llm = AsyncMock()
            mock_llm.generate_json = AsyncMock(return_value={
                "intro": "冒頭の台本",
                "ending": "エンディングの台本"
            })
            mock_llm_config = {"model": "gpt-4", "api_key": "test"}
            mock_llm_factory.create = MagicMock(return_value=mock_llm)

            stage = IntroEndingStage(config)
            context = GenerationContext(
                keyword="test keyword",
                content_type="youtube",
                structure=[{"section": "セクション1", "description": "内容", "estimated_time": "2分"}]
            )
            context.client_config = {"channel_name": "テストチャンネル", "presenter_name": "テスト登場者"}

            result = await stage.execute(context)

            assert result.intro == "冒頭の台本"
            assert result.ending == "エンディングの台本"


@pytest.mark.asyncio
async def test_youtube_body_stage_execution():
    """Test YouTubeBodyStage execution"""
    from ai_writing.stages.youtube_body import YouTubeBodyStage
    from ai_writing.core.context import GenerationContext

    config = MagicMock()
    config.llm = MagicMock()
    config.prompts_folder = MagicMock()

    with patch("ai_writing.stages.youtube_body.PromptLoader") as mock_loader:
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
                        "heading": "セクション1",
                        "content": "台本本文"
                    }
                ]
            })
            mock_llm_config = {"model": "gpt-4", "api_key": "test"}
            mock_llm_factory.create = MagicMock(return_value=mock_llm)

            stage = YouTubeBodyStage(config)
            context = GenerationContext(
                keyword="test keyword",
                content_type="youtube",
                structure=[{"section": "セクション1", "description": "内容", "estimated_time": "2分"}]
            )

            result = await stage.execute(context)

            assert len(result.sections) == 1
            assert result.sections[0].heading == "セクション1"
            assert result.sections[0].content == "台本本文"
