"""E2E tests — Stripe webhook handling."""

import json
from unittest.mock import patch, MagicMock


def test_webhook_missing_signature(client):
    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=json.dumps({"type": "test"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "signature" in resp.get_json()["error"]


@patch("app.stripe_service.stripe.Webhook.construct_event")
def test_webhook_checkout_completed(mock_construct, client):
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_abc",
                "customer": "cus_test123",
                "subscription": "sub_test_456",
            }
        },
    }

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=json.dumps({"id": "evt_test"}),
        content_type="application/json",
        headers={"Stripe-Signature": "t=123,v1=fakesig"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


@patch("app.stripe_service.stripe.Webhook.construct_event")
def test_webhook_subscription_created(mock_construct, client):
    mock_construct.return_value = {
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_test_789",
                "customer": "cus_test123",
                "status": "active",
            }
        },
    }

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=json.dumps({"id": "evt_test2"}),
        content_type="application/json",
        headers={"Stripe-Signature": "t=123,v1=fakesig"},
    )
    assert resp.status_code == 200


@patch("app.stripe_service.stripe.Webhook.construct_event")
def test_webhook_payment_succeeded(mock_construct, client):
    mock_construct.return_value = {
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_test_100",
                "customer": "cus_test123",
                "amount_paid": 4999,
            }
        },
    }

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=json.dumps({"id": "evt_test3"}),
        content_type="application/json",
        headers={"Stripe-Signature": "t=123,v1=fakesig"},
    )
    assert resp.status_code == 200


@patch("app.stripe_service.stripe.Webhook.construct_event")
def test_webhook_payment_failed(mock_construct, client):
    mock_construct.return_value = {
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "id": "in_test_fail",
                "customer": "cus_test123",
            }
        },
    }

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=json.dumps({"id": "evt_test4"}),
        content_type="application/json",
        headers={"Stripe-Signature": "t=123,v1=fakesig"},
    )
    assert resp.status_code == 200


@patch("app.stripe_service.stripe.Webhook.construct_event")
def test_webhook_subscription_deleted(mock_construct, client):
    mock_construct.return_value = {
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_test_cancel",
                "customer": "cus_test123",
            }
        },
    }

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=json.dumps({"id": "evt_test5"}),
        content_type="application/json",
        headers={"Stripe-Signature": "t=123,v1=fakesig"},
    )
    assert resp.status_code == 200


@patch("app.stripe_service.stripe.Webhook.construct_event")
def test_webhook_payment_intent_succeeded(mock_construct, client):
    mock_construct.return_value = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_done",
                "amount": 5000,
            }
        },
    }

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=json.dumps({"id": "evt_test6"}),
        content_type="application/json",
        headers={"Stripe-Signature": "t=123,v1=fakesig"},
    )
    assert resp.status_code == 200


@patch("app.stripe_service.stripe.Webhook.construct_event")
def test_webhook_invalid_signature(mock_construct, client):
    import stripe
    mock_construct.side_effect = stripe.error.SignatureVerificationError("bad sig", "sig")

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=json.dumps({"id": "evt_bad"}),
        content_type="application/json",
        headers={"Stripe-Signature": "t=123,v1=invalid"},
    )
    assert resp.status_code == 400
    assert "invalid signature" in resp.get_json()["error"]
