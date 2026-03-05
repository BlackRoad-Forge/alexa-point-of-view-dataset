#!/usr/bin/env python3
"""Smoke tests for the Cloudflare Worker dataset API logic.

These tests validate the response structure locally by parsing the worker source.
For live testing, use: curl https://<worker-url>/health
"""

import json
import os
import sys


def test_worker_source_exists():
    worker_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "workers",
        "dataset-api.js",
    )
    assert os.path.exists(worker_path), f"Worker source not found at {worker_path}"

    with open(worker_path, "r") as f:
        content = f.read()

    # Verify expected endpoints are defined
    assert '"/stats"' in content, "Missing /stats endpoint"
    assert '"/health"' in content, "Missing /health endpoint"
    assert '"/sample"' in content, "Missing /sample endpoint"

    # Verify CORS headers
    assert "Access-Control-Allow-Origin" in content, "Missing CORS headers"

    # Verify dataset metadata
    assert "46562" in content, "Incorrect total_pairs count"
    assert "32593" in content, "Incorrect train count"

    print("Worker source validation: PASSED")


def test_wrangler_config():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "workers",
        "wrangler.toml",
    )
    assert os.path.exists(config_path), f"wrangler.toml not found at {config_path}"

    with open(config_path, "r") as f:
        content = f.read()

    assert "pov-dataset-api" in content, "Missing worker name"
    assert "dataset-api.js" in content, "Missing main entry"
    assert "compatibility_date" in content, "Missing compatibility_date"

    print("Wrangler config validation: PASSED")


if __name__ == "__main__":
    test_worker_source_exists()
    test_wrangler_config()
    print("\nAll worker tests passed.")
