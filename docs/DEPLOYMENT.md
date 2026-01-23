# デプロイメントガイド

## 概要

本プロジェクトは以下のプラットフォームでデプロイされます：

- **バックエンド**: Railway（Python FastAPI + WebSocket）
- **フロントエンド**: Vercel（Next.js 14）

## プラットフォーム選定理由

| 要件 | Railway | Vercel |
|------|---------|--------|
| Pythonサポート | ✅ ネイティブ | ⚠️ 関数のみ |
| WebSocket | ✅ 完全サポート | ❌ 未サポート |
| Next.js | ✅ サポート | ✅ 最適化済み |
| 無料枠 | ✅ $5/月相当 | ✅ 無制限 |
| デプロイ速度 | ⚠️ 遅い | ✅ 速い |
| HTTPS | ✅ 自動 | ✅ 自動 |

## 前提条件

1. GitHubリポジトリ: `https://github.com/tndg16-bot/ai-writing-automation`
2. ブランチ: `phase-4-youtube-yukkuri`
3. 環境変数:
   - `OPENAI_API_KEY` (Railway)

## ステップ1: Railway（バックエンド）にデプロイ

### 1-1. Railwayプロジェクト作成

1. [Railway](https://railway.app) にアクセスし、GitHubでログイン
2. "New Project" → "Deploy from GitHub repo" を選択
3. リポジトリ `tndg16-bot/ai-writing-automation` を選択
4. ブランチ `phase-4-youtube-yukkuri` を選択
5. "Deploy" をクリック

### 1-2. 環境変数設定

1. Railwayプロジェクトの "Variables" タブに移動
2. 以下の変数を追加:
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 1-3. Railway URLの取得

1. Railwayプロジェクトの "Settings" → "Domains" に移動
2. 割り当てられたURLをメモ:
   ```
   https://ai-writing-api.railway.app
   ```

### 1-4. 自動デプロイ設定

1. Railwayプロジェクトの "Settings" → "GitHub"
2. "Automatic Deploys" を有効にする
3. `phase-4-youtube-yukkuri` ブランチを設定

## ステップ2: Vercel（フロントエンド）にデプロイ

### 2-1. Vercelプロジェクト作成

1. [Vercel](https://vercel.com) にアクセスし、GitHubでログイン
2. "Add New..." → "Project" を選択
3. GitHubリポジトリをインポート:
   - `tndg16-bot/ai-writing-automation`
4. プロジェクト設定:
   - **Framework Preset**: Next.js
   - **Root Directory**: `./frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 2-2. 環境変数設定

1. Vercelプロジェクトの "Settings" → "Environment Variables" に移動
2. 以下の変数を追加:
   ```
   NEXT_PUBLIC_API_URL=https://ai-writing-api.railway.app
   ```
   ※ `https://ai-writing-api.railway.app` は実際のRailway URLに置き換えてください

### 2-3. デプロイ実行

1. "Deploy" ボタンをクリック
2. デプロイが完了したら、Vercel URLをメモ:
   ```
   https://ai-writing-automation.vercel.app
   ```

### 2-4. 自動デプロイ設定

1. Vercelプロジェクトの "Settings" → "Git"
2. "Auto-Deploy" を有効にする
3. `phase-4-youtube-yukkuri` ブランチを設定

## ステップ3: デプロイの確認

### 3-1. バックエンドヘルスチェック

```bash
curl https://ai-writing-api.railway.app/health
```

期待される応答:
```json
{"status":"ok","version":"0.2.0"}
```

### 3-2. フロントエンドアクセス

ブラウザで以下のURLにアクセス:
```
https://ai-writing-automation.vercel.app
```

### 3-3. API連携確認

1. フロントエンドで記事生成を試す
2. WebSocket通信が正常に動作していることを確認

## ステップ4: カスタムドメイン設定（オプション）

### 4-1. Vercelにカスタムドメインを追加

1. Vercelプロジェクトの "Settings" → "Domains"
2. カスタムドメインを追加:
   ```
   ai-writing.yourdomain.com
   ```
3. DNS設定を指示に従って更新

### 4-2. Railwayにカスタムドメインを追加

1. Railwayプロジェクトの "Settings" → "Domains"
2. API用のカスタムドメインを追加:
   ```
   api.yourdomain.com
   ```
3. DNS設定を指示に従って更新

## トラブルシューティング

### 問題1: Railwayデプロイが失敗する

**症状**: Build failing

**原因**:
- `Procfile` が正しく設定されていない
- Pythonの依存関係がインストールできない

**解決策**:
1. `api/requirements.txt` を確認
2. `Procfile` を確認:
   ```
   web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```
3. RailwayのLogsを確認

### 問題2: Vercelデプロイが失敗する

**症状**: Build failing

**原因**:
- `NEXT_PUBLIC_API_URL` が設定されていない
- 依存関係が正しくインストールできない

**解決策**:
1. VercelのEnvironment Variablesを確認
2. `frontend/package.json` を確認
3. `next.config.js` を確認

### 問題3: APIリクエストがCORSエラーになる

**症状**: CORS policy error

**原因**:
- CORS設定が正しくない
- Railway URLが正しく設定されていない

**解決策**:
1. `api/main.py` のCORS設定を確認:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # 本番環境ではドメインを指定
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
2. `NEXT_PUBLIC_API_URL` を確認

### 問題4: WebSocket接続が失敗する

**症状**: WebSocket connection failed

**原因**:
- RailwayがWebSocketをサポートしていない
- CORS設定が間違っている

**解決策**:
1. RailwayのWebSocket対応を確認
2. `NEXT_PUBLIC_API_URL` が `ws://` または `wss://` であることを確認

## 費用見積もり

### 無料枠

- **Vercel**: 無料枠無制限
- **Railway**: $5/月相当（1プロジェクト、512MB RAM、500時間/月）

### 有料プラン

- **Vercel Pro**: $20/月（本番運用推奨）
- **Railway Starter**: $5/月（無制限プロジェクト、1GB RAM）

## 監視とログ

### Railway

- **Logs**: Real-time deployment logs
- **Metrics**: CPU, Memory, Network
- **Alerts**: Uptime monitoring

### Vercel

- **Analytics**: Web Vitals, traffic
- **Logs**: Build and deployment logs
- **Speed Insights**: Core Web Vitals

## 次のステップ

1. **監視設定**: Uptime monitoring, error tracking
2. **バックアップ**: Database backups, disaster recovery
3. **スケーリング**: Auto-scaling, CDN
4. **セキュリティ**: HTTPS, rate limiting, auth

## 参考リンク

- [Railway Documentation](https://railway.app/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
