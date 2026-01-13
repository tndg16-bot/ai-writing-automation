"""Intro Ending Stage - YouTube用冒頭とエンディングを作成"""

from typing import Any

from ai_writing.core.context import GenerationContext
from ai_writing.stages.base import BaseStage
from ai_writing.utils.prompt_loader import PromptLoader


class IntroEndingStage(BaseStage):
    """YouTube用冒頭・エンディング作成ステージ"""

    prompt_file = "03_intro_ending.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "youtube")

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """冒頭とエンディングを作成"""
        from ai_writing.services.llm.base import LLMFactory

        # プロンプトをロード
        prompt_data = self.prompt_loader.load(self.prompt_file)

        # LLMを初期化
        llm_config = self.config.llm.model_dump(exclude={"provider"})
        llm = LLMFactory.create(self.config.llm.provider, **llm_config)

        # プロンプトを構築
        system_prompt = prompt_data.get("system", "")
        user_prompt = prompt_data.get("user", "")

        # チャンネル情報（クライアント設定またはデフォルト）
        channel_name = context.client_config.get("channel_name", "チャンネル名")
        presenter_name = context.client_config.get("presenter_name", "あなた")

        # 構成をテキスト形式に変換
        structure_text = self._format_structure(context.structure)

        # 変数を置換
        user_prompt = user_prompt.replace("{{keyword}}", context.keyword)
        user_prompt = user_prompt.replace("{{structure}}", structure_text)
        user_prompt = user_prompt.replace("{{channel_name}}", channel_name)
        user_prompt = user_prompt.replace("{{presenter_name}}", presenter_name)

        # LLMで生成
        result = await llm.generate_json(
            user_prompt,
            system_prompt=system_prompt,
        )

        # コンテキストに保存
        context.intro = result.get("intro")
        context.ending = result.get("ending")
        context.channel_name = channel_name
        context.presenter_name = presenter_name

        print(f"  冒頭・エンディング: 作成完了")

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
