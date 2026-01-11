"""LLM サービス基底クラス"""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLM(ABC):
    """LLM サービスの基底クラス"""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """テキストを生成する

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）
            **kwargs: 追加パラメータ

        Returns:
            生成されたテキスト
        """
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """JSON形式でテキストを生成する

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）
            **kwargs: 追加パラメータ

        Returns:
            パースされたJSONオブジェクト
        """
        pass


class LLMFactory:
    """LLMサービスのファクトリ"""

    @staticmethod
    def create(provider: str, **config: Any) -> BaseLLM:
        """プロバイダー名からLLMインスタンスを作成

        Args:
            provider: プロバイダー名（openai）
            **config: 設定パラメータ

        Returns:
            LLMインスタンス
        """
        if provider == "openai":
            from ai_writing.services.llm.openai import OpenAILLM

            return OpenAILLM(**config)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
