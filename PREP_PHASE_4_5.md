# Phase 4 & 5: ユーザー準備タスク

## Phase 4: YouTube/ゆっくり対応

### プロンプトテンプレート作成（ユーザー作業）

#### YouTube台本用プロンプト

**prompts/youtube/01_search_intent.yaml**
```yaml
name: "YouTube検索意図調査"
description: "キーワードから動画の検索意図グルーピングを抽出"

system: |
  あなたはYouTube動画のプロデューサーです。

user: |
  「{{keyword}}」というキーワードでYouTube動画を作成します。
  このキーワードの検索意図をグルーピングしてください。

  #制約条件
  ・検索意図をカテゴライズする（例：初心者向け、中級者向け、トラブル解決、比較など）
  ・それぞれの意図に含まれる具体的なキーワードを3つずつ挙げる
  ・視聴者の属性を考慮する

  #出力形式
  以下のJSON形式で出力してください：
  ```json
  {
    "persona": "視聴者ペルソナ",
    "search_intents": [
      {
        "category": "カテゴリ名",
        "keywords": ["キーワード1", "キーワード2", "キーワード3"]
      }
    ]
  }
  ```

output_parser: "json"
```

**prompts/youtube/02_structure.yaml**
```yaml
name: "YouTube目次構成作成"
description: "上位記事を統合して動画目次を作成"

system: |
  あなたはYouTube動画のプロデューサーです。

user: |
  「{{keyword}}」というキーワードでYouTube動画を作成します。
  以下の上位記事の構成を読み込んで、統合目次を作成してください。

  #上位記事の構成
  {{top5_structure}}

  #検索意図
  {{search_intents}}

  #制約条件
  ・上位記事の構成を統合し、動画の目次として整理する
  ・10分〜20分の動画に適した構成にする（5〜7つのセクション）
  ・各セクションは2000文字程度の目安
  ・視聴者が最後まで見たくなるような流れを意識する

  #出力形式
  以下のJSON形式で出力してください：
  ```json
  {
    "structure": [
      {
        "section": "セクション1",
        "description": "内容の説明",
        "estimated_time": "2分"
      }
    ]
  }
  ```

output_parser: "json"
```

**prompts/youtube/03_intro_ending.yaml**
```yaml
name: "YouTube冒頭・エンディング作成"
description: "動画の冒頭とエンディングを作成"

system: |
  あなたはYouTube動画のプロデューサーです。

user: |
  「{{keyword}}」というキーワードでYouTube動画を作成します。
  動画の冒頭とエンディングを作成してください。

  #目次構成
  {{structure}}

  #チャンネル情報
  チャンネル名: {{channel_name}}
  登場者: {{presenter_name}}

  #制約条件
  ・冒頭は視聴者を引き込むフックを含める
  ・冒頭には本動画で得られるメリットを明確に伝える
  ・エンディングはチャンネル登録をお願いする

  #出力形式
  以下のJSON形式で出力してください：
  ```json
  {
    "intro": "冒頭の台本",
    "ending": "エンディングの台本"
  }
  ```

output_parser: "json"
```

**prompts/youtube/04_body.yaml**
```yaml
name: "YouTube本文作成"
description: "動画の本文を作成"

system: |
  あなたはYouTube動画のプロデューサーです。

user: |
  「{{keyword}}」というキーワードでYouTube動画を作成します。
  各セクションの台本を作成してください。

  #目次構成
  {{structure}}

  #検索意図
  {{search_intents}}

  #制約条件
  ・口語体で書く（「〜ですね」「〜でしょう」等）
  ・各セクションは2000文字程度
  ・視聴者が理解しやすいように具体例や比喩を使う
  ・専門用語はわかりやすく説明する

  #出力形式
  以下のJSON形式で出力してください：
  ```json
  {
    "sections": [
      {
        "heading": "セクション名",
        "content": "台本本文"
      }
    ]
  }
  ```

output_parser: "json"
```

#### ゆっくり台本用プロンプト

**prompts/yukkuri/01_search_intent.yaml**
```yaml
name: "ゆっくり動画検索意図調査"
description: "キーワードからゆっくり動画の検索意図を抽出"

system: |
  あなたはゆっくり動画のシナリオライターです。

user: |
  「{{keyword}}」というキーワードでゆっくり解説動画を作成します。
  このキーワードの検索意図を抽出してください。

  #制約条件
  ・視聴者は初心者〜中級者を想定
  ・わかりやすさを重視した意図にする

  #出力形式
  以下のJSON形式で出力してください：
  ```json
  {
    "persona": "視聴者ペルソナ",
    "needs": ["ニーズ1", "ニーズ2"]
  }
  ```

output_parser: "json"
```

**prompts/yukkuri/02_structure.yaml**
```yaml
name: "ゆっくり動画構成作成"
description: "動画の構成を作成"

system: |
  あなたはゆっくり動画のシナリオライターです。

user: |
  「{{keyword}}」というキーワードでゆっくり解説動画を作成します。
  動画の構成を作成してください。

  #上位記事の構成
  {{top5_structure}}

  #制約条件
  ・霊夢と魔理沙の掛け合い形式にする
  ・5分〜10分の動画に適した構成（3〜5セクション）
  ・各セクションで霊夢が解説、魔理沙が補足の役割

  #出力形式
  以下のJSON形式で出力してください：
  ```json
  {
    "structure": [
      {
        "topic": "トピック",
        "reimu_role": "霊夢の役割",
        "marisa_role": "魔理沙の役割"
      }
    ]
  }
  ```

output_parser: "json"
```

**prompts/yukkuri/03_script.yaml**
```yaml
name: "ゆっくり動画台本作成"
description: "霊夢・魔理沙の掛け合い台本を作成"

system: |
  あなたはゆっくり動画のシナリオライターです。
  霊夢と魔理沙の口調を再現してください。

  霊夢の口調：
  ・わかりやすく丁寧に解説する
  ・「〜ね」「〜よ」といった語尾を使う
  ・魔理沙の質問に対して答える役割

  魔理沙の口調：
  ・少し砕けた口調
  ・「〜だぜ」「〜なのだ」といった語尾を使う
  ・霊夢の解説にツッコミを入れる役割

user: |
  「{{keyword}}」というキーワードでゆっくり解説動画を作成します。
  各セクションの台本を作成してください。

  #構成
  {{structure}}

  #制約条件
  ・霊夢と魔理沙の掛け合い形式
  ・各セクションは1000〜1500文字程度
  ・自然な会話の流れを意識する
  ・専門用語は霊夢がわかりやすく説明する

  #出力形式
  以下のJSON形式で出力してください：
  ```json
  {
    "sections": [
      {
        "heading": "セクション名",
        "reimu": "霊夢の台本",
        "marisa": "魔理沙の台本"
      }
    ]
  }
  ```

output_parser: "json"
```

## Phase 5: 拡張・最適化

### Midjourney連携準備（ユーザー作業）

#### Midjourneyアカウントの準備
1. **Midjourney Discordサーバーに参加**
   - https://discord.gg/midjourney にアクセス
   - Discordアカウントが必要

2. **Midjourneyサブスクリプション**
   - Basic Plan ($10/月) 〜 Standard Plan ($30/月)
   - 画像生成回数に応じて選択

3. **Discord Bot Tokenの取得**
   - Discord Developer PortalでBotを作成
   - Bot Tokenを取得

4. **Discord Server IDの確認**
   - Midjourneyを使用するDiscordサーバーのIDを取得

#### 設定ファイルの追記
`.env`に以下を追加：
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_SERVER_ID=your_discord_server_id_here
MIDJOURNEY_CHANNEL_ID=your_midjourney_channel_id_here
```

### Canva連携準備（ユーザー作業）

#### Canva APIアカウントの準備
1. **Canva Developersに登録**
   - https://www.canva.com/developers/register にアクセス
   - 開発者アカウントを作成

2. **APIキーの取得**
   - プロジェクトを作成
   - API Keyを取得

3. **テンプレートIDの確認**
   - 使用するCanvaテンプレートのIDを確認

#### 設定ファイルの追記
`.env`に以下を追加：
```bash
CANVA_API_KEY=your_canva_api_key_here
CANVA_TEMPLATE_ID=your_template_id_here
```

### 履歴管理準備（ユーザー作業）

#### データベースの選択
以下のいずれかを選択：
- **SQLite**（ローカル開発用、推奨）
- **PostgreSQL**（本番環境用）

#### SQLiteを使用する場合（推奨）
追加の準備は不要。システムで自動的に作成されます。

#### PostgreSQLを使用する場合
1. **PostgreSQLインストール**
   ```bash
   # Windows: https://www.postgresql.org/download/windows/
   # macOS: brew install postgresql
   # Linux: sudo apt install postgresql
   ```

2. **データベース作成**
   ```sql
   CREATE DATABASE ai_writing_history;
   ```

3. **設定ファイルの追記**
   `.env`に以下を追加：
   ```bash
   DATABASE_URL=postgresql://username:password@localhost/ai_writing_history
   ```

### 追加のPython依存関係（システムがインストール）

Phase 5で必要なライブラリ：
```bash
# Midjourney連携
discord.py>=2.3.0

# Canva連携
canva-python>=1.0.0

# データベース
sqlalchemy>=2.0.0
alembic>=1.13.0

# キャッシュ強化
redis>=5.0.0  # オプション
```

### YouTube/ゆっくり向けGoogle Docsテンプレート

**templates/youtube_default.json**
```json
{
  "title": "{{ selected_title or 'YouTube動画台本' }}",
  "sections": [
    {
      "type": "heading",
      "level": 1,
      "text": "{{ selected_title or 'YouTube動画台本' }}"
    },
    {
      "type": "paragraph",
      "text": "\n"
    },
    {
      "type": "heading",
      "level": 2,
      "text": "冒頭"
    },
    {
      "type": "paragraph",
      "text": "\n"
    },
    {
      "type": "paragraph",
      "text": "{{ intro or '' }}"
    },
    {
      "type": "paragraph",
      "text": "\n\n"
    },
    {
      "type": "loop",
      "variable": "sections",
      "item_name": "section",
      "sections": [
        {
          "type": "heading",
          "level": 2,
          "text": "{{ section.heading }}"
        },
        {
          "type": "paragraph",
          "text": "\n"
        },
        {
          "type": "paragraph",
          "text": "{{ section.content }}"
        },
        {
          "type": "paragraph",
          "text": "\n\n"
        }
      ]
    },
    {
      "type": "heading",
      "level": 2,
      "text": "エンディング"
    },
    {
      "type": "paragraph",
      "text": "\n"
    },
    {
      "type": "paragraph",
      "text": "{{ ending or '' }}"
    }
  ]
}
```

**templates/yukkuri_default.json**
```json
{
  "title": "{{ selected_title or 'ゆっくり解説動画台本' }}",
  "sections": [
    {
      "type": "heading",
      "level": 1,
      "text": "{{ selected_title or 'ゆっくり解説動画台本' }}"
    },
    {
      "type": "paragraph",
      "text": "\n"
    },
    {
      "type": "paragraph",
      "text": "キャラクター: 霊夢、魔理沙"
    },
    {
      "type": "paragraph",
      "text": "\n\n"
    },
    {
      "type": "loop",
      "variable": "sections",
      "item_name": "section",
      "sections": [
        {
          "type": "heading",
          "level": 2,
          "text": "{{ section.heading }}"
        },
        {
          "type": "paragraph",
          "text": "\n"
        },
        {
          "type": "heading",
          "level": 3,
          "text": "霊夢"
        },
        {
          "type": "paragraph",
          "text": "\n"
        },
        {
          "type": "paragraph",
          "text": "{{ section.reimu }}"
        },
        {
          "type": "paragraph",
          "text": "\n"
        },
        {
          "type": "heading",
          "level": 3,
          "text": "魔理沙"
        },
        {
          "type": "paragraph",
          "text": "\n"
        },
        {
          "type": "paragraph",
          "text": "{{ section.marisa }}"
        },
        {
          "type": "paragraph",
          "text": "\n\n"
        }
      ]
    }
  ]
}
```

## 準備チェックリスト

### Phase 4 準備
- [ ] プロンプトテンプレートを作成（YouTube）
- [ ] プロンプトテンプレートを作成（ゆっくり）
- [ ] YouTube台本用テンプレート（youtube_default.json）を作成
- [ ] ゆっくり台本用テンプレート（yukkuri_default.json）を作成

### Phase 5 準備
- [ ] Midjourney: Discordアカウント作成
- [ ] Midjourney: Midjourneyサブスクリプション購入
- [ ] Midjourney: Discord Bot Token取得
- [ ] Canva: Canva Developersアカウント作成
- [ ] Canva: APIキー取得
- [ ] Canva: テンプレートID確認
- [ ] データベース: SQLite/PostgreSQL選択
- [ ] データベース: PostgreSQL使用の場合、インストールと設定

## 実装開始フロー

1. **プロンプトテンプレートの作成**（ユーザー作業）
   - 上記のYAMLファイルをコピーして `prompts/youtube/` と `prompts/yukkuri/` に保存

2. **Google Docsテンプレートの作成**（ユーザー作業）
   - 上記のJSONファイルを `templates/` に保存

3. **設定ファイルの更新**（ユーザー作業）
   - `.env`に必要な環境変数を追加
   - Midjourney、Canvaの認証情報を追加

4. **実装の開始**（システム作業）
   - プロンプトテンプレート作成完了後、実装を開始します
