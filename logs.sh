#!/bin/bash
# View OpenClaw logs

echo "📜 OpenClaw Logs"
echo "=================================================="
echo ""

if [ "$1" == "honcho" ]; then
    echo "Honcho Logs:"
    sudo tail -f /var/log/honcho.log
elif [ "$1" == "error" ]; then
    echo "Error Logs:"
    sudo tail -f /var/log/openclaw-error.log /var/log/honcho-error.log
else
    echo "OpenClaw Logs:"
    sudo tail -f /var/log/openclaw.log
fi
