# AI ライティング自動化システム - ロードマップ

## フェーズ概要

| Phase | 名称 | 期間目安 | 成果物 |
|-------|------|---------|--------|
| **Phase 0** | 環境構築 | 1日 | ✅ 完了 | リポジトリ、開発環境、認証設定 |
| **Phase 1** | コア機能 | 3-4日 | ✅ 完了 | ブログ生成パイプライン（テキストのみ） |
| **Phase 2** | 画像生成 | 2-3日 | ✅ 完了 | DALL-E/Gemini連携、画像挿入 |
| **Phase 3** | Google Docs出力 | 2日 | ✅ 完了 | テンプレート、自動ドキュメント生成 |
| **Phase 4** | YouTube/ゆっくり対応 | 2日 | ✅ 完了 | 台本生成パイプライン |
| **Phase 5** | 拡張・最適化 | 継続 | ✅ 完了 | Midjourney/Canva、UI、履歴管理 |
| **Phase 6** | UI/UX改善 | - | ✅ 完了 | Rich対応、プログレスバー、エラーメッセージ強化 |
| **Phase 7** | 履歴管理機能 | - | ✅ 完了 | SQLiteデータベース、履歴保存・検索・バージョン管理 |
| **Phase 8** | パフォーマンス最適化 | - | ✅ 完了 | LLMキャッシュ、並列処理、ストリーミング、メモリ最適化、レートリミット |
| **Phase 9** | エコシステム拡張 | - | ✅ 完了 | Midjourney・Canva完全実装、フォールバック戦略 |

---

## Phase 0: 環境構築

### 目標
- GitHubリポジトリ作成
- Python環境セットアップ
- 外部サービス認証設定

### タスク

#### P0-1: リポジトリ作成
- [x] GitHub リポジトリ `ai-writing-automation` 作成
- [x] README.md 初期化
- [x] .gitignore 設定（Python用）
- [x] LICENSE 設定（MIT推奨）

#### P0-2: プロジェクト初期化
- [x] pyproject.toml 作成
- [x] 依存関係定義
- [x] src/ai_writing パッケージ構造作成
- [x] .env.example 作成

#### P0-3: 外部サービス設定
- [x] OpenAI API キー設定・動作確認
- [x] Google Cloud プロジェクト作成
- [x] Google Docs API 有効化
- [x] OAuth2認証フロー実装
- [x] Gemini API キー設定（オプション）

#### P0-4: 開発環境
- [x] pytest 設定
- [x] pre-commit hooks 設定（black, ruff）
- [x] CI/CD 基盤（GitHub Actions）

---

## Phase 1: コア機能（ブログ生成パイプライン）

### 目標
- キーワード入力 → テキスト記事生成までを完成
- CLI で実行可能

### タスク

#### P1-1: 基盤実装
- [x] core/config.py - 設定管理
- [x] core/context.py - 生成コンテキスト
- [x] core/exceptions.py - カスタム例外
- [x] utils/prompt_loader.py - プロンプト読み込み

#### P1-2: LLMサービス実装
- [x] services/llm/base.py - 基底クラス
- [x] services/llm/openai.py - OpenAI実装
- [x] リトライ機構実装
- [x] ユニットテスト

#### P1-3: パイプライン基盤
- [x] pipeline/base.py - パイプライン基底クラス
- [x] stages/base.py - ステージ基底クラス

#### P1-4: ブログ生成ステージ実装
- [x] stages/search_intent.py - 検索意図調査
- [x] stages/structure.py - 構成作成
- [x] stages/title.py - タイトル作成
- [x] stages/lead.py - リード文作成
- [x] stages/body.py - 本文作成
- [x] stages/summary.py - まとめ文作成

#### P1-5: プロンプトテンプレート作成
- [x] prompts/blog/01_search_intent.yaml
- [x] prompts/blog/02_structure.yaml
- [x] prompts/blog/03_title.yaml
- [x] prompts/blog/04_lead.yaml
- [x] prompts/blog/05_body.yaml
- [x] prompts/blog/06_summary.yaml

#### P1-6: ブログパイプライン統合
- [x] pipeline/blog.py - ブログパイプライン
- [x] 統合テスト
- [x] CLI 基本実装 (cli.py)

---

## Phase 2: 画像生成

### 目標
- 記事に適した画像を自動生成
- 画像挿入ルールのカスタマイズ機能

### タスク

#### P2-1: 画像生成基盤
- [x] services/image/base.py - 基底クラス・ファクトリ
- [x] 画像保存・キャッシュ機構

#### P2-2: DALL-E実装
- [x] services/image/dalle.py
- [x] 画像生成プロンプト自動作成
- [x] テスト

#### P2-3: Gemini実装
- [x] services/image/gemini.py
- [x] テスト

#### P2-4: 画像挿入ルール
- [x] 設定ファイルで挿入位置を制御
- [x] クライアント別設定対応
- [x] stages/image_generation.py

---

## Phase 3: Google Docs出力

### 目標
- 生成したコンテンツをGoogle Docsに自動組み立て
- テンプレートによる差し込み機能

### タスク

#### P3-1: Google Docs サービス
- [x] services/google/docs.py
- [x] ドキュメント作成
- [x] テキスト挿入
- [x] 画像挿入
- [x] スタイル適用（見出し等）

#### P3-2: テンプレートエンジン
- [x] templates/engine.py - Jinja2ラッパー
- [x] templates/renderer.py - ドキュメントレンダラー
- [x] 差し込み変数定義

#### P3-3: テンプレート作成
- [x] templates/blog_default.json
- [x] クライアント別テンプレート対応

#### P3-4: 統合
- [x] パイプラインにGoogle Docs出力を統合
- [x] E2Eテスト

---

## Phase 4: YouTube/ゆっくり対応

### 目標
- YouTube台本生成パイプライン
- ゆっくり解説台本（霊夢・魔理沙形式）

### タスク

#### P4-1: YouTube台本
- [x] prompts/youtube/*.yaml 作成
- [x] stages/intro_ending.py
- [x] pipeline/youtube.py
- [x] テスト

#### P4-2: ゆっくり台本
- [x] prompts/yukkuri/*.yaml 作成
- [x] pipeline/yukkuri.py
- [x] キャラクター口調の検証・調整

#### P4-3: 統合
- [x] CLI に content-type オプション追加
- [x] Google Docs テンプレート追加

---

## Phase 6: UI/UX改善

### 目標
- Richライブラリを使用したCLIの視覚的改善
- プログレスバーの実装
- エラーメッセージの強化

### タスク

#### P6-1: Richライブラリ導入
- [x] Richライブラリのインストール・設定
- [x] カラフルな出力表示

#### P6-2: プログレスバー
- [x] 各ステージの進捗表示
- [x] 全体の進捗表示

#### P6-3: エラーメッセージ強化
- [x] 解決策を含むエラーメッセージ
- [x] 詳細なエラーログ

#### P6-4: CLI改善
- [x] コマンド補完機能
- [x] 使用例の表示

---

## Phase 7: 履歴管理機能

### 目標
- SQLiteデータベースによる履歴管理
- 生成履歴の保存・検索・バージョン管理

### タスク

#### P7-1: データベース層
- [x] core/database.py - データベースアクセス層
- [x] テーブル定義・マイグレーション

#### P7-2: 履歴管理サービス
- [x] core/history_manager.py - 履歴管理サービス
- [x] 生成履歴の保存・検索・バージョン管理

#### P7-3: CLIコマンド
- [x] history CLIコマンドの実装
- [x] 履歴一覧、検索、詳細表示、統計情報

---

## Phase 8: パフォーマンス最適化

### 目標
- LLMキャッシュ、並列処理、ストリーミング、メモリ最適化、レートリミット対応

### タスク

#### P8-1: LLMキャッシュ
- [x] services/llm/cache.py - TTL付き永続キャッシュ
- [x] ディスクキャッシュの実装

#### P8-2: 並列処理
- [x] utils/parallel.py - asyncioによる並列実行
- [x] タイトル・本文・画像の並列生成

#### P8-3: ストリーミング
- [x] utils/streaming.py - OpenAIストリーミング対応
- [x] リアルタイム出力の実装

#### P8-4: メモリ最適化
- [x] utils/memory.py - チャンキング・メモリ監視
- [x] メモリ効率の改善

#### P8-5: レートリミット
- [x] services/llm/retry.py - tenacityによる指数バックオフ
- [x] APIレートリミット対応

#### P8-6: CLIコマンド
- [x] perf CLIコマンドの実装
- [x] パフォーマンス統計の表示・クリア

---

## Phase 9: エコシステム拡張

### 目標
- Midjourney・Canva完全実装、フォールバック戦略

### タスク

#### P9-1: Midjourney実装
- [x] services/image/midjourney.py - Discord API経由で画像生成
- [x] ポーリングによる進捗監視
- [x] プロンプトエンハンスメント

#### P9-2: Canva実装
- [x] services/image/canva.py - Canva Designs API実装
- [x] テンプレート管理
- [x] デザインのエクスポート機能

#### P9-3: フォールバック戦略
- [x] services/image/fallback.py - 複数のプロバイダー間で自動フォールバック
- [x] 重み付けフォールバック戦略の実装

#### P9-4: 設定ファイルの拡張
- [x] Midjourney/Canva設定項目を追加
- [x] Discord/Canva環境変数の追加

---

## Phase 10: 将来の拡張（実装中）

### 目標
- Web UI、分析機能、自動化の強化

### タスク

#### P10-1: Web UI
- [x] Web UI 検討（FastAPI + Next.js 14）
- [x] ダッシュボードの実装
- [x] リアルタイム進捗表示
- [ ] ブラウザ上の記事編集機能

#### P10-2: 分析機能
- [ ] 記事パフォーマンス分析
- [x] SEOスコア計算
- [x] コンテンツ品質評価
- [ ] トレンド分析

#### P10-3: 自動化
- [x] 定期生成のスケジューリング
- [x] 複数キーワードの一括生成
- [ ] キーワードの自動提案
- [ ] 記事の自動更新機能

---

## Phase 11: データ活用（計画中）

### 目標
- ユーザーデータの活用、パーソナライズ、A/Bテスト

### タスク

#### P11-1: データ分析
- [ ] ユーザー行動分析
- [ ] 成功記事のパターン抽出
- [ ] コンテンツパフォーマンスの追跡

#### P11-2: パーソナライズ
- [ ] ユーザー別設定の最適化
- [ ] クライアント別の推奨設定
- [ ] 自動調整機能

#### P11-3: A/Bテスト
- [ ] タイトルのA/Bテスト
- [ ] 構成のA/Bテスト
- [ ] 画像のA/Bテスト
- [ ] 結果の自動分析

---

## Phase 12: エコシステム統合（計画中）

### 目標
- 外部サービスとの連携、プラグインシステム

### タスク

#### P12-1: 外部サービス連携
- [ ] WordPress連携
- [ ] Notion連携
- [ ] Slack通知
- [ ] Google Analytics連携

#### P12-2: プラグインシステム
- [ ] プラグインAPIの設計
- [ ] カスタムステージの開発
- [ ] コミュニティプラグインのサポート

#### P12-3: API公開
- [ ] RESTful APIの実装
- [ ] APIドキュメントの作成
- [ ] SDKの開発

---

## Phase 5: 拡張・最適化

### 目標
- 追加の画像生成サービス
- ユーザビリティ向上
- パフォーマンス最適化

### タスク

#### P5-1: 追加画像サービス
- [x] services/image/midjourney.py
- [x] services/image/canva.py

#### P5-2: UI（将来）
- [ ] Web UI 検討（Streamlit or FastAPI + React）

#### P5-3: 履歴・バージョン管理
- [x] 生成履歴のDB保存
- [x] 過去生成の再利用

#### P5-4: パフォーマンス
- [x] 並列生成（複数h2の同時生成）
- [x] キャッシュ機構強化

---

## GitHub Issues 構造

```
ai-writing-automation/
├── Milestone: Phase 0 - 環境構築
│   ├── Issue #1: リポジトリ初期化
│   ├── Issue #2: Python環境セットアップ
│   ├── Issue #3: OpenAI API連携
│   └── Issue #4: Google Cloud設定
│
├── Milestone: Phase 1 - コア機能
│   ├── Issue #5: 設定管理システム
│   ├── Issue #6: LLMサービス実装
│   ├── Issue #7: パイプライン基盤
│   ├── Issue #8: ブログ生成ステージ
│   ├── Issue #9: プロンプトテンプレート
│   └── Issue #10: CLI実装
│
├── Milestone: Phase 2 - 画像生成
│   ├── Issue #11: 画像生成基盤
│   ├── Issue #12: DALL-E連携
│   ├── Issue #13: Gemini連携
│   └── Issue #14: 画像挿入ルール
│
├── Milestone: Phase 3 - Google Docs出力
│   ├── Issue #15: Google Docs API連携
│   ├── Issue #16: テンプレートエンジン
│   └── Issue #17: ドキュメント組み立て
│
├── Milestone: Phase 4 - YouTube/ゆっくり
│   ├── Issue #18: YouTube台本パイプライン
│   └── Issue #19: ゆっくり台本パイプライン
│
└── Milestone: Phase 5 - 拡張
    ├── Issue #20: Midjourney連携
    ├── Issue #21: Canva連携
    └── Issue #22: Web UI
```

---

## 優先度マトリクス

| タスク | 重要度 | 緊急度 | 優先度 | 状況 |
|--------|--------|--------|--------|--------|
| P0: 環境構築 | 高 | 高 | **P0** | ✅ 完了 |
| P1: ブログ生成 | 高 | 高 | **P0** | ✅ 完了 |
| P2: 画像生成(DALL-E/Gemini) | 高 | 中 | **P1** | ✅ 完了 |
| P3: Google Docs出力 | 高 | 中 | **P1** | ✅ 完了 |
| P4: YouTube/ゆっくり | 中 | 低 | **P2** | ✅ 完了 |
| P5: Midjourney/Canva | 低 | 低 | **P3** | ✅ 完了 |
| P6: UI/UX改善 | 中 | 中 | **P2** | ✅ 完了 |
| P7: 履歴管理 | 中 | 中 | **P2** | ✅ 完了 |
| P8: パフォーマンス | 中 | 中 | **P2** | ✅ 完了 |
| P9: エコシステム拡張 | 低 | 低 | **P3** | ✅ 完了 |
| P10: Web UI | 中 | 低 | **P2** | 🟡 計画中 |
| P10: 分析機能 | 中 | 低 | **P2** | 🟡 計画中 |
| P10: 自動化 | 中 | 低 | **P2** | 🟡 計画中 |
| P11: データ活用 | 低 | 低 | **P3** | 🟡 計画中 |
| P12: エコシステム統合 | 低 | 低 | **P3** | 🟡 計画中 |

---

## 次のアクション

1. **完了**: Phase 0-9 完了 ✅
2. **進行中**: Phase 10 計画策定 🟡
3. **次**: Phase 10-1: Web UI 開発
4. **リリース**: v0.3.0 リリース準備（本日）
