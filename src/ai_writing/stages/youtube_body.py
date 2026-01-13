"""YouTube Body Stage - YouTube用本文を作成"""

from typing import Any

from ai_writing.core.context import GenerationContext
from ai_writing.stages.base import BaseStage
from ai_writing.utils.prompt_loader import PromptLoader


class YouTubeBodyStage(BaseStage):
    """YouTube用本文作成ステージ"""

    prompt_file = "04_body.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "youtube")

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """YouTube本文を作成"""
        from ai_writing.core.context import Section
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

        # 検索意図をテキスト形式に変換
        # search_intentsをcontextから取得（YouTubeの検索意図調査ステージで保存されるはず）
        search_intents = context.structure if "structure" in dir(context.structure[0]) and "search_intents" in str(context.structure[0]) else []
        # 構造の各要素から検索意図を取得（簡易的な実装）
        search_intents_text = "\n".join([
            f"{i+1}. {s.get('section', '')}" for i, s in enumerate(context.structure)
        ])

        # 変数を置換
        user_prompt = user_prompt.replace("{{keyword}}", context.keyword)
        user_prompt = user_prompt.replace("{{structure}}", structure_text)
        user_prompt = user_prompt.replace("{{search_intents}}", search_intents_text)

        # LLMで生成
        result = await llm.generate_json(
            user_prompt,
            system_prompt=system_prompt,
        )

        # セクションを作成
        sections_data = result.get("sections", [])
        sections = []
        for section_data in sections_data:
            section = Section(
                heading=section_data.get("heading", ""),
                content=section_data.get("content", ""),
                subsections=[],
                image_path=None,
            )
            sections.append(section)

        # コンテキストに保存
        context.sections = sections

        print(f"  YouTube本文: {len(sections)}セクション作成完了")

        return context

    def _format_structure(self, structure: list[dict[str, Any]]) -> str:
        """構成をテキスト形式に変換"""
        lines = []
        for i, item in enumerate(structure, 1):
            section = item.get("section", "")
            description = item.get("description", "")
            estimated_time = item.get("estimated_time", "")
            lines.append(f"{i}. {section}")
            if description:
                lines.append(f"   内容: {description}")
            if estimated_time:
                lines.append(f"   時間: {estimated_time}")
        return "\n".join(lines)

    def _format_search_intents(self, search_intents: list[dict[str, Any]]) -> str:
        """検索意図をテキスト形式に変換"""
        if not search_intents:
            return ""

        lines = []
        for intent in search_intents:
            category = intent.get("category", "")
            keywords = intent.get("keywords", [])
            lines.append(f"カテゴリ: {category}")
            lines.append(f"キーワード: {', '.join(keywords)}")
        return "\n".join(lines)
