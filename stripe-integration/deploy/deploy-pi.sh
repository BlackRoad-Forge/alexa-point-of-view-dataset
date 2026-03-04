#!/usr/bin/env bash
set -euo pipefail

# Deploy Stripe integration to BlackRoad Pi cluster
# Usage: ./deploy-pi.sh [node|all]
#
# Nodes:
#   blackroad-pi  (192.168.4.64) - gateway
#   aria64        (192.168.4.38) - worker
#   alice         (192.168.4.49) - worker
#   lucidia-alt   (192.168.4.99) - worker

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="blackroad/stripe-integration"
IMAGE_TAG="latest"

declare -A NODES=(
    ["blackroad-pi"]="192.168.4.64"
    ["aria64"]="192.168.4.38"
    ["alice"]="192.168.4.49"
    ["lucidia-alt"]="192.168.4.99"
)

declare -A PORTS=(
    ["blackroad-pi"]="8080"
    ["aria64"]="8081"
    ["alice"]="8082"
    ["lucidia-alt"]="8083"
)

TARGET="${1:-all}"

deploy_node() {
    local node="$1"
    local ip="${NODES[$node]}"
    local port="${PORTS[$node]}"

    echo "==> Deploying to $node ($ip:$port)..."

    # Build ARM64 image
    docker buildx build \
        --platform linux/arm64 \
        -t "$IMAGE_NAME:$IMAGE_TAG" \
        -f "$PROJECT_DIR/Dockerfile.pi" \
        "$PROJECT_DIR" \
        --load

    # Save and transfer image
    docker save "$IMAGE_NAME:$IMAGE_TAG" | ssh "pi@$ip" "docker load"

    # Stop existing container and start new one
    ssh "pi@$ip" bash <<EOF
docker stop stripe-integration 2>/dev/null || true
docker rm stripe-integration 2>/dev/null || true
docker run -d \
    --name stripe-integration \
    --restart unless-stopped \
    -p $port:8080 \
    --env-file /home/pi/.env.stripe \
    -e NODE_NAME=$node \
    -e NODE_IP=$ip \
    "$IMAGE_NAME:$IMAGE_TAG"
EOF

    echo "==> $node deployed successfully on port $port"
}

if [ "$TARGET" = "all" ]; then
    for node in "${!NODES[@]}"; do
        deploy_node "$node"
    done
    echo ""
    echo "=== All nodes deployed ==="
    echo "Gateway:  http://192.168.4.64:8080/api/v1/health"
    echo "Aria64:   http://192.168.4.38:8081/api/v1/health"
    echo "Alice:    http://192.168.4.49:8082/api/v1/health"
    echo "Lucidia:  http://192.168.4.99:8083/api/v1/health"
else
    if [[ -v "NODES[$TARGET]" ]]; then
        deploy_node "$TARGET"
    else
        echo "Unknown node: $TARGET"
        echo "Available: ${!NODES[*]}"
        exit 1
    fi
fi
