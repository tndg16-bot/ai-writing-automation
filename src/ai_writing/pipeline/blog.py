"""Blog Pipeline - ブログ記事生成パイプライン"""
from typing import Any

from ai_writing.core.config import Config
from ai_writing.pipeline.base import BasePipeline
from ai_writing.stages.search_intent import SearchIntentStage
from ai_writing.stages.structure import StructureStage
from ai_writing.stages.title import TitleStage
from ai_writing.stages.lead import LeadStage
from ai_writing.stages.body import BodyStage
from ai_writing.stages.summary import SummaryStage
from ai_writing.stages.image_generation import ImageGenerationStage
from ai_writing.stages.docs_output import DocsOutputStage


class BlogPipeline(BasePipeline):
    """ブログ記事生成パイプライン"""

    content_type = "blog"

    def _build_stages(self) -> list:
        """ブログ生成ステージを構築"""
        stages = [
            SearchIntentStage(self.config),
            StructureStage(self.config),
            TitleStage(self.config),
            LeadStage(self.config),
            BodyStage(self.config),
            SummaryStage(self.config),
            # DocsOutputStage(self.config),  # Google認証が必要なため一時無効
        ]

        # 画像生成はデフォルトでは無効（クライアント設定で有効化）
        # 注: 実際の有効/無効はクライアント設定または環境変数で制御
        # ImageGenerationStage 内部でチェックされる

        return stages
