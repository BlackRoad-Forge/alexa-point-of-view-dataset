import os
from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

FLASK_ENV = os.environ.get("FLASK_ENV", "production")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "8080"))
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")

NODE_NAME = os.environ.get("NODE_NAME", "unknown")
NODE_IP = os.environ.get("NODE_IP", "127.0.0.1")
UPSTREAM_URL = os.environ.get("UPSTREAM_URL", "https://edge.blackroad.io")

# Pi cluster nodes for routing
PI_CLUSTER = {
    "blackroad-pi": {"ip": "192.168.4.64", "port": 8080, "role": "gateway"},
    "aria64": {"ip": "192.168.4.38", "port": 8080, "role": "worker"},
    "alice": {"ip": "192.168.4.49", "port": 8080, "role": "worker"},
    "lucidia-alt": {"ip": "192.168.4.99", "port": 8080, "role": "worker"},
}

# Products/pricing configuration
PRODUCTS = {
    "blackroad-agent-basic": {
        "name": "BlackRoad Agent - Basic",
        "price_cents": 999,
        "currency": "usd",
        "interval": "month",
    },
    "blackroad-agent-pro": {
        "name": "BlackRoad Agent - Pro",
        "price_cents": 4999,
        "currency": "usd",
        "interval": "month",
    },
    "blackroad-agent-enterprise": {
        "name": "BlackRoad Agent - Enterprise",
        "price_cents": 19999,
        "currency": "usd",
        "interval": "month",
    },
}
