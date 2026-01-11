"""Summary Stage - まとめ文作成ステージ"""
import json
from typing import Any

from ai_writing.core.context import GenerationContext
from ai_writing.stages.base import BaseStage
from ai_writing.core.exceptions import AIWritingError
from ai_writing.utils.prompt_loader import PromptLoader


class SummaryStage(BaseStage):
    """まとめ文作成ステージ"""

    prompt_file = "06_summary.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "blog")

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """まとめ文（200-300文字）を作成"""
        # プロンプトを読み込む
        prompt = self.prompt_loader.render(self.prompt_file, {
            "keyword": context.keyword,
            "title": context.selected_title,
            "structure": context.get_structure_text(),
        })

        try:
            # LLMからまとめ文を取得
            from ai_writing.services.llm.base import LLMFactory
            llm_config = self.config.llm.model_dump(exclude={"provider"})
            llm = LLMFactory.create(self.config.llm.provider, **llm_config)

            response = await llm.generate(
                prompt=prompt["user"],
                system_prompt=prompt["system"]
            )

            # まとめ文をコンテキストに保存
            context.summary = response.strip()
            
            return context

        except Exception as e:
            raise AIWritingError(f"まとめ文作成に失敗しました: {e}")
