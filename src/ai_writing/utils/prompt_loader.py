"""プロンプトテンプレート読み込み"""

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, BaseLoader


class PromptLoader:
    """プロンプトテンプレートを読み込んで変数展開する"""

    def __init__(self, prompts_folder: Path | str):
        self.prompts_folder = Path(prompts_folder)
        self.env = Environment(loader=BaseLoader(), autoescape=False)

    def load(self, prompt_path: str) -> dict[str, Any]:
        """プロンプトファイルを読み込む"""
        full_path = self.prompts_folder / prompt_path
        if not full_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {full_path}")

        with open(full_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def render(self, prompt_path: str, variables: dict[str, Any]) -> dict[str, str]:
        """プロンプトを読み込んで変数展開する"""
        prompt_data = self.load(prompt_path)

        result = {}

        # system プロンプト
        if "system" in prompt_data:
            template = self.env.from_string(prompt_data["system"])
            result["system"] = template.render(**variables)

        # user プロンプト
        if "user" in prompt_data:
            template = self.env.from_string(prompt_data["user"])
            result["user"] = template.render(**variables)

        # メタデータ
        result["name"] = prompt_data.get("name", "")
        result["output_parser"] = prompt_data.get("output_parser", "text")

        return result
