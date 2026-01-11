"""Search Intent Stage - 検索意図調査ステージ"""
import json
from typing import Any

from ai_writing.core.context import GenerationContext
from ai_writing.stages.base import BaseStage
from ai_writing.core.exceptions import AIWritingError
from ai_writing.utils.prompt_loader import PromptLoader


class SearchIntentStage(BaseStage):
    """検索意図調査ステージ"""

    prompt_file = "01_search_intent.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "blog")

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """検索意図調査を実行"""
        # プロンプトを読み込む
        prompt = self.prompt_loader.render(self.prompt_file, {
            "keyword": context.keyword
        })

        try:
            # LLMからJSON応答を取得
            from ai_writing.services.llm.base import LLMFactory
            llm_config = self.config.llm.model_dump(exclude={"provider"})
            llm = LLMFactory.create(self.config.llm.provider, **llm_config)
            
            response = await llm.generate_json(
                prompt["user"],
                system_prompt=prompt["system"]
            )

            # 結果をコンテキストに保存
            context.persona = response["persona"]
            context.needs_explicit = response["needs_explicit"]
            context.needs_latent = response["needs_latent"]

            return context

        except Exception as e:
            raise AIWritingError(f"検索意図調査に失敗しました: {e}") from e
