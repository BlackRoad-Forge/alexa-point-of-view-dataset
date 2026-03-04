"""Flask application factory and entry point."""

import logging
from flask import Flask
from app.routes import api
from app.config import FLASK_HOST, FLASK_PORT, FLASK_ENV

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(api, url_prefix="/api/v1")
    return app


def main():
    app = create_app()
    debug = FLASK_ENV != "production"
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=debug)


if __name__ == "__main__":
    main()
