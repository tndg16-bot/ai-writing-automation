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
            "top5_structure": "（上位記事の構成は省略）",  # 簡略化
            "needs_explicit": ", ".join(context.needs_explicit) if context.needs_explicit else "",
            "needs_latent": ", ".join(context.needs_latent) if context.needs_latent else "",
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
            
            # デバッグ出力
            print(f"  [DEBUG] 構成LLM応答:\n{response[:500]}...")

            # 応答をパースして構成として保存
            # テキスト形式（h2: 見出し, h3: サブ見出し）または Markdown形式
            import re
            lines = response.split("\n")
            structure = []
            for line in lines:
                line = line.strip()
                
                # h2：見出し 形式（全角コロン）
                if line.startswith("h2：") or line.startswith("H2："):
                    heading = line.split("：", 1)[1].strip() if "：" in line else ""
                    if heading:
                        structure.append({"level": "h2", "heading": heading})
                # h2: 見出し 形式（半角コロン）
                elif line.lower().startswith("h2:"):
                    heading = line.split(":", 1)[1].strip() if ":" in line else ""
                    if heading:
                        structure.append({"level": "h2", "heading": heading})
                # h3：見出し 形式（全角コロン）
                elif line.startswith("h3：") or line.startswith("H3："):
                    heading = line.split("：", 1)[1].strip() if "：" in line else ""
                    if heading:
                        structure.append({"level": "h3", "heading": heading})
                # h3: 見出し 形式（半角コロン）
                elif line.lower().startswith("h3:"):
                    heading = line.split(":", 1)[1].strip() if ":" in line else ""
                    if heading:
                        structure.append({"level": "h3", "heading": heading})
                # Markdown形式: ## 見出し
                elif line.startswith("## ") and not line.startswith("### "):
                    heading = line[3:].strip()
                    if heading:
                        structure.append({"level": "h2", "heading": heading})
                # Markdown形式: ### 見出し
                elif line.startswith("### "):
                    heading = line[4:].strip()
                    if heading:
                        structure.append({"level": "h3", "heading": heading})
                # 番号付きリスト形式: 1. h2 見出し
                elif re.match(r'^\d+\.\s*(h2|H2)[：:]\s*', line):
                    match = re.match(r'^\d+\.\s*(h2|H2)[：:]\s*(.+)', line)
                    if match:
                        structure.append({"level": "h2", "heading": match.group(2).strip()})
                elif re.match(r'^\d+\.\s*(h3|H3)[：:]\s*', line):
                    match = re.match(r'^\d+\.\s*(h3|H3)[：:]\s*(.+)', line)
                    if match:
                        structure.append({"level": "h3", "heading": match.group(2).strip()})

            # デバッグ出力
            print(f"  構成抽出: {len(structure)} 件の見出しを検出")

            context.structure = structure
            return context

        except Exception as e:
            raise AIWritingError(f"構成作成に失敗しました: {e}") from e
