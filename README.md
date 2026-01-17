# AI Writing Automation

AIライティングノウハウの自動化システム - キーワードからGoogle Docs完成稿まで

## 概要

本山貴裕氏のAIライティングノウハウ（スプレッドシート）を自動化し、キーワード入力からGoogle Docs完成稿までをワンストップで生成するシステムです。

## 機能

- **ブログ記事生成**: 検索意図調査 → 構成 → タイトル → リード文 → 本文 → まとめ
- **YouTube台本生成**: 一人語り形式の台本自動生成
- **ゆっくり動画台本**: 霊夢・魔理沙の掛け合い形式
- **画像生成**: DALL-E / Gemini / Midjourney / Canva 連携
- **Google Docs出力**: テンプレートベースの自動ドキュメント生成

## セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/tndg16-bot/ai-writing-automation.git
cd ai-writing-automation

# 仮想環境作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係インストール
pip install -e ".[dev]"

# 環境変数設定
cp .env.example .env
# .env を編集してAPIキーを設定
```

## 使い方

```bash
# ブログ記事を生成
python -m ai_writing generate "AI副業" --content-type blog

# YouTube台本を生成
python -m ai_writing generate "犬の飼い方" --content-type youtube

# クライアント設定を指定
python -m ai_writing generate "投資信託" --client client_a
```

## ドキュメント

- [要件定義書](REQUIREMENTS.md)
- [アーキテクチャ設計書](ARCHITECTURE.md)
- [ロードマップ](ROADMAP.md)

## 開発状況

- [x] Phase 0: 環境構築 (100%)
- [x] Phase 1: コア機能（ブログ生成） (100%)
- [x] Phase 2: 画像生成 (100%)
- [x] Phase 3: Google Docs出力 (100%)
- [x] Phase 4: YouTube/ゆっくり対応 (100%)
- [ ] Phase 5: 拡張・最適化 (60%)

**全体進捗: 95%** ✅

## ライセンス

MIT License
