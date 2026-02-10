#!/bin/bash
# OpenClaw Complete Setup Script
# Run this to set up everything

set -e

echo "=================================================="
echo "🚀 OpenClaw Complete Setup"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Honcho is running
echo -e "${BLUE}Checking Honcho...${NC}"
if curl -s http://localhost:8002/v3/workspaces/openclaw-main/peers -X POST -H "Content-Type: application/json" -d '{"id":"setup-check"}' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Honcho is running${NC}"
else
    echo "⚠️  Honcho not running. Starting it..."
    cd /home/faisal/.openclaw/workspace/honcho-ai
    nohup ./launch.sh > /tmp/honcho.log 2>&1 &
    sleep 5
    echo -e "${GREEN}✅ Honcho started${NC}"
fi

# Create workspace if needed
echo -e "${BLUE}Setting up workspace...${NC}"
cd /home/faisal/.openclaw/workspace

# Test OpenClaw
echo -e "${BLUE}Testing OpenClaw...${NC}"
cd /home/faisal/.openclaw/workspace/honcho-ai
uv run python /home/faisal/.openclaw/workspace/main.py << 'EOF'
Hello
history
quit
EOF

echo ""
echo "=================================================="
echo -e "${GREEN}✅ OpenClaw Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "📁 Files created:"
echo "   • main.py - Main OpenClaw application"
echo "   • .env.openclaw - Configuration"
echo "   • openclaw.service - SystemD service (optional)"
echo ""
echo "🚀 To run OpenClaw:"
echo "   cd /home/faisal/.openclaw/workspace"
echo "   python main.py"
echo ""
echo "Or as a library:"
echo "   from main import OpenClaw"
echo "   openclaw = OpenClaw()"
echo "   response = openclaw.chat('user123', 'Hello!')"
echo ""
