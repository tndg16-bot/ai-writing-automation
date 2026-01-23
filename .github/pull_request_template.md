## 📝 変更概要 (Summary)

1行で何をしたのかを簡潔に説明してください。

## 変更種類 (Type of Change)

- [ ] 新機能 (New Feature)
- [ ] バグ修正 (Bug Fix)
- [ ] 破壊的変更 (Breaking Change)
- [ ] ドキュメント更新 (Documentation Update)
- [ ] リファクタリング (Refactoring)
- [ ] パフォーマンス改善 (Performance Improvement)
- [ ] デザイン変更 (Design Update)

## 🔧 変更内容 (Detailed Description)

変更内容を詳しく説明してください。

## 🧪 テスト (Testing)

変更内容をテストする方法を説明してください。

- [ ] ローカルで動作確認済み
- [ ] ユニットテストに合格
- [ ] 統合テストに合格

## 🎯 関連Issue (Related Issues)

このPRが解決するIssue番号を記載してください。

Closes #(Issue番号)
Related to #(Issue番号)

## ✅ チェックリスト (Checklist)

- [ ] ラベル命名ルールに従ってラベルを適用
- [ ] サブタスク形式で進捗を記録
- [ ] Issueの状態を適切に更新（open/closed）
- [ ] コードスタイルに従っている
- [ ] テストが通っている
- [ ] ドキュメントが更新されている

## 💬 追加情報 (Additional Information)

必要であれば、他に知っておくべき情報を記載してください。

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
