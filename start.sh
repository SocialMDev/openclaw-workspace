#!/bin/bash
# OpenClaw Launcher
# Starts all OpenClaw services

echo "🚀 Starting OpenClaw..."

# Start Honcho if not running
if ! curl -s http://localhost:8002/v3/workspaces/openclaw-main/peers -X POST -H "Content-Type: application/json" -d '{"id":"ping"}' > /dev/null 2>&1; then
    echo "  Starting Honcho..."
    cd /home/faisal/.openclaw/workspace/honcho-ai
    nohup ./launch.sh > /tmp/honcho.log 2>&1 &
    sleep 5
    echo "  ✅ Honcho started"
else
    echo "  ✅ Honcho already running"
fi

# Start API Server
echo "  Starting API Server..."
cd /home/faisal/.openclaw/workspace/honcho-ai
nohup uv run python /home/faisal/.openclaw/workspace/api_server.py > /tmp/openclaw-api.log 2>&1 &
sleep 3

echo ""
echo "=================================================="
echo "✅ OpenClaw is running!"
echo "=================================================="
echo ""
echo "Services:"
echo "  Honcho API:  http://localhost:8002"
echo "  OpenClaw:    http://localhost:8080"
echo ""
echo "Test:"
echo "  curl -X POST http://localhost:8080/chat \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"user_id\": \"test\", \"message\": \"Hello!\"}'"
echo ""
echo "View logs:"
echo "  tail -f /tmp/honcho.log"
echo "  tail -f /tmp/openclaw-api.log"
echo ""
echo "To stop:"
echo "  pkill -f 'api_server.py'"
echo "  pkill -f 'uvicorn'"
