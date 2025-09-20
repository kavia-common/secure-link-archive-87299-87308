def test_health_check(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json().get("message") == "Healthy"
