"""Base stage class for content generation"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any

from ai_writing.core.context import GenerationContext
from ai_writing.core.exceptions import AIWritingError, StageError


class BaseStage(ABC):
    """Base class for content generation stages"""

    def __init__(self, config: Any):
        self.config = config

    @abstractmethod
    async def execute(self, context: GenerationContext) -> GenerationContext:
        """Execute this stage and return updated context"""
        pass
