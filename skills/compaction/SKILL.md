---
name: compaction
description: |
  Compress and summarize conversation context to prevent token limit errors in long-running sessions.
  
  USE WHEN:
  - Session is approaching token limits (warning signs: slow responses, truncated outputs)
  - You're running a multi-hour task with many back-and-forth exchanges
  - You want to preserve key decisions while removing redundant conversation
  - You see "context length exceeded" or similar errors
  - You want to checkpoint progress in a long workflow
  
  DON'T USE WHEN:
  - Session is short (< 20 messages) - no benefit
  - You need full conversation history for legal/audit purposes
  - The task is nearly complete (better to finish than compact)
  - You're in the middle of a critical multi-step operation (complete first)
  
  COMPACTION STRATEGY:
  - Preserves: System prompt, tool definitions, key decisions, recent context (last 5 turns)
  - Summarizes: Older conversation into condensed decision log
  - Removes: Redundant examples, intermediate thought processes, successful tool outputs
  
  OUTPUTS: Compacted session summary, token savings estimate
  TOOLS: Read/Write (session analysis), Bash (compression utilities)
---

# Context Compaction

Prevent context window exhaustion in long-running agent sessions.

## What is Compaction?

Compaction compresses conversation history by:
1. **Summarizing older exchanges** into key decisions
2. **Removing redundant content** (successful tool outputs, repetitive patterns)
3. **Preserving critical context** (system prompt, recent turns, important decisions)

## When to Compact

**Warning Signs:**
- Responses getting slower
- "Context length exceeded" errors
- Truncated tool outputs
- Session running > 1 hour with many exchanges

**Best Practice:** Compact proactively every ~50 turns or 2 hours

## Usage

### Manual Compaction

```bash
# Run compaction analysis
python3 skills/compaction/compaction.py analyze

# Compact with custom threshold
python3 skills/compaction/compaction.py compact --keep-recent 10

# View compaction report
python3 skills/compaction/compaction.py report
```

### Automatic Compaction

Enable auto-compaction in your session:
```bash
# Enable (compacts when >80% of context used)
python3 skills/compaction/compaction.py auto-enable --threshold 0.8

# Disable
python3 skills/compaction/compaction.py auto-disable
```

## What Gets Preserved

| Priority | Content | Action |
|----------|---------|--------|
| Critical | System prompt, tool schemas | Never removed |
| High | Last 5 conversation turns | Never summarized |
| Medium | Key decisions, user preferences | Preserved verbatim |
| Low | Successful tool outputs | Summarized to outcome only |
| Minimal | Intermediate reasoning | Removed if redundant |

## Example Compaction

**Before (5000 tokens):**
```
User: Search for tweets about AI
[Assistant calls x-scraper - 20 lines of output]
Assistant: Found 20 tweets...
User: Now analyze sentiment
[Assistant calls analysis - 50 lines of code and output]
Assistant: Sentiment is positive...
[... 40 more exchanges ...]
```

**After (1500 tokens):**
```
[SUMMARY]: Session included Twitter scraping and sentiment analysis. 
Key decisions: Used x-scraper for data collection, positive sentiment 
detected in AI-related tweets. Proceeding to [current task].

User: [current request]
```

## Best Practices

1. **Compact at natural breakpoints** - after completing a subtask
2. **Save checkpoints before major operations** - `compaction.py checkpoint`
3. **Review summaries** - ensure critical context wasn't lost
4. **Don't over-compact** - keep important error messages and fixes

## Edge Cases

**Compaction removes something important:**
- Check `artifacts/compaction/last-summary.md` for full summary
- Restore from checkpoint if needed
- Mark critical info with "[PRESERVE]" prefix in future

**Still hitting limits after compaction:**
- Reduce `--keep-recent` value
- Use more aggressive summarization
- Split into multiple sessions

**Auto-compaction triggered at wrong time:**
- Disable auto mode for critical operations
- Trigger manual compaction at safe points
