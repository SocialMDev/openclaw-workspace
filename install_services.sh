#!/bin/bash
# Install OpenClaw and Honcho as system services
# This ensures they start on boot and always run

set -e

echo "=================================================="
echo "🔧 Installing OpenClaw System Services"
echo "=================================================="

# Create log files
sudo touch /var/log/openclaw.log /var/log/openclaw-error.log
sudo touch /var/log/honcho.log /var/log/honcho-error.log
sudo chown faisal:faisal /var/log/openclaw*.log /var/log/honcho*.log

# Copy service files
echo "📋 Installing service files..."
sudo cp /home/faisal/.openclaw/workspace/honcho.service /etc/systemd/system/
sudo cp /home/faisal/.openclaw/workspace/openclaw.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
echo "🔄 Enabling auto-start on boot..."
sudo systemctl enable honcho.service
sudo systemctl enable openclaw.service

# Stop any running instances
echo "🛑 Stopping any running instances..."
pkill -f "api_server.py" 2>/dev/null || true
pkill -f "uvicorn.*8002" 2>/dev/null || true
sleep 2

# Start services
echo "🚀 Starting services..."
sudo systemctl start honcho.service
sleep 5
sudo systemctl start openclaw.service
sleep 3

# Check status
echo ""
echo "=================================================="
echo "📊 Service Status"
echo "=================================================="
echo ""
echo "Honcho:"
sudo systemctl status honcho.service --no-pager -l | head -15
echo ""
echo "OpenClaw:"
sudo systemctl status openclaw.service --no-pager -l | head -15

echo ""
echo "=================================================="
echo "✅ Installation Complete!"
echo "=================================================="
echo ""
echo "Services will now:"
echo "  • Start automatically on system boot"
echo "  • Restart if they crash"
echo "  • Always stay running"
echo ""
echo "Commands:"
echo "  sudo systemctl status honcho     - Check Honcho status"
echo "  sudo systemctl status openclaw   - Check OpenClaw status"
echo "  sudo systemctl restart honcho    - Restart Honcho"
echo "  sudo systemctl restart openclaw  - Restart OpenClaw"
echo "  sudo systemctl stop honcho       - Stop Honcho"
echo "  sudo systemctl stop openclaw     - Stop OpenClaw"
echo ""
echo "Logs:"
echo "  tail -f /var/log/honcho.log"
echo "  tail -f /var/log/openclaw.log"
echo ""
echo "Test:"
echo "  curl http://localhost:8080/health"
echo "=================================================="
