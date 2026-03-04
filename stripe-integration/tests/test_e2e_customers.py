"""E2E tests — customer endpoints."""

from unittest.mock import patch, MagicMock


def _mock_customer(id="cus_test123", email="test@blackroad.io", name="Test User"):
    c = MagicMock()
    c.id = id
    c.email = email
    c.name = name
    return c


@patch("app.stripe_service.stripe.Customer.create")
def test_create_customer(mock_create, client):
    mock_create.return_value = _mock_customer()

    resp = client.post("/api/v1/customers", json={
        "email": "test@blackroad.io",
        "name": "Test User",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["customer_id"] == "cus_test123"
    assert data["email"] == "test@blackroad.io"


def test_create_customer_missing_email(client):
    resp = client.post("/api/v1/customers", json={})
    assert resp.status_code == 400
    assert "email" in resp.get_json()["error"]


def test_create_customer_no_body(client):
    resp = client.post("/api/v1/customers", content_type="application/json")
    assert resp.status_code == 400


@patch("app.stripe_service.stripe.Customer.retrieve")
def test_get_customer(mock_retrieve, client):
    mock_retrieve.return_value = _mock_customer()

    resp = client.get("/api/v1/customers/cus_test123")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["customer_id"] == "cus_test123"
    assert data["email"] == "test@blackroad.io"
    assert data["name"] == "Test User"


@patch("app.stripe_service.stripe.Customer.retrieve")
def test_get_customer_not_found(mock_retrieve, client):
    mock_retrieve.side_effect = Exception("No such customer")

    resp = client.get("/api/v1/customers/cus_nonexistent")
    assert resp.status_code == 404
