"""Title Stage - タイトル作成ステージ"""
import json
from typing import Any

from ai_writing.core.context import GenerationContext
from ai_writing.stages.base import BaseStage
from ai_writing.core.exceptions import AIWritingError
from ai_writing.utils.prompt_loader import PromptLoader


class TitleStage(BaseStage):
    """タイトル作成ステージ"""

    prompt_file = "03_title.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "blog")

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """SEO記事のタイトル案を10個生成"""
        # プロンプトを読み込む
        prompt = self.prompt_loader.render(self.prompt_file, {
            "keyword": context.keyword,
            "persona": context.get_persona_text(),
        })

        try:
            # LLMからテキスト応答を取得
            from ai_writing.services.llm.base import LLMFactory
            llm_config = self.config.llm.model_dump(exclude={"provider"})
            llm = LLMFactory.create(self.config.llm.provider, **llm_config)

            response = await llm.generate(
                prompt["user"],
                system_prompt=prompt["system"]
            )

            # 応答をパースしてタイトル案として保存
            # 行単位で分割
            titles = [line.strip() for line in response.split("\n") if line.strip()]
            context.titles = titles
            # 最初のタイトルを選択
            context.selected_title = titles[0] if titles else None

            return context

        except Exception as e:
            raise AIWritingError(f"タイトル作成に失敗しました: {e}") from e
