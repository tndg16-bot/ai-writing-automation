# Changelog

このプロジェクトのバージョン履歴と変更点を記録します。

---

## [Unreleased]

---

## [0.3.0] - 2025-01-18

### 追加

#### Phase 7: 履歴管理機能
- SQLiteデータベースによる履歴管理機能を追加
  - `core/database.py` - データベースアクセス層
  - `core/history_manager.py` - 履歴管理サービス
- 生成履歴の保存・検索・バージョン管理機能
- `history` CLIコマンドの実装
  - 履歴一覧、検索、詳細表示、統計情報

#### Phase 8: パフォーマンス最適化
- LLMレスポンスキャッシュの実装
  - `services/llm/cache.py` - TTL付き永続キャッシュ
- 並列処理の最適化
  - `utils/parallel.py` - asyncioによる並列実行
  - タイトル・本文・画像の並列生成
- ストリーミングレスポンスのサポート
  - `utils/streaming.py` - OpenAIストリーミング対応
- メモリ最適化
  - `utils/memory.py` - チャンキング・メモリ監視
- レートリミット対応
  - `services/llm/retry.py` - tenacityによる指数バックオフ
- `perf` CLIコマンドの実装
  - パフォーマンス統計の表示・クリア

#### Phase 9: エコシステム拡張
- Midjourney完全実装（Discord Bot + API）
  - `services/image/midjourney.py` - Discord API経由で画像生成
  - ポーリングによる進捗監視
  - プロンプトエンハンスメント
- Canva完全実装（API + テンプレート）
  - `services/image/canva.py` - Canva Designs API実装
  - テンプレート管理
  - デザインのエクスポート機能
- プロバイダーフォールバック戦略
  - `services/image/fallback.py` - 複数のプロバイダー間で自動フォールバック
  - 重み付けフォールバック戦略の実装
- 設定ファイルの拡張
  - Midjourney/Canva設定項目を追加
  - Discord/Canva環境変数の追加

#### その他
- ユーティリティファイルの更新
  - `utils/__init__.py` - 新規ユーティリティの追加
  - `services/image/__init__.py` - フォールバック機能の追加
  - `services/llm/__init__.py` - キャッシュ・リトライ機能の追加
- `.env.example` - 新規環境変数の追加
- `config.yaml` - データベース・キャッシュ・Midjourney/Canva設定を追加
- `pyproject.toml` - psutilライブラリの追加

#### ドキュメント
- 新規ドキュメントの追加
  - `PROJECT_PHASES.md` - プロジェクトフェーズの一覧
  - `PROJECT_SUMMARY.md` - プロジェクトサマリー
  - `QUICKSTART.md` - クイックスタートガイド
  - `MONETIZATION_TUTORIAL.md` - 収益化チュートリアル
  - `CHANGELOG.md` - バージョン履歴（更新）

### バグ修正
- CLIの絵文字表示をASCII文字に置換（Windows CP932対応）
- `cli.py` のエンコーディング問題を修正

---

## [0.2.0] - 2025-01-17

### 追加

#### Phase 6: UI/UX改善
- Richライブラリを使用したCLIの視覚的改善
- プログレスバーの実装
- カラフルな出力表示
- エラーメッセージの強化（解決策を含む）
- コマンド補完機能の実装
- 使用例の表示

#### バージョン
- バージョン: 0.1.0 → 0.2.0

---

## [0.1.0] - 2025-01-11

### 変更

- プロジェクトの初期構築
  - GitHubリポジトリの作成
  - Python環境セットアップ
  - 外部サービス認証設定（OpenAI, Google）
  - 開発環境の構築（pytest, pre-commit, CI/CD）

#### Phase 0: 環境構築
- [x] GitHubリポジトリ `ai-writing-automation` 作成
- [x] README.md 初期化
- [x] .gitignore 設定（Python用）
- [x] LICENSE 設定（MIT推奨）

#### Phase 0: Python環境セットアップ
- [x] pyproject.toml 作成
- [x] 依存関係定義
- [x] src/ai_writing パッケージ構造作成
- [x] .env.example 作成

#### Phase 0: 外部サービス認証設定
- [x] OpenAI API キー設定・動作確認
- [x] Google Cloud プロジェクト作成
- [x] Google Docs API 有効化
- [x] OAuth2認証フロー実装
- [x] Gemini API キー設定（オプション）

#### Phase 0: 開発環境構築
- [x] pytest 設定
- [x] pre-commit hooks 設定（black, ruff）
- [x] CI/CD 基盤（GitHub Actions）

---

## [0.0.0] - プロジェクト開始

### 変更
- プロジェクト開始
- README.md 作成
- ライセンス設定（MIT）
