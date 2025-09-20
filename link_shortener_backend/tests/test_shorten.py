from datetime import datetime, timezone
from unittest.mock import patch

import pytest


@pytest.mark.usefixtures("ensure_shorten_routes")
def test_shorten_happy_path(client, monkeypatch):
    # Arrange: deterministic get_base_url and archive_url
    monkeypatch.setenv("BACKEND_BASE_URL", "http://api.example.com")

    fake_rec = {
        "id": "abc123",
        "code": "deadbeef",
        "original_url": "https://example.org/article",
        "archived_at": datetime(2024, 1, 1, tzinfo=timezone.utc).isoformat(),
        "archive_file": "/tmp/archives/deadbeef.txt",
        "content_type": "text/html",
        "note": "hello",
    }

    with patch("src.api.services.archive_url", return_value=fake_rec) as mock_archive, \
         patch("src.api.services.get_base_url", return_value="http://api.example.com"):
        # Act
        resp = client.post("/api/urls/shorten", json={"url": fake_rec["original_url"], "note": "hello"})

    # Assert
    assert resp.status_code in (200, 201)
    data = resp.json()
    # Expected response fields based on models.ShortenResponse (id, code, short_url, original_url, archived_at)
    assert data["id"] == fake_rec["id"]
    assert data["code"] == fake_rec["code"]
    assert data["original_url"] == fake_rec["original_url"]
    assert "short_url" in data
    assert data["short_url"].startswith("http://api.example.com")
    # Ensure service used
    mock_archive.assert_called_once_with(fake_rec["original_url"], note="hello")


@pytest.mark.usefixtures("ensure_shorten_routes")
def test_shorten_invalid_url_returns_400(client):
    # Provide an invalid URL string; request validation should fail or endpoint should handle and return 400
    resp = client.post("/api/urls/shorten", json={"url": "notaurl"})
    assert resp.status_code in (400, 422)  # 422 for Pydantic validation, 400 if endpoint validates differently
