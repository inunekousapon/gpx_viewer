---
name: fastapi-jinja2
description: FastAPI + Jinja2によるテンプレートベースのWebアプリケーション実装スキル。APIではなくHTMLテンプレート出力に特化。Docker Dev Container構成での開発環境を提供。使用タイミング：(1) Webアプリケーション新規開発、(2) サーバーサイドレンダリング実装、(3) 管理画面・ダッシュボード構築、(4) フォームベースのアプリケーション開発。
---

# FastAPI + Jinja2 Template Skill

FastAPI と Jinja2 を使用したテンプレートベース Web アプリケーション実装スキル。

## 基本方針

| 項目 | 方針 |
|------|------|
| レンダリング | **サーバーサイド（SSR）** |
| テンプレート | **Jinja2** |
| 出力形式 | **HTML**（JSON API ではない） |
| 開発環境 | **Docker Dev Container** |
| パッケージ管理 | **uv**（pip 禁止） |

## プロジェクト構造

```
project/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── home.py
│   │   └── users.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── components/
│   │   │   ├── header.html
│   │   │   ├── footer.html
│   │   │   └── flash_messages.html
│   │   ├── home/
│   │   │   └── index.html
│   │   └── users/
│   │       ├── list.html
│   │       ├── detail.html
│   │       └── form.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   └── services/
│       ├── __init__.py
│       └── user_service.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_home.py
```

## Dev Container 構成

### .devcontainer/devcontainer.json

```json
{
  "name": "FastAPI Jinja2 Dev",
  "dockerComposeFile": ["../docker-compose.yml"],
  "service": "app",
  "workspaceFolder": "/workspace",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.mypy-type-checker",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "samuelcolvin.jinjahtml",
        "bradlc.vscode-tailwindcss"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/workspace/.venv/bin/python",
        "python.analysis.typeCheckingMode": "strict",
        "[python]": {
          "editor.defaultFormatter": "ms-python.black-formatter",
          "editor.formatOnSave": true
        },
        "[jinja-html]": {
          "editor.defaultFormatter": "esbenp.prettier-vscode"
        }
      }
    }
  },
  "postCreateCommand": "uv sync",
  "remoteUser": "vscode"
}
```

### .devcontainer/Dockerfile

```dockerfile
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# uv インストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 作業ディレクトリ
WORKDIR /workspace

# 非rootユーザー設定
USER vscode

# uv の設定
ENV UV_LINK_MODE=copy
ENV PATH="/workspace/.venv/bin:$PATH"
```

### docker-compose.yml

```yaml
services:
  app:
    build:
      context: .
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - .:/workspace:cached
    ports:
      - "8000:8000"
    environment:
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
    command: sleep infinity
```

## 依存関係

### pyproject.toml

```toml
[project]
name = "webapp"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.12",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.0",
    "black>=24.0",
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

[tool.black]
line-length = 88
target-version = ["py312"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

## コア実装

### src/config.py

```python
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    app_name: str = "Web Application"
    debug: bool = False
    
    # パス設定
    base_dir: Path = Path(__file__).resolve().parent
    templates_dir: Path = base_dir / "templates"
    static_dir: Path = base_dir / "static"


settings = Settings()
```

### src/dependencies.py

```python
from fastapi import Request
from fastapi.templating import Jinja2Templates
from typing import Any

from config import settings


# Jinja2テンプレート設定
templates = Jinja2Templates(directory=settings.templates_dir)


def flash(request: Request, message: str, category: str = "info") -> None:
    """フラッシュメッセージを追加"""
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


def get_flashed_messages(request: Request) -> list[dict[str, str]]:
    """フラッシュメッセージを取得してクリア"""
    messages: list[dict[str, str]] = request.session.pop("_messages", [])
    return messages


class TemplateResponse:
    """テンプレートレスポンスヘルパー"""
    
    def __init__(self, request: Request) -> None:
        self.request = request
        self.context: dict[str, Any] = {
            "request": request,
            "app_name": settings.app_name,
        }
    
    def add_context(self, **kwargs: Any) -> "TemplateResponse":
        """コンテキストを追加"""
        self.context.update(kwargs)
        return self
    
    def render(self, template_name: str) -> Any:
        """テンプレートをレンダリング"""
        self.context["messages"] = get_flashed_messages(self.request)
        return templates.TemplateResponse(
            request=self.request,
            name=template_name,
            context=self.context,
        )
```

### src/main.py

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from config import settings
from routers import home, users


def create_app() -> FastAPI:
    """アプリケーションファクトリ"""
    app = FastAPI(
        title=settings.app_name,
        docs_url=None,  # Swagger UI 無効化
        redoc_url=None,  # ReDoc 無効化
        openapi_url=None,  # OpenAPI スキーマ無効化
    )
    
    # ミドルウェア
    app.add_middleware(
        SessionMiddleware,
        secret_key="your-secret-key-change-in-production",
    )
    
    # 静的ファイル
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
    
    # ルーター
    app.include_router(home.router)
    app.include_router(users.router, prefix="/users")
    
    return app


app = create_app()
```

### src/routers/home.py

```python
from fastapi import APIRouter, Request

from dependencies import TemplateResponse


router = APIRouter()


@router.get("/")
def index(request: Request) -> TemplateResponse:
    """ホームページ"""
    return (
        TemplateResponse(request)
        .add_context(title="ホーム")
        .render("home/index.html")
    )
```

### src/routers/users.py

```python
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from dependencies import TemplateResponse, flash
from models.user import User, CreateUserForm
from services.user_service import UserService


router = APIRouter()


@router.get("/")
def user_list(request: Request) -> TemplateResponse:
    """ユーザー一覧"""
    service = UserService()
    users = service.get_all()
    
    return (
        TemplateResponse(request)
        .add_context(title="ユーザー一覧", users=users)
        .render("users/list.html")
    )


@router.get("/new")
def user_new(request: Request) -> TemplateResponse:
    """ユーザー作成フォーム"""
    return (
        TemplateResponse(request)
        .add_context(title="新規ユーザー", form=CreateUserForm())
        .render("users/form.html")
    )


@router.post("/new")
def user_create(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
) -> RedirectResponse:
    """ユーザー作成処理"""
    form = CreateUserForm(name=name, email=email)
    
    # バリデーション
    if not form.is_valid():
        flash(request, "入力内容にエラーがあります", "error")
        return (
            TemplateResponse(request)
            .add_context(title="新規ユーザー", form=form)
            .render("users/form.html")
        )
    
    # 保存
    service = UserService()
    service.create(form)
    
    flash(request, "ユーザーを作成しました", "success")
    return RedirectResponse(url="/users", status_code=303)


@router.get("/{user_id}")
def user_detail(request: Request, user_id: int) -> TemplateResponse:
    """ユーザー詳細"""
    service = UserService()
    user = service.get_by_id(user_id)
    
    return (
        TemplateResponse(request)
        .add_context(title=f"ユーザー: {user.name}", user=user)
        .render("users/detail.html")
    )
```

## テンプレート

### src/templates/base.html

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ app_name }}{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', path='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    {% include "components/header.html" %}
    
    <main class="container">
        {% include "components/flash_messages.html" %}
        {% block content %}{% endblock %}
    </main>
    
    {% include "components/footer.html" %}
    
    <script src="{{ url_for('static', path='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### src/templates/components/flash_messages.html

```html
{% if messages %}
<div class="flash-messages">
    {% for msg in messages %}
    <div class="alert alert-{{ msg.category }}">
        {{ msg.message }}
        <button type="button" class="close" onclick="this.parentElement.remove()">×</button>
    </div>
    {% endfor %}
</div>
{% endif %}
```

### src/templates/components/header.html

```html
<header class="header">
    <nav class="nav">
        <a href="/" class="nav-brand">{{ app_name }}</a>
        <ul class="nav-menu">
            <li><a href="/">ホーム</a></li>
            <li><a href="/users">ユーザー</a></li>
        </ul>
    </nav>
</header>
```

### src/templates/components/footer.html

```html
<footer class="footer">
    <p>&copy; 2026 {{ app_name }}. All rights reserved.</p>
</footer>
```

### src/templates/home/index.html

```html
{% extends "base.html" %}

{% block title %}{{ title }} - {{ app_name }}{% endblock %}

{% block content %}
<h1>{{ title }}</h1>
<p>ようこそ {{ app_name }} へ</p>
{% endblock %}
```

### src/templates/users/list.html

```html
{% extends "base.html" %}

{% block title %}{{ title }} - {{ app_name }}{% endblock %}

{% block content %}
<h1>{{ title }}</h1>

<a href="/users/new" class="btn btn-primary">新規作成</a>

<table class="table">
    <thead>
        <tr>
            <th>ID</th>
            <th>名前</th>
            <th>メール</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>
                <a href="/users/{{ user.id }}">詳細</a>
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="4">ユーザーがいません</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

### src/templates/users/form.html

```html
{% extends "base.html" %}

{% block title %}{{ title }} - {{ app_name }}{% endblock %}

{% block content %}
<h1>{{ title }}</h1>

<form method="post" class="form">
    <div class="form-group">
        <label for="name">名前</label>
        <input 
            type="text" 
            id="name" 
            name="name" 
            value="{{ form.name or '' }}"
            class="form-control {% if form.errors.name %}is-invalid{% endif %}"
            required
        >
        {% if form.errors.name %}
        <div class="invalid-feedback">{{ form.errors.name }}</div>
        {% endif %}
    </div>
    
    <div class="form-group">
        <label for="email">メールアドレス</label>
        <input 
            type="email" 
            id="email" 
            name="email" 
            value="{{ form.email or '' }}"
            class="form-control {% if form.errors.email %}is-invalid{% endif %}"
            required
        >
        {% if form.errors.email %}
        <div class="invalid-feedback">{{ form.errors.email }}</div>
        {% endif %}
    </div>
    
    <button type="submit" class="btn btn-primary">保存</button>
    <a href="/users" class="btn btn-secondary">キャンセル</a>
</form>
{% endblock %}
```

## モデル・フォーム

### src/models/user.py

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Any


class User(BaseModel):
    """ユーザーモデル"""
    
    model_config = ConfigDict(frozen=True)
    
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(...)


class CreateUserForm(BaseModel):
    """ユーザー作成フォーム"""
    
    name: str = ""
    email: str = ""
    errors: dict[str, str] = Field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """バリデーション実行"""
        self.errors = {}
        
        if not self.name:
            self.errors["name"] = "名前は必須です"
        elif len(self.name) > 100:
            self.errors["name"] = "名前は100文字以内で入力してください"
        
        if not self.email:
            self.errors["email"] = "メールアドレスは必須です"
        elif "@" not in self.email:
            self.errors["email"] = "有効なメールアドレスを入力してください"
        
        return len(self.errors) == 0
```

## 開発コマンド

```bash
# Dev Container 起動後

# 依存関係インストール
uv sync

# 開発サーバー起動
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 型チェック
uv run mypy src/

# コード整形
uv run black src/ tests/

# テスト実行
uv run pytest tests/ -v
```

## テスト

### tests/conftest.py

```python
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """テストクライアント"""
    return TestClient(app)
```

### tests/test_home.py

```python
from fastapi.testclient import TestClient


def test_home_returns_html(client: TestClient) -> None:
    """ホームページがHTMLを返す"""
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "ホーム" in response.text
```

## チェックリスト

### Dev Container

- [ ] devcontainer.json 作成済み
- [ ] Dockerfile 作成済み
- [ ] docker-compose.yml 作成済み
- [ ] VS Code 拡張機能設定済み

### 実装

- [ ] API エンドポイント無効化（docs_url=None 等）
- [ ] Jinja2 テンプレート設定済み
- [ ] 静的ファイル設定済み
- [ ] セッションミドルウェア設定済み
- [ ] フラッシュメッセージ実装済み

### テンプレート

- [ ] base.html（レイアウト）
- [ ] コンポーネント分離
- [ ] フォームバリデーション表示

## スキル連携

| スキル | 呼び出しタイミング |
|--------|-------------------|
| python-implementation | Python コード実装時 |
| test-first-development | テスト実装時 |
| code-reviewer | 実装完了後のレビュー |
