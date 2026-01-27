"""アプリケーション設定"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""

    app_name: str = "GPX Map Viewer"
    debug: bool = False

    # パス設定
    base_dir: Path = Path(__file__).resolve().parent
    templates_dir: Path = base_dir / "templates"
    static_dir: Path = base_dir / "static"

    # ファイルアップロード設定
    max_upload_size: int = 50 * 1024 * 1024  # 50MB


settings = Settings()
