# AI ライティング自動化システム - 要件定義書

## 1. プロジェクト概要

### 1.1 目的
本山貴裕氏のAIライティングノウハウ（スプレッドシート）を自動化し、キーワード入力から Google Docs 完成稿までをワンストップで生成するシステムを構築する。

### 1.2 スコープ
- **In Scope**: ブログ記事生成、YouTube台本生成、画像生成・配置、Google Docs出力
- **Out of Scope**: WordPress直接投稿、YouTube直接アップロード（将来拡張）

---

## 2. 機能要件

### 2.1 コンテンツ生成パイプライン

#### 2.1.1 ブログ記事生成フロー
| 工程 | 入力 | 出力 | 自動化方法 |
|------|------|------|-----------|
| 1. 検索意図調査 | キーワード | ペルソナ、顕在/潜在ニーズ | ChatGPT API |
| 2. 構成作成 | 上位記事データ、ペルソナ | h2/h3見出し構成 | ラッコキーワード + ChatGPT API |
| 3. タイトル作成 | 構成、ペルソナ | タイトル案10個 | ChatGPT API |
| 4. リード文作成 | タイトル、構成、ペルソナ | リード文（150-200字） | ChatGPT API |
| 5. 本文作成 | 構成、ペルソナ | 本文（PREP法） | ChatGPT API |
| 6. まとめ文作成 | 構成、タイトル | まとめ（200-300字） | ChatGPT API |

#### 2.1.2 YouTube台本生成フロー
| 工程 | 入力 | 出力 | 自動化方法 |
|------|------|------|-----------|
| 1. 検索意図調査 | キーワード | 検索意図グルーピング | ChatGPT API |
| 2. 目次構成作成 | 上位記事構成 | 統合目次 | ChatGPT API |
| 3. 冒頭&エンディング | 目次、変数 | イントロ/エンディング | ChatGPT API |
| 4. 本文作成 | 目次、検索意図 | 本文（2000字/セクション） | ChatGPT API |

#### 2.1.3 ゆっくり動画台本
- 霊夢・魔理沙の掛け合い形式
- YouTube台本と同じ工程、異なるプロンプト

### 2.2 画像生成機能

#### 2.2.1 対応画像生成サービス
| サービス | 優先度 | 接続方法 |
|---------|--------|---------|
| DALL-E (OpenAI) | P0 | OpenAI API |
| Gemini (Google) | P0 | Gemini API |
| Midjourney | P1 | 非公式API or Discord Bot |
| Canva | P1 | Canva API |

#### 2.2.2 画像挿入ルール（カスタマイズ可能）
```yaml
# 設定例
image_insertion:
  rules:
    - position: "after_h2"        # h2見出しの後
      enabled: true
    - position: "after_lead"      # リード文の後
      enabled: true
    - position: "before_summary"  # まとめの前
      enabled: false
  custom_positions: []            # クライアント指定の挿入位置
```

### 2.3 Google Docs 出力機能

#### 2.3.1 テンプレート機能
- 差し込み変数によるカスタマイズ
- クライアント別テンプレート管理
- 画像配置位置の指定

#### 2.3.2 差し込み変数
```
{{title}}           - 記事タイトル
{{lead}}            - リード文
{{h2_1}}            - 1つ目のh2見出し
{{h2_1_content}}    - 1つ目のh2の本文
{{h3_1_1}}          - 1つ目のh2配下の1つ目のh3
{{image_1}}         - 1つ目の画像挿入位置
{{summary}}         - まとめ文
{{persona}}         - ペルソナ情報
{{keyword}}         - メインキーワード
```

---

## 3. 非機能要件

### 3.1 パフォーマンス
- 1記事生成: 5分以内（画像生成含む）
- 並列処理: 複数記事の同時生成対応

### 3.2 拡張性
- 新しい画像生成サービスの追加が容易
- プロンプトテンプレートの外部ファイル管理
- クライアント別設定のプロファイル管理

### 3.3 エラーハンドリング
- API障害時のリトライ機構
- 部分的な生成結果の保存・再開

---

## 4. 技術スタック

### 4.1 コア技術
| 領域 | 技術 | 理由 |
|------|------|------|
| 言語 | Python 3.11+ | 豊富なAI/APIライブラリ |
| LLM API | OpenAI API (GPT-4) | スプレッドシートの想定モデル |
| Google連携 | Google Docs API | 最終出力先 |
| 設定管理 | YAML/TOML | 人間が編集しやすい |

### 4.2 ライブラリ（予定）
```
openai              - ChatGPT API
google-api-python-client - Google Docs API
google-auth         - Google認証
pydantic            - 設定・データバリデーション
jinja2              - テンプレートエンジン
httpx               - HTTP クライアント
rich                - CLI表示
typer               - CLI フレームワーク
```

---

## 5. システム構成図

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI / Web UI                            │
│                    (typer / FastAPI - 将来)                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      Core Engine                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Pipeline   │  │  Template   │  │   Config    │             │
│  │  Manager    │  │   Engine    │  │   Manager   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
┌─────────▼────────────────▼────────────────▼─────────────────────┐
│                      Service Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   LLM       │  │   Image     │  │  Google     │             │
│  │  Service    │  │  Generator  │  │  Docs       │             │
│  │ (ChatGPT)   │  │  Service    │  │  Service    │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────────┐  ┌──────────────┐
    │ OpenAI   │    │ DALL-E       │  │ Google       │
    │ API      │    │ Gemini       │  │ Docs API     │
    └──────────┘    │ Midjourney   │  └──────────────┘
                    │ Canva        │
                    └──────────────┘
```

---

## 6. データフロー

```
[キーワード入力]
       │
       ▼
[検索意図調査] ──→ {persona, needs} を保存
       │
       ▼
[構成作成] ──→ {structure} を保存
       │
       ▼
[タイトル作成] ──→ {titles[]} から選択
       │
       ▼
[リード文作成] ──→ {lead} を保存
       │
       ▼
[本文作成] ──→ {sections[]} を保存 (h2ごとに並列可)
       │
       ▼
[まとめ作成] ──→ {summary} を保存
       │
       ▼
[画像生成] ──→ {images[]} を保存 (設定に基づき生成)
       │
       ▼
[Google Docs組み立て] ──→ 完成ドキュメントURL出力
```

---

## 7. 設定ファイル構造

### 7.1 プロジェクト設定 (config.yaml)
```yaml
project:
  name: "ai-writing-automation"
  version: "0.1.0"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.7

image:
  default_provider: "dalle"
  providers:
    dalle:
      enabled: true
      model: "dall-e-3"
    gemini:
      enabled: true
    midjourney:
      enabled: false
    canva:
      enabled: false

google_docs:
  template_folder: "./templates"
  output_folder_id: "YOUR_GOOGLE_DRIVE_FOLDER_ID"

prompts:
  folder: "./prompts"
```

### 7.2 クライアント別設定 (clients/client_a.yaml)
```yaml
client:
  name: "クライアントA"
  
content:
  type: "blog"  # blog | youtube | yukkuri
  
image_insertion:
  after_h2: true
  after_lead: true
  before_summary: false
  custom_positions:
    - after: "h2:3"  # 3つ目のh2の後
    
template:
  name: "client_a_template"
  
tone:
  formality: "casual"  # casual | formal
  target_age: "30s"
```

---

## 8. 成果物一覧

| 成果物 | 説明 |
|--------|------|
| `ai_writing/` | メインパッケージ |
| `ai_writing/pipeline/` | 生成パイプライン |
| `ai_writing/services/` | 外部API連携 |
| `ai_writing/templates/` | Jinja2テンプレート |
| `prompts/` | プロンプトテンプレート（YAML） |
| `clients/` | クライアント別設定 |
| `cli.py` | CLIエントリーポイント |
| `tests/` | テストコード |

---

## 9. 制約・前提条件

### 9.1 前提
- OpenAI API キーを保有
- Google Cloud プロジェクト作成済み（Docs API有効化）
- Python 3.11+ 環境

### 9.2 制約
- ラッコキーワードは手動CSV取得（API非公開）
- Midjourney APIは非公式のため不安定の可能性

---

## 10. 用語集

| 用語 | 説明 |
|------|------|
| ペルソナ | 想定読者のプロフィール（年齢、職業、悩みなど） |
| 顕在ニーズ | ユーザーが明確に認識している欲求 |
| 潜在ニーズ | ユーザーが言語化していない深層の欲求 |
| PREP法 | Point-Reason-Example-Point の文章構成法 |
| h2/h3 | HTML見出しタグ。記事の大見出し/小見出し |
