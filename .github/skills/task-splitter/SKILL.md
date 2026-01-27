---
name: task-splitter
description: 設計をもとにタスク分割を行うスキル。design-architectスキルで決定した設計を実装可能なタスクに分解し、優先順位と必要スキルセットを設定する。出力ファイル：design_task.yaml, tdd_task.yaml, implement_task.yaml, review_task.yaml。使用タイミング：(1) design-architectスキルからの呼び出し、(2) 設計ドキュメントからのタスク分割、(3) プロジェクト計画の作成、(4) スプリント計画。
---

# Task Splitter Skill

設計をもとに実装タスクを分割するスキル。

## 入力

`design_to_task.yaml` を読み込み、設計内容を把握する。

## ワークフロー

### 1. 設計内容の分析

design_to_task.yaml から以下を抽出：
- アーキテクチャコンポーネント
- データフロー
- 設計決定事項

### 2. タスク分割の実行

設計を4つのカテゴリに分割：

#### 設計タスク (design_task.yaml)
- インターフェース設計
- データモデル設計
- API設計
- セキュリティ設計

#### TDDタスク (tdd_task.yaml)
- テストケース設計
- テスト実装
- モック/スタブ作成

#### 実装タスク (implement_task.yaml)
- コンポーネント実装
- 統合処理
- エラーハンドリング

#### レビュータスク (review_task.yaml)
- コードレビュー
- セキュリティレビュー
- パフォーマンスレビュー

### 3. 優先順位の設定

各タスクに優先順位を付与：
- **P0 (Critical)**: ブロッカー、即座に対応必須
- **P1 (High)**: コア機能、早期に対応
- **P2 (Medium)**: 重要だが緊急ではない
- **P3 (Low)**: あると良い機能

### 4. スキルセットの判定

各タスクに必要なスキルを設定：
- `frontend`: フロントエンド開発
- `backend`: バックエンド開発
- `database`: データベース設計・管理
- `devops`: インフラ・CI/CD
- `security`: セキュリティ
- `testing`: テスト設計・実装
- `design`: UI/UXデザイン

## 出力フォーマット

### design_task.yaml

```yaml
# design_task.yaml
tasks:
  - id: "DESIGN-001"
    title: "タスクタイトル"
    description: "詳細説明"
    priority: "P1"
    estimated_hours: 4
    skills_required:
      - "backend"
      - "database"
    dependencies: []
    acceptance_criteria:
      - "完了条件1"
      - "完了条件2"
    deliverables:
      - "成果物1"
```

### tdd_task.yaml

```yaml
# tdd_task.yaml
tasks:
  - id: "TDD-001"
    title: "テストタスクタイトル"
    description: "詳細説明"
    priority: "P1"
    estimated_hours: 2
    skills_required:
      - "testing"
      - "backend"
    dependencies:
      - "DESIGN-001"
    test_types:
      - "unit"
      - "integration"
    target_coverage: 80
    next_skill: "test-first-development"
```

### implement_task.yaml

```yaml
# implement_task.yaml
tasks:
  - id: "IMPL-001"
    title: "実装タスクタイトル"
    description: "詳細説明"
    priority: "P1"
    estimated_hours: 8
    skills_required:
      - "backend"
    dependencies:
      - "TDD-001"
    components:
      - "コンポーネント名"
    next_skill: "implementation"
```

### review_task.yaml

```yaml
# review_task.yaml
tasks:
  - id: "REVIEW-001"
    title: "レビュータスクタイトル"
    description: "詳細説明"
    priority: "P1"
    estimated_hours: 2
    skills_required:
      - "backend"
      - "security"
    dependencies:
      - "IMPL-001"
    review_types:
      - "code_quality"
      - "security"
      - "performance"
    next_skill: "code-reviewer"
```

## タスク分割の原則

- **Single Responsibility**: 1タスク1責務
- **Testable**: テスト可能な粒度
- **Estimable**: 見積もり可能（最大8時間）
- **Independent**: 可能な限り独立
- **Traceable**: 設計に追跡可能

## スキル連携

| 次のスキル | 呼び出しタイミング |
|-----------|-------------------|
| ui-ux-designer | UI/UXデザインが必要な場合 |
| test-first-development | TDDタスク実行時 |
| implementation | 実装タスク実行時 |
| code-reviewer | レビュータスク実行時 |
