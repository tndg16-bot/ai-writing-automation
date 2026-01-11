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


class BlogPipeline(BasePipeline):
    """ブログ記事生成パイプライン"""

    content_type = "blog"

    def _build_stages(self) -> list:
        """ブログ生成ステージを構築"""
        return [
            SearchIntentStage(self.config),
            StructureStage(self.config),
            TitleStage(self.config),
            LeadStage(self.config),
            BodyStage(self.config),
            SummaryStage(self.config),
        ]
