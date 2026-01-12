"""Test Docs Output Stage - DocsOutputStage unit tests"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ai_writing.core.context import GenerationContext, Section
from ai_writing.stages.docs_output import DocsOutputStage


@pytest.fixture
def mock_config():
    """モック設定"""
    config = MagicMock()
    config.google_docs = {"template_folder": "templates"}
    return config


@pytest.fixture
def mock_context():
    """モックコンテキスト"""
    return GenerationContext(
        keyword="AI副業",
        content_type="blog",
        persona="30代会社員",
        needs_explicit=["AIで稼ぎたい"],
        needs_latent=["時間の自由を得たい"],
        structure=[{"level": "h2", "heading": "はじめに"}],
        titles=["AI副業で月10万円稼ぐ方法"],
        selected_title="AI副業で月10万円稼ぐ方法",
        lead="AI副業の始め方を解説します。",
        sections=[
            Section(
                heading="はじめに",
                content="AI副業は副業の新しい形です。",
                subsections=[],
            )
        ],
        summary="AI副業を始めましょう。",
        client_config={"enable_docs": True},
    )


@pytest.fixture
def mock_youtube_context():
    """YouTube台本用のモックコンテキスト"""
    return GenerationContext(
        keyword="犬の飼い方",
        content_type="youtube",
        persona="ペット初心者",
        needs_explicit=["飼い方を知りたい"],
        needs_latent=["癒されたい"],
        structure=[],
        titles=["【初心者向け】犬の飼い方完全ガイド"],
        selected_title="【初心者向け】犬の飼い方完全ガイド",
        lead="",
        sections=[],
        summary="",
        intro="こんにちは、今日は犬の飼い方を解説します。",
        ending="最後までご視聴ありがとうございました。",
        channel_name="ペットチャンネル",
        presenter_name="太郎",
        client_config={"enable_docs": True, "template": "youtube_template.json"},
    )


class TestDocsOutputStageInit:
    """初期化テスト"""

    def test_init_sets_config(self, mock_config):
        """設定が正しく設定されること"""
        stage = DocsOutputStage(mock_config)
        assert stage.config == mock_config

    def test_init_services_are_none(self, mock_config):
        """サービスが初期化時はNoneであること"""
        stage = DocsOutputStage(mock_config)
        assert stage._auth_manager is None
        assert stage._docs_service is None
        assert stage._template_engine is None
        assert stage._renderer is None


class TestDocsOutputStageSkip:
    """スキップ条件テスト"""

    @pytest.mark.asyncio
    async def test_skip_when_docs_disabled(self, mock_config, mock_context):
        """enable_docs=Falseの場合スキップすること"""
        mock_context.client_config["enable_docs"] = False

        stage = DocsOutputStage(mock_config)
        result = await stage.execute(mock_context)

        # コンテキストがそのまま返されること
        assert result == mock_context
        # docs_urlが設定されないこと
        assert "docs_url" not in result.client_config

    @pytest.mark.asyncio
    async def test_default_enabled_when_not_specified(self, mock_config):
        """enable_docsが指定されていない場合はデフォルトで有効"""
        context = GenerationContext(
            keyword="test",
            content_type="blog",
            client_config={},  # enable_docs not specified
        )

        # サービス初期化をモック
        with patch.object(DocsOutputStage, "_initialize_services") as mock_init:
            with patch.object(
                DocsOutputStage, "_context_to_dict", return_value={}
            ):
                stage = DocsOutputStage(mock_config)
                stage._renderer = MagicMock()
                stage._renderer.render_to_docs.return_value = "https://docs.google.com/test"

                result = await stage.execute(context)

                # サービス初期化が呼ばれること（スキップされていない）
                mock_init.assert_called_once()


class TestDocsOutputStageExecute:
    """実行テスト"""

    @pytest.mark.asyncio
    async def test_execute_success(self, mock_config, mock_context):
        """正常実行でdocs_urlが設定されること"""
        expected_url = "https://docs.google.com/document/d/12345"

        with patch.object(DocsOutputStage, "_initialize_services"):
            stage = DocsOutputStage(mock_config)
            stage._renderer = MagicMock()
            stage._renderer.render_to_docs.return_value = expected_url

            result = await stage.execute(mock_context)

            assert result.client_config["docs_url"] == expected_url
            stage._renderer.render_to_docs.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_calls_context_to_dict(self, mock_config, mock_context):
        """_context_to_dictが呼ばれること"""
        with patch.object(DocsOutputStage, "_initialize_services"):
            with patch.object(
                DocsOutputStage, "_context_to_dict", return_value={"test": "data"}
            ) as mock_to_dict:
                stage = DocsOutputStage(mock_config)
                stage._renderer = MagicMock()
                stage._renderer.render_to_docs.return_value = "https://example.com"

                await stage.execute(mock_context)

                mock_to_dict.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_execute_raises_error_on_failure(self, mock_config, mock_context):
        """エラー時にAIWritingErrorが発生すること"""
        from ai_writing.core.exceptions import AIWritingError

        with patch.object(DocsOutputStage, "_initialize_services"):
            stage = DocsOutputStage(mock_config)
            stage._renderer = MagicMock()
            stage._renderer.render_to_docs.side_effect = Exception("API Error")

            with pytest.raises(AIWritingError) as excinfo:
                await stage.execute(mock_context)

            assert "Google Docs出力に失敗しました" in str(excinfo.value)


class TestDocsOutputStageTemplateName:
    """テンプレート名取得テスト"""

    def test_get_template_name_from_client_config(self, mock_config, mock_context):
        """client_configからテンプレート名を取得"""
        mock_context.client_config["template"] = "custom_template.json"

        stage = DocsOutputStage(mock_config)
        template_name = stage._get_template_name(mock_context)

        assert template_name == "custom_template.json"

    def test_get_template_name_default_blog(self, mock_config, mock_context):
        """デフォルトでblog_default.jsonを返す"""
        mock_context.client_config.pop("template", None)
        mock_context.content_type = "blog"

        stage = DocsOutputStage(mock_config)
        template_name = stage._get_template_name(mock_context)

        assert template_name == "blog_default.json"

    def test_get_template_name_default_youtube(self, mock_config, mock_youtube_context):
        """YouTubeの場合youtube_default.jsonを返す"""
        mock_youtube_context.client_config.pop("template", None)

        stage = DocsOutputStage(mock_config)
        template_name = stage._get_template_name(mock_youtube_context)

        assert template_name == "youtube_default.json"


class TestDocsOutputStageContextToDict:
    """コンテキスト変換テスト"""

    def test_context_to_dict_basic_fields(self, mock_config, mock_context):
        """基本フィールドが正しく変換されること"""
        stage = DocsOutputStage(mock_config)
        result = stage._context_to_dict(mock_context)

        assert result["keyword"] == "AI副業"
        assert result["content_type"] == "blog"
        assert result["persona"] == "30代会社員"
        assert result["selected_title"] == "AI副業で月10万円稼ぐ方法"
        assert result["lead"] == "AI副業の始め方を解説します。"
        assert result["summary"] == "AI副業を始めましょう。"

    def test_context_to_dict_lists(self, mock_config, mock_context):
        """リストフィールドが正しく変換されること"""
        stage = DocsOutputStage(mock_config)
        result = stage._context_to_dict(mock_context)

        assert result["needs_explicit"] == ["AIで稼ぎたい"]
        assert result["needs_latent"] == ["時間の自由を得たい"]
        assert result["titles"] == ["AI副業で月10万円稼ぐ方法"]

    def test_context_to_dict_sections(self, mock_config, mock_context):
        """セクションが正しく変換されること"""
        stage = DocsOutputStage(mock_config)
        result = stage._context_to_dict(mock_context)

        assert len(result["sections"]) == 1
        section = result["sections"][0]
        assert section["heading"] == "はじめに"
        assert section["content"] == "AI副業は副業の新しい形です。"
        assert section["subsections"] == []
        assert section["image_path"] is None

    def test_context_to_dict_youtube_fields(self, mock_config, mock_youtube_context):
        """YouTube用フィールドが正しく変換されること"""
        stage = DocsOutputStage(mock_config)
        result = stage._context_to_dict(mock_youtube_context)

        assert result["intro"] == "こんにちは、今日は犬の飼い方を解説します。"
        assert result["ending"] == "最後までご視聴ありがとうございました。"
        assert result["channel_name"] == "ペットチャンネル"
        assert result["presenter_name"] == "太郎"


class TestDocsOutputStageInitializeServices:
    """サービス初期化テスト"""

    def test_initialize_services_creates_all_services(self, mock_config):
        """全サービスが初期化されること"""
        # Google services mock
        mock_auth_manager = MagicMock()
        mock_credentials = MagicMock()
        mock_auth_manager.load_credentials.return_value = mock_credentials

        mock_docs_service = MagicMock()
        mock_template_engine = MagicMock()
        mock_renderer = MagicMock()

        # インポート先のモジュールをパッチ
        with patch(
            "ai_writing.services.google.GoogleAuthManager",
            return_value=mock_auth_manager,
        ) as MockAuth:
            with patch(
                "ai_writing.services.google.GoogleDocsService",
                return_value=mock_docs_service,
            ) as MockDocs:
                with patch(
                    "ai_writing.templates.TemplateEngine",
                    return_value=mock_template_engine,
                ) as MockEngine:
                    with patch(
                        "ai_writing.templates.DocumentRenderer",
                        return_value=mock_renderer,
                    ) as MockRenderer:
                        stage = DocsOutputStage(mock_config)
                        stage._initialize_services()

                        # AuthManager
                        MockAuth.assert_called_once()
                        mock_auth_manager.load_credentials.assert_called_once()

                        # DocsService
                        MockDocs.assert_called_once_with(mock_credentials)

                        # TemplateEngine
                        MockEngine.assert_called_once()

                        # DocumentRenderer
                        MockRenderer.assert_called_once_with(
                            mock_template_engine, mock_docs_service
                        )

                        # 属性が設定されていること
                        assert stage._auth_manager == mock_auth_manager
                        assert stage._docs_service == mock_docs_service
                        assert stage._template_engine == mock_template_engine
                        assert stage._renderer == mock_renderer
