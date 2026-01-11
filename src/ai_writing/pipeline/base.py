"""Base pipeline class for AI content generation"""
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Any

from ai_writing.core.context import GenerationContext
from ai_writing.core.exceptions import AIWritingError, PipelineError


class BasePipeline(ABC):
    """Pipeline base class for content generation workflows"""

    def __init__(self, config: Any):
        self.config = config
        self.stages = self._build_stages()

    @abstractmethod
    def _build_stages(self) -> list:
        """Build the list of stages for this pipeline"""
        pass

    async def run(self, keyword: str, content_type: str = "blog") -> GenerationContext:
        """Execute the pipeline and return final context"""
        context = GenerationContext(
            keyword=keyword,
            content_type=content_type,
        )

        try:
            for stage in self.stages:
                context = await stage.execute(context)
        except Exception as e:
            raise PipelineError(f"Pipeline execution failed: {e}") from e

        return context
