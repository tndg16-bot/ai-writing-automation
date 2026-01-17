"""Base pipeline class for AI content generation"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Any, Callable

from ai_writing.core.context import GenerationContext
from ai_writing.core.exceptions import AIWritingError, PipelineError
from rich.console import Console

console = Console()


class BasePipeline(ABC):
    """Pipeline base class for content generation workflows"""

    def __init__(self, config: Any):
        self.config = config
        self.stages = self._build_stages()

    @abstractmethod
    def _build_stages(self) -> list:
        """Build the list of stages for this pipeline"""
        pass

    async def run(
        self, keyword: str, content_type: str = "blog", progress_callback: Optional[Callable] = None
    ) -> GenerationContext:
        """Execute pipeline and return final context"""
        context = GenerationContext(
            keyword=keyword,
            content_type=content_type,
        )

        stage_name = ""
        try:
            for i, stage in enumerate(self.stages, 1):
                # ステージ名を表示
                stage_name = stage.__class__.__name__.replace("Stage", "")
                console.print(f"[dim]  → {i}/{len(self.stages)}: {stage_name}[/dim]")

                # ステージ実行
                context = await stage.execute(context)

                # プログレス更新
                if progress_callback:
                    progress_callback(advance=1)
        except Exception as e:
            console.print(f"[red]✗ エラー: {stage_name} ステージで失敗しました[/red]")
            raise PipelineError(f"Pipeline execution failed: {e}") from e

        return context
