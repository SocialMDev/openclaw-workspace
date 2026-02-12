# End-to-End Workflow Example: Twitter Sentiment Analysis

This document demonstrates how all the new agent primitives work together in a real-world scenario.

## Scenario

Analyze sentiment of tweets about "AI" over a 3-hour workflow with multiple steps:
1. Collect tweets (1 hour - may hit rate limits)
2. Clean and preprocess (30 min)
3. Run sentiment analysis (1 hour - computationally intensive)
4. Generate report (30 min)

## Complete Workflow

### Step 1: Initialize with Secrets

```bash
# Store credentials securely (done once)
python3 skills/secrets-manager/secrets.py set x-cookies "$(cat ~/cookies.json)"

# Initialize workflow
python3 skills/long-runner/scripts/init.py --name "ai-sentiment-analysis"
```

### Step 2: Collect Data (Phase 1)

```bash
# Set initial state
python3 skills/long-runner/scripts/state.py set phase "data-collection"
python3 skills/long-runner/scripts/state.py set tweets_collected 0
python3 skills/long-runner/scripts/state.py set target_tweets 1000

# Run collection with checkpoint
python3 skills/x-scraper/x_scraper.py \
  search "artificial intelligence OR AI" \
  --limit 1000 \
  --output artifacts/data/ai-tweets-raw.json

# Update state with results
python3 skills/long-runner/scripts/state.py set tweets_collected 1000

# Checkpoint after collection
python3 skills/long-runner/scripts/checkpoint.py create "collection-complete" \
  --description "Collected 1000 tweets about AI"
```

### Step 3: Monitor Token Usage

```bash
# Check if we're approaching limits
node skills/token-monitor/token-monitor.js --limit 5

# If high usage detected, compact context
python3 skills/compaction/compaction.py checkpoint "before-processing"
```

### Step 4: Clean Data (Phase 2)

```bash
# Update state
python3 skills/long-runner/scripts/state.py set phase "cleaning"

# Clean tweets (example script)
python3 clean_tweets.py \
  artifacts/data/ai-tweets-raw.json \
  artifacts/data/ai-tweets-clean.json

# Checkpoint
python3 skills/long-runner/scripts/checkpoint.py create "cleaning-complete"
```

### Step 5: Analyze Sentiment (Phase 3 - Long Running)

```bash
# Update state
python3 skills/long-runner/scripts/state.py set phase "sentiment-analysis"

# This step takes ~1 hour - checkpoint every 15 minutes
python3 analyze_sentiment.py \
  artifacts/data/ai-tweets-clean.json \
  artifacts/reports/sentiment-results.json

# ... session interrupted here, new session starts ...
```

### Step 6: Resume After Interruption

```bash
# New session - resume from checkpoint
python3 skills/long-runner/scripts/checkpoint.py list
# Shows: sentiment-analysis-partial.json

# Load state
python3 skills/long-runner/scripts/state.py list
# Shows: phase=sentiment-analysis, progress=65%

# Continue from checkpoint
python3 analyze_sentiment.py \
  --resume-from artifacts/reports/sentiment-results.json \
  --output artifacts/reports/sentiment-complete.json

python3 skills/long-runner/scripts/checkpoint.py create "analysis-complete"
```

### Step 7: Generate Report (Phase 4)

```bash
# Final phase
python3 skills/long-runner/scripts/state.py set phase "reporting"

# Generate final report
python3 generate_report.py \
  artifacts/reports/sentiment-complete.json \
  artifacts/exports/final-report.md

# Final checkpoint
python3 skills/long-runner/scripts/checkpoint.py create "workflow-complete"
```

### Step 8: Export & Cleanup

```bash
# Export workflow summary
python3 skills/long-runner/scripts/state.py export > artifacts/exports/workflow-state.json

# Archive checkpoints (keep last 3)
python3 skills/long-runner/scripts/checkpoint.py cleanup --keep 3

# Final token report
node skills/token-monitor/token-monitor.js \
  --days 1 \
  --output artifacts/reports/token-usage.json
```

## Key Patterns Demonstrated

### 1. Secrets Management
- Credentials stored securely in `~/.openclaw/secrets/`
- Injected at runtime via `$X_COOKIES` placeholder
- Never exposed in conversation context

### 2. Artifact Handoff
- Raw data → `artifacts/data/`
- Intermediate results → `artifacts/reports/`
- Final deliverables → `artifacts/exports/`
- All timestamped for traceability

### 3. State Persistence
- Phase tracking: `initialization` → `collection` → `analysis` → `reporting`
- Progress counters: `tweets_collected`, `processed_count`
- Resumable after interruption

### 4. Checkpoint/Resume
- Checkpoints created at natural boundaries
- Can resume from any checkpoint
- Automatic backup to global checkpoints dir

### 5. Token Management
- Monitor usage during long runs
- Compact context when approaching limits
- Preserve critical decisions during compaction

### 6. Security
- Network allowlist in `security.yaml`
- Secrets isolated from context
- Read-only analysis tools

## File Structure After Workflow

```
~/.openclaw/workspace/
├── artifacts/
│   ├── data/
│   │   ├── ai-tweets-raw-2026-02-12.json
│   │   └── ai-tweets-clean-2026-02-12.json
│   ├── reports/
│   │   ├── sentiment-results-2026-02-12.json
│   │   └── token-usage-2026-02-12.json
│   └── exports/
│       ├── final-report-2026-02-12.md
│       └── workflow-state-2026-02-12.json
├── workflows/
│   └── ai-sentiment-analysis/
│       ├── state.json
│       ├── checkpoints/
│       │   ├── collection-complete.json
│       │   ├── cleaning-complete.json
│       │   ├── analysis-complete.json
│       │   └── latest.json
│       ├── inputs/
│       ├── outputs/
│       └── logs/
└── checkpoints/
    └── ai-sentiment-analysis-*.json (backups)
```

## Benefits of This Approach

1. **Fault Tolerance**: Can resume from any checkpoint after crashes
2. **Transparency**: All state changes tracked and auditable
3. **Efficiency**: Context compaction prevents token overflow
4. **Security**: Credentials never exposed
5. **Reproducibility**: Complete state capture enables replay
6. **Monitoring**: Token usage tracked throughout

## Command Reference

```bash
# Full workflow in one session (ideal)
python3 run_full_workflow.py --workflow ai-sentiment-analysis

# Or step-by-step with manual checkpoints
python3 step1_collect.py && \
python3 step2_clean.py && \
python3 step3_analyze.py && \
python3 step4_report.py

# Or resume from interruption
python3 skills/long-runner/scripts/resume.py --latest
```

## Troubleshooting

### "No workflow found"
```bash
# Check if initialized
ls workflows/

# Re-initialize if needed
python3 skills/long-runner/scripts/init.py --name "ai-sentiment-analysis"
```

### "Checkpoint corrupted"
```bash
# List all checkpoints
python3 skills/long-runner/scripts/checkpoint.py list

# Restore from earlier
python3 skills/long-runner/scripts/resume.py --checkpoint collection-complete
```

### "Token limit exceeded"
```bash
# Compact context
python3 skills/compaction/compaction.py checkpoint "before-critical-step"

# Or start fresh session with --resume
python3 step3_analyze.py --resume-from artifacts/reports/sentiment-results.json
```
