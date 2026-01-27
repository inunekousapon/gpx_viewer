---
name: test-first-development
description: テストファースト開発（TDD）を行うスキル。依頼された設計についてインターフェース設計を行い、テストケースを作成・実装する。テストを実行して失敗を確認し、implementationスキルを呼び出して実装を依頼する。出力ファイル：output_interface_design.yaml。使用タイミング：(1) 新規機能開発、(2) リファクタリング前のテスト追加、(3) バグ修正時のテスト追加、(4) task-splitterからのTDDタスク実行時。
---

# Test First Development Skill

テストファースト開発（TDD）を実践するスキル。

## TDDサイクル

```
Red → Green → Refactor
 ↑__________________|
```

1. **Red**: 失敗するテストを書く
2. **Green**: テストを通す最小限の実装（implementationスキル呼び出し）
3. **Refactor**: コードを改善（implementationスキル呼び出し）

## ワークフロー

### 1. インターフェース設計

設計ドキュメントから以下を定義し、`output_interface_design.yaml` に出力：

```yaml
# output_interface_design.yaml
interface_design:
  name: "インターフェース名"
  version: "1.0.0"
  created_at: "YYYY-MM-DD"

modules:
  - name: "モジュール名"
    description: "モジュールの責務"
    
    interfaces:
      - name: "InterfaceName"
        description: "インターフェースの説明"
        methods:
          - name: "methodName"
            description: "メソッドの説明"
            parameters:
              - name: "param1"
                type: "string"
                required: true
                description: "パラメータ説明"
            returns:
              type: "ReturnType"
              description: "戻り値説明"
            throws:
              - type: "ErrorType"
                condition: "発生条件"
                
    types:
      - name: "TypeName"
        description: "型の説明"
        properties:
          - name: "property1"
            type: "string"
            required: true
            description: "プロパティ説明"

    enums:
      - name: "EnumName"
        description: "列挙型の説明"
        values:
          - name: "VALUE_1"
            description: "値の説明"

contracts:
  - interface: "InterfaceName"
    preconditions:
      - "事前条件"
    postconditions:
      - "事後条件"
    invariants:
      - "不変条件"
```

### 2. テストケース設計

インターフェース設計に基づきテストケースを設計：

#### テストカテゴリ
- **正常系**: 期待通りの入力で期待通りの出力
- **境界値**: エッジケース、上限/下限値
- **異常系**: エラー入力、例外処理
- **統合**: コンポーネント間連携

#### テストケース例

```yaml
test_cases:
  - id: "TC-001"
    interface: "InterfaceName"
    method: "methodName"
    category: "normal|boundary|error|integration"
    description: "テストケースの説明"
    
    setup:
      - "前提条件/セットアップ"
    
    input:
      param1: "入力値"
    
    expected:
      result: "期待される結果"
      side_effects:
        - "期待される副作用"
    
    teardown:
      - "後処理"
```

### 3. テスト実装

テストケースをコードに実装する。

#### テストファイル構造

```
tests/
├── unit/
│   └── module_name/
│       └── interface_name_test.{ext}
├── integration/
│   └── feature_name_test.{ext}
└── fixtures/
    └── test_data.{ext}
```

#### テスト命名規則

```
test_[メソッド名]_[状況]_[期待結果]
```

例: `test_calculate_withValidInput_returnsCorrectSum`

### 4. テスト実行（Red Phase）

テストを実行し、**失敗することを確認**する。

```bash
# テスト実行コマンド例
pytest tests/ -v
npm test
go test ./...
```

失敗を確認したら：
1. 失敗したテストを記録
2. `implementation` スキルを呼び出し
3. 実装完了後、再度テスト実行

### 5. 実装スキルの呼び出し

失敗したテストをもとに `implementation` スキルを呼び出す：

```yaml
# implementation スキルへの引き継ぎ情報
tdd_handoff:
  interface_design_file: "output_interface_design.yaml"
  failing_tests:
    - test_file: "tests/unit/user_service_test.py"
      test_name: "test_create_user_withValidData_returnsUser"
      error_message: "NameError: name 'UserService' is not defined"
  
  implementation_targets:
    - interface: "UserService"
      methods:
        - "create_user"
        - "get_user"
      
  constraints:
    - "テストが通る最小限の実装"
    - "YAGNI原則を遵守"
```

### 6. テスト再実行（Green Phase）

実装完了後：
1. 全テストを再実行
2. 全てパスすれば次のリファクタリングまたは新しいテストへ
3. 失敗があれば `implementation` スキルを再度呼び出し

### 7. 完了判定

以下の条件を満たしたら `code-reviewer` スキルを呼び出し：
- 全テストがパス
- カバレッジ目標達成（通常80%以上）
- リファクタリング完了

## テスト品質基準

| 基準 | 目標値 |
|------|--------|
| ラインカバレッジ | 80%以上 |
| ブランチカバレッジ | 70%以上 |
| テスト実行時間 | ユニット: 10秒以内 |
| フレーキー率 | 0% |

---

## Python テスト実装ガイド

Python でのテスト実装に特化したガイドライン。

### 基本原則

| 原則 | 説明 |
|------|------|
| シンプル構成 | Arrange → Act → Assert の3フェーズ |
| パラメータ化禁止 | 複雑な `@pytest.mark.parametrize` を避ける |
| C1カバレッジ | **90%以上必須**（理想は100%） |
| テスト技法 | 境界値分析、ペアワイズ法を活用 |

### テスト構造: Arrange-Act-Assert (AAA)

全てのテストは以下の3フェーズで構成する：

```python
def test_create_user_with_valid_data_returns_user() -> None:
    # ========== Arrange（準備）==========
    # テストデータのセットアップ
    user_data = CreateUserRequest(
        name="田中太郎",
        email="tanaka@example.com",
    )
    repository = InMemoryUserRepository()
    service = UserService(repository=repository)
    
    # ========== Act（実行）==========
    # テスト対象の実行
    result = service.create_user(user_data)
    
    # ========== Assert（検証）==========
    # 結果の検査
    assert result.name == "田中太郎"
    assert result.email == "tanaka@example.com"
    assert result.id > 0
```

### パラメータ化の制限

#### ❌ 禁止: 複雑なパラメータ化

```python
# 禁止: 複雑で読みにくい
@pytest.mark.parametrize(
    "name,email,age,role,expected_error",
    [
        ("", "a@b.com", 20, "user", ValidationError),
        ("John", "", 20, "user", ValidationError),
        ("John", "a@b.com", -1, "user", ValidationError),
        ("John", "a@b.com", 20, "", ValidationError),
        # ... 大量のケース
    ],
)
def test_create_user_validation(name, email, age, role, expected_error):
    ...
```

#### ✅ 推奨: 個別テストメソッド

```python
def test_create_user_with_empty_name_raises_validation_error() -> None:
    """名前が空の場合はValidationErrorを発生させる"""
    # Arrange
    user_data = CreateUserRequest(name="", email="test@example.com")
    service = UserService(repository=InMemoryUserRepository())
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        service.create_user(user_data)
    
    assert "name" in str(exc_info.value)


def test_create_user_with_invalid_email_raises_validation_error() -> None:
    """メールアドレスが無効な場合はValidationErrorを発生させる"""
    # Arrange
    user_data = CreateUserRequest(name="田中", email="invalid-email")
    service = UserService(repository=InMemoryUserRepository())
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        service.create_user(user_data)
    
    assert "email" in str(exc_info.value)
```

#### ✅ 許容: シンプルなパラメータ化のみ

```python
# 許容: 単純な値のバリエーションのみ
@pytest.mark.parametrize("age", [0, 1, 17, 18, 19, 120, 121])
def test_validate_age_boundary(age: int) -> None:
    """年齢の境界値テスト"""
    # Arrange
    validator = AgeValidator(min_age=18, max_age=120)
    
    # Act
    result = validator.is_valid(age)
    
    # Assert
    expected = 18 <= age <= 120
    assert result == expected
```

### C1カバレッジ（分岐カバレッジ）

#### 目標: 90%以上（理想100%）

```bash
# カバレッジ計測
uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing

# HTMLレポート生成
uv run pytest tests/ --cov=src --cov-branch --cov-report=html
```

#### 分岐を網羅するテスト設計

```python
# テスト対象コード
def calculate_discount(price: int, is_member: bool, coupon_code: str | None) -> int:
    if price <= 0:
        raise ValueError("価格は正の値である必要があります")
    
    discount_rate: float = 0.0
    
    if is_member:                    # 分岐1: 会員判定
        discount_rate += 0.1
    
    if coupon_code is not None:      # 分岐2: クーポン有無
        if coupon_code == "SALE20":  # 分岐3: クーポン種類
            discount_rate += 0.2
        elif coupon_code == "SALE10":
            discount_rate += 0.1
    
    return int(price * (1 - discount_rate))
```

```python
# C1カバレッジ100%を達成するテスト
class TestCalculateDiscount:
    """calculate_discount関数のテスト"""
    
    def test_with_negative_price_raises_value_error(self) -> None:
        """価格が0以下の場合はValueErrorを発生"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            calculate_discount(price=0, is_member=False, coupon_code=None)
    
    def test_non_member_without_coupon_returns_full_price(self) -> None:
        """非会員・クーポンなしは割引なし"""
        # Arrange & Act
        result = calculate_discount(price=1000, is_member=False, coupon_code=None)
        # Assert
        assert result == 1000
    
    def test_member_without_coupon_returns_10_percent_off(self) -> None:
        """会員・クーポンなしは10%割引"""
        # Arrange & Act
        result = calculate_discount(price=1000, is_member=True, coupon_code=None)
        # Assert
        assert result == 900
    
    def test_non_member_with_sale20_coupon_returns_20_percent_off(self) -> None:
        """非会員・SALE20クーポンは20%割引"""
        # Arrange & Act
        result = calculate_discount(price=1000, is_member=False, coupon_code="SALE20")
        # Assert
        assert result == 800
    
    def test_non_member_with_sale10_coupon_returns_10_percent_off(self) -> None:
        """非会員・SALE10クーポンは10%割引"""
        # Arrange & Act
        result = calculate_discount(price=1000, is_member=False, coupon_code="SALE10")
        # Assert
        assert result == 900
    
    def test_member_with_sale20_coupon_returns_30_percent_off(self) -> None:
        """会員・SALE20クーポンは30%割引"""
        # Arrange & Act
        result = calculate_discount(price=1000, is_member=True, coupon_code="SALE20")
        # Assert
        assert result == 700
    
    def test_non_member_with_unknown_coupon_returns_full_price(self) -> None:
        """非会員・不明なクーポンは割引なし"""
        # Arrange & Act
        result = calculate_discount(price=1000, is_member=False, coupon_code="UNKNOWN")
        # Assert
        assert result == 1000
```

### 境界値分析

境界値テストは以下のポイントを必ずテストする：

| ポイント | 説明 |
|----------|------|
| 最小値-1 | 範囲外（下限） |
| 最小値 | 境界値（下限） |
| 最小値+1 | 範囲内（下限近傍） |
| 最大値-1 | 範囲内（上限近傍） |
| 最大値 | 境界値（上限） |
| 最大値+1 | 範囲外（上限） |

```python
class TestAgeValidation:
    """年齢バリデーション（有効範囲: 0-120歳）のテスト"""
    
    # 下限境界
    def test_age_minus_1_is_invalid(self) -> None:
        """-1歳は無効"""
        assert not is_valid_age(-1)
    
    def test_age_0_is_valid(self) -> None:
        """0歳は有効（下限）"""
        assert is_valid_age(0)
    
    def test_age_1_is_valid(self) -> None:
        """1歳は有効"""
        assert is_valid_age(1)
    
    # 上限境界
    def test_age_119_is_valid(self) -> None:
        """119歳は有効"""
        assert is_valid_age(119)
    
    def test_age_120_is_valid(self) -> None:
        """120歳は有効（上限）"""
        assert is_valid_age(120)
    
    def test_age_121_is_invalid(self) -> None:
        """121歳は無効"""
        assert not is_valid_age(121)
```

### ペアワイズ法（All-Pairs法）

複数のパラメータの組み合わせを効率的にテストする技法。

#### 適用場面

- 3つ以上のパラメータがある
- 全組み合わせテストは現実的でない
- 2因子間の相互作用を検証したい

#### 例: 検索機能のテスト

パラメータ:
- カテゴリ: `electronics`, `books`, `clothing`
- 価格帯: `low`, `medium`, `high`
- ソート: `price_asc`, `price_desc`, `rating`
- 在庫: `in_stock`, `all`

全組み合わせ: 3×3×3×2 = 54ケース → ペアワイズ: 約12ケース

```python
class TestSearchFunctionPairwise:
    """検索機能のペアワイズテスト"""
    
    # ペアワイズ法で抽出したテストケース
    def test_search_electronics_low_price_asc_in_stock(self) -> None:
        # Arrange
        params = SearchParams(
            category="electronics",
            price_range="low",
            sort="price_asc",
            stock_filter="in_stock",
        )
        # Act
        result = search_products(params)
        # Assert
        assert all(p.category == "electronics" for p in result)
        assert all(p.in_stock for p in result)
    
    def test_search_electronics_medium_price_desc_all(self) -> None:
        # Arrange
        params = SearchParams(
            category="electronics",
            price_range="medium",
            sort="price_desc",
            stock_filter="all",
        )
        # Act
        result = search_products(params)
        # Assert
        assert all(p.category == "electronics" for p in result)
    
    def test_search_books_low_rating_all(self) -> None:
        # Arrange
        params = SearchParams(
            category="books",
            price_range="low",
            sort="rating",
            stock_filter="all",
        )
        # Act
        result = search_products(params)
        # Assert
        assert all(p.category == "books" for p in result)
    
    # ... 残りのペアワイズケース
```

#### ペアワイズテストケース生成ツール

```bash
# pict (Microsoft製) を使用
# https://github.com/microsoft/pict

# 入力ファイル (params.txt)
# category: electronics, books, clothing
# price: low, medium, high
# sort: price_asc, price_desc, rating
# stock: in_stock, all

# 実行
pict params.txt > test_cases.txt
```

### Fixture設計

#### シンプルなFixture

```python
import pytest
from typing import Generator


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    """テスト用リポジトリ"""
    return InMemoryUserRepository()


@pytest.fixture
def user_service(user_repository: InMemoryUserRepository) -> UserService:
    """テスト用サービス"""
    return UserService(repository=user_repository)


@pytest.fixture
def sample_user() -> User:
    """テスト用ユーザー"""
    return User(
        id=1,
        name="テスト太郎",
        email="test@example.com",
    )
```

#### リソースクリーンアップ

```python
@pytest.fixture
def database_connection() -> Generator[Connection, None, None]:
    """データベース接続（終了時にクリーンアップ）"""
    # Arrange
    conn = create_test_connection()
    
    yield conn
    
    # Teardown
    conn.rollback()
    conn.close()
```

### pytest 設定

#### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=src",
    "--cov-branch",
    "--cov-report=term-missing",
    "--cov-fail-under=90",
]

[tool.coverage.run]
branch = true
source = ["src"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 90
```

### Python テストチェックリスト

- [ ] 全テストが AAA構造（Arrange-Act-Assert）
- [ ] 複雑なパラメータ化を使用していない
- [ ] C1カバレッジ 90%以上
- [ ] 境界値テストを実施
- [ ] 必要に応じてペアワイズ法を適用
- [ ] Fixtureはシンプルに保つ
- [ ] テスト命名が明確（何をテストしているか分かる）

---

## 出力ファイル

| ファイル名 | 用途 |
|-----------|------|
| output_interface_design.yaml | インターフェース設計書 |

## スキル連携

| スキル | 呼び出しタイミング |
|--------|-------------------|
| implementation | テスト失敗後、実装依頼時 |
| python-implementation | Python実装の場合 |
| code-reviewer | 全テストパス後、レビュー依頼時 |
