"""Flask routes — API endpoints for Stripe integration."""

import json
import logging
from flask import Blueprint, request, jsonify

from app import stripe_service
from app.config import NODE_NAME, NODE_IP, PI_CLUSTER, STRIPE_PUBLISHABLE_KEY

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__)


@api.route("/health", methods=["GET"])
def health():
    """Health check — returns node info."""
    return jsonify({
        "status": "ok",
        "node": NODE_NAME,
        "ip": NODE_IP,
    })


@api.route("/cluster/status", methods=["GET"])
def cluster_status():
    """Return Pi cluster node status."""
    return jsonify({
        "nodes": PI_CLUSTER,
        "current_node": NODE_NAME,
    })


@api.route("/config", methods=["GET"])
def get_config():
    """Return publishable key for frontend."""
    return jsonify({
        "publishable_key": STRIPE_PUBLISHABLE_KEY,
    })


# --- Customer endpoints ---

@api.route("/customers", methods=["POST"])
def create_customer():
    """Create a new Stripe customer."""
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "email is required"}), 400

    customer = stripe_service.create_customer(
        email=data["email"],
        name=data.get("name"),
        metadata=data.get("metadata"),
    )
    return jsonify({"customer_id": customer.id, "email": customer.email}), 201


@api.route("/customers/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    """Retrieve a Stripe customer."""
    try:
        customer = stripe_service.get_customer(customer_id)
        return jsonify({
            "customer_id": customer.id,
            "email": customer.email,
            "name": customer.name,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# --- Checkout / Payment endpoints ---

@api.route("/checkout/session", methods=["POST"])
def create_checkout():
    """Create a Stripe Checkout Session."""
    data = request.get_json()
    if not data or "price_id" not in data:
        return jsonify({"error": "price_id is required"}), 400

    session = stripe_service.create_checkout_session(
        price_id=data["price_id"],
        customer_id=data.get("customer_id"),
        success_url=data.get("success_url"),
        cancel_url=data.get("cancel_url"),
    )
    return jsonify({"session_id": session.id, "url": session.url}), 201


@api.route("/payment-intent", methods=["POST"])
def create_payment_intent():
    """Create a one-time payment intent."""
    data = request.get_json()
    if not data or "amount" not in data:
        return jsonify({"error": "amount (in cents) is required"}), 400

    intent = stripe_service.create_payment_intent(
        amount_cents=int(data["amount"]),
        currency=data.get("currency", "usd"),
        customer_id=data.get("customer_id"),
        metadata=data.get("metadata"),
    )
    return jsonify({
        "payment_intent_id": intent.id,
        "client_secret": intent.client_secret,
        "status": intent.status,
    }), 201


# --- Subscription endpoints ---

@api.route("/subscriptions/<customer_id>", methods=["GET"])
def list_subscriptions(customer_id):
    """List active subscriptions for a customer."""
    subs = stripe_service.list_subscriptions(customer_id)
    return jsonify({
        "subscriptions": [
            {"id": s.id, "status": s.status, "current_period_end": s.current_period_end}
            for s in subs.data
        ]
    })


@api.route("/subscriptions/<subscription_id>/cancel", methods=["POST"])
def cancel_subscription(subscription_id):
    """Cancel a subscription."""
    sub = stripe_service.cancel_subscription(subscription_id)
    return jsonify({"id": sub.id, "status": sub.status})


# --- Billing portal ---

@api.route("/billing-portal", methods=["POST"])
def billing_portal():
    """Create a billing portal session."""
    data = request.get_json()
    if not data or "customer_id" not in data:
        return jsonify({"error": "customer_id is required"}), 400

    session = stripe_service.create_billing_portal_session(
        customer_id=data["customer_id"],
        return_url=data.get("return_url"),
    )
    return jsonify({"url": session.url})


# --- Products ---

@api.route("/products", methods=["POST"])
def create_product():
    """Create a product + price from config."""
    data = request.get_json()
    if not data or "product_key" not in data:
        return jsonify({"error": "product_key is required"}), 400

    try:
        product, price = stripe_service.create_product_and_price(data["product_key"])
        return jsonify({
            "product_id": product.id,
            "price_id": price.id,
            "name": product.name,
            "amount": price.unit_amount,
            "currency": price.currency,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# --- Webhook ---

@api.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    """Handle incoming Stripe webhooks."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    if not sig_header:
        return jsonify({"error": "missing signature"}), 400

    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except stripe_service.stripe.error.SignatureVerificationError:
        logger.warning("Webhook signature verification failed")
        return jsonify({"error": "invalid signature"}), 400
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 400

    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info(f"Webhook received: {event_type} on node {NODE_NAME}")

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(event_data)
    elif event_type == "customer.subscription.created":
        _handle_subscription_created(event_data)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(event_data)
    elif event_type == "invoice.payment_succeeded":
        _handle_payment_succeeded(event_data)
    elif event_type == "invoice.payment_failed":
        _handle_payment_failed(event_data)
    elif event_type == "payment_intent.succeeded":
        _handle_payment_intent_succeeded(event_data)

    return jsonify({"status": "ok"}), 200


def _handle_checkout_completed(session):
    logger.info(f"Checkout completed: session={session.get('id')}, customer={session.get('customer')}")


def _handle_subscription_created(subscription):
    logger.info(f"Subscription created: {subscription.get('id')} for customer {subscription.get('customer')}")


def _handle_subscription_deleted(subscription):
    logger.info(f"Subscription cancelled: {subscription.get('id')}")


def _handle_payment_succeeded(invoice):
    logger.info(f"Payment succeeded: invoice={invoice.get('id')}, amount={invoice.get('amount_paid')}")


def _handle_payment_failed(invoice):
    logger.warning(f"Payment failed: invoice={invoice.get('id')}, customer={invoice.get('customer')}")


def _handle_payment_intent_succeeded(intent):
    logger.info(f"PaymentIntent succeeded: {intent.get('id')}, amount={intent.get('amount')}")
