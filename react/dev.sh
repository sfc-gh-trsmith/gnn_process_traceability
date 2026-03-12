#!/bin/bash
set -e

cd "$(dirname "$0")"

CONTAINER_NAME="gnn-traceability"
IMAGE_NAME="gnn-traceability-app"

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║  GNN Process Traceability - React App Development Server         ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

if [ -z "$SNOWFLAKE_PAT" ]; then
    echo "⚠️  Warning: SNOWFLAKE_PAT environment variable not set"
    echo "   The app will show a connection error banner until set."
    echo "   Export it with: export SNOWFLAKE_PAT=your_token"
    echo ""
fi

EXISTING=$(docker ps -aq -f name="^${CONTAINER_NAME}$")
if [ -n "$EXISTING" ]; then
    echo "🔄 Stopping existing container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo "   Container stopped and removed."
    echo ""
fi

echo "🔨 Building Docker image..."
docker build -t "$IMAGE_NAME" .
echo "   Build complete."
echo ""

echo "🚀 Starting container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p 5173:5173 \
    -e SNOWFLAKE_CONNECTION_NAME=demo \
    -e SNOWFLAKE_PAT="${SNOWFLAKE_PAT:-}" \
    "$IMAGE_NAME"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "✅ App is running!"
echo ""
echo "   Frontend:  http://localhost:5173"
echo "   API:       http://localhost:5173/api/health"
echo ""
echo "   Logs:      docker logs -f $CONTAINER_NAME"
echo "   Stop:      docker stop $CONTAINER_NAME"
echo "═══════════════════════════════════════════════════════════════════"
