"""Image Generation Stage - 画像生成ステージ"""

from typing import Any

from ai_writing.core.context import GenerationContext, Section
from ai_writing.core.exceptions import AIWritingError
from ai_writing.services.image.base import ImageGenerationResult, ImageGeneratorFactory
from ai_writing.stages.base import BaseStage
from ai_writing.utils.prompt_loader import PromptLoader


class ImageGenerationStage(BaseStage):
    """画像生成ステージ"""

    prompt_file = "07_image_generation.yaml"

    def __init__(self, config: Any):
        super().__init__(config)
        self.prompt_loader = PromptLoader(config.prompts_folder / "blog")

    def _calculate_insertion_positions(
        self,
        sections: list[Section],
        image_config: dict[str, Any],
    ) -> dict[int, str]:
        """画像挿入位置を計算

        Args:
            sections: セクションリスト
            image_config: 画像生成設定

        Returns:
            {セクションインデックス: 画像生成プロンプト} のマップ
        """
        insertion_rules = image_config.get("insertion_rules", {})
        positions = {}

        for i, section in enumerate(sections):
            should_insert = False

            if insertion_rules.get("after_h2", False) and i == 0:
                should_insert = True
            elif insertion_rules.get("after_lead", False):
                should_insert = True

            if should_insert:
                positions[i] = section

        return positions

    async def execute(self, context: GenerationContext) -> GenerationContext:
        """各セクションに挿入する画像を生成"""
        if not context.sections:
            raise AIWritingError("セクションが作成されていません")

        # 画像生成設定を取得
        image_config = context.client_config.get("image_generation", {})

        if not image_config.get("enabled", False):
            print("  画像生成: スキップ（無効）")
            return context

        # 挿入ルールを計算
        positions = self._calculate_insertion_positions(context.sections, image_config)

        if not positions:
            print("  画像生成: 挿入位置なし")
            return context

        # APIキーを環境変数から取得
        from ai_writing.core.config import EnvSettings

        env_settings = EnvSettings()

        # 画像ジェネレータを初期化
        generator_config = image_config.get("generator", {})
        provider = generator_config.get("provider", "dalle")

        if provider == "dalle":
            api_key = generator_config.get("api_key") or env_settings.openai_api_key
            generator = ImageGeneratorFactory.create(
                provider,
                api_key=api_key,
                model=generator_config.get("model", "dall-e-3"),
            )
        elif provider == "gemini":
            api_key = generator_config.get("api_key") or env_settings.google_api_key
            generator = ImageGeneratorFactory.create(
                provider,
                api_key=api_key,
                model=generator_config.get("model", "imagen-3.0-generate-001"),
            )
        else:
            raise AIWritingError(f"Unsupported image provider: {provider}")

        # 各位置で画像を生成
        images = []
        for idx, section in positions.items():
            try:
                # 画像生成プロンプトを作成
                prompt = self.prompt_loader.render(self.prompt_file, {
                    "keyword": context.keyword,
                    "heading": section.heading,
                    "content": section.content[:200],  # 先頭200文字を使用
                })

                from ai_writing.services.llm.base import LLMFactory
                llm_config = self.config.llm.model_dump(exclude={"provider"})
                llm = LLMFactory.create(self.config.llm.provider, **llm_config)

                image_prompt = await llm.generate(
                    prompt["user"],
                    system_prompt=prompt["system"]
                )

                # 画像を生成
                result: ImageGenerationResult = await generator.generate_with_cache(
                    prompt=image_prompt.strip(),
                    style=image_config.get("style", "natural"),
                    size=image_config.get("size", "1024x1024"),
                )

                # 画像情報を保存
                image_info = {
                    "section_index": idx,
                    "section_heading": section.heading,
                    "prompt": image_prompt,
                    "url": result.url,
                    "provider": result.provider,
                    "model": result.model,
                    "cached": result.cached,
                }

                images.append(image_info)

                # 対応するセクションに画像パスを設定
                context.sections[idx].image_path = result.url

                print(f"  画像生成: {section.heading}")

            except Exception as e:
                print(f"  画像生成エラー ({section.heading}): {e}")
                continue

        context.images = images
        return context
