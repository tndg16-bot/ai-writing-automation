# AI ライティング自動化システム - アーキテクチャ設計書

## 1. ディレクトリ構造

```
ai-writing-automation/
├── README.md
├── REQUIREMENTS.md          # 要件定義書
├── ARCHITECTURE.md          # 本ドキュメント
├── pyproject.toml           # プロジェクト設定
├── .env.example             # 環境変数テンプレート
├── .gitignore
│
├── config/
│   ├── config.yaml          # メイン設定
│   └── clients/             # クライアント別設定
│       └── default.yaml
│
├── prompts/                  # プロンプトテンプレート
│   ├── blog/
│   │   ├── 01_search_intent.yaml
│   │   ├── 02_structure.yaml
│   │   ├── 03_title.yaml
│   │   ├── 04_lead.yaml
│   │   ├── 05_body.yaml
│   │   └── 06_summary.yaml
│   ├── youtube/
│   │   ├── 01_search_intent.yaml
│   │   ├── 02_structure.yaml
│   │   ├── 03_intro_ending.yaml
│   │   └── 04_body.yaml
│   └── yukkuri/
│       ├── 03_intro_ending.yaml
│       └── 04_body.yaml
│
├── templates/                # Google Docs テンプレート
│   ├── blog_default.json
│   ├── youtube_default.json
│   └── yukkuri_default.json
│
├── src/
│   └── ai_writing/
│       ├── __init__.py
│       ├── cli.py            # CLIエントリーポイント
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py     # 設定管理
│       │   ├── context.py    # 生成コンテキスト
│       │   └── exceptions.py # カスタム例外
│       │
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── base.py       # パイプライン基底クラス
│       │   ├── blog.py       # ブログ生成パイプライン
│       │   ├── youtube.py    # YouTube台本パイプライン
│       │   └── yukkuri.py    # ゆっくり台本パイプライン
│       │
│       ├── stages/           # パイプラインの各ステージ
│       │   ├── __init__.py
│       │   ├── search_intent.py
│       │   ├── structure.py
│       │   ├── title.py
│       │   ├── lead.py
│       │   ├── body.py
│       │   ├── summary.py
│       │   └── intro_ending.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── llm/
│       │   │   ├── __init__.py
│       │   │   ├── base.py       # LLM基底クラス
│       │   │   └── openai.py     # OpenAI実装
│       │   │
│       │   ├── image/
│       │   │   ├── __init__.py
│       │   │   ├── base.py       # 画像生成基底クラス
│       │   │   ├── dalle.py      # DALL-E実装
│       │   │   ├── gemini.py     # Gemini実装
│       │   │   ├── midjourney.py # Midjourney実装
│       │   │   └── canva.py      # Canva実装
│       │   │
│       │   └── google/
│       │       ├── __init__.py
│       │       └── docs.py       # Google Docs操作
│       │
│       ├── templates/
│       │   ├── __init__.py
│       │   ├── engine.py     # テンプレートエンジン
│       │   └── renderer.py   # ドキュメントレンダラー
│       │
│       └── utils/
│           ├── __init__.py
│           ├── prompt_loader.py  # プロンプト読み込み
│           └── validators.py     # バリデーション
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_pipeline/
│   ├── test_services/
│   └── test_templates/
│
└── docs/
    ├── setup.md              # セットアップ手順
    └── usage.md              # 使い方ガイド
```

---

## 2. コンポーネント詳細

### 2.1 Core モジュール

#### config.py
```python
from pydantic import BaseModel
from pathlib import Path
import yaml

class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7

class ImageConfig(BaseModel):
    default_provider: str = "dalle"
    providers: dict[str, dict]

class Config(BaseModel):
    llm: LLMConfig
    image: ImageConfig
    google_docs: dict
    prompts_folder: Path
    
    @classmethod
    def load(cls, path: Path) -> "Config":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

#### context.py
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GenerationContext:
    """生成プロセス全体で共有されるコンテキスト"""
    keyword: str
    content_type: str  # blog | youtube | yukkuri
    
    # 生成結果を蓄積
    persona: Optional[str] = None
    needs_explicit: Optional[list[str]] = None
    needs_latent: Optional[list[str]] = None
    structure: Optional[list[dict]] = None
    titles: Optional[list[str]] = None
    selected_title: Optional[str] = None
    lead: Optional[str] = None
    sections: list[dict] = field(default_factory=list)
    summary: Optional[str] = None
    images: list[dict] = field(default_factory=list)
    
    # クライアント設定
    client_config: Optional[dict] = None
```

### 2.2 Pipeline モジュール

#### base.py
```python
from abc import ABC, abstractmethod
from ai_writing.core.context import GenerationContext

class BasePipeline(ABC):
    """パイプライン基底クラス"""
    
    def __init__(self, config, client_config=None):
        self.config = config
        self.client_config = client_config
        self.stages = self._build_stages()
    
    @abstractmethod
    def _build_stages(self) -> list:
        """パイプラインのステージを構築"""
        pass
    
    async def run(self, keyword: str) -> GenerationContext:
        """パイプラインを実行"""
        context = GenerationContext(
            keyword=keyword,
            content_type=self.content_type,
            client_config=self.client_config
        )
        
        for stage in self.stages:
            context = await stage.execute(context)
        
        return context
```

#### blog.py
```python
from ai_writing.pipeline.base import BasePipeline
from ai_writing.stages import (
    SearchIntentStage,
    StructureStage,
    TitleStage,
    LeadStage,
    BodyStage,
    SummaryStage
)

class BlogPipeline(BasePipeline):
    content_type = "blog"
    
    def _build_stages(self) -> list:
        return [
            SearchIntentStage(self.config),
            StructureStage(self.config),
            TitleStage(self.config),
            LeadStage(self.config),
            BodyStage(self.config),
            SummaryStage(self.config),
        ]
```

### 2.3 Stages モジュール

#### search_intent.py
```python
from ai_writing.stages.base import BaseStage
from ai_writing.core.context import GenerationContext

class SearchIntentStage(BaseStage):
    """検索意図調査ステージ"""
    
    prompt_file = "01_search_intent.yaml"
    
    async def execute(self, context: GenerationContext) -> GenerationContext:
        prompt = self.load_prompt(context)
        
        response = await self.llm.generate(prompt)
        
        # レスポンスをパース
        parsed = self.parse_response(response)
        
        context.persona = parsed["persona"]
        context.needs_explicit = parsed["needs_explicit"]
        context.needs_latent = parsed["needs_latent"]
        
        return context
```

### 2.4 Services モジュール

#### llm/base.py
```python
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

class LLMFactory:
    @staticmethod
    def create(provider: str, config: dict) -> BaseLLM:
        if provider == "openai":
            from ai_writing.services.llm.openai import OpenAILLM
            return OpenAILLM(config)
        raise ValueError(f"Unknown provider: {provider}")
```

#### image/base.py
```python
from abc import ABC, abstractmethod
from pathlib import Path

class BaseImageGenerator(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Path:
        """画像を生成してローカルパスを返す"""
        pass

class ImageGeneratorFactory:
    @staticmethod
    def create(provider: str, config: dict) -> BaseImageGenerator:
        providers = {
            "dalle": "ai_writing.services.image.dalle.DalleGenerator",
            "gemini": "ai_writing.services.image.gemini.GeminiGenerator",
            "midjourney": "ai_writing.services.image.midjourney.MidjourneyGenerator",
            "canva": "ai_writing.services.image.canva.CanvaGenerator",
        }
        # 動的インポートして返す
        ...
```

#### google/docs.py
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GoogleDocsService:
    def __init__(self, credentials: Credentials):
        self.service = build('docs', 'v1', credentials=credentials)
        self.drive_service = build('drive', 'v3', credentials=credentials)
    
    def create_document(self, title: str) -> str:
        """新規ドキュメントを作成してIDを返す"""
        doc = self.service.documents().create(body={"title": title}).execute()
        return doc["documentId"]
    
    def insert_text(self, doc_id: str, text: str, index: int):
        """テキストを挿入"""
        requests = [{
            "insertText": {
                "location": {"index": index},
                "text": text
            }
        }]
        self.service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()
    
    def insert_image(self, doc_id: str, image_url: str, index: int):
        """画像を挿入"""
        requests = [{
            "insertInlineImage": {
                "location": {"index": index},
                "uri": image_url,
                "objectSize": {
                    "width": {"magnitude": 400, "unit": "PT"},
                    "height": {"magnitude": 300, "unit": "PT"}
                }
            }
        }]
        self.service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()
    
    def apply_heading_style(self, doc_id: str, start: int, end: int, level: int):
        """見出しスタイルを適用"""
        requests = [{
            "updateParagraphStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "paragraphStyle": {"namedStyleType": f"HEADING_{level}"},
                "fields": "namedStyleType"
            }
        }]
        self.service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()
```

### 2.5 Templates モジュール

#### engine.py
```python
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class TemplateEngine:
    def __init__(self, templates_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=False
        )
    
    def render(self, template_name: str, context: dict) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
```

---

## 3. プロンプトテンプレート形式

### prompts/blog/01_search_intent.yaml
```yaml
name: "検索意図調査"
description: "キーワードからペルソナと顕在・潜在ニーズを抽出"

system: |
  あなたはSEOを十分に理解してるプロのWebライターです。

user: |
  #命令書
  「{{keyword}}」というキーワードでSEO記事を書きます。
  このキーワードのペルソナ、顕在ニーズ、潜在ニーズを教えてください。

  #制約条件
  ・ペルソナは年齢や性別、年収、生活スタイルなどの情報を書く
  ・顕在ニーズと潜在ニーズはそれぞれ2つずつ書く

  #出力形式
  ・ペルソナは100文字程度で書く
  ・顕在ニーズと潜在ニーズはそれぞれ2つずつ挙げて、80文字程度で書く
  ・「：」などの記号は使わない
  
  以下のJSON形式で出力してください：
  ```json
  {
    "persona": "ペルソナの説明",
    "needs_explicit": ["顕在ニーズ1", "顕在ニーズ2"],
    "needs_latent": ["潜在ニーズ1", "潜在ニーズ2"]
  }
  ```

output_parser: "json"
```

---

## 4. CLI インターフェース

### cli.py
```python
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def generate(
    keyword: str = typer.Argument(..., help="メインキーワード"),
    content_type: str = typer.Option("blog", help="コンテンツタイプ: blog|youtube|yukkuri"),
    client: str = typer.Option("default", help="クライアント設定名"),
    output: Path = typer.Option(None, help="ローカル出力先（指定なしでGoogle Docs）"),
):
    """AIライティングを実行"""
    ...

@app.command()
def list_clients():
    """利用可能なクライアント設定を一覧"""
    ...

@app.command()
def validate_config():
    """設定ファイルを検証"""
    ...

if __name__ == "__main__":
    app()
```

**使用例:**
```bash
# ブログ記事を生成
python -m ai_writing generate "AI副業" --content-type blog

# クライアント指定
python -m ai_writing generate "投資信託" --client client_a

# YouTube台本
python -m ai_writing generate "犬の飼い方" --content-type youtube
```

---

## 5. エラーハンドリング戦略

```python
# exceptions.py
class AIWritingError(Exception):
    """基底例外"""
    pass

class LLMError(AIWritingError):
    """LLM API関連エラー"""
    pass

class ImageGenerationError(AIWritingError):
    """画像生成エラー"""
    pass

class GoogleDocsError(AIWritingError):
    """Google Docs操作エラー"""
    pass

class ConfigurationError(AIWritingError):
    """設定エラー"""
    pass
```

### リトライ戦略
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_llm_with_retry(self, prompt: str):
    return await self.llm.generate(prompt)
```

---

## 6. 将来の拡張ポイント

| 拡張 | 実装方法 |
|------|---------|
| Web UI | FastAPI + React/Next.js |
| WordPress投稿 | WordPress REST API連携 |
| 履歴管理 | SQLite/PostgreSQL |
| バッチ処理 | Celery + Redis |
| A/Bテスト | 複数プロンプトの比較機能 |
