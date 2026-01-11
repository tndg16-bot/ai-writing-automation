"""Structure Stage - 構成作成ステージ"""
from typing import Any

from ai_writing.core.context import GenerationContext
from ai_writing.stages.base import BaseStage
from ai_writing.core.exceptions import AIWritingError
from ai_writing.utils.prompt_loader import PromptLoader


class StructureStage(BaseStage):
    """構成作成ステージ"""

    prompt_file = "02_structure.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "blog")

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """上位記事を参考にh2/h3見出し構成を作成"""
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

            # 応答をパースして構成として保存
            # テキスト形式（h2: 見出し, h3: サブ見出し）
            lines = response.split("\n")
            structure = []
            for line in lines:
                line = line.strip()
                if line.startswith("h2："):
                    structure.append({"level": "h2", "heading": line.replace("h2：", "").strip()})
                elif line.startswith("h3："):
                    structure.append({"level": "h3", "heading": line.replace("h3：", "").strip()})

            context.structure = structure
            return context

        except Exception as e:
            raise AIWritingError(f"構成作成に失敗しました: {e}") from e
