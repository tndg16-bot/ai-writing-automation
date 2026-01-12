"""Yukkuri Pipeline - ゆっくり台本生成パイプライン"""
from typing import Any

from ai_writing.core.config import Config
from ai_writing.pipeline.base import BasePipeline
from ai_writing.stages.search_intent import SearchIntentStage
from ai_writing.stages.structure import StructureStage
from ai_writing.stages.yukkuri_script import YukkuriScriptStage
from ai_writing.stages.docs_output import DocsOutputStage


class YukkuriPipeline(BasePipeline):
    """ゆっくり台本生成パイプライン"""

    content_type = "yukkuri"

    def _build_stages(self) -> list:
        """ゆっくり台本生成ステージを構築"""
        stages = [
            SearchIntentStage(self.config),
            StructureStage(self.config),
            YukkuriScriptStage(self.config),
            DocsOutputStage(self.config),
        ]

        return stages
