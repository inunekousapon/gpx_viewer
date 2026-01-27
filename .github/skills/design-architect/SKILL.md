---
name: design-architect
description: システム設計・アーキテクチャ設計を行うスキル。依頼された設計についてWeb検索で正しい設計方法を調査し、価値の高い設計を検討する。不要な設計の削除と不足している設計の追加を判断し、最終的な設計が決まったらtask-splitterスキルを呼び出す。使用タイミング：(1) 新規システムの設計依頼、(2) アーキテクチャの検討、(3) 技術選定、(4) 設計レビュー、(5) 設計の最適化。
---

# Design Architect Skill

システム設計・アーキテクチャ設計を行うためのスキル。

## ワークフロー

### 1. 設計要件の収集

依頼内容から以下を明確化する：
- 解決したい課題・目的
- 対象ユーザー・ステークホルダー
- 機能要件・非機能要件
- 制約条件（予算、期間、技術スタック）

### 2. 設計調査

Web検索を活用し、以下を調査する：
- 類似システムの設計パターン
- ベストプラクティス
- 最新の技術トレンド
- 潜在的なリスクと対策

調査結果は根拠とともに記録する。

### 3. 設計の価値評価

各設計案について以下の観点で評価：

| 評価軸 | 説明 |
|--------|------|
| ビジネス価値 | ROI、競合優位性 |
| 技術的実現性 | 実装難易度、技術成熟度 |
| 保守性 | 変更容易性、テスト容易性 |
| スケーラビリティ | 負荷対応、拡張性 |
| セキュリティ | 脅威対策、コンプライアンス |

### 4. 設計の最適化

依頼内容に対して：
- **不要な設計**: オーバーエンジニアリング、YAGNI違反を特定し削除
- **不足している設計**: 見落としている要件、エッジケースを特定し追加

### 5. 設計決定の出力

設計が確定したら `design_to_task.yaml` を出力する。

```yaml
# design_to_task.yaml
design:
  name: "設計名"
  version: "1.0.0"
  created_at: "YYYY-MM-DD"
  
summary:
  purpose: "設計の目的"
  scope: "スコープ"
  
architecture:
  type: "アーキテクチャタイプ（例：Microservices, Monolith, Serverless）"
  components:
    - name: "コンポーネント名"
      responsibility: "責務"
      technology: "使用技術"
      
  data_flow:
    - from: "送信元"
      to: "送信先"
      description: "データフロー説明"

decisions:
  - id: "ADR-001"
    title: "決定事項タイトル"
    context: "背景・文脈"
    decision: "決定内容"
    rationale: "根拠"
    consequences: "影響"

removed_designs:
  - name: "削除した設計"
    reason: "削除理由"

added_designs:
  - name: "追加した設計"
    reason: "追加理由"

next_skill:
  name: "task-splitter"
  input_file: "design_to_task.yaml"
```

### 6. 次スキルの呼び出し

設計完了後、`task-splitter` スキルを呼び出し、タスク分割を依頼する。

## 設計原則

以下の原則に従う：
- **KISS**: シンプルに保つ
- **YAGNI**: 必要になるまで作らない
- **DRY**: 繰り返しを避ける
- **SOLID**: オブジェクト指向設計原則
- **Separation of Concerns**: 関心の分離

## 出力ファイル

| ファイル名 | 用途 |
|-----------|------|
| design_to_task.yaml | タスク分割スキルへの引き継ぎ情報 |
