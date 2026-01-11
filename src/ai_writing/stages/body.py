"""Body Stage - 本文作成ステージ（PREP法）"""
from typing import Any

from ai_writing.core.context import GenerationContext, Section
from ai_writing.stages.base import BaseStage
from ai_writing.core.exceptions import AIWritingError
from ai_writing.utils.prompt_loader import PromptLoader


class BodyStage(BaseStage):
    """本文作成ステージ"""

    prompt_file = "05_body.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "blog")

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """PREP法で各h2/h3セクションを生成"""
        # 構成からセクションを取得
        structure = context.structure
        if not structure:
            raise AIWritingError("構成が作成されていません")

        sections = []
        for item in structure:
            heading = item["heading"]
            level = item["level"]

            # 出力したい見出しを特定
            if level == "h2":
                output_heading = heading
            elif level == "h3":
                output_heading = f"h2：{structure[structure.index(item) - 1]['heading']}"
            else:
                continue

            # プロンプトを読み込む
            prompt = self.prompt_loader.render(self.prompt_file, {
                "keyword": context.keyword,
                "persona": context.get_persona_text(),
                "heading": output_heading,
                "structure": context.get_structure_text(),
            })

            try:
                # LLMから本文を取得
                from ai_writing.services.llm.base import LLMFactory
                llm_config = self.config.llm.model_dump(exclude={"provider"})
                llm = LLMFactory.create(self.config.llm.provider, **llm_config)

                response = await llm.generate(
                    prompt["user"],
                    system_prompt=prompt["system"]
                )

                # セクションとして追加
                section = Section(heading=heading, content=response.strip())
                sections.append(section)

                # 進捗表示
                print(f"  セクション作成: {heading}")

            except Exception as e:
                raise AIWritingError(f"本文作成に失敗しました: {e}") from e

        # 全セクションをコンテキストに保存
        context.sections = sections
        return context
