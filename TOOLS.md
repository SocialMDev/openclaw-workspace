# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Token Monitor

Custom skill to analyze OpenClaw token usage across sessions.

**Location:** `skills/token-monitor/`

**Usage:**
```bash
# Basic analysis
node skills/token-monitor/token-monitor.js

# Show top 10
node skills/token-monitor/token-monitor.js --limit 10

# Detailed breakdown with tool analysis
node skills/token-monitor/token-monitor.js --detail

# Last 7 days only
node skills/token-monitor/token-monitor.js --days 7
```

**What it shows:**
- Per-session token counts (input/output/total/context)
- Cost estimates
- Top token-burning sessions
- Token distribution stats (avg, median, percentiles)

---

## Honcho Memory Integration

Persistent memory system for OpenClaw using Honcho.

**Location:** `honcho_integration.py`

**Status:** ✅ Operational (authenticated with JWT)

**API Endpoint:** http://localhost:8002 (localhost only)

**Quick Usage:**
```python
from honcho_integration import OpenClawMemory, before_turn_inject_memory, after_turn_store_memory

# Initialize memory
memory = OpenClawMemory(workspace_id="openclaw")

# Store user message
memory.store_message(user_id="faisal", message="Hello!")

# Get conversation history
history = memory.get_history(user_id="faisal")

# Get formatted context for LLM prompt
context = memory.get_context_for_prompt(user_id="faisal", limit=10)

# Get AI insights about user
insights = memory.get_user_insights(user_id="faisal")
```

**OpenClaw Integration Hooks:**
```python
# Before processing (injects memory into prompt)
context = before_turn_inject_memory(user_id, message)
prompt = context + f"User: {message}\nAssistant:"

# After processing (stores conversation)
after_turn_store_memory(user_id, message, assistant_response)
```

**Features:**
- Persistent conversation storage
- Semantic search (embeddings enabled)
- User insights via dialectic API
- JWT authentication
- Daily automated backups

**System Status:**
```bash
# Check API health
curl -s http://localhost:8002/v3/workspaces/list \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -X POST -d '{}'

# Check deriver logs
tail -f /tmp/honcho-deriver.log

# Check queue status
curl -s http://localhost:8002/v3/workspaces/<workspace_id>/queue/status \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Backup:** Daily at 2:00 AM to `/var/backups/honcho/`

---

Add whatever helps you do your job. This is your cheat sheet.
