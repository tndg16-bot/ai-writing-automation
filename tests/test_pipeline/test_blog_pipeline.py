"""Test Blog Pipeline integration"""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ai_writing.core.context import GenerationContext
from ai_writing.core.config import Config


# LLMFactoryは各stageモジュール内で動的にインポートされるため、
# ai_writing.services.llm.baseをパッチする
LLM_FACTORY_PATCH = "ai_writing.services.llm.base.LLMFactory"


DOCS_STAGE_INIT_SERVICES_PATCH = "ai_writing.stages.docs_output.DocsOutputStage._initialize_services"


@pytest.fixture
def mock_config(prompts_path: Path):
    """モック設定"""
    config = MagicMock(spec=Config)
    config.llm = MagicMock()
    config.llm.provider = "openai"
    config.llm.model = "gpt-4"
    config.llm.temperature = 0.7
    config.llm.max_tokens = 4096
    config.prompts_folder = prompts_path
    config.google_docs = {"template_folder": "templates"}
    return config


@pytest.mark.asyncio
async def test_blog_pipeline_initialization(mock_config):
    """BlogPipelineの初期化テスト"""
    from ai_writing.pipeline.blog import BlogPipeline

    pipeline = BlogPipeline(mock_config)

    assert pipeline.content_type == "blog"
    assert len(pipeline.stages) == 7  # 6 original + DocsOutputStage
    assert pipeline.config == mock_config


@pytest.mark.asyncio
async def test_blog_pipeline_build_stages_order(mock_config):
    """_build_stagesが正しい順序でステージを返すテスト"""
    from ai_writing.pipeline.blog import BlogPipeline

    pipeline = BlogPipeline(mock_config)

    stage_names = [stage.__class__.__name__ for stage in pipeline.stages]

    expected_order = [
        "SearchIntentStage",
        "StructureStage",
        "TitleStage",
        "LeadStage",
        "BodyStage",
        "SummaryStage",
        "DocsOutputStage",
    ]

    assert stage_names == expected_order


@pytest.mark.asyncio
async def test_blog_pipeline_full_execution(mock_config):
    """パイプラインの全実行テスト（モックLLM）"""
    from ai_writing.pipeline.blog import BlogPipeline

    # 各ステージのexecuteをモック
    mock_context = GenerationContext(keyword="AI副業", content_type="blog")

    # LLMのモック
    with patch(LLM_FACTORY_PATCH) as mock_llm_factory:
        mock_llm = AsyncMock()
        mock_llm_factory.create.return_value = mock_llm

        # 検索意図調査のモック
        mock_llm.generate_json = AsyncMock(return_value={
            "persona": "30代男性、会社員",
            "needs_explicit": ["AIで稼ぎたい"],
            "needs_latent": ["時間の自由を得たい"],
        })

        # 構成作成のモック
        mock_llm.generate = AsyncMock(side_effect=[
            # StructureStage
            "h2：はじめに\nh2：方法",
            # TitleStage
            "【2025年】AI副業で月10万円稼ぐ方法！初心者でも始められる5つのおすすめ\n",
            # LeadStage
            "AI技術の進化により、誰もが副業で収入を得られる時代がやってきました。この記事では、AIを活用して月10万円を目指す具体的な方法を紹介します。",
            # BodyStage (1回目) - for "はじめに"
            "AI副業は、AIツールを活用して稼ぐ新しい形のビジネスモデルです。需要が高く、初期投資も少なくて済むのが特徴です。",
            # BodyStage (2回目) - for "方法"
            "ChatGPTは文章作成に最適なAIツールです。記事作成、メール作成、SNS投稿など、様々な用途で活用できます。",
            # SummaryStage
            "AI副業は初心者でも始めやすいビジネスです。ChatGPTを活用することで、効率的に収入を得ることができます。まずは小さな案件から始めて、徐々にスキルと収入を増やしていきましょう。",
        ])

        # DocsOutputStageをモック（Google APIを使わない）
        with patch(DOCS_STAGE_INIT_SERVICES_PATCH):
            from ai_writing.stages.docs_output import DocsOutputStage

            pipeline = BlogPipeline(mock_config)

            # DocsOutputStageの_rendererをモック
            docs_stage = pipeline.stages[-1]
            docs_stage._renderer = MagicMock()
            docs_stage._renderer.render_to_docs.return_value = "https://docs.google.com/test"

            result = await pipeline.run("AI副業")

            # コンテキストの検証
            assert result.keyword == "AI副業"
            assert result.persona == "30代男性、会社員"
            assert result.needs_explicit == ["AIで稼ぎたい"]
            assert result.needs_latent == ["時間の自由を得たい"]
            assert len(result.titles) > 0
            assert result.selected_title is not None
            assert result.lead is not None
            assert len(result.sections) > 0
            assert result.summary is not None


@pytest.mark.asyncio
async def test_blog_pipeline_context_accumulation(mock_config):
    """コンテキストが正しく蓄積されるテスト"""
    from ai_writing.pipeline.blog import BlogPipeline

    # 最小限のモック
    mock_context = GenerationContext(keyword="テスト", content_type="blog")

    with patch(LLM_FACTORY_PATCH) as mock_llm_factory:
        mock_llm = AsyncMock()
        mock_llm_factory.create.return_value = mock_llm

        mock_llm.generate_json = AsyncMock(return_value={
            "persona": "テストユーザー",
            "needs_explicit": ["テストニーズ"],
            "needs_latent": [],
        })

        mock_llm.generate = AsyncMock(side_effect=[
            "h2：テスト見出し",
            "テストタイトル",
            "テストリード",
            "テスト本文",
            "テストまとめ",
        ])

        # DocsOutputStageをモック（Google APIを使わない）
        with patch(DOCS_STAGE_INIT_SERVICES_PATCH):
            from ai_writing.stages.docs_output import DocsOutputStage

            pipeline = BlogPipeline(mock_config)

            # DocsOutputStageの_rendererをモック
            docs_stage = pipeline.stages[-1]
            docs_stage._renderer = MagicMock()
            docs_stage._renderer.render_to_docs.return_value = "https://docs.google.com/test"

            result = await pipeline.run("テスト")

            # 各ステージでコンテキストが正しく更新されているか確認
            assert result.persona is not None
            assert len(result.structure) > 0
            assert len(result.titles) > 0
            assert result.lead is not None
            assert len(result.sections) > 0
            assert result.summary is not None


@pytest.mark.asyncio
async def test_blog_pipeline_error_handling(mock_config):
    """パイプラインのエラーハンドリングテスト"""
    from ai_writing.pipeline.blog import BlogPipeline
    from ai_writing.core.exceptions import PipelineError

    with patch(LLM_FACTORY_PATCH) as mock_llm_factory:
        mock_llm = AsyncMock()
        mock_llm_factory.create.return_value = mock_llm

        # LLMエラーをシミュレート
        mock_llm.generate_json = AsyncMock(side_effect=Exception("API Error"))

        pipeline = BlogPipeline(mock_config)

        with pytest.raises(PipelineError):
            await pipeline.run("テスト")
