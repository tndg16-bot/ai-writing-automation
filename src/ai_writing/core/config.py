"""設定管理"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LLMConfig(BaseModel):
    """LLM設定"""

    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    base_url: str | None = None
    api_key: str | None = None


class ImageProviderConfig(BaseModel):
    """画像生成プロバイダー設定"""

    enabled: bool = False
    model: str | None = None


class ImageConfig(BaseModel):
    """画像生成設定"""

    default_provider: str = "dalle"
    providers: dict[str, ImageProviderConfig] = Field(default_factory=dict)


class ImageInsertionConfig(BaseModel):
    """画像挿入ルール設定"""

    after_h2: bool = True
    after_lead: bool = True
    before_summary: bool = False
    custom_positions: list[dict[str, str]] = Field(default_factory=list)


class GoogleDocsConfig(BaseModel):
    """Google Docs設定"""

    template_folder: str = "./templates"
    output_folder_id: str | None = None


class Config(BaseModel):
    """メイン設定"""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    image: ImageConfig = Field(default_factory=ImageConfig)
    image_insertion: ImageInsertionConfig = Field(default_factory=ImageInsertionConfig)
    google_docs: GoogleDocsConfig = Field(default_factory=GoogleDocsConfig)
    prompts_folder: Path = Path("./prompts")

    @classmethod
    def load(cls, path: Path | str) -> "Config":
        """YAMLファイルから設定を読み込む"""
        path = Path(path)
        if not path.exists():
            return cls()

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)

    @classmethod
    def load_with_client(cls, config_path: Path | str, client_path: Path | str | None = None) -> "Config":
        """メイン設定とクライアント設定をマージして読み込む"""
        config = cls.load(config_path)

        if client_path:
            client_path = Path(client_path)
            if client_path.exists():
                with open(client_path, encoding="utf-8") as f:
                    client_data = yaml.safe_load(f) or {}

                # クライアント設定でオーバーライド
                if "llm" in client_data:
                    # 既存の設定をdictにしてマージ
                    llm_dict = config.llm.model_dump()
                    llm_dict.update(client_data["llm"])
                    config.llm = LLMConfig(**llm_dict)

                if "image" in client_data:
                    image_dict = config.image.model_dump()
                    image_dict.update(client_data["image"])
                    config.image = ImageConfig(**image_dict)

                if "image_insertion" in client_data:
                    config.image_insertion = ImageInsertionConfig(**client_data["image_insertion"])

        return config


class EnvSettings(BaseSettings):
    """環境変数からの設定"""

    openai_api_key: str = ""
    google_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    midjourney_token: str = ""
    canva_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
