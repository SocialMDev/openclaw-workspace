---
name: long-runner
description: |
  Manage multi-step, long-running workflows (1+ hours) with checkpointing, state persistence,
  and resume capabilities. Essential for complex tasks that span multiple sessions or require
  continuity across interruptions.
  
  USE WHEN:
  - Task will take 1+ hours to complete
  - You need to pause and resume work later
  - Multiple discrete steps with dependencies between them
  - Installing dependencies that should persist across steps
  - Processing large datasets incrementally
  - Workflow requires artifact handoff between steps
  - You need fault tolerance (can recover from crashes)
  
  DON'T USE WHEN:
  - Task is simple and completes in < 15 minutes
  - Each step is independent with no shared state
  - You're running one-shot commands with no continuity needs
  - All data fits in a single prompt/context window
  
  WORKFLOW PATTERN:
  1. Initialize: Create workspace, install deps, set up state
  2. Execute steps: Process incrementally with checkpoints
  3. Handoff: Write artifacts to artifacts/ directory
  4. Resume: Load state from checkpoint and continue
  
  OUTPUTS: Workflow state files, checkpoints, final artifacts
  TOOLS: Read/Write (state management), Bash (step execution)
  ARTIFACTS: Checkpoints to checkpoints/, outputs to artifacts/
---

# Long-Runner Workflow Manager

Build reliable multi-hour agent workflows with checkpointing and state management.

## The Problem

Long-running agent tasks face challenges:
- **Context limits** - Conversations get too long
- **Interruptions** - Sessions end, processes crash
- **State loss** - Dependencies, intermediate results disappear
- **No continuity** - Each session starts fresh

## The Solution

Long-runner provides:
- **Checkpointing** - Save progress at key milestones
- **State persistence** - Store workflow state between steps
- **Resume capability** - Continue from last checkpoint
- **Artifact handoff** - Standardized output locations

## Workflow Pattern

### 1. Initialize
```bash
# Create workflow workspace
python3 skills/long-runner/init.py --name "twitter-analysis"

# Install dependencies (persisted)
python3 skills/long-runner/step.py --deps "pip install pandas requests"

# Set initial state
python3 skills/long-runner/state.py set phase "data-collection"
python3 skills/long-runner/state.py set total_tweets 0
```

### 2. Execute Steps
```bash
# Run a step with automatic checkpointing
python3 skills/long-runner/step.py exec --name "collect-tweets" --checkpoint \
  "python3 skills/x-scraper/x_scraper.py search 'AI' --limit 100"

# Update state
python3 skills/long-runner/state.py set phase "analysis"
python3 skills/long-runner/state.py increment total_tweets 100
```

### 3. Continue with State
```bash
# Next step uses previous outputs
python3 skills/long-runner/step.py exec --name "analyze-sentiment" \
  --input artifacts/data/collect-tweets-output.json \
  --output artifacts/reports/sentiment.json \
  "python3 analyze.py {input} {output}"
```

### 4. Resume After Interruption
```bash
# List available checkpoints
python3 skills/long-runner/checkpoint.py list

# Resume from specific checkpoint
python3 skills/long-runner/resume.py --checkpoint twitter-analysis-step-3

# Or resume from latest
python3 skills/long-runner/resume.py --latest
```

## Directory Structure

```
~/.openclaw/workspace/
├── workflows/                     # Workflow-specific directories
│   └── {workflow-name}/
│       ├── state.json            # Current workflow state
│       ├── checkpoints/          # Saved checkpoints
│       │   ├── step-1.json
│       │   ├── step-2.json
│       │   └── latest.json
│       ├── inputs/               # Input files for steps
│       ├── outputs/              # Step outputs
│       └── logs/                 # Execution logs
├── artifacts/                    # Cross-workflow artifacts
│   ├── data/
│   ├── reports/
│   └── exports/
└── checkpoints/                  # Global checkpoint backup
```

## State Management

### Basic State Operations
```bash
# Set values
python3 skills/long-runner/state.py set key "value"
python3 skills/long-runner/state.py set count 42

# Get values
python3 skills/long-runner/state.py get key

# Increment numeric values
python3 skills/long-runner/state.py increment count 1

# List all state
python3 skills/long-runner/state.py list

# Export state
python3 skills/long-runner/state.py export > workflow-state.json

# Import state
python3 skills/long-runner/state.py import workflow-state.json
```

### State Schema Example
```json
{
  "workflow_name": "twitter-analysis",
  "created_at": "2026-02-12T10:00:00Z",
  "last_updated": "2026-02-12T12:30:00Z",
  "current_phase": "sentiment-analysis",
  "phases_completed": ["data-collection", "cleaning"],
  "data": {
    "total_tweets": 1500,
    "unique_users": 450,
    "errors": 3
  },
  "artifacts": [
    "artifacts/data/raw-tweets.json",
    "artifacts/data/clean-tweets.json"
  ]
}
```

## Checkpointing

### Automatic Checkpoints
Checkpoints created automatically:
- After each step completion
- Before/after dependency installation
- When state changes significantly
- On graceful shutdown

### Manual Checkpoints
```bash
# Create named checkpoint
python3 skills/long-runner/checkpoint.py create "before-risky-change"

# Create checkpoint with description
python3 skills/long-runner/checkpoint.py create "phase-2-complete" \
  --description "Completed data collection, starting analysis"
```

### Checkpoint Contents
```json
{
  "timestamp": "2026-02-12T12:30:00Z",
  "step_number": 5,
  "step_name": "sentiment-analysis",
  "state": { /* full workflow state */ },
  "artifacts": [ /* list of artifact paths */ ],
  "environment": {
    "installed_packages": ["pandas", "requests"],
    "env_vars": { /* relevant env vars */ }
  }
}
```

## Best Practices

### Design for Long Runs from Start
```python
# Good: Install deps once, reuse
python3 skills/long-runner/step.py --deps "pip install pandas numpy"

# Bad: Installing deps in every step
```

### Checkpoint at Natural Boundaries
- After data collection completes
- Before risky operations
- After major transformations
- When entering new phase

### Use Artifact Directory
```python
# Good: Standard location
--output artifacts/data/processed.csv

# Bad: Random location
--output /tmp/output.csv
```

### Handle Failures Gracefully
```bash
# Check if previous step succeeded before continuing
python3 skills/long-runner/step.py exec --require-previous \
  "python3 next-step.py"
```

## Example: Multi-Hour Twitter Analysis

```bash
# Initialize workflow
python3 skills/long-runner/init.py --name "crypto-sentiment"

# Step 1: Collect data (30 min)
python3 skills/long-runner/step.py exec --name "collect" --checkpoint \
  --output artifacts/data/crypto-tweets.json \
  "python3 skills/x-scraper/x_scraper.py search 'bitcoin OR crypto' --limit 1000"

# Step 2: Clean data (15 min)
python3 skills/long-runner/step.py exec --name "clean" --checkpoint \
  --input artifacts/data/crypto-tweets.json \
  --output artifacts/data/clean-tweets.json \
  "python3 clean_tweets.py {input} {output}"

# Step 3: Analyze sentiment (45 min) - MAY BE INTERRUPTED HERE
python3 skills/long-runner/step.py exec --name "sentiment" --checkpoint \
  --input artifacts/data/clean-tweets.json \
  --output artifacts/reports/sentiment.json \
  "python3 sentiment_analysis.py {input} {output}"

# ... session ends, new session starts ...

# Resume from last checkpoint
python3 skills/long-runner/resume.py --latest

# Step 4: Generate report (20 min)
python3 skills/long-runner/step.py exec --name "report" --checkpoint \
  --input artifacts/reports/sentiment.json \
  --output artifacts/exports/final-report.md \
  "python3 generate_report.py {input} {output}"

# Export workflow summary
python3 skills/long-runner/export.py --format markdown
```

## Edge Cases

### Checkpoint Corruption
```bash
# List all checkpoints
python3 skills/long-runner/checkpoint.py list

# Restore from earlier checkpoint
python3 skills/long-runner/resume.py --checkpoint crypto-sentiment-step-2

# Or start fresh but preserve artifacts
python3 skills/long-runner/init.py --name "crypto-sentiment-v2" \
  --import-artifacts from crypto-sentiment
```

### Disk Space Issues
```bash
# Clean old checkpoints (keep last 5)
python3 skills/long-runner/checkpoint.py cleanup --keep 5

# Archive completed workflows
python3 skills/long-runner/archive.py crypto-sentiment
```

### Dependency Conflicts
```bash
# Create isolated environment per workflow
python3 skills/long-runner/init.py --name "project-a" --venv

# Or use existing venv
python3 skills/long-runner/init.py --name "project-b" --venv-path ./venv
```

## References

- **State Schema**: See [references/state-schema.md](references/state-schema.md)
- **Checkpoint Format**: See [references/checkpoint-format.md](references/checkpoint-format.md)
- **API Reference**: See [references/api.md](references/api.md)
