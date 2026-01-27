---
name: implementation
description: テストケースに基づいて実装を行うスキル。test-first-developmentスキルで作成されたテストケースをパスする実装を行う。実装完了後はテスト実行のためtest-first-developmentスキルを呼び出し、テストパス後はcode-reviewerスキルを呼び出す。使用タイミング：(1) test-first-developmentからの実装依頼、(2) 既存コードのリファクタリング、(3) バグ修正実装。
---

# Implementation Skill

テストケースに基づいて実装を行うスキル。

## ワークフロー

### 1. 入力情報の確認

以下のファイル/情報を確認：
- `output_interface_design.yaml`: インターフェース設計
- 失敗しているテストケース
- 実装対象のインターフェース/メソッド

### 2. 実装計画

#### 実装順序の決定
1. 依存関係のないコンポーネントから開始
2. 下位レイヤーから上位レイヤーへ
3. シンプルなメソッドから複雑なメソッドへ

#### 実装アプローチ
- **最小実装**: テストをパスする最小限のコード
- **インクリメンタル**: 小さな変更を積み重ねる
- **YAGNI**: 必要になるまで作らない

### 3. 実装実行

#### コード構造

```
src/
├── domain/          # ドメインロジック
│   ├── models/      # エンティティ、値オブジェクト
│   └── services/    # ドメインサービス
├── application/     # アプリケーション層
│   ├── usecases/    # ユースケース
│   └── dto/         # データ転送オブジェクト
├── infrastructure/  # インフラ層
│   ├── repositories/# リポジトリ実装
│   └── external/    # 外部サービス連携
└── interfaces/      # インターフェース層
    ├── api/         # API エンドポイント
    └── cli/         # CLIコマンド
```

#### 実装チェックリスト

- [ ] インターフェース設計に準拠
- [ ] エラーハンドリング実装
- [ ] ログ出力実装
- [ ] ドキュメントコメント記述
- [ ] 命名規則遵守

### 4. コーディング規約

#### 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| クラス | PascalCase | `UserService` |
| メソッド | camelCase/snake_case | `getUser`/`get_user` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 変数 | camelCase/snake_case | `userName`/`user_name` |

#### コード品質

```
可読性 > パフォーマンス（早期最適化を避ける）
```

- 1メソッド: 20行以内目標
- 1クラス: 200行以内目標
- サイクロマティック複雑度: 10以下

### 5. エラーハンドリング

#### エラー分類

| 種類 | 対応 |
|------|------|
| バリデーションエラー | 400系エラー、詳細メッセージ |
| ビジネスルール違反 | カスタム例外、ログ記録 |
| システムエラー | 500系エラー、アラート |
| 外部サービスエラー | リトライ、フォールバック |

#### 例外設計

```
BaseException
├── ValidationException
├── BusinessException
│   ├── NotFoundExeption
│   └── ConflictException
└── InfrastructureException
    ├── DatabaseException
    └── ExternalServiceException
```

### 6. テスト実行依頼

実装完了後、`test-first-development` スキルを呼び出し：

```yaml
# test-first-development スキルへの引き継ぎ情報
implementation_result:
  status: "completed"
  implemented_components:
    - interface: "UserService"
      file: "src/domain/services/user_service.py"
      methods:
        - name: "create_user"
          status: "implemented"
        - name: "get_user"
          status: "implemented"
  
  changes:
    - file: "src/domain/services/user_service.py"
      type: "created"
    - file: "src/domain/models/user.py"
      type: "created"
  
  request: "テスト実行と結果確認"
```

### 7. テスト結果対応

#### テスト成功時
1. カバレッジ確認
2. リファクタリング検討
3. `code-reviewer` スキル呼び出し

#### テスト失敗時
1. 失敗原因分析
2. 修正実装
3. 再度 `test-first-development` スキル呼び出し

### 8. リファクタリング

テストパス後、以下の改善を検討：

#### リファクタリングパターン

| パターン | 適用場面 |
|----------|----------|
| Extract Method | 長いメソッド |
| Extract Class | 大きすぎるクラス |
| Rename | 不明確な命名 |
| Replace Magic Number | ハードコードされた値 |
| Introduce Parameter Object | 多すぎるパラメータ |

## 実装原則

### SOLID原則

- **S**: 単一責任の原則
- **O**: 開放閉鎖の原則
- **L**: リスコフの置換原則
- **I**: インターフェース分離の原則
- **D**: 依存性逆転の原則

### クリーンコード

- 意図を明確にする命名
- 小さな関数
- 副作用を避ける
- コメントより自己文書化

## スキル連携

| スキル | 呼び出しタイミング |
|--------|-------------------|
| test-first-development | 実装完了後、テスト実行依頼 |
| code-reviewer | 全テストパス後、レビュー依頼 |
