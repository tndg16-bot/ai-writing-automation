# Contributing Guidelines

感謝いたします！このプロジェクトへの貢献を考えていただき、ありがとうございます。

---

## 📋 ラベル命名ルール (Label Naming Rules)

### ステータスラベル (Status Labels)
- `in-progress` - Issueが進行中
- `not_started` - Issueが未着手
- `completed` - Issueが完了（closed状態にする前に使用）

### カテゴリラベル (Category Labels)
- `enhancement` - 新機能や要求
- `bug` - バグ修正
- `documentation` - ドキュメント関連
- `performance` - パフォーマンス関連
- `integration` - 統合関連

### 優先度ラベル (Priority Labels)
- `high-priority` - 高優先度
- `medium-priority` - 中優先度
- `low-priority` - 低優先度

---

## 📝 サブタスク形式 (Subtask Format)

各Issueでは以下の形式でサブタスクを管理してください：

```markdown
### 主要なタスク
- [x] 完了したタスク
- [ ] 未完了のタスク

### 追加タスク
- [ ] タスクA
- [ ] タスクB
```

### 進捗計算

- `- [x]` で完了したタスクをカウント
- `- [ ]` で未完了のタスクをカウント
- 完了率 = (完了タスク数 / 全タスク数) × 100%

### ステータス判定

1. Issueが `closed` 状態 → **完了**
2. Issueに `in-progress` ラベル → **進行中**
3. Issueにサブタスクがあり、1つ以上完了 → **進行中**
4. Issueにサブタスクがあり、全て完了 → **完了**
5. タイトルに `[3/5]` 形式 → **進行中**
6. 上記以外 → **未着手**

---

## 🚀 開発の始め方 (Getting Started)

### Prerequisites

- Node.js 18以上
- Python 3.9以上（一部のツール用）
- npm / poetry（パッケージマネージャー）
- GitHubアカウント

### セットアップ

1. リポジトリをクローン
   ```bash
   git clone https://github.com/tndg16-bot/papa.git
   cd papa
   ```

2. 必要なプロジェクトへ移動
   ```bash
   cd Apps/[プロジェクト名]
   ```

3. 依存関係をインストール
   ```bash
   # Node.jsプロジェクトの場合
   npm install
   # Pythonプロジェクトの場合
   poetry install
   ```

4. 開発サーバーを起動
   ```bash
   # Next.js
   npm run dev
   # Python CLI
   poetry run cli
   ```

---

## 🧪 テスト (Testing)

### Node.jsプロジェクト

テストを実行するには：
```bash
npm run test
```

### Pythonプロジェクト

テストを実行するには：
```bash
poetry run pytest
```

---

## 📨 コミットメッセージ (Commit Messages)

コミットメッセージは以下の形式に従ってください：

```
[タイプ] 簡潔な説明

詳細な説明（必要であれば）
```

### タイプ

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `style`: コードスタイル（フォーマットなど）
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: その他の変更

---

## 📖 ドキュメント (Documentation)

- ドキュメントは `docs/` または `README.md` に保存してください
- Markdown形式を使用してください
- 日本語または英語で記述してください

---

## 💬 質問・提案 (Questions & Suggestions)

質問や提案がある場合は、Issueを開いてください。

---

## 🏷️ プロジェクト構造 (Project Structure)

```
papa/
├── Apps/
│   ├── Main/
│   │   ├── portfolio/          # ポートフォリオサイト
│   │   ├── nihongo-ai/
│   │   │   └── nihongo-mate/  # 日本語学習SaaS
│   │   ├── gamified-mandala-chart/
│   │   ├── talent-diagnosis/    # 適性診断ツール
│   │   └── task-manager/       # タスク管理ツール
│   └── Tools/
│       ├── ai-writing-automation/  # AI執筆自動化
│       ├── kindle-pdf-extension/   # Kindle PDF拡張機能
│       ├── AntigravityVault/
│       ├── calendar-sync-manager/
│       ├── SessionVault/
│       └── TermLog/
├── .github/                   # GitHubルール（共通）
└── System/                    # システム設定
```
