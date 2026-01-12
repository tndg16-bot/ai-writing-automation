# AIライティング自動化システム 利用マニュアル

このドキュメントでは、AIライティング自動化システムのセットアップ方法から基本的な使い方までを解説します。
このツールを使うことで、キーワード選定から構成案作成、記事執筆、さらにはYouTube台本の作成までを自動化できます。

## 目次
1. [前提条件](#前提条件)
2. [事前準備（APIキー）](#事前準備apiキー)
3. [インストール手順](#インストール手順)
4. [設定](#設定)
5. [使い方](#使い方)
6. [よくある質問](#よくある質問)

---

## 1. 前提条件

このツールを使用するには、お使いのパソコンに以下のソフトウェアがインストールされている必要があります。

*   **Python (バージョン 3.11 以上)**
    *   [Python公式サイト](https://www.python.org/downloads/)からダウンロードしてインストールしてください。
    *   インストール時、「Add Python to PATH」にチェックを入れるのを忘れないでください。
*   **Git**
    *   [Git公式サイト](https://git-scm.com/downloads)からインストールしてください。

## 2. 事前準備（APIキー）

このシステムは複数のAIサービスやGoogleサービスを利用します。以下のAPIキーを取得し、手元に控えておいてください。

1.  **OpenAI API Key** (必須)
    *   ChatGPTを利用するために必要です。
    *   [OpenAI API](https://platform.openai.com/) から取得。
2.  **Google Gemini API Key** (画像生成などで使用)
    *   [Google AI Studio](https://makersuite.google.com/app/apikey) から取得。
3.  **Google Cloud Project credentials** (Google Docs出力用)
    *   Google Docsに自動書き込みを行う場合に必要です。
    *   `credentials.json` というファイルをダウンロードしておきます。

## 3. インストール手順

ターミナル（PowerShellやコマンドプロンプト）を開き、以下のコマンドを順番に実行してください。

### 手順1: リポジトリのダウンロード
```bash
git clone https://github.com/tndg16-bot/ai-writing-automation.git
cd ai-writing-automation
```

### 手順2: 仮想環境の作成
プロジェクト専用の部屋（仮想環境）を作ります。他への影響を防ぐためです。
```bash
python -m venv .venv
```

### 手順3: 仮想環境の有効化
Windowsの場合:
```bash
.venv\Scripts\activate
```
※ 左側に `(.venv)` と表示されれば成功です。

### 手順4: 必要な機能のインストール
```bash
pip install -e ".[dev]"
```
※ 少し時間がかかります。

## 4. 設定

ダウンロードしたフォルダの中に `.env.example` というファイルがあります。これをコピーして `.env` という名前のファイルを作成します。

```bash
copy .env.example .env
```

作成した `.env` ファイルをメモ帳やVSCodeで開き、`your_api_key_here` と書かれている部分を、手順2で取得した実際のAPIキーに書き換えて保存してください。

```ini
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxx
```

## 5. 使い方

すべての準備が整いました。ターミナルで以下のコマンドを入力して実行します。

### 基本: ブログ記事の生成
「AI副業」というテーマで記事を書きたい場合:

```bash
python -m ai_writing generate "AI副業" --content-type blog
```

### 応用: YouTube台本の生成
「犬の飼い方」というテーマで動画台本を作りたい場合:

```bash
python -m ai_writing generate "犬の飼い方" --content-type youtube
```

### 生成されたファイルの場所
処理が完了すると、`output` フォルダ（または設定した保存先）に、Markdown形式やGoogle Docs形式で成果物が保存されます。

## 6. よくある質問

**Q. エラーが出て動かない**
A. まず `.env` ファイルに正しいAPIキーが入っているか確認してください。また、Pythonのバージョンが古いとうまく動かないことがあります。

**Q. 途中で止まってしまう**
A. AIのAPIには通信制限がある場合があります。少し時間を置いてから再実行してみてください。
