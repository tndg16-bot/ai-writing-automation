"""YouTube Pipeline - YouTube台本生成パイプライン"""
from typing import Any

from ai_writing.core.config import Config
from ai_writing.pipeline.base import BasePipeline
from ai_writing.stages.search_intent import SearchIntentStage
from ai_writing.stages.structure import StructureStage
from ai_writing.stages.intro_ending import IntroEndingStage
from ai_writing.stages.youtube_body import YouTubeBodyStage
from ai_writing.stages.docs_output import DocsOutputStage


class YouTubePipeline(BasePipeline):
    """YouTube台本生成パイプライン"""

    content_type = "youtube"

    def _build_stages(self) -> list:
        """YouTube台本生成ステージを構築"""
        stages = [
            SearchIntentStage(self.config),
            StructureStage(self.config),
            IntroEndingStage(self.config),
            YouTubeBodyStage(self.config),
            DocsOutputStage(self.config),
        ]

        return stages
