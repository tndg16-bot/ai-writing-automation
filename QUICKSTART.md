# Quick Start Guide - 5分で始めるAIライティング自動化

**最短でツールを使い始めるためのガイド**

---

## 🚀 5分クイックスタート

### 前提条件（1分で確認）

以下が揃っていることを確認してください：

| 必須項目 | チェック |
|---------|---------|
| Python 3.11+ | ✅ `python --version` で確認 |
| Git | ✅ `git --version` で確認 |
| OpenAI API Key | ✅ [OpenAI Platform](https://platform.openai.com/) で取得 |

### ステップ1: ツールのダウンロード（30秒）

```bash
# リポジトリをクローン
git clone https://github.com/tndg16-bot/ai-writing-automation.git
cd ai-writing-automation
```

### ステップ2: 仮想環境の作成と有効化（1分）

```bash
# 仮想環境作成
python -m venv .venv

# 仮想環境有効化（Windows）
.venv\Scripts\activate

# 仮想環境有効化（Mac/Linux）
source .venv/bin/activate
```

成功すると、プロンプトの先頭に `(.venv)` と表示されます。

### ステップ3: 依存関係のインストール（2分）

```bash
pip install -e ".[dev]"
```

「Successfully installed ...」と表示されればOK！

### ステップ4: APIキーの設定（30秒）

```bash
# 環境変数ファイルのコピー
copy .env.example .env
```

`.env` ファイルを開いて、以下の行を編集：

```ini
# 必須: OpenAI APIキー
OPENAI_API_KEY=sk-ここにあなたのAPIキーを貼り付け
```

### ステップ5: 実行！（10秒）

```bash
# ブログ記事を生成
python -m ai_writing generate "AI副業" --content-type blog

# YouTube台本を生成
python -m ai_writing generate "犬の飼い方" --content-type youtube
```

生成されたファイルは `output` フォルダに保存されます。

---

## ✅ セットアップ完了チェック

以下のコマンドで、セットアップが正しくできているか確認できます：

```bash
python -m ai_writing --help
```

ヘルプが表示されれば、セットアップ完了です！

---

## 📖 次に読むべきドキュメント

- [完全ガイド](docs/COMPLETE_GUIDE.md) - 包括的な使い方と運用フロー
- [初心者ガイド](docs/BEGINNERS_GUIDE.md) - AI・SEO・ライティングの基礎知識
- [利用マニュアル](MANUAL.md) - 詳細な使い方

---

## 🆘 もしエラーが出たら

| エラー | 解決方法 |
|--------|---------|
| `'python' は認識されていません` | Pythonを再インストールし、「Add Python to PATH」にチェック |
| APIキーエラー | `.env` ファイルに正しいAPIキーが設定されているか確認 |
| `Rate limit exceeded` | 数分待ってから再実行 |

詳細なトラブルシューティングは[完全ガイド](docs/COMPLETE_GUIDE.md#12-トラブルシューティングよくある質問)を参照してください。

---

## 💡 基本的な使い方

### ブログ記事生成

```bash
python -m ai_writing generate "キーワード" --content-type blog
```

例:
```bash
python -m ai_writing generate "AI副業 初心者" --content-type blog
```

### YouTube台本生成

```bash
python -m ai_writing generate "キーワード" --content-type youtube
```

例:
```bash
python -m ai_writing generate "ChatGPT 使い方" --content-type youtube
```

### ゆっくり動画台本生成

```bash
python -m ai_writing generate "キーワード" --content-type yukkuri
```

例:
```bash
python -m ai_writing generate "副業 コツ" --content-type yukkuri
```

---

## 🎯 コマンドオプション

| オプション | 説明 | 例 |
|-----------|------|-----|
| `--content-type` | コンテンツタイプを指定 | `blog`, `youtube`, `yukkuri` |
| `--client` | クライアント設定を指定 | `default`, `client_a` |
| `--output` | 出力先を指定 | `./output` |

例:
```bash
python -m ai_writing generate "投資信託" --content-type blog --client default
```

---

## 📊 生成されるコンテンツ

| コンテンツタイプ | 主な出力ファイル |
|----------------|----------------|
| ブログ記事 | Markdown形式の記事 |
| YouTube台本 | 視聴者を引きつける台本（フック含む） |
| ゆっくり台本 | 霊夢・魔理沙の掛け合い形式台本 |

---

## 🎓 この後の学習

1. **基本的な使い方を把握** - このクイックスタートで完了 ✅
2. **詳細な使い方を学ぶ** - [完全ガイド](docs/COMPLETE_GUIDE.md)を読む
3. **AI・SEOの基礎を理解する** - [初心者ガイド](docs/BEGINNERS_GUIDE.md)を読む
4. **運用フローを学ぶ** - 第10章「全体の運用フロー詳細」を参照
5. **実践で学ぶ** - 実際に記事を生成し、編集・公開してみる

---

## 🤝 コミュニティ

- **GitHub Issues**: https://github.com/tndg16-bot/ai-writing-automation/issues
- **ドキュメント**: [docs/](./docs/) フォルダ

---

**Happy Writing! ✨**
