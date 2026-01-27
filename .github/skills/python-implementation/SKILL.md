---
name: python-implementation
description: Python実装を行うスキル。uvによる環境構築、pydanticによる型定義、mypyによる型チェック、blackによるコード整形を必須とする堅牢なPython開発。使用タイミング：(1) Python新規実装、(2) Pythonリファクタリング、(3) Python型安全性強化、(4) test-first-developmentからのPython実装依頼。
---

# Python Implementation Skill

堅牢なPython実装を行うスキル。

## 基本原則

### 絶対遵守事項

| 項目 | ルール |
|------|--------|
| パッケージ管理 | **uv のみ使用**（pip 禁止） |
| 型アノテーション | **全ての関数・変数に必須** |
| 型定義 | **pydantic を使用** |
| 型チェック | **mypy でエラー0件** |
| コード整形 | **black で整形** |
| Union型 | **極力避ける** |

## 環境構築

### uv によるプロジェクト初期化

```bash
# プロジェクト作成
uv init project-name
cd project-name

# 仮想環境作成
uv venv

# 依存関係追加
uv add pydantic
uv add --dev mypy black pytest

# 開発用依存関係のインストール
uv sync
```

### ⚠️ 禁止事項

```bash
# 以下は絶対に使用しない
pip install xxx        # 禁止
pip freeze             # 禁止
python -m pip xxx      # 禁止
```

### pyproject.toml 設定

```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.0",
    "black>=24.0",
    "pytest>=8.0",
]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_any_generics = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_configs = true
show_error_codes = true
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true

[tool.black]
line-length = 88
target-version = ["py311"]
```

## 型定義

### pydantic モデルの使用

#### 基本的なモデル定義

```python
from pydantic import BaseModel, Field, ConfigDict


class User(BaseModel):
    """ユーザーモデル"""
    
    model_config = ConfigDict(
        strict=True,
        frozen=True,
    )
    
    id: int = Field(..., gt=0, description="ユーザーID")
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    is_active: bool = Field(default=True)
```

#### 値オブジェクト

```python
from pydantic import BaseModel, Field, ConfigDict


class UserId(BaseModel):
    """ユーザーID値オブジェクト"""
    
    model_config = ConfigDict(frozen=True)
    
    value: int = Field(..., gt=0)


class Email(BaseModel):
    """メールアドレス値オブジェクト"""
    
    model_config = ConfigDict(frozen=True)
    
    value: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
```

#### リクエスト/レスポンス

```python
from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    """ユーザー作成リクエスト"""
    
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")


class CreateUserResponse(BaseModel):
    """ユーザー作成レスポンス"""
    
    id: int
    name: str
    email: str
    created_at: str
```

### 型アノテーション規則

#### 必須パターン

```python
from collections.abc import Sequence
from typing import Final

# 変数には必ず型アノテーション
count: int = 0
name: str = "example"
items: list[str] = []

# 定数はFinalを使用
MAX_RETRY: Final[int] = 3
DEFAULT_TIMEOUT: Final[float] = 30.0

# 関数は引数・戻り値に型アノテーション必須
def calculate_total(prices: Sequence[int], tax_rate: float) -> int:
    """合計金額を計算する"""
    subtotal: int = sum(prices)
    total: int = int(subtotal * (1 + tax_rate))
    return total
```

#### 禁止パターン

```python
# ❌ 禁止: 型アノテーションなし
def bad_function(x, y):
    return x + y

# ❌ 禁止: Any型の使用
from typing import Any
def process(data: Any) -> Any:
    pass

# ❌ 禁止: Union型の乱用
from typing import Union
value: Union[int, str, None] = None  # 避ける

# ❌ 禁止: dict[str, Any]
config: dict[str, Any] = {}  # 避ける
```

#### 推奨パターン（Union型を避ける）

```python
# ✅ 推奨: 具体的な型を定義
from pydantic import BaseModel


class SuccessResult(BaseModel):
    """成功結果"""
    value: int
    message: str


class ErrorResult(BaseModel):
    """エラー結果"""
    error_code: str
    error_message: str


# 結果型を使う場合はResult patternで
class ProcessResult(BaseModel):
    """処理結果"""
    success: bool
    data: SuccessResult | None = None
    error: ErrorResult | None = None
    
    @classmethod
    def ok(cls, value: int, message: str) -> "ProcessResult":
        return cls(
            success=True,
            data=SuccessResult(value=value, message=message),
        )
    
    @classmethod
    def fail(cls, code: str, message: str) -> "ProcessResult":
        return cls(
            success=False,
            error=ErrorResult(error_code=code, error_message=message),
        )
```

### Optionalの扱い

```python
from pydantic import BaseModel, Field


class SearchParams(BaseModel):
    """検索パラメータ"""
    
    # Noneを許容する場合は明示的に
    query: str
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    category_id: int | None = Field(default=None)  # 明示的にNone許容
```

## 実装ワークフロー

### 1. 型定義の作成

最初に pydantic モデルで型を定義：

```bash
# ファイル作成
touch src/models/user.py
```

### 2. インターフェース実装

Protocol を使用した抽象化：

```python
from typing import Protocol
from collections.abc import Sequence

from models.user import User, UserId


class UserRepository(Protocol):
    """ユーザーリポジトリインターフェース"""
    
    def find_by_id(self, user_id: UserId) -> User | None:
        """IDでユーザーを検索"""
        ...
    
    def find_all(self) -> Sequence[User]:
        """全ユーザーを取得"""
        ...
    
    def save(self, user: User) -> User:
        """ユーザーを保存"""
        ...
```

### 3. 実装

```python
from collections.abc import Sequence

from models.user import User, UserId
from repositories.user_repository import UserRepository


class InMemoryUserRepository:
    """インメモリユーザーリポジトリ実装"""
    
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
    
    def find_by_id(self, user_id: UserId) -> User | None:
        return self._users.get(user_id.value)
    
    def find_all(self) -> Sequence[User]:
        return list(self._users.values())
    
    def save(self, user: User) -> User:
        self._users[user.id] = user
        return user
```

### 4. 型チェック実行

```bash
# mypy で型チェック（エラー0件必須）
uv run mypy src/

# エラーがある場合は必ず修正
# 以下のような回避は禁止
# type: ignore  # 禁止
# cast()の乱用  # 禁止
```

### 5. コード整形

```bash
# black で整形
uv run black src/ tests/

# 整形チェック（CI用）
uv run black --check src/ tests/
```

### 6. テスト実行

```bash
# pytest 実行
uv run pytest tests/ -v
```

## コマンドチートシート

```bash
# 環境構築
uv init                     # プロジェクト初期化
uv venv                     # 仮想環境作成
uv add <package>            # パッケージ追加
uv add --dev <package>      # 開発用パッケージ追加
uv sync                     # 依存関係同期
uv lock                     # lockファイル更新

# 開発
uv run python script.py     # スクリプト実行
uv run mypy src/            # 型チェック
uv run black src/ tests/    # コード整形
uv run pytest tests/ -v     # テスト実行

# 確認
uv pip list                 # インストール済みパッケージ一覧
uv tree                     # 依存関係ツリー
```

## ディレクトリ構造

```
project/
├── pyproject.toml
├── uv.lock
├── src/
│   ├── __init__.py
│   ├── models/           # pydantic モデル
│   │   ├── __init__.py
│   │   └── user.py
│   ├── repositories/     # リポジトリ
│   │   ├── __init__.py
│   │   └── user_repository.py
│   ├── services/         # ビジネスロジック
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── main.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_user_service.py
```

## チェックリスト

### 実装前

- [ ] uv でプロジェクト初期化済み
- [ ] pydantic, mypy, black インストール済み
- [ ] pyproject.toml 設定済み

### 実装中

- [ ] 全ての型を pydantic モデルで定義
- [ ] 全ての関数に型アノテーション
- [ ] Union型を極力使用しない
- [ ] Any型を使用しない

### 実装後

- [ ] `uv run mypy src/` エラー0件
- [ ] `uv run black src/ tests/` 実行済み
- [ ] `uv run pytest tests/` 全パス

## スキル連携

| スキル | 呼び出しタイミング |
|--------|-------------------|
| test-first-development | 実装完了後、テスト実行依頼 |
| code-reviewer | 全テストパス後、レビュー依頼 |
