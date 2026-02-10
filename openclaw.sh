#!/bin/bash
# OpenClaw Control Script
# Usage: ./openclaw.sh [start|stop|restart|status|logs|monitor]

COMMAND=${1:-status}

case $COMMAND in
    start)
        echo "🚀 Starting OpenClaw..."
        sudo systemctl start honcho
        sleep 3
        sudo systemctl start openclaw
        echo "✅ Started"
        ;;
    stop)
        echo "🛑 Stopping OpenClaw..."
        sudo systemctl stop openclaw
        sudo systemctl stop honcho
        echo "✅ Stopped"
        ;;
    restart)
        echo "🔄 Restarting OpenClaw..."
        sudo systemctl restart honcho
        sleep 3
        sudo systemctl restart openclaw
        echo "✅ Restarted"
        ;;
    status)
        echo "📊 OpenClaw Status:"
        echo ""
        echo "Honcho:"
        sudo systemctl status honcho --no-pager -l | grep -E "Active:|Loaded:|Main PID:"
        echo ""
        echo "OpenClaw:"
        sudo systemctl status openclaw --no-pager -l | grep -E "Active:|Loaded:|Main PID:"
        echo ""
        echo "Test API:"
        curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || echo "API not responding"
        ;;
    logs)
        echo "📜 Logs (Ctrl+C to exit):"
        sudo tail -f /var/log/openclaw.log /var/log/honcho.log
        ;;
    monitor)
        ./monitor.sh
        ;;
    install)
        sudo ./install_services.sh
        ;;
    *)
        echo "OpenClaw Control Script"
        echo ""
        echo "Usage: ./openclaw.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start     - Start services"
        echo "  stop      - Stop services"
        echo "  restart   - Restart services"
        echo "  status    - Check status (default)"
        echo "  logs      - View logs"
        echo "  monitor   - Monitor services"
        echo "  install   - Install system services"
        ;;
esac
