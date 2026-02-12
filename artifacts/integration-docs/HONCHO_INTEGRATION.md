# OpenClaw + Honcho Memory Integration

## Overview

OpenClaw is now integrated with Honcho for persistent memory storage.

## Architecture

```
OpenClaw Agent
    │
    ├── Before Turn: Retrieve context from Honcho
    │   └── GET /v3/workspaces/{ws}/sessions/{session}/context
    │
    ├── LLM Call: Generate response with context
    │
    └── After Turn: Store conversation in Honcho
        └── POST /v3/workspaces/{ws}/sessions/{session}/messages
```

## Services

| Service | Status | Command |
|---------|--------|---------|
| Honcho API | ✅ Active | `sudo systemctl status honcho-api` |
| Honcho Deriver | ✅ Active | `sudo systemctl status honcho-deriver` |

## Configuration

**API Endpoint:** `http://localhost:8002`  
**JWT Token:** Configured in `honcho_integration.py`  
**Workspace:** `openclaw`  

## Management Commands

```bash
# Check status
sudo systemctl status honcho-api
sudo systemctl status honcho-deriver

# Restart services
sudo systemctl restart honcho-api
sudo systemctl restart honcho-deriver

# View logs
sudo journalctl -u honcho-api -f
sudo journalctl -u honcho-deriver -f

# Start/stop
sudo systemctl start honcho-api
sudo systemctl stop honcho-api
```

## Backup

- **Schedule:** Daily at 2:00 AM
- **Script:** `/usr/local/bin/honcho-backup.sh`
- **Location:** `/var/backups/honcho/`
- **Retention:** 7 days

## Integration Code

See `honcho_integration.py` for the Python module used by OpenClaw.
