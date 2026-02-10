#!/bin/bash
# OpenClaw Monitor - Check if services are running and restart if needed

echo "🔍 Checking OpenClaw Services..."
echo ""

# Check Honcho
if systemctl is-active --quiet honcho; then
    echo "✅ Honcho: Running (PID: $(systemctl show --property=MainPID --value honcho))"
else
    echo "❌ Honcho: Not running - restarting..."
    sudo systemctl restart honcho
    sleep 3
    if systemctl is-active --quiet honcho; then
        echo "   ✅ Honcho restarted successfully"
    else
        echo "   ❌ Honcho failed to restart"
    fi
fi

# Check OpenClaw
if systemctl is-active --quiet openclaw; then
    echo "✅ OpenClaw: Running (PID: $(systemctl show --property=MainPID --value openclaw))"
else
    echo "❌ OpenClaw: Not running - restarting..."
    sudo systemctl restart openclaw
    sleep 3
    if systemctl is-active --quiet openclaw; then
        echo "   ✅ OpenClaw restarted successfully"
    else
        echo "   ❌ OpenClaw failed to restart"
    fi
fi

# Test API response
echo ""
echo "🧪 Testing API..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ API responding correctly"
else
    echo "❌ API not responding"
fi

echo ""
echo "📊 Recent Logs:"
echo "  Honcho:    $(tail -1 /var/log/honcho.log 2>/dev/null || echo 'No logs')"
echo "  OpenClaw:  $(tail -1 /var/log/openclaw.log 2>/dev/null || echo 'No logs')"

echo ""
echo "💡 Commands:"
echo "  ./monitor.sh     - Check status"
echo "  ./restart.sh     - Restart services"
echo "  ./logs.sh        - View logs"
