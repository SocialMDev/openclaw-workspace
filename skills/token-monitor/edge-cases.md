# Edge Cases & Negative Examples

## When This Skill Fails or Returns Unexpected Results

### 1. No Session Files Found
**Symptom**: "No sessions found" or empty output
**Cause**: 
- OpenClaw not installed
- Session directory doesn't exist at expected path
- No sessions have been created yet
**Fix**:
```bash
# Verify OpenClaw is installed
which openclaw

# Check session directory exists
ls ~/.openclaw/agents/*/sessions/
```

### 2. Permission Denied
**Symptom**: "EACCES: permission denied" error
**Cause**: Session files owned by different user or insufficient permissions
**Fix**:
```bash
# Fix permissions
sudo chown -R $USER:$USER ~/.openclaw/

# Or run with appropriate user
```

### 3. Corrupted Session Data
**Symptom**: Token counts showing as NaN, null, or wildly incorrect values
**Cause**: 
- Session file was truncated during write
- JSON corruption in session metadata
- Mixed format versions
**Fix**:
- Individual corrupted sessions can be skipped (script handles gracefully)
- Report issue to OpenClaw if widespread

### 4. Stale Data
**Symptom**: "Last Active" shows old timestamp for clearly active session
**Cause**: Session persistence hasn't occurred recently
**Fix**:
- Data reflects last saved state, not real-time
- Force session persistence if needed (varies by OpenClaw version)

### 5. Missing Cost Estimates
**Symptom**: Cost column shows $0.00 or "N/A"
**Cause**:
- Model pricing not configured
- Unknown model used in session
- Token counts incomplete
**Fix**:
- Update pricing config in token-monitor.js
- Add your model's per-token pricing

## Common Misfires (Don't Use When)

❌ **"Show me current token usage in real-time"** - This is retrospective analysis only

❌ **"Set a token limit of 100k"** - This skill is read-only, cannot set limits

❌ **"Show me tokens for this exact message"** - Only session-level aggregates

❌ **"Block high-token sessions"** - No control capabilities, analysis only

❌ **"Show me tokens for sessions on another machine"** - Only local OpenClaw instance

❌ **"Export to Google Sheets"** - JSON/CSV only, no direct integrations

## Alternative Approaches

| If You Need... | Use Instead |
|----------------|-------------|
| Real-time token tracking | OpenClaw's native `/status` or session events |
| Set token budgets | Configure in OpenClaw gateway settings |
| Per-message breakdown | Parse session JSONL files directly |
| Cross-machine analysis | Aggregate exported JSON files manually |
| Automated alerts on high usage | Cron job + message tool integration |

## Performance Notes

- **Large session counts** (>100 sessions): Analysis may take 5-10 seconds
- **Large transcript files** (>10MB each): Memory usage can spike temporarily
- **Concurrent execution**: Safe to run while OpenClaw is active (read-only)

## Troubleshooting

### Debug Mode
```bash
# Run with verbose output
DEBUG=1 node skills/token-monitor/token-monitor.js
```

### Check File Access
```bash
# Verify session files exist and are readable
ls -la ~/.openclaw/agents/*/sessions/sessions.json
```

### Test with Single Session
```bash
# Analyze just one session by key
node skills/token-monitor/token-monitor.js --session <session-key>
```

## Known Limitations

1. **No historical aggregation** - Shows current state only, no trend analysis
2. **Local only** - Cannot analyze remote/sessionless instances
3. **Pricing estimates** - May not match actual billing from provider
4. **Tool analysis** - Requires parsing transcript files (can be slow)
