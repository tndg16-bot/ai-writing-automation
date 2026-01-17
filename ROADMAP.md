# AI ライティング自動化システム - ロードマップ

## フェーズ概要

| Phase | 名称 | 期間目安 | 成果物 |
|-------|------|---------|--------|
| **Phase 0** | 環境構築 | 1日 | リポジトリ、開発環境、認証設定 |
| **Phase 1** | コア機能 | 3-4日 | ブログ生成パイプライン（テキストのみ） |
| **Phase 2** | 画像生成 | 2-3日 | DALL-E/Gemini連携、画像挿入 |
| **Phase 3** | Google Docs出力 | 2日 | テンプレート、自動ドキュメント生成 |
| **Phase 4** | YouTube/ゆっくり対応 | 2日 | 台本生成パイプライン |
| **Phase 5** | 拡張・最適化 | 継続 | Midjourney/Canva、UI、履歴管理 |

---

## Phase 0: 環境構築

### 目標
- GitHubリポジトリ作成
- Python環境セットアップ
- 外部サービス認証設定

### タスク

#### P0-1: リポジトリ作成
- [ ] GitHub リポジトリ `ai-writing-automation` 作成
- [ ] README.md 初期化
- [ ] .gitignore 設定（Python用）
- [ ] LICENSE 設定（MIT推奨）

#### P0-2: プロジェクト初期化
- [ ] pyproject.toml 作成
- [ ] 依存関係定義
- [ ] src/ai_writing パッケージ構造作成
- [ ] .env.example 作成

#### P0-3: 外部サービス設定
- [ ] OpenAI API キー設定・動作確認
- [ ] Google Cloud プロジェクト作成
- [ ] Google Docs API 有効化
- [ ] OAuth2認証フロー実装
- [ ] Gemini API キー設定（オプション）

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
- [ ] core/config.py - 設定管理
- [ ] core/context.py - 生成コンテキスト
- [ ] core/exceptions.py - カスタム例外
- [ ] utils/prompt_loader.py - プロンプト読み込み

#### P1-2: LLMサービス実装
- [ ] services/llm/base.py - 基底クラス
- [ ] services/llm/openai.py - OpenAI実装
- [ ] リトライ機構実装
- [ ] ユニットテスト

#### P1-3: パイプライン基盤
- [ ] pipeline/base.py - パイプライン基底クラス
- [ ] stages/base.py - ステージ基底クラス

#### P1-4: ブログ生成ステージ実装
- [ ] stages/search_intent.py - 検索意図調査
- [ ] stages/structure.py - 構成作成
- [ ] stages/title.py - タイトル作成
- [ ] stages/lead.py - リード文作成
- [ ] stages/body.py - 本文作成
- [ ] stages/summary.py - まとめ文作成

#### P1-5: プロンプトテンプレート作成
- [ ] prompts/blog/01_search_intent.yaml
- [ ] prompts/blog/02_structure.yaml
- [ ] prompts/blog/03_title.yaml
- [ ] prompts/blog/04_lead.yaml
- [ ] prompts/blog/05_body.yaml
- [ ] prompts/blog/06_summary.yaml

#### P1-6: ブログパイプライン統合
- [ ] pipeline/blog.py - ブログパイプライン
- [ ] 統合テスト
- [ ] CLI 基本実装 (cli.py)

---

## Phase 2: 画像生成

### 目標
- 記事に適した画像を自動生成
- 画像挿入ルールのカスタマイズ機能

### タスク

#### P2-1: 画像生成基盤
- [ ] services/image/base.py - 基底クラス・ファクトリ
- [ ] 画像保存・キャッシュ機構

#### P2-2: DALL-E実装
- [ ] services/image/dalle.py
- [ ] 画像生成プロンプト自動作成
- [ ] テスト

#### P2-3: Gemini実装
- [ ] services/image/gemini.py
- [ ] テスト

#### P2-4: 画像挿入ルール
- [ ] 設定ファイルで挿入位置を制御
- [ ] クライアント別設定対応
- [ ] stages/image_generation.py

---

## Phase 3: Google Docs出力

### 目標
- 生成したコンテンツをGoogle Docsに自動組み立て
- テンプレートによる差し込み機能

### タスク

#### P3-1: Google Docs サービス
- [ ] services/google/docs.py
- [ ] ドキュメント作成
- [ ] テキスト挿入
- [ ] 画像挿入
- [ ] スタイル適用（見出し等）

#### P3-2: テンプレートエンジン
- [ ] templates/engine.py - Jinja2ラッパー
- [ ] templates/renderer.py - ドキュメントレンダラー
- [ ] 差し込み変数定義

#### P3-3: テンプレート作成
- [ ] templates/blog_default.json
- [ ] クライアント別テンプレート対応

#### P3-4: 統合
- [ ] パイプラインにGoogle Docs出力を統合
- [ ] E2Eテスト

---

## Phase 4: YouTube/ゆっくり対応

### 目標
- YouTube台本生成パイプライン
- ゆっくり解説台本（霊夢・魔理沙形式）

### タスク

#### P4-1: YouTube台本
- [ ] prompts/youtube/*.yaml 作成
- [ ] stages/intro_ending.py
- [ ] pipeline/youtube.py
- [ ] テスト

#### P4-2: ゆっくり台本
- [ ] prompts/yukkuri/*.yaml 作成
- [ ] pipeline/yukkuri.py
- [ ] キャラクター口調の検証・調整

#### P4-3: 統合
- [ ] CLI に content-type オプション追加
- [ ] Google Docs テンプレート追加

---

## Phase 5: 拡張・最適化

### 目標
- 追加の画像生成サービス
- ユーザビリティ向上
- パフォーマンス最適化

### タスク

#### P5-1: 追加画像サービス
- [ ] services/image/midjourney.py
- [ ] services/image/canva.py

#### P5-2: UI（将来）
- [ ] Web UI 検討（Streamlit or FastAPI + React）

#### P5-3: 履歴・バージョン管理
- [ ] 生成履歴のDB保存
- [ ] 過去生成の再利用

#### P5-4: パフォーマンス
- [ ] 並列生成（複数h2の同時生成）
- [ ] キャッシュ機構強化

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

| タスク | 重要度 | 緊急度 | 優先度 |
|--------|--------|--------|--------|
| P0: 環境構築 | 高 | 高 | **P0** |
| P1: ブログ生成 | 高 | 高 | **P0** |
| P2: 画像生成(DALL-E/Gemini) | 高 | 中 | **P1** |
| P3: Google Docs出力 | 高 | 中 | **P1** |
| P4: YouTube/ゆっくり | 中 | 低 | **P2** |
| P5: Midjourney/Canva | 低 | 低 | **P3** |
| P5: Web UI | 低 | 低 | **P3** |

---

## 次のアクション

1. **✅ 完了**: GitHub リポジトリ作成
2. **✅ 完了**: Phase 0 完了
3. **✅ 完了**: Phase 1 完了（ブログ生成MVP）
4. **✅ 完了**: Phase 2 完了（画像生成）
5. **✅ 完了**: Phase 3 完了（Google Docs出力）
6. **✅ 完了**: Phase 4 完了（YouTube/ゆっくり対応）
7. **🔄 進行中**: Phase 5 完了（拡張・最適化）
   - [x] Midjourney連携
   - [x] Canva連携
   - [x] 履歴・バージョン管理
   - [ ] Web UI実装（将来）
   - [ ] 並列生成実装（将来）
