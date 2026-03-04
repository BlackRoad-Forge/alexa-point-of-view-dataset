"""E2E tests — checkout, payment intent, and subscription endpoints."""

from unittest.mock import patch, MagicMock


def _mock_session(id="cs_test_abc", url="https://checkout.stripe.com/test"):
    s = MagicMock()
    s.id = id
    s.url = url
    return s


def _mock_intent(id="pi_test_xyz", client_secret="pi_test_xyz_secret_abc", status="requires_payment_method"):
    i = MagicMock()
    i.id = id
    i.client_secret = client_secret
    i.status = status
    return i


def _mock_subscription(id="sub_test_123", status="active", current_period_end=1700000000):
    s = MagicMock()
    s.id = id
    s.status = status
    s.current_period_end = current_period_end
    return s


# --- Checkout Session ---

@patch("app.stripe_service.stripe.checkout.Session.create")
def test_create_checkout_session(mock_create, client):
    mock_create.return_value = _mock_session()

    resp = client.post("/api/v1/checkout/session", json={
        "price_id": "price_test_abc",
        "customer_id": "cus_test123",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["session_id"] == "cs_test_abc"
    assert "checkout.stripe.com" in data["url"]


def test_create_checkout_missing_price(client):
    resp = client.post("/api/v1/checkout/session", json={})
    assert resp.status_code == 400
    assert "price_id" in resp.get_json()["error"]


# --- Payment Intent ---

@patch("app.stripe_service.stripe.PaymentIntent.create")
def test_create_payment_intent(mock_create, client):
    mock_create.return_value = _mock_intent()

    resp = client.post("/api/v1/payment-intent", json={
        "amount": 5000,
        "currency": "usd",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["payment_intent_id"] == "pi_test_xyz"
    assert data["client_secret"] == "pi_test_xyz_secret_abc"
    assert data["status"] == "requires_payment_method"


def test_create_payment_intent_missing_amount(client):
    resp = client.post("/api/v1/payment-intent", json={})
    assert resp.status_code == 400


@patch("app.stripe_service.stripe.PaymentIntent.create")
def test_create_payment_intent_with_customer(mock_create, client):
    mock_create.return_value = _mock_intent()

    resp = client.post("/api/v1/payment-intent", json={
        "amount": 9999,
        "customer_id": "cus_test123",
        "metadata": {"order": "blackroad-agent-pro"},
    })
    assert resp.status_code == 201
    mock_create.assert_called_once()
    call_kwargs = mock_create.call_args[1]
    assert call_kwargs["customer"] == "cus_test123"
    assert call_kwargs["metadata"] == {"order": "blackroad-agent-pro"}


# --- Subscriptions ---

@patch("app.stripe_service.stripe.Subscription.list")
def test_list_subscriptions(mock_list, client):
    mock_list.return_value = MagicMock(data=[_mock_subscription()])

    resp = client.get("/api/v1/subscriptions/cus_test123")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["subscriptions"]) == 1
    assert data["subscriptions"][0]["id"] == "sub_test_123"
    assert data["subscriptions"][0]["status"] == "active"


@patch("app.stripe_service.stripe.Subscription.cancel")
def test_cancel_subscription(mock_cancel, client):
    mock_cancel.return_value = _mock_subscription(status="canceled")

    resp = client.post("/api/v1/subscriptions/sub_test_123/cancel")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "canceled"


# --- Billing Portal ---

@patch("app.stripe_service.stripe.billing_portal.Session.create")
def test_billing_portal(mock_create, client):
    mock_portal = MagicMock()
    mock_portal.url = "https://billing.stripe.com/session/test"
    mock_create.return_value = mock_portal

    resp = client.post("/api/v1/billing-portal", json={
        "customer_id": "cus_test123",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "billing.stripe.com" in data["url"]


def test_billing_portal_missing_customer(client):
    resp = client.post("/api/v1/billing-portal", json={})
    assert resp.status_code == 400


# --- Products ---

@patch("app.stripe_service.stripe.Price.create")
@patch("app.stripe_service.stripe.Product.create")
def test_create_product(mock_product, mock_price, client):
    prod = MagicMock(id="prod_test")
    prod.name = "BlackRoad Agent - Basic"
    mock_product.return_value = prod
    price = MagicMock(id="price_test")
    price.unit_amount = 999
    price.currency = "usd"
    mock_price.return_value = price

    resp = client.post("/api/v1/products", json={
        "product_key": "blackroad-agent-basic",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["product_id"] == "prod_test"
    assert data["price_id"] == "price_test"
    assert data["amount"] == 999


def test_create_product_unknown_key(client):
    resp = client.post("/api/v1/products", json={
        "product_key": "nonexistent-product",
    })
    assert resp.status_code == 400
