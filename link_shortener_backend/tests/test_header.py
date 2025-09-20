import pytest


@pytest.mark.usefixtures("ensure_header_routes")
def test_header_style_endpoint(client):
    resp = client.get("/api/header/style.css")
    assert resp.status_code == 200
    assert "text/css" in resp.headers.get("content-type", "")
    # Expect style to include at least a class/id marker related to header
    assert "header" in resp.text.lower()


@pytest.mark.usefixtures("ensure_header_routes")
def test_header_script_endpoint(client):
    resp = client.get("/api/header/script.js")
    assert resp.status_code == 200
    ct = resp.headers.get("content-type", "")
    # Could be application/javascript or text/javascript depending on implementation
    assert "javascript" in ct
    # Expect script to include a reference to compare or header init
    body_lower = resp.text.lower()
    assert ("compare" in body_lower) or ("header" in body_lower)
