"""Shared test fixtures."""

import os
import pytest

# Set test env vars before importing app
os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake_key_for_testing"
os.environ["STRIPE_PUBLISHABLE_KEY"] = "pk_test_fake_key_for_testing"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_fake_secret_for_testing"
os.environ["NODE_NAME"] = "test-node"
os.environ["NODE_IP"] = "127.0.0.1"

from app.server import create_app


@pytest.fixture
def app():
    """Create test application."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
