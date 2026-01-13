"""Yukkuri Script Stage - ゆっくり動画台本を作成"""

from typing import Any

from ai_writing.core.context import GenerationContext, Section
from ai_writing.stages.base import BaseStage
from ai_writing.utils.prompt_loader import PromptLoader


class YukkuriScriptStage(BaseStage):
    """ゆっくり動画台本作成ステージ"""

    prompt_file = "03_script.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "yukkuri")

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """ゆっくり動画台本を作成"""
        from ai_writing.services.llm.base import LLMFactory

        # プロンプトをロード
        prompt_data = self.prompt_loader.load(self.prompt_file)

        # LLMを初期化
        llm_config = self.config.llm.model_dump(exclude={"provider"})
        llm = LLMFactory.create(self.config.llm.provider, **llm_config)

        # プロンプトを構築
        system_prompt = prompt_data.get("system", "")
        user_prompt = prompt_data.get("user", "")

        # 構成をテキスト形式に変換
        structure_text = self._format_structure(context.structure)

        # 変数を置換
        user_prompt = user_prompt.replace("{{keyword}}", context.keyword)
        user_prompt = user_prompt.replace("{{structure}}", structure_text)

        # LLMで生成
        result = await llm.generate_json(
            user_prompt,
            system_prompt=system_prompt,
        )

        # セクションを作成（霊夢と魔理沙の台本）
        sections_data = result.get("sections", [])
        sections = []
        for section_data in sections_data:
            # 霊夢と魔理沙の台本を結合
            reimu_script = section_data.get("reimu", "")
            marisa_script = section_data.get("marisa", "")

            # 台本を結合（見出しとしてheadingを使用）
            content = f"霊夢:\n{reimu_script}\n\n魔理沙:\n{marisa_script}"

            section = Section(
                heading=section_data.get("heading", ""),
                content=content,
                subsections=[],
                image_path=None,
            )
            sections.append(section)

        # コンテキストに保存
        context.sections = sections

        print(f"  ゆっくり台本: {len(sections)}セクション作成完了")

        return context

    def _format_structure(self, structure: list[dict[str, Any]]) -> str:
        """構成をテキスト形式に変換"""
        lines = []
        for i, item in enumerate(structure, 1):
            topic = item.get("topic", "")
            reimu_role = item.get("reimu_role", "")
            marisa_role = item.get("marisa_role", "")
            lines.append(f"{i}. {topic}")
            lines.append(f"   霊夢: {reimu_role}")
            lines.append(f"   魔理沙: {marisa_role}")
        return "\n".join(lines)
