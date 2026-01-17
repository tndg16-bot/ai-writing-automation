# AI Writing Automation - 意思決定リスト & タスク

> 最終更新: 2026-01-12

---

## ✅ 完了した意思決定

### 2026-01-17: GitHubへのプッシュ
- **決定**: プッシュする
- **実行内容**: `git push origin feat/add-ollama-support`
- **結果**: ✅ 成功
- **URL**: https://github.com/tndg16-bot/ai-writing-automation/tree/feat/add-ollama-support

### 2026-01-18: 残タスクの実行
- **決定**: 並列実行ですべての残タスクを実行
- **実行内容**:
  - パッケージインストール: `pip install -e ".[dev]"`
  - `.env.example`にOllama設定を追加
  - GitHub Actions CI/CD設定ファイルを作成
  - pre-commit hooks設定ファイルを作成
  - テスト実行: `pytest tests/ -v` (149/149成功)
  - Pydanticの非推奨警告を修正
- **結果**: ✅ すべて成功
- **URL**: https://github.com/tndg16-bot/ai-writing-automation/commit/92ff37f

---

## ✅ 完了した意思決定

### 2026-01-12: Ollamaモデルの選択
- **決定**: Qwen2.5:7b を使用
- **理由**: JSON出力に対応、日本語も良好

---

## 📋 タスクリスト

### 進行中
- [ ] 生成された記事 `output/ai-fukugyo.md` の品質確認
- [ ] Google Docs認証の設定（DocsOutputStageを有効化する場合）

### 完了
- [x] Ollama対応の実装
- [x] 構成パーサーの改善（複数フォーマット対応）
- [x] MANUAL.md の作成
- [x] テスト記事の生成成功

### 未着手（今後の予定）
- [ ] YouTube台本生成のテスト
- [ ] ゆっくり台本生成のテスト
- [ ] 画像生成機能のテスト
- [ ] OpenAI APIでの品質比較テスト

---

## 📌 メモ

- ローカルLLM（Ollama）での生成は時間がかかる（1記事30分〜1時間程度）
- 高品質・高速を求める場合はOpenAI APIの利用を推奨
- 現在のブランチ: `feat/add-ollama-support`
