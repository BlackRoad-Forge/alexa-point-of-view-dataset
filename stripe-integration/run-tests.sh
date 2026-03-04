#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "=== Installing dependencies ==="
pip install -q -r requirements.txt

echo ""
echo "=== Running E2E tests ==="
python -m pytest tests/ -v --tb=short --co -q 2>/dev/null
echo ""
python -m pytest tests/ -v --tb=short

echo ""
echo "=== All tests passed ==="
