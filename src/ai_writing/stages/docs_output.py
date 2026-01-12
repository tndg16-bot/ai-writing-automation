"""Docs Output Stage - 生成されたコンテンツをGoogle Docsに出力"""
from pathlib import Path
from typing import Any

from ai_writing.core.context import GenerationContext
from ai_writing.core.exceptions import AIWritingError
from ai_writing.stages.base import BaseStage


class DocsOutputStage(BaseStage):
    """Google Docs出力ステージ"""

    def __init__(self, config: Any):
        super().__init__(config)
        self._auth_manager = None
        self._docs_service = None
        self._template_engine = None
        self._renderer = None

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """コンテキストをGoogle Docsに出力

        1. Check if docs output is enabled
        2. Initialize services (lazy)
        3. Determine template name from client config
        4. Convert context to dict
        5. Render to Google Docs
        6. Save URL to context.client_config["docs_url"]
        """
        # Skip if disabled
        if not context.client_config.get("enable_docs", True):
            print("  Google Docs出力: スキップ（設定で無効化）")
            return context

        try:
            self._initialize_services()
            template_name = self._get_template_name(context)
            print(f"  Google Docs出力開始: テンプレート={template_name}")

            context_dict = self._context_to_dict(context)
            doc_url = self._renderer.render_to_docs(context_dict, template_name)

            print(f"  Google Docs作成完了: {doc_url}")
            context.client_config["docs_url"] = doc_url

            return context
        except Exception as e:
            raise AIWritingError(f"Google Docs出力に失敗しました: {e}") from e

    def _initialize_services(self):
        """Initialize Google services lazily"""
        from ai_writing.services.google import GoogleAuthManager, GoogleDocsService
        from ai_writing.templates import DocumentRenderer, TemplateEngine

        token_dir = Path.home() / ".cache" / "ai-writing" / "google"
        token_file = token_dir / "token.json"

        self._auth_manager = GoogleAuthManager(token_file=token_file)
        credentials = self._auth_manager.load_credentials()

        self._docs_service = GoogleDocsService(credentials)

        templates_dir = Path(self.config.google_docs.get("template_folder", "templates"))
        self._template_engine = TemplateEngine(templates_dir)

        self._renderer = DocumentRenderer(self._template_engine, self._docs_service)

    def _get_template_name(self, context: GenerationContext) -> str:
        """Get template name from client config"""
        template_name = context.client_config.get("template", None)
        if template_name:
            return template_name
        return f"{context.content_type}_default.json"

    def _context_to_dict(self, context: GenerationContext) -> dict:
        """Convert GenerationContext to dict for template rendering"""
        return {
            "keyword": context.keyword,
            "content_type": context.content_type,
            "persona": context.persona,
            "needs_explicit": context.needs_explicit,
            "needs_latent": context.needs_latent,
            "structure": context.structure,
            "titles": context.titles,
            "selected_title": context.selected_title,
            "lead": context.lead,
            "sections": [
                {
                    "heading": s.heading,
                    "content": s.content,
                    "subsections": [
                        {"heading": sub.heading, "content": sub.content}
                        for sub in s.subsections
                    ],
                    "image_path": s.image_path,
                }
                for s in context.sections
            ],
            "summary": context.summary,
            "images": context.images,
            # YouTube/yukkuri fields
            "intro": context.intro,
            "ending": context.ending,
            "channel_name": context.channel_name,
            "presenter_name": context.presenter_name,
        }
