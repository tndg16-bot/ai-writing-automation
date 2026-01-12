"""Test Docs Integration - DocsOutputStage integration with BlogPipeline"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ai_writing.core.context import GenerationContext, Section
from ai_writing.core.config import Config
from ai_writing.pipeline.blog import BlogPipeline


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


@pytest.fixture
def mock_llm():
    """モックLLMインスタンス"""
    llm = AsyncMock()
    llm.generate_json = AsyncMock(
        return_value={
            "persona": "30代男性、会社員",
            "needs_explicit": ["AIで稼ぎたい"],
            "needs_latent": ["時間の自由を得たい"],
        }
    )
    llm.generate = AsyncMock(
        side_effect=[
            "h2：はじめに\nh2：方法",  # Structure
            "【2025年】AI副業で月10万円稼ぐ方法！",  # Title
            "AI副業の始め方を解説します。",  # Lead
            "AI副業は新しい働き方です。",  # Body 1
            "様々な方法があります。",  # Body 2
            "AI副業を始めましょう。",  # Summary
        ]
    )
    return llm


class TestBlogPipelineWithDocsOutput:
    """BlogPipelineとDocsOutputStageの統合テスト"""

    @pytest.mark.asyncio
    async def test_pipeline_includes_docs_output_stage(self, mock_config):
        """パイプラインにDocsOutputStageが含まれること"""
        pipeline = BlogPipeline(mock_config)

        stage_names = [stage.__class__.__name__ for stage in pipeline.stages]

        assert "DocsOutputStage" in stage_names
        # DocsOutputStageはSummaryStageの後にあるべき
        summary_index = stage_names.index("SummaryStage")
        docs_index = stage_names.index("DocsOutputStage")
        assert docs_index > summary_index

    @pytest.mark.asyncio
    async def test_pipeline_stage_count_with_docs(self, mock_config):
        """パイプラインのステージ数が正しいこと"""
        pipeline = BlogPipeline(mock_config)

        # 6 original stages + 1 DocsOutputStage = 7
        assert len(pipeline.stages) == 7

    @pytest.mark.asyncio
    async def test_pipeline_runs_with_docs_enabled(self, mock_config, mock_llm):
        """Docs出力が有効な場合パイプラインが正常に実行されること"""
        expected_url = "https://docs.google.com/document/d/test123"

        with patch(LLM_FACTORY_PATCH) as mock_llm_factory:
            mock_llm_factory.create.return_value = mock_llm

            with patch(DOCS_STAGE_INIT_SERVICES_PATCH):
                from ai_writing.stages.docs_output import DocsOutputStage

                # _rendererをモック
                with patch.object(
                    DocsOutputStage,
                    "_context_to_dict",
                    return_value={"test": "data"},
                ):
                    pipeline = BlogPipeline(mock_config)

                    # DocsOutputStageの_rendererをモック
                    docs_stage = pipeline.stages[-1]
                    docs_stage._renderer = MagicMock()
                    docs_stage._renderer.render_to_docs.return_value = expected_url

                    result = await pipeline.run("AI副業")

                    # docs_urlがコンテキストに設定されていること
                    assert result.client_config["docs_url"] == expected_url

    @pytest.mark.asyncio
    async def test_pipeline_runs_with_docs_disabled(self, mock_config, mock_llm):
        """Docs出力が無効な場合スキップされること"""
        with patch(LLM_FACTORY_PATCH) as mock_llm_factory:
            mock_llm_factory.create.return_value = mock_llm

            pipeline = BlogPipeline(mock_config)

            # client_configでenable_docs=Falseを設定するためのモック
            original_run = pipeline.run

            async def run_with_disabled_docs(keyword):
                from ai_writing.core.context import GenerationContext

                context = GenerationContext(
                    keyword=keyword,
                    content_type="blog",
                    client_config={"enable_docs": False},
                )

                for stage in pipeline.stages:
                    context = await stage.execute(context)

                return context

            result = await run_with_disabled_docs("AI副業")

            # docs_urlが設定されていないこと
            assert "docs_url" not in result.client_config

    @pytest.mark.asyncio
    async def test_pipeline_handles_docs_error_gracefully(self, mock_config, mock_llm):
        """Docs出力でエラーが発生した場合適切に処理されること"""
        from ai_writing.core.exceptions import AIWritingError

        with patch(LLM_FACTORY_PATCH) as mock_llm_factory:
            mock_llm_factory.create.return_value = mock_llm

            with patch(DOCS_STAGE_INIT_SERVICES_PATCH):
                from ai_writing.stages.docs_output import DocsOutputStage

                pipeline = BlogPipeline(mock_config)

                # DocsOutputStageの_rendererをモックしてエラーを発生させる
                docs_stage = pipeline.stages[-1]
                docs_stage._renderer = MagicMock()
                docs_stage._renderer.render_to_docs.side_effect = Exception(
                    "API Error"
                )

                # PipelineErrorがスローされることを確認
                # （BasePipelineがStageErrorをPipelineErrorにラップする）
                with pytest.raises(Exception):  # AIWritingError or PipelineError
                    await pipeline.run("AI副業")


class TestDocsOutputStageIntegration:
    """DocsOutputStageの統合テスト"""

    @pytest.mark.asyncio
    async def test_docs_stage_receives_full_context(self, mock_config, mock_llm):
        """DocsOutputStageが完全なコンテキストを受け取ること"""
        received_context = None

        with patch(LLM_FACTORY_PATCH) as mock_llm_factory:
            mock_llm_factory.create.return_value = mock_llm

            with patch(DOCS_STAGE_INIT_SERVICES_PATCH):
                from ai_writing.stages.docs_output import DocsOutputStage

                original_execute = DocsOutputStage.execute

                async def capture_execute(self, context):
                    nonlocal received_context
                    received_context = context
                    # スキップするために無効化
                    context.client_config["enable_docs"] = False
                    return context

                with patch.object(DocsOutputStage, "execute", capture_execute):
                    pipeline = BlogPipeline(mock_config)
                    await pipeline.run("AI副業")

        # コンテキストに必要な情報が含まれていること
        assert received_context is not None
        assert received_context.keyword == "AI副業"
        assert received_context.persona is not None
        assert len(received_context.structure) > 0
        assert len(received_context.titles) > 0
        assert received_context.selected_title is not None
        assert received_context.lead is not None
        assert len(received_context.sections) > 0
        assert received_context.summary is not None

    @pytest.mark.asyncio
    async def test_docs_url_persists_in_context(self, mock_config, mock_llm):
        """docs_urlがコンテキストに保持されること"""
        expected_url = "https://docs.google.com/document/d/abc123"

        with patch(LLM_FACTORY_PATCH) as mock_llm_factory:
            mock_llm_factory.create.return_value = mock_llm

            with patch(DOCS_STAGE_INIT_SERVICES_PATCH):
                from ai_writing.stages.docs_output import DocsOutputStage

                with patch.object(
                    DocsOutputStage,
                    "_context_to_dict",
                    return_value={},
                ):
                    pipeline = BlogPipeline(mock_config)

                    # _rendererをモック
                    docs_stage = pipeline.stages[-1]
                    docs_stage._renderer = MagicMock()
                    docs_stage._renderer.render_to_docs.return_value = expected_url

                    result = await pipeline.run("AI副業")

                    # docs_urlがコンテキストに設定されていること
                    assert "docs_url" in result.client_config
                    assert result.client_config["docs_url"] == expected_url


class TestDocsOutputWithMockedGoogleServices:
    """Googleサービスをモックした統合テスト"""

    @pytest.mark.asyncio
    async def test_full_docs_output_flow(self, mock_config):
        """完全なDocs出力フローのテスト"""
        # モックのセットアップ
        mock_auth_manager = MagicMock()
        mock_credentials = MagicMock()
        mock_auth_manager.load_credentials.return_value = mock_credentials

        mock_docs_service = MagicMock()
        mock_docs_service.create_document.return_value = "doc_id_123"
        mock_docs_service.get_document_url.return_value = (
            "https://docs.google.com/document/d/doc_id_123"
        )

        mock_template_engine = MagicMock()
        mock_template_engine.render_template.return_value = '{"title": "Test", "sections": []}'

        mock_renderer = MagicMock()
        mock_renderer.render_to_docs.return_value = (
            "https://docs.google.com/document/d/doc_id_123"
        )

        # コンテキストを作成
        context = GenerationContext(
            keyword="AI副業",
            content_type="blog",
            persona="30代会社員",
            needs_explicit=["稼ぎたい"],
            needs_latent=["自由が欲しい"],
            structure=[{"level": "h2", "heading": "テスト"}],
            titles=["テストタイトル"],
            selected_title="テストタイトル",
            lead="テストリード",
            sections=[Section(heading="テスト", content="テスト内容")],
            summary="テストまとめ",
            client_config={"enable_docs": True},
        )

        # パッチを適用してステージを実行（インポート先のモジュールをパッチ）
        with patch(
            "ai_writing.services.google.GoogleAuthManager",
            return_value=mock_auth_manager,
        ):
            with patch(
                "ai_writing.services.google.GoogleDocsService",
                return_value=mock_docs_service,
            ):
                with patch(
                    "ai_writing.templates.TemplateEngine",
                    return_value=mock_template_engine,
                ):
                    with patch(
                        "ai_writing.templates.DocumentRenderer",
                        return_value=mock_renderer,
                    ):
                        from ai_writing.stages.docs_output import DocsOutputStage

                        stage = DocsOutputStage(mock_config)
                        result = await stage.execute(context)

                        # 検証
                        assert "docs_url" in result.client_config
                        assert (
                            result.client_config["docs_url"]
                            == "https://docs.google.com/document/d/doc_id_123"
                        )
                        mock_renderer.render_to_docs.assert_called_once()
