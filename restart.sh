#!/bin/bash
# Restart OpenClaw services

echo "🔄 Restarting OpenClaw Services..."
echo ""

sudo systemctl restart honcho
echo "✅ Honcho restarted"

sleep 3

sudo systemctl restart openclaw
echo "✅ OpenClaw restarted"

echo ""
sleep 2

./monitor.sh
