def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_readyz(client):
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_metrics(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
    assert "portfolio_platform_build_info" in r.text


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "portfolio-platform-api"
