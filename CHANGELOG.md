# Changelog

このプロジェクトのバージョン履歴と変更点を記録します。

---

## [Unreleased]

### 追加予定
- Midjourney 連携
- Canva 連携
- Web UI (Streamlit or FastAPI + React)
- 履歴管理機能
- WordPress直接投稿

---

## [0.2.0] - 2025-01-18

### 追加
- **第10章: 全体の運用フロー詳細** - 週間スケジュール、ブログ生成フロー、YouTube生成フロー、マルチプラットフォーム活用、収益化ロードマップ
- **第11章: YouTube台本生成の拡充** - 一人語り・ゆっくり動画、ワークフロー、カスタマイズ、収益化、チャンネル運営
- **プロジェクトサマリー** - 一目でわかる全体像
- **クイックスタートガイド** - 5分で使える最小限の手順

### 改善
- 完全ガイドを2,675行に拡張（Mermaid図表7本追加）
- 第10章と第11章を大幅に拡充
- 目次の説明を更新

### 文書化
- COMPLETE_GUIDE.md: 2,250行 → 2,675行
- BEGINNERS_GUIDE.md: 721行
- MANUAL.md: 111行
- PROJECT_SUMMARY.md: 新規作成
- QUICKSTART.md: 新規作成

---

## [0.1.0] - 2025-01-17

### 追加
- **Phase 0: 環境構築**
  - GitHubリポジトリ作成
  - Python環境セットアップ
  - 外部サービス認証設定
  - 開発環境構築（pytest, pre-commit, CI/CD）

- **Phase 1: コア機能（ブログ生成）**
  - core/config.py - 設定管理
  - core/context.py - 生成コンテキスト
  - core/exceptions.py - カスタム例外
  - utils/prompt_loader.py - プロンプト読み込み
  - services/llm/base.py - LLM基底クラス
  - services/llm/openai.py - OpenAI実装
  - pipeline/base.py - パイプライン基底クラス
  - pipeline/blog.py - ブログパイプライン
  - stages/search_intent.py - 検索意図調査
  - stages/structure.py - 構成作成
  - stages/title.py - タイトル作成
  - stages/lead.py - リード文作成
  - stages/body.py - 本文作成
  - stages/summary.py - まとめ文作成
  - prompts/blog/*.yaml - ブログ用プロンプトテンプレート（6つ）

- **Phase 2: 画像生成**
  - services/image/base.py - 画像生成基底クラス
  - services/image/dalle.py - DALL-E実装
  - services/image/gemini.py - Gemini実装
  - stages/image_generation.py - 画像生成ステージ

- **Phase 3: Google Docs出力**
  - services/google/docs.py - Google Docs API操作
  - templates/engine.py - テンプレートエンジン
  - templates/renderer.py - ドキュメントレンダラー
  - stages/docs_output.py - Google Docs出力ステージ

- **Phase 4: YouTube/ゆっくり対応**
  - pipeline/youtube.py - YouTubeパイプライン
  - pipeline/yukkuri.py - ゆっくりパイプライン
  - stages/intro_ending.py - 冒頭・エンディング作成
  - stages/youtube_body.py - YouTube本文作成
  - stages/yukkuri_script.py - ゆっくり台本作成
  - prompts/youtube/*.yaml - YouTube用プロンプトテンプレート（4つ）
  - prompts/yukkuri/*.yaml - ゆっくり用プロンプトテンプレート（3つ）

- **Phase 5: 拡張・最適化**
  - services/image/midjourney.py - Midjourney実装（予定）
  - services/image/canva.py - Canva実装（予定）
  - services/history/models.py - 履歴管理モデル
  - services/history/service.py - 履歴管理サービス

- **ドキュメント**
  - README.md - プロジェクト概要
  - REQUIREMENTS.md - 要件定義書
  - ARCHITECTURE.md - アーキテクチャ設計書
  - ROADMAP.md - 開発ロードマップ
  - MANUAL.md - 利用マニュアル
  - COMPLETE_GUIDE.md - 完全ガイド（2,250行）
  - BEGINNERS_GUIDE.md - 初心者ガイド（721行）

- **CLI**
  - cli.py - コマンドラインインターフェース
  - `generate` コマンド - コンテンツ生成
  - `list-clients` コマンド - クライアント設定一覧
  - `validate-config` コマンド - 設定ファイル検証

### 改善
- リトライ機構の実装
- エラーハンドリングの強化
- 設定管理の柔軟性向上
- プロンプトテンプレートの外部ファイル管理

### テスト
- tests/test_pipeline/ - パイプラインテスト
- tests/test_services/ - サービステスト
- tests/test_stages/ - ステージテスト
- tests/test_templates/ - テンプレートテスト
- pytest設定とasyncio対応

### 依存関係
- openai >= 1.0.0
- google-api-python-client >= 2.100.0
- pydantic >= 2.0.0
- jinja2 >= 3.1.0
- httpx >= 0.25.0
- rich >= 13.0.0
- typer >= 0.9.0
- pyyaml >= 6.0.0
- tenacity >= 8.2.0
- python-dotenv >= 1.0.0
- google-generativeai >= 0.5.0
- diskcache >= 5.6.0
- pillow >= 10.0.0
- aiofiles >= 23.0.0

---

## [0.0.1] - 2025-01-12

### 追加
- 初期プロジェクトセットアップ
- 要件定義書（REQUIREMENTS.md）
- アーキテクチャ設計書（ARCHITECTURE.md）
- 開発ロードマップ（ROADMAP.md）
- pyproject.toml 設定

### 変更
- なし

### 削除
- なし

---

## バージョン管理ポリシー

このプロジェクトは[セマンティックバージョニング](https://semver.org/)に従います：

- **MAJOR** - 後方互換性のない変更
- **MINOR** - 後方互換性のある機能追加
- **PATCH** - 後方互換性のあるバグ修正

---

## 変更タイプ

| タイプ | 説明 |
|-------|------|
| `追加` | 新機能の追加 |
| `変更` | 既存機能の変更（後方互換性あり） |
| `削除` | 機能の削除（後方互換性なし） |
| `修正` | バグ修正 |
| `改善` | パフォーマンスや使い勝手の向上 |
| `文書化` | ドキュメントの追加・更新 |
| `テスト` | テストの追加・更新 |
| `依存関係` | 外部ライブラリの変更 |

---

[Unreleased]: https://github.com/tndg16-bot/ai-writing-automation/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/tndg16-bot/ai-writing-automation/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/tndg16-bot/ai-writing-automation/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/tndg16-bot/ai-writing-automation/releases/tag/v0.0.1
