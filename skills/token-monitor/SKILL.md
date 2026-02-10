# Token Monitor

Analyze OpenClaw token usage across sessions and identify top token burners.

## Usage

```bash
# Analyze all sessions
openclaw run skill token-monitor

# Show top 10 sessions by token usage
openclaw run skill token-monitor -- --limit 10

# Show detailed breakdown including tool usage patterns
openclaw run skill token-monitor -- --detail

# Filter by date range (last N days)
openclaw run skill token-monitor -- --days 7
```

## What It Tracks

- **Per-session tokens**: input, output, total, context
- **Top token consumers**: which sessions burned the most
- **Tool usage patterns**: which tools are called most frequently
- **Cost estimates**: based on configured model pricing

## Files Analyzed

- `~/.openclaw/agents/<agentId>/sessions/sessions.json` — session metadata with token counters
- `~/.openclaw/agents/<agentId>/sessions/*.jsonl` — transcript files for tool analysis
- `/tmp/openclaw/openclaw-*.log` — gateway logs for request-level data

## Output Columns

| Column | Description |
|--------|-------------|
| Session | Session key (truncated for display) |
| Input | Input tokens consumed |
| Output | Output tokens generated |
| Total | Total tokens (input + output) |
| Context | Current context window usage |
| Last Active | When the session was last updated |
| Cost | Estimated cost (if pricing configured) |
