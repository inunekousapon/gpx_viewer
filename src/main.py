"""FastAPIアプリケーション"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.routers import home, api


def create_app() -> FastAPI:
    """アプリケーションファクトリ"""
    app = FastAPI(
        title=settings.app_name,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    # 静的ファイル
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

    # ルーター
    app.include_router(home.router)
    app.include_router(api.router)

    return app


app = create_app()
