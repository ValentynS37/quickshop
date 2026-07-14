from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    settings = Settings(
        app_env="test",
        bads_api_key="test-key",
        database_url="sqlite:///:memory:",
        openai_api_key=None,
        cors_origins=["http://testserver"],
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture()
def headers() -> dict[str, str]:
    return {"X-BADS-API-Key": "test-key"}
