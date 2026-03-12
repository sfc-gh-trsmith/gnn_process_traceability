#!/bin/bash
set -e

cd "$(dirname "$0")"

CONTAINER_NAME="gnn-traceability"
IMAGE_NAME="gnn-traceability-app"

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║  GNN Process Traceability - React App Development Server         ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

MISSING_VARS=""

if [ -z "$SNOWFLAKE_PAT" ]; then
    MISSING_VARS="$MISSING_VARS SNOWFLAKE_PAT"
fi

if [ -z "$SNOWFLAKE_ACCOUNT" ]; then
    MISSING_VARS="$MISSING_VARS SNOWFLAKE_ACCOUNT"
fi

if [ -z "$SNOWFLAKE_USER" ]; then
    MISSING_VARS="$MISSING_VARS SNOWFLAKE_USER"
fi

if [ -n "$MISSING_VARS" ]; then
    echo "❌ Error: Required environment variables not set:$MISSING_VARS"
    echo ""
    echo "   Export them with:"
    echo "     export SNOWFLAKE_PAT=your_token"
    echo "     export SNOWFLAKE_ACCOUNT=your_account"
    echo "     export SNOWFLAKE_USER=your_user"
    echo ""
    exit 1
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
    -e SNOWFLAKE_PAT="${SNOWFLAKE_PAT}" \
    -e SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT}" \
    -e SNOWFLAKE_USER="${SNOWFLAKE_USER}" \
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
