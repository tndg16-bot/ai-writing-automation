# デプロイ実施ガイド（Railway + Vercel）

## 概要
Railwayでバックエンドを、Vercelでフロントエンドをデプロイする手順を説明します。

---

## 事前準備

### 必要な情報

| 項目 | 値 |
|------|-----|
| **GitHubリポジトリ** | tndg16-bot/ai-writing-automation |
| **ブランチ** | phase-4-youtube-yukkuri |
| **OPENAI_API_KEY** | あなたのAPIキー |

### 前提条件

✅ `railway.json` - 作成済み
✅ `frontend/vercel.json` - 作成済み
✅ `Procfile` - 作成済み
✅ `docs/DEPLOYMENT.md` - 作成済み

---

## Part 1: Railwayデプロイ（バックエンド）

### ステップ1: Railwayプロジェクト作成

1. [Railway](https://railway.app) にアクセス
2. GitHubアカウントでログイン
3. 右上の "New Project" をクリック
4. "Deploy from GitHub repo" をクリック
5. リポジトリ一覧から `tndg16-bot/ai-writing-automation` を選択
6. ブランチ `phase-4-youtube-yukkuri` を選択

### ステップ2: 環境変数設定

1. プロジェクト作成後、プロジェクトの "Variables" タブに移動
2. "New Variable" をクリック
3. 以下の変数を追加:

| 変数名 | 値 |
|--------|-----|
| `OPENAI_API_KEY` | `sk-xxxxxxxxxxxxxxxxxxxxxxxx` |

※ APIキーは必ず有効なものを入力してください

### ステップ3: デプロイ実行

1. "Deploy" ボタンをクリック
2. 自動的にビルドとデプロイが開始されます
3. 完了するまで待機します（通常2-3分）

### ステップ4: Railway URLの取得

1. プロジェクトの "Settings" → "Domains" に移動
2. 割り当てられたURLをコピー:
   ```
   https://ai-writing-api-xxxx.railway.app
   ```

### ステップ5: ヘルスチェック確認

1. ターミナルで以下を実行:
   ```bash
   curl https://ai-writing-api-xxxx.railway.app/health
   ```

2. 以下のJSONが返ってくれば成功です:
   ```json
   {"status":"ok","version":"0.1.0"}
   ```

---

## Part 2: Vercelデプロイ（フロントエンド）

### ステップ1: Vercelプロジェクト作成

1. [Vercel](https://vercel.com) にアクセス
2. GitHubアカウントでログイン
3. 右上の "Add New..." → "Project" をクリック
4. GitHubリポジトリ一覧から `tndg16-bot/ai-writing-automation` をインポート

### ステップ2: プロジェクト設定

1. **Root Directory**: `./frontend` を設定
2. **Framework Preset**: Next.js を選択
3. **Build Command**: `npm run build`（自動で設定されるはず）
4. **Output Directory**: `.next`（自動で設定されるはず）

### ステップ3: 環境変数設定

1. プロジェクトの "Settings" → "Environment Variables" に移動
2. "New Variable" をクリック
3. 以下の変数を追加:

| 変数名 | 値 |
|--------|-----|
| `NEXT_PUBLIC_API_URL` | `https://ai-writing-api-xxxx.railway.app` |

※ `https://ai-writing-api-xxxx.railway.app` はPart 1で取得したRailway URLに置き換えてください

### ステップ4: デプロイ実行

1. "Deploy" ボタンをクリック
2. 自動的にビルドとデプロイが開始されます
3. 完了するまで待機します（通常1-2分）

### ステップ5: Vercel URLの取得

1. デプロイ完了後、ダッシュボードからURLをコピー:
   ```
   https://ai-writing-automation.vercel.app
   ```

---

## Part 3: 統合テスト

### テスト1: バックエンドヘルスチェック

```bash
curl https://ai-writing-api-xxxx.railway.app/health
```

### テスト2: フロントエンドアクセス

ブラウザで `https://ai-writing-automation.vercel.app` にアクセス

### テスト3: 機能テスト

1. トップページが表示される
2. "Generate Content" フォームが表示される
3. 統計が表示される
4. 履歴一覧が表示される

---

## Part 4: 実際の運用

### 記事生成の手順

1. フロントエンドで "Generate Content" をクリック
2. キーワードを入力（例: `AI副業`）
3. コンテンツタイプを選択（Blog / YouTube / ゆっくり）
4. クライアントを選択（default）
5. 「生成」ボタンをクリック
6. リアルタイム進捗が表示される
7. 生成完了後、結果が表示される

### 履歴の確認

1. トップページの "History" タブをクリック
2. 過去の生成履歴が一覧表示される
3. 詳細をクリックすると、生成内容が確認できる

---

## トラブルシューティング

### Railwayデプロイ失敗の場合

| エラー | 原因 | 解決策 |
|------|------|--------|
| Build failing | 依存関係の問題 | `pyproject.toml` のdependenciesを確認 |
| Runtime error | 互換性の問題 | Python 3.11を使用 |
| API key invalid | 環境変数の設定ミス | `OPENAI_API_KEY` を再確認 |

### Vercelデプロイ失敗の場合

| エラー | 原因 | 解決策 |
|------|------|--------|
| Build failing | TypeScriptエラー | `npm run build` をローカルで実行してエラー確認 |
| Environment variable not found | 設定ミス | `NEXT_PUBLIC_API_URL` を再確認 |
| API connection failed | CORSエラー | Railway URLが正しいか確認 |

### API連携エラーの場合

| エラー | 原因 | 解決策 |
|------|------|--------|
| CORS error | オリジン不一致 | Vercel環境変数のURLを確認 |
| 404 Not Found | エンドポイントの間違い | `/health` → `/` の確認 |
| 500 Server Error | バックエンドのエラー | RailwayのLogsを確認 |

---

## 成功の目安り

以下がすべて正常に動作すればデプロイ成功です：

- ✅ Railwayバックエンドが稼動している
- ✅ Vercelフロントエンドが表示される
- ✅ ヘルスチェックが正常に返る
- ✅ フロントエンドからバックエンドのAPIが呼び出せる
- ✅ 記事生成が実行できる
- ✅ リアルタイム進捗が表示される
- ✅ 履歴管理が動作している

---

## 次のステップ

デプロイ成功後、以下の改善を検討してください：

1. **カスタムドメイン設定**
   - Railway: `api.yourdomain.com`
   - Vercel: `app.yourdomain.com`

2. **SSL証明書**
   - Railway: 自動的にSSL証明書が発行されます
   - Vercel: 自動的にSSL証明書が発行されます

3. **CDNの設定**
   - Vercel: グローバルCDNで高速化

4. **監視とアラート**
   - uptime監視
   - エラートラート（Sentryなど）

---

## ドキュメントの参照

- [README.md](README.md) - プロジェクト概要
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - 進捗状況
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - デプロイ詳細ガイド

---

## サポート

問題が発生した場合は、以下のドキュメントを参照してください：

1. [Railway Docs](https://railway.app/docs)
2. [Vercel Docs](https://vercel.com/docs)

---

**最終更新**: 2026-01-23 21:00 JST
