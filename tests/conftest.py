"""pytest設定"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """テストクライアント"""
    return TestClient(app)
