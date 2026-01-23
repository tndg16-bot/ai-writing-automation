---
name: 📝 Standard Issue
about: 'Create a standard issue'
title: '[Type] Issue Title'
labels: enhancement
assignees: ''

---

## 概要 (Overview)

簡潔に問題や要求を説明してください。

## 背景 (Background)

このIssueが必要な背景やコンテキストを説明してください。

## タスク (Tasks)

各タスクは `- [ ]` 形式で記述してください。完了したタスクは `- [x]` に変更してください。

### 必須タスク (Required Tasks)
- [ ] タスク1
- [ ] タスク2
- [ ] タスク3

### 追加タスク (Additional Tasks)
- [ ] 追加タスク1
- [ ] 追加タスク2

## 成功基準 (Acceptance Criteria)

- [ ] 基準1
- [ ] 基準2
- [ ] 基準3

## 関連ドキュメント (Related Documentation)

- [関連ドキュメントのリンク1](URL)
- [関連ドキュメントのリンク2](URL)

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

**進捗計算**:
- `- [x]` で完了したタスクをカウント
- `- [ ]` で未完了のタスクをカウント
- 完了率 = (完了タスク数 / 全タスク数) × 100%

**ステータス判定**:
1. Issueが `closed` 状態 → **完了**
2. Issueに `in-progress` ラベル → **進行中**
3. Issueにサブタスクがあり、1つ以上完了 → **進行中**
4. Issueにサブタスクがあり、全て完了 → **完了**
5. タイトルに `[3/5]` 形式 → **進行中**
6. 上記以外 → **未着手**
