"""E2E full flow test — simulates a complete customer journey through Stripe."""

from unittest.mock import patch, MagicMock


class TestFullCustomerFlow:
    """End-to-end: signup -> create product -> checkout -> payment -> cancel."""

    @patch("app.stripe_service.stripe.billing_portal.Session.create")
    @patch("app.stripe_service.stripe.Subscription.cancel")
    @patch("app.stripe_service.stripe.Subscription.list")
    @patch("app.stripe_service.stripe.checkout.Session.create")
    @patch("app.stripe_service.stripe.Price.create")
    @patch("app.stripe_service.stripe.Product.create")
    @patch("app.stripe_service.stripe.Customer.create")
    def test_full_subscription_lifecycle(
        self,
        mock_cust_create,
        mock_prod_create,
        mock_price_create,
        mock_checkout_create,
        mock_sub_list,
        mock_sub_cancel,
        mock_portal_create,
        client,
    ):
        # Step 1: Create customer
        mock_cust_create.return_value = MagicMock(
            id="cus_flow_001", email="alexa@blackroad.io"
        )
        resp = client.post("/api/v1/customers", json={
            "email": "alexa@blackroad.io",
            "name": "Alexa Amundson",
            "metadata": {"org": "BlackRoad OS, Inc."},
        })
        assert resp.status_code == 201
        customer_id = resp.get_json()["customer_id"]
        assert customer_id == "cus_flow_001"

        # Step 2: Create product
        prod = MagicMock(id="prod_flow_001")
        prod.name = "BlackRoad Agent - Pro"
        mock_prod_create.return_value = prod
        price = MagicMock(id="price_flow_001")
        price.unit_amount = 4999
        price.currency = "usd"
        mock_price_create.return_value = price
        resp = client.post("/api/v1/products", json={
            "product_key": "blackroad-agent-pro",
        })
        assert resp.status_code == 201
        price_id = resp.get_json()["price_id"]
        assert price_id == "price_flow_001"

        # Step 3: Create checkout session
        mock_checkout_create.return_value = MagicMock(
            id="cs_flow_001", url="https://checkout.stripe.com/pay/cs_flow_001"
        )
        resp = client.post("/api/v1/checkout/session", json={
            "price_id": price_id,
            "customer_id": customer_id,
            "success_url": "https://edge.blackroad.io/success",
            "cancel_url": "https://edge.blackroad.io/cancel",
        })
        assert resp.status_code == 201
        session_data = resp.get_json()
        assert session_data["session_id"] == "cs_flow_001"
        assert "checkout.stripe.com" in session_data["url"]

        # Step 4: List subscriptions (after payment completes via webhook)
        mock_sub_list.return_value = MagicMock(data=[
            MagicMock(id="sub_flow_001", status="active", current_period_end=1700000000),
        ])
        resp = client.get(f"/api/v1/subscriptions/{customer_id}")
        assert resp.status_code == 200
        subs = resp.get_json()["subscriptions"]
        assert len(subs) == 1
        assert subs[0]["status"] == "active"

        # Step 5: Access billing portal
        mock_portal_create.return_value = MagicMock(
            url="https://billing.stripe.com/session/flow_001"
        )
        resp = client.post("/api/v1/billing-portal", json={
            "customer_id": customer_id,
            "return_url": "https://edge.blackroad.io/account",
        })
        assert resp.status_code == 200
        assert "billing.stripe.com" in resp.get_json()["url"]

        # Step 6: Cancel subscription
        mock_sub_cancel.return_value = MagicMock(
            id="sub_flow_001", status="canceled"
        )
        resp = client.post("/api/v1/subscriptions/sub_flow_001/cancel")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "canceled"

    @patch("app.stripe_service.stripe.PaymentIntent.create")
    @patch("app.stripe_service.stripe.Customer.create")
    def test_one_time_payment_flow(self, mock_cust_create, mock_pi_create, client):
        # Step 1: Create customer
        mock_cust_create.return_value = MagicMock(
            id="cus_onetime_001", email="user@blackroad.io"
        )
        resp = client.post("/api/v1/customers", json={
            "email": "user@blackroad.io",
        })
        assert resp.status_code == 201
        customer_id = resp.get_json()["customer_id"]

        # Step 2: Create payment intent
        mock_pi_create.return_value = MagicMock(
            id="pi_onetime_001",
            client_secret="pi_onetime_001_secret",
            status="requires_payment_method",
        )
        resp = client.post("/api/v1/payment-intent", json={
            "amount": 15000,
            "currency": "usd",
            "customer_id": customer_id,
            "metadata": {"product": "blackroad-agent-enterprise-addon"},
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["payment_intent_id"] == "pi_onetime_001"
        assert data["client_secret"] == "pi_onetime_001_secret"
        assert data["status"] == "requires_payment_method"

    def test_cluster_routing_during_flow(self, client):
        """Verify the cluster routing info is available during payment flows."""
        resp = client.get("/api/v1/cluster/status")
        assert resp.status_code == 200
        nodes = resp.get_json()["nodes"]

        # All 4 Pi nodes should be reachable
        assert len(nodes) == 4
        assert nodes["blackroad-pi"]["role"] == "gateway"
        assert nodes["aria64"]["role"] == "worker"
        assert nodes["alice"]["role"] == "worker"
        assert nodes["lucidia-alt"]["role"] == "worker"
