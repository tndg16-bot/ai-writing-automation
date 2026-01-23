---
name: New Issue
about: 'Create a new issue for ai-writing-automation'
title: '[PhaseX] Issue Title'
labels: enhancement
assignees: ''

---

## 概要 (Overview)

簡潔に問題や要請を説明してください。

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

### フェーズラベル (Phase Labels)
- `phase1` - Phase 1: 基礎アーキテクチャ
- `phase2` - Phase 2: 画像生成
- `phase3` - Phase 3: Google Docs出力
- `phase7` - Phase 7: 履歴管理機能
- `phase8` - Phase 8: パフォーマンス最適化
- `phase9` - Phase 9: エコシステム拡張

### カテゴリラベル (Category Labels)
- `enhancement` - 新機能や要請
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
- Issueが `closed` 状態 → **完了**
- Issueに `in-progress` ラベル → **進行中**
- Issueにサブタスクがあり、1つ以上完了 → **進行中**
- Issueにサブタスクがあり、全て完了 → **完了**
- タイトルに `[3/5]` 形式 → **進行中**
- 上記以外 → **未着手**
