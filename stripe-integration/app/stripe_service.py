"""Core Stripe service — handles checkout sessions, webhooks, and customer management."""

import stripe
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, PRODUCTS

stripe.api_key = STRIPE_SECRET_KEY


def create_customer(email, name=None, metadata=None):
    """Create a Stripe customer."""
    params = {"email": email}
    if name:
        params["name"] = name
    if metadata:
        params["metadata"] = metadata
    return stripe.Customer.create(**params)


def get_customer(customer_id):
    """Retrieve a Stripe customer by ID."""
    return stripe.Customer.retrieve(customer_id)


def create_product_and_price(product_key):
    """Create a Stripe product + recurring price from config."""
    cfg = PRODUCTS.get(product_key)
    if not cfg:
        raise ValueError(f"Unknown product: {product_key}")

    product = stripe.Product.create(
        name=cfg["name"],
        metadata={"product_key": product_key},
    )

    price = stripe.Price.create(
        product=product.id,
        unit_amount=cfg["price_cents"],
        currency=cfg["currency"],
        recurring={"interval": cfg["interval"]},
    )

    return product, price


def create_checkout_session(price_id, customer_id=None, success_url=None, cancel_url=None):
    """Create a Stripe Checkout Session for subscription."""
    params = {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success_url or "https://edge.blackroad.io/success?session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": cancel_url or "https://edge.blackroad.io/cancel",
    }
    if customer_id:
        params["customer"] = customer_id
    return stripe.checkout.Session.create(**params)


def create_payment_intent(amount_cents, currency="usd", customer_id=None, metadata=None):
    """Create a one-time PaymentIntent."""
    params = {
        "amount": amount_cents,
        "currency": currency,
        "automatic_payment_methods": {"enabled": True},
    }
    if customer_id:
        params["customer"] = customer_id
    if metadata:
        params["metadata"] = metadata
    return stripe.PaymentIntent.create(**params)


def construct_webhook_event(payload, sig_header):
    """Verify and construct a Stripe webhook event."""
    return stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)


def cancel_subscription(subscription_id):
    """Cancel a subscription immediately."""
    return stripe.Subscription.cancel(subscription_id)


def list_subscriptions(customer_id):
    """List active subscriptions for a customer."""
    return stripe.Subscription.list(customer=customer_id, status="active")


def create_billing_portal_session(customer_id, return_url=None):
    """Create a Stripe billing portal session for self-service."""
    return stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url or "https://edge.blackroad.io/account",
    )
