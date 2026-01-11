"""生成コンテキスト - パイプライン全体で共有されるデータ"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Section:
    """記事セクション（h2単位）"""

    heading: str
    content: str
    subsections: list["Subsection"] = field(default_factory=list)
    image_path: str | None = None


@dataclass
class Subsection:
    """サブセクション（h3単位）"""

    heading: str
    content: str


@dataclass
class GenerationContext:
    """生成プロセス全体で共有されるコンテキスト"""

    # 入力
    keyword: str
    content_type: str = "blog"  # blog | youtube | yukkuri

    # 検索意図調査の結果
    persona: str | None = None
    needs_explicit: list[str] = field(default_factory=list)
    needs_latent: list[str] = field(default_factory=list)

    # 構成
    structure: list[dict[str, Any]] = field(default_factory=list)

    # タイトル
    titles: list[str] = field(default_factory=list)
    selected_title: str | None = None

    # コンテンツ
    lead: str | None = None
    sections: list[Section] = field(default_factory=list)
    summary: str | None = None

    # YouTube/ゆっくり用
    intro: str | None = None
    ending: str | None = None
    channel_name: str | None = None
    presenter_name: str | None = None

    # 画像
    images: list[dict[str, Any]] = field(default_factory=list)

    # クライアント設定
    client_config: dict[str, Any] = field(default_factory=dict)

    # メタデータ
    raw_responses: dict[str, str] = field(default_factory=dict)

    def get_persona_text(self) -> str:
        """ペルソナ情報をテキスト形式で取得"""
        parts = []
        if self.persona:
            parts.append(f"ペルソナ\n{self.persona}")
        if self.needs_explicit:
            parts.append(f"顕在ニーズ\n" + "\n".join(self.needs_explicit))
        if self.needs_latent:
            parts.append(f"潜在ニーズ\n" + "\n".join(self.needs_latent))
        return "\n\n".join(parts)

    def get_structure_text(self) -> str:
        """構成をテキスト形式で取得"""
        lines = []
        for item in self.structure:
            level = item.get("level", "h2")
            heading = item.get("heading", "")
            lines.append(f"{level}：{heading}")
        return "\n".join(lines)
