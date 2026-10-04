from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.auth import AuthenticatedUser, get_authenticated_user
from app.main import app
from app.storage import subscribers
from app.storage.db import get_session


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_authenticated_user] = lambda: AuthenticatedUser(
        id="user-1",
        email="reader@example.com",
    )
    app.dependency_overrides[get_session] = lambda: object()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_preferences_default_to_unsubscribed(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def no_subscriber(*_args: object) -> None:
        return None

    monkeypatch.setattr(subscribers, "get_subscriber", no_subscriber)

    response = client.get("/api/preferences")

    assert response.status_code == 200
    assert response.json() == {
        "enabled": False,
        "topics": [
            "research",
            "labs",
            "startups",
            "security",
            "tooling",
        ],
    }


def test_update_preferences_persists_authenticated_email(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saved: dict[str, object] = {}

    async def save_preferences(
        _session: object,
        **values: object,
    ) -> SimpleNamespace:
        saved.update(values)
        return SimpleNamespace(
            active=values["enabled"],
            topics=",".join(values["topics"]),  # type: ignore[arg-type]
        )

    monkeypatch.setattr(subscribers, "save_preferences", save_preferences)

    response = client.put(
        "/api/preferences",
        json={"enabled": True, "topics": ["research", "security"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "enabled": True,
        "topics": ["research", "security"],
    }
    assert saved == {
        "user_id": "user-1",
        "email": "reader@example.com",
        "enabled": True,
        "topics": ["research", "security"],
    }


def test_update_preferences_rejects_empty_topics(client: TestClient) -> None:
    response = client.put(
        "/api/preferences",
        json={"enabled": True, "topics": []},
    )

    assert response.status_code == 422
