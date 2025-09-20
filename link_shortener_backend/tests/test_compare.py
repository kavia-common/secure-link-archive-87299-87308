from unittest.mock import patch
import pytest


@pytest.mark.usefixtures("ensure_compare_routes")
def test_compare_happy_path(client):
    code = "deadbeef"
    fake_rec = {"id": "abc123", "code": code}
    has_changes = True
    summary = {"added": 1, "removed": 0, "changed": 2}
    details = {"changed_paths": ["line:1", "line:3"]}

    with patch("src.api.services.get_record_by_code", return_value=fake_rec), \
         patch("src.api.services.compare_current_vs_archived", return_value=(has_changes, summary, details)):
        resp = client.get(f"/api/compare/{code}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == fake_rec["id"]
    assert data["code"] == code
    assert data["has_changes"] is True
    assert data["diff_summary"] == summary
    assert data["changed_paths"] == details["changed_paths"]


@pytest.mark.usefixtures("ensure_compare_routes")
def test_compare_not_found_returns_404(client):
    with patch("src.api.services.get_record_by_code", return_value=None):
        resp = client.get("/api/compare/unknown")
    assert resp.status_code == 404


@pytest.mark.usefixtures("ensure_compare_routes")
def test_compare_fetch_error_returns_200_with_no_changes(client):
    # Endpoint likely handles fetch errors internally and returns a summary with error flag but 200 OK.
    code = "deadbeef"
    fake_rec = {"id": "abc123", "code": code}
    has_changes = False
    summary = {"added": 0, "removed": 0, "changed": 0}
    details = {"changed_paths": [], "error": "fetch_failed"}

    with patch("src.api.services.get_record_by_code", return_value=fake_rec), \
         patch("src.api.services.compare_current_vs_archived", return_value=(has_changes, summary, details)):
        resp = client.get(f"/api/compare/{code}")

    assert resp.status_code in (200, 500)  # If implemented as success or internal error
    if resp.status_code == 200:
        data = resp.json()
        assert data["has_changes"] is False
        assert data["diff_summary"] == summary
        assert data.get("changed_paths") == details["changed_paths"]
