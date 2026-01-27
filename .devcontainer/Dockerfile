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
