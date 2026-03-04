"""E2E tests — health, config, and cluster status endpoints."""


def test_health_returns_ok(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["node"] == "test-node"
    assert data["ip"] == "127.0.0.1"


def test_cluster_status(client):
    resp = client.get("/api/v1/cluster/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "nodes" in data
    assert "blackroad-pi" in data["nodes"]
    assert "aria64" in data["nodes"]
    assert "alice" in data["nodes"]
    assert "lucidia-alt" in data["nodes"]
    assert data["nodes"]["blackroad-pi"]["ip"] == "192.168.4.64"
    assert data["nodes"]["aria64"]["ip"] == "192.168.4.38"
    assert data["current_node"] == "test-node"


def test_config_returns_publishable_key(client):
    resp = client.get("/api/v1/config")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "publishable_key" in data
    assert data["publishable_key"].startswith("pk_test_")
