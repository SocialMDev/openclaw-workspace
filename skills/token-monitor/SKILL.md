---
name: token-monitor
description: |
  Analyze OpenClaw token usage across sessions to identify consumption patterns,
  top token-burning sessions, and cost estimates.
  
  USE WHEN:
  - You need to understand token consumption across sessions
  - You want to identify which sessions are using the most tokens
  - You need cost estimates for agent usage
  - You're investigating high token usage or unexpected costs
  - You want to analyze tool usage patterns across sessions
  - You need to identify sessions that might benefit from compaction
  
  DON'T USE WHEN:
  - You need real-time token tracking (this is retrospective analysis)
  - You want to modify/set token limits (this is read-only analysis)
  - You need per-message token breakdown (shows session aggregates only)
  - OpenClaw is not installed or session files don't exist
  - You need to analyze current in-progress session (waits for session persistence)
  
  OUTPUTS: Token usage reports, session rankings, tool usage statistics
  TOOLS: Bash (node.js script), Read (session files)
  ARTIFACTS: Writes reports to artifacts/reports/
---

# Token Monitor

Analyze OpenClaw token usage across sessions and identify top token burners.

## Quick Start

```bash
# Analyze all sessions
node skills/token-monitor/token-monitor.js

# Show top 10 sessions by token usage
node skills/token-monitor/token-monitor.js --limit 10

# Show detailed breakdown including tool usage patterns
node skills/token-monitor/token-monitor.js --detail

# Filter by date range (last N days)
node skills/token-monitor/token-monitor.js --days 7

# Save report to artifacts
node skills/token-monitor/token-monitor.js --output artifacts/reports/token-usage.json
```

## What It Tracks

- **Per-session tokens**: input, output, total, context
- **Top token consumers**: which sessions burned the most
- **Tool usage patterns**: which tools are called most frequently
- **Cost estimates**: based on configured model pricing
- **Session longevity**: how long sessions have been running

## Files Analyzed

- `~/.openclaw/agents/<agentId>/sessions/sessions.json` — session metadata with token counters
- `~/.openclaw/agents/<agentId>/sessions/*.jsonl` — transcript files for tool analysis
- `/tmp/openclaw/openclaw-*.log` — gateway logs for request-level data

## Output Formats

### Default (Console Table)
```
Session        Input   Output  Total   Context  Last Active         Cost
session-abc    15,234  8,921   24,155  85%      2026-02-12 04:30    $0.45
session-xyz    42,100  12,400  54,500  92%      2026-02-12 03:15    $1.02
```

### JSON (for programmatic use)
```json
{
  "generated_at": "2026-02-12T04:42:00Z",
  "total_sessions": 15,
  "total_tokens": 450230,
  "sessions": [
    {
      "session_key": "session-abc",
      "input_tokens": 15234,
      "output_tokens": 8921,
      "total_tokens": 24155,
      "context_percent": 85,
      "last_active": "2026-02-12T04:30:00Z",
      "estimated_cost": 0.45
    }
  ]
}
```

## Use Cases

### Identify High-Token Sessions for Compaction
```bash
node skills/token-monitor/token-monitor.js --limit 5
# Then use compaction skill on those sessions
```

### Weekly Usage Report
```bash
node skills/token-monitor/token-monitor.js --days 7 --output artifacts/reports/weekly-tokens.json
```

### Cost Analysis
```bash
node skills/token-monitor/token-monitor.js --detail | grep -E "(Session|Cost)"
```

## References

- **Edge Cases**: See [edge-cases.md](edge-cases.md)
- **Cost Calculation**: See [references/pricing.md](references/pricing.md)

## Limitations

- Requires read access to OpenClaw session files
- Session data is only as current as last persistence
- Cost estimates use default pricing (may not match your provider)
