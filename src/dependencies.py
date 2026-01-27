"""依存性注入・共通ユーティリティ"""

from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.config import settings


# Jinja2テンプレート設定
templates = Jinja2Templates(directory=settings.templates_dir)


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
        return templates.TemplateResponse(
            request=self.request,
            name=template_name,
            context=self.context,
        )
