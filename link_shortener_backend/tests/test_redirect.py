from unittest.mock import patch
import pytest


@pytest.mark.usefixtures("ensure_redirect_routes")
def test_redirect_serves_archived_with_header(client):
    code = "deadbeef"
    original_url = "https://example.org/article"
    archived_norm = "Archived Title\nArchived Body Line 1\nArchived Body Line 2"

    fake_rec = {
        "id": "abc123",
        "code": code,
        "original_url": original_url,
        "archived_at": "2024-01-01T00:00:00+00:00",
        "archive_file": "/tmp/archives/deadbeef.txt",
        "content_type": "text/html",
        "note": None,
    }

    with patch("src.api.services.get_record_by_code", return_value=fake_rec), \
         patch("src.api.services.get_archived_content", return_value=archived_norm):
        resp = client.get(f"/r/{code}")

    # The redirect endpoint should return HTML, include some floating header markers, and include archived content
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    text = resp.text
    # Expect floating header hooks: CSS/JS endpoints referenced
    assert "/api/header/style.css" in text
    assert "/api/header/script.js" in text
    # Archived content presence (normalized)
    assert "Archived Title" in text


@pytest.mark.usefixtures("ensure_redirect_routes")
def test_redirect_not_found_returns_404(client):
    with patch("src.api.services.get_record_by_code", return_value=None):
        resp = client.get("/r/unknown123")
    assert resp.status_code == 404
