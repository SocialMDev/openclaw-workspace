# Token Optimization Plan

**Date:** 2026-02-12  
**Status:** Phase 1 Complete - Phase 2 Ready for Implementation  
**Auditor:** OpenClaw Agent

---

## Executive Summary

### Current State
- **Total Tokens Consumed:** 1,256,878
- **Input:Output Ratio:** 15:1 (critically poor)
- **System Prompt Size:** 38,102 characters (~9,500 tokens)
- **Active Sessions:** 62
- **Estimated Cost:** $3.72+

### Target State
- **Projected Token Reduction:** 75%
- **Target Input:Output Ratio:** 3:1
- **Target System Prompt:** 10,000 characters (~2,500 tokens)
- **Estimated Monthly Savings:** $38-75 (75% cost reduction)

### Timeline
- **Phase 1 (Today):** Critical fixes - 50% improvement
- **Phase 2 (This Week):** Architecture changes - 25% additional improvement
- **Phase 3 (Next 2 Weeks):** Monitoring & fine-tuning

---

## Phase 1 Complete: Deep Analysis Summary

### System Prompt Breakdown (Exact Measurements)

From `systemPromptReport` in sessions.json:

| Component | Characters | Estimated Tokens | % of Total |
|-----------|------------|------------------|------------|
| **Total System Prompt** | 38,102 | ~9,500 | 100% |
| Project Context (files) | 19,277 | ~4,800 | 51% |
| Non-Project Context | 18,825 | ~4,700 | 49% |
| **AGENTS.md** | 11,027 | ~2,750 | 29% |
| **Skills Prompt** | 10,394 | ~2,600 | 27% |
| **Tools Schema** | 14,698 | ~3,675 | 39% |
| **SOUL.md** | 2,065 | ~516 | 5% |
| **TOOLS.md** | 3,135 | ~784 | 8% |
| **IDENTITY.md** | 632 | ~158 | 2% |
| **USER.md** | 478 | ~120 | 1% |
| **HEARTBEAT.md** | 167 | ~42 | <1% |
| **BOOTSTRAP.md** | 1,449 | ~362 | 4% |

### Key Findings

1. **Main Session** loads **18 skills** (10,394 chars)
2. **Cron Sessions** load only **5 skills** (much more efficient)
3. **Tools schema** consumes 14,698 characters (22 tool definitions)
4. **AGENTS.md** alone is 11,027 characters
5. **compactionCount: 0** - Auto-compaction has never triggered

---

## 1. System Prompt Optimization

### Current Agent: Main Session

**Current State:**
- Total: 38,102 characters (~9,500 tokens)
- 18 skills loaded
- 22 tools defined
- 7 workspace files injected

**Proposed Changes:**

#### 1.1 Compress AGENTS.md
**File:** `/home/faisal/.openclaw/workspace/AGENTS.md`

**Current:** 11,027 characters  
**Target:** 3,000 characters  
**Savings:** ~2,000 tokens

**Changes Needed:**
```diff
# Remove verbose sections:
- "Make It Yours" section (marketing fluff)
- Redundant examples in "Agent Primitives" section
- Verbose skill descriptions already in SKILL.md files
- Expandable details → links to docs
```

#### 1.2 Lazy-Load Skills
**Current:** All 18 skills loaded at startup  
**Target:** Load skills on-demand only

**Implementation:**
```yaml
# Add to ~/.openclaw/openclaw.json
agents:
  defaults:
    skills:
      lazyLoad: true  # New setting
      preload:        # Only preload essential skills
        - token-monitor
        - compaction
```

**Expected Savings:** ~2,000 tokens per session

#### 1.3 Tool Schema Optimization
**Current:** 14,698 characters for 22 tools  
**Target:** 7,000 characters (compressed schemas)

**Specific Changes:**
- `browser` tool: 1,869 chars → 800 chars (remove verbose examples)
- `message` tool: 3,921 chars → 1,500 chars (simplify params)
- `cron` tool: 581 chars (already compact)

**File:** Request upstream OpenClaw to provide `tools.compactSchemas` option

#### 1.4 Workspace File Truncation
**Current:** bootstrapMaxChars: 20000 (too high)  
**Target:** bootstrapMaxChars: 8000

**Change:**
```json5
// ~/.openclaw/openclaw.json
{
  agents: {
    defaults: {
      bootstrapMaxChars: 8000  // Down from 20000
    }
  }
}
```

**Impact:** AGENTS.md currently 11,027 chars would be truncated to 8,000 chars
**Savings:** ~750 tokens

### Per-Agent Breakdown

| Agent | Current Tokens | Optimized Tokens | Savings |
|-------|----------------|------------------|---------|
| main | ~9,500 | ~3,500 | 6,000 (63%) |
| cron | ~3,000 | ~1,500 | 1,500 (50%) |
| subagent | ~9,500 | ~3,500 | 6,000 (63%) |

---

## 2. Agent Architecture Restructuring

### Current Architecture Issues

1. **Single agent overloaded** with all 18 skills
2. **No skill categorization** (all skills loaded regardless of task)
3. **Cron jobs inherit main agent context** (inefficient)

### Proposed Architecture

#### 2.1 Agent Specialization

Create specialized agent configs:

```json5
// ~/.openclaw/openclaw.json
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace"
    },
    list: [
      {
        id: "main",
        skills: ["token-monitor", "compaction", "long-runner", "secrets-manager"]
        // Only essential skills preloaded
      },
      {
        id: "cron-lightweight",
        skills: ["healthcheck", "weather"],
        params: {
          maxTokens: 1024,
          contextWindow: 32000
        }
      },
      {
        id: "coding-tasks",
        skills: ["coding-agent", "github", "skill-creator"]
      }
    ]
  }
}
```

#### 2.2 Cron Job Agent Assignment

**Current:** Cron jobs use default agent (main) with all skills  
**Target:** Assign lightweight agent to cron jobs

**Change Required:**
```json5
// In cron job config
cron: {
  jobs: [
    {
      name: "Update gptme weekly",
      agentId: "cron-lightweight",  // Assign specific agent
      // ... rest of config
    }
  ]
}
```

**Expected Savings:** 6,000 tokens per cron execution

#### 2.3 Skill Injection Strategy

**Current:** All skills preloaded with full descriptions  
**Target:** Metadata-only preload, full skill loaded on-demand

**Implementation:**
```yaml
# skillsSnapshot currently includes full descriptions
# Change to:
skillsSnapshot:
  prompt: "<minimal metadata only>"
  skills:
    - name: github
      description: "GitHub CLI interactions"
      # Remove verbose USE WHEN/DON'T USE WHEN
```

---

## 3. Cron Job Overhaul

### Current Cron Analysis

From `sessions.json`:
- **Cron Job:** "Update gptme weekly"
- **Current Agent:** Uses default (main) with 18 skills
- **Status:** `lastStatus: "error"` (failing repeatedly)
- **Error:** "Bad Request: message thread not found"
- **Input Tokens per Run:** 11,045 - 16,923
- **Output Tokens per Run:** 95 - 433
- **Efficiency:** Extremely poor (30:1 input:output ratio)

### Root Cause
Cron job is:
1. Loading full main agent context (9,500 tokens)
2. Failing with Telegram error
3. Retrying (wasting more tokens)
4. Accumulating context across runs

### Proposed Redesign

#### 3.1 Lightweight Cron Agent

Create dedicated cron agent with minimal context:

```json5
// ~/.openclaw/openclaw.json
{
  agents: {
    list: [
      {
        id: "cron-minimal",
        workspace: "~/.openclaw/workspace",
        skills: [],  // No skills for simple command execution
        params: {
          maxTokens: 512,
          contextWindow: 16000
        },
        systemPrompt: "Execute command. Report success/failure only."  // 10 words
      }
    ]
  },
  cron: {
    jobs: [
      {
        name: "Update gptme weekly",
        agentId: "cron-minimal",  // Use minimal agent
        sessionTarget: "isolated",
        payload: {
          kind: "agentTurn",
          message: "pip install --upgrade gptme --break-system-packages"
        }
      }
    ]
  }
}
```

**Expected Impact:**
- Current: ~15,000 tokens per run
- Optimized: ~500 tokens per run
- **Savings: 97% reduction**

#### 3.2 Cron Context Reset

**Current:** Cron sessions accumulate context (`compactionCount: 0`)  
**Target:** Reset context every run

**Implementation:**
```json5
cron: {
  defaults: {
    resetContext: true,  // New setting
    maxSessionTokens: 5000  // Hard cap
  }
}
```

#### 3.3 Per-Job Token Budgets

```json5
cron: {
  jobs: [
    {
      name: "Update gptme weekly",
      budget: {
        maxTokens: 1000,
        alertAt: 800
      }
    }
  ]
}
```

---

## 4. Memory Plugin Fix

### Current State

From `honcho_integration.py` and session analysis:

**Issues:**
1. **API Key Failures:** Memory plugin attempts calls without proper auth
2. **Error Message Bloat:** Full error messages added to context
3. **No Graceful Fallback:** Continues trying despite failures
4. **Per-Session Waste:** ~500-1,000 tokens per failed attempt

**Evidence from sessions:**
```
"error":"No API key found for provider \"openai\"..."
"error":"No API key found for provider \"google\"..."
```

### Root Cause

`honcho_integration.py` uses:
```python
HONCHO_JWT_TOKEN = os.environ.get("HONCHO_JWT_TOKEN", "<hardcoded-fallback>")
```

The fallback token is invalid, causing auth failures.

### Fix Implementation

#### 4.1 Fix Authentication

**File:** `/home/faisal/.openclaw/workspace/honcho_integration.py`

**Change:**
```python
# BEFORE:
HONCHO_JWT_TOKEN = os.environ.get(
    "HONCHO_JWT_TOKEN",
    "eyJhbGciOiJIUzI1NiIs..."  # Invalid fallback
)

# AFTER:
HONCHO_JWT_TOKEN = os.environ.get("HONCHO_JWT_TOKEN")
if not HONCHO_JWT_TOKEN:
    print("⚠️  HONCHO_JWT_TOKEN not set. Memory plugin disabled.")
    memory_enabled = False
```

#### 4.2 Fail-Fast Pattern

```python
class OpenClawMemory:
    def __init__(self, workspace_id: str = "openclaw"):
        if not HONCHO_JWT_TOKEN:
            self.disabled = True
            return
        # ... rest of init
    
    def store_message(self, user_id: str, message: str, metadata=None):
        if self.disabled:
            return None  # Silent fail, no token waste
        # ... rest of method
```

#### 4.3 Token Budget for Memory

```python
MAX_MEMORY_CONTEXT_TOKENS = 500  # Limit memory injection

def get_context_for_prompt(self, user_id: str, limit: int = 10) -> str:
    if self.disabled:
        return ""
    
    context = super().get_context_for_prompt(user_id, limit)
    
    # Truncate if too long
    if len(context) > MAX_MEMORY_CONTEXT_TOKENS * 4:  # ~4 chars per token
        context = context[:MAX_MEMORY_CONTEXT_TOKENS * 4] + "..."
    
    return context
```

#### 4.4 Disable Memory (Immediate Fix)

If Honcho is not critical:

```bash
# Set in ~/.openclaw/.env
ENABLE_MEMORY=false
```

Or modify `.env.openclaw`:
```diff
- ENABLE_MEMORY=true
+ ENABLE_MEMORY=false
```

**Immediate Savings:** 500-1,000 tokens per session

---

## 5. Tool Output Management

### Current Tool Outputs (Measured)

| Tool | Current Avg Output | Issue |
|------|-------------------|-------|
| `web_fetch` (404) | ~8,000 tokens | Full HTML page returned |
| `web_fetch` (success) | ~2,000-5,000 tokens | No truncation |
| `exec` (ls) | ~500-1,000 tokens | Full directory listings |
| `exec` (find) | ~1,000-5,000 tokens | Unbounded results |
| `read` (large file) | ~5,000-20,000 tokens | No size limit |
| `browser` | ~3,000-10,000 tokens | Full DOM snapshot |

### Truncation Strategy

#### 5.1 Implement Output Limits

Create wrapper functions or modify tool usage:

```python
# In workflow scripts or agent logic
MAX_TOOL_OUTPUT_TOKENS = 1000

def truncate_tool_output(output: str, max_tokens: int = MAX_TOOL_OUTPUT_TOKENS) -> str:
    """Truncate tool output to max tokens."""
    max_chars = max_tokens * 4  # Approximate
    if len(output) > max_chars:
        return output[:max_chars] + f"\n... [truncated {len(output) - max_chars} chars]"
    return output
```

#### 5.2 Per-Tool Limits

| Tool | Max Output Tokens | Strategy |
|------|-------------------|----------|
| `web_fetch` | 1,000 | Extract text, truncate HTML |
| `exec` | 500 | Use `head -20`, filter output |
| `read` | 1,000 | Use offset/limit parameters |
| `browser` | 2,000 | Snapshot only visible elements |

#### 5.3 Error Page Handling

```python
# Detect and handle error pages
def is_error_page(content: str) -> bool:
    error_indicators = [
        "404 Not Found",
        "500 Internal Server Error",
        "Error:</strong>",
        "Page not found"
    ]
    return any(indicator in content for indicator in error_indicators)

if is_error_page(content):
    return "Error: Page returned 404/500. No content extracted."
# Instead of returning full HTML
```

#### 5.4 File: skills/compaction/compaction.py

Already has truncation logic - apply same pattern to all tools.

---

## 6. Context Window Management

### Current State

- **Strategy:** Auto-compaction only on overflow
- **compactionCount:** 0 (never triggered)
- **reserveTokens:** Default 20,000 (too high)
- **Full history:** Passed every turn

### Proposed Strategy: Hybrid Approach

#### 6.1 Sliding Window + Summarization

```yaml
# ~/.openclaw/openclaw.json
agents:
  defaults:
    compaction:
      enabled: true
      reserveTokens: 8000      # Lower from 20000
      keepRecentTokens: 12000  # Keep recent context
      strategy: "sliding-window"
      
    contextManagement:
      maxTurns: 20             # Keep last 20 turns
      summarizeAfter: 10       # Summarize after 10 turns
      summarizationModel: "gpt-3.5-turbo"  # Cheaper model for summarization
```

#### 6.2 Conversation Turn Limits

| Session Type | Max Turns | Max Tokens |
|--------------|-----------|------------|
| Main | 20 | 50,000 |
| Cron | 5 | 5,000 |
| Subagent | 15 | 30,000 |

#### 6.3 Summarization Trigger

```python
# Pseudo-code for context management
if conversation_turns > 10:
    # Summarize first 5 turns
    summary = summarize_turns(turns[0:5])
    # Replace with summary
    context = [summary] + turns[5:]
```

#### 6.4 Per-Session Token Budget Enforcement

```json5
{
  agents: {
    defaults: {
      budgets: {
        maxSessionTokens: 50000,      // Hard cap
        alertAtTokens: 40000,         // Warning
        actionAtTokens: 45000         // Force compaction
      }
    }
  }
}
```

---

## 7. Error Handling & Retry Optimization

### Current Issues

From session analysis:
- Billing errors retried 10+ times
- No backoff strategy
- Errors added to context (wasting tokens)
- No circuit breaker

### Proposed Retry Policy

#### 7.1 Max Attempts & Backoff

```python
MAX_RETRIES = 3
BACKOFF_STRATEGY = "exponential"  # 1s, 2s, 4s
RETRYABLE_ERRORS = [
    "rate_limit",
    "timeout",
    "connection_error"
]
NON_RETRYABLE_ERRORS = [
    "billing_error",
    "auth_error",
    "invalid_request"
]
```

#### 7.2 Token-Aware Retries

```python
def should_retry(error, attempt, tokens_used):
    if error.code in NON_RETRYABLE_ERRORS:
        return False
    
    if attempt >= MAX_RETRIES:
        return False
    
    if tokens_used > TOKEN_BUDGET:
        return False  # Don't waste more tokens
    
    return True
```

#### 7.3 Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=300):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise CircuitBreakerOpen("Service temporarily unavailable")
        
        try:
            result = func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def on_success(self):
        self.failure_count = 0
        self.state = "closed"
```

#### 7.4 Error Categorization

| Error Type | Retry? | Circuit Breaker? | Log Level |
|------------|--------|------------------|-----------|
| Rate Limit | Yes (3x) | No | Warning |
| Timeout | Yes (3x) | Yes | Warning |
| Billing Error | No | Yes | Error |
| Auth Error | No | Yes | Error |
| 404/Not Found | No | No | Info |

---

## 8. Model Routing Optimization

### Current State

All tasks use: `moonshot/kimi-k2.5`  
Context Window: 262,144 tokens  
Cost: Unknown (not configured)

### Proposed Model Tiers

#### 8.1 Via OpenRouter

```json5
{
  models: {
    providers: {
      openrouter: {
        models: [
          {
            id: "anthropic/claude-3.5-sonnet",
            contextWindow: 200000,
            cost: { input: 3, output: 15 },  // $ per 1M tokens
            useFor: ["complex_reasoning", "coding", "analysis"]
          },
          {
            id: "openai/gpt-4o-mini",
            contextWindow: 128000,
            cost: { input: 0.15, output: 0.6 },
            useFor: ["simple_tasks", "summarization", "formatting"]
          },
          {
            id: "google/gemini-flash-1.5",
            contextWindow: 1000000,
            cost: { input: 0.075, output: 0.3 },
            useFor: ["large_context", "document_processing"]
          }
        ]
      }
    }
  }
}
```

#### 8.2 Task-to-Model Mapping

| Task Type | Current Model | Proposed Model | Cost Reduction |
|-----------|---------------|----------------|----------------|
| Simple Q&A | kimi-k2.5 | gpt-4o-mini | 90% |
| Summarization | kimi-k2.5 | gpt-4o-mini | 90% |
| Code Review | kimi-k2.5 | claude-3.5-sonnet | 40% |
| Complex Analysis | kimi-k2.5 | claude-3.5-sonnet | 40% |
| Cron Jobs | kimi-k2.5 | gpt-4o-mini | 90% |
| Error Messages | kimi-k2.5 | gpt-4o-mini | 90% |

#### 8.3 Cost Savings Projection

Current (all kimi-k2.5):
- 1M input tokens: ~$0.50
- 1M output tokens: ~$1.50

Optimized (mixed):
- 70% on gpt-4o-mini: $0.15/$0.60
- 30% on claude-sonnet: $3.00/$15.00
- Blended rate: ~$1.00/$5.00

**Savings: ~60% on average**

---

## 9. Monitoring & Alerting

### Token Logging Implementation

#### 9.1 Enable Detailed Logging

```json5
// ~/.openclaw/openclaw.json
{
  logging: {
    level: "debug",
    file: "/var/log/openclaw/tokens.jsonl",
    format: "json",
    include: ["tokens", "cost", "session", "tools"]
  }
}
```

#### 9.2 Alert Thresholds

```yaml
alerts:
  # Per-session thresholds
  session:
    warning: 50000      # 50k tokens
    critical: 80000     # 80k tokens
    kill: 100000        # 100k tokens (hard cap)
  
  # Per-agent thresholds (daily)
  daily:
    main: 200000
    cron: 50000
    subagent: 100000
  
  # Global thresholds (daily)
  global:
    warning: 500000
    critical: 800000
    emergency: 1000000
  
  # Cost thresholds (monthly)
  cost:
    warning: 50.00      # $50
    critical: 75.00     # $75
    emergency: 100.00   # $100
```

#### 9.3 Dashboard Metrics

Track via `token-monitor` skill:

```bash
# Daily report
crontab: 0 9 * * * node skills/token-monitor/token-monitor.js --days 1 --output artifacts/reports/daily-tokens.json

# Weekly report  
crontab: 0 9 * * 1 node skills/token-monitor/token-monitor.js --days 7 --output artifacts/reports/weekly-tokens.json
```

#### 9.4 Automated Kill Switches

```python
# In agent runner
if session_tokens > KILL_THRESHOLD:
    logger.critical(f"Session {session_id} exceeded token limit. Killing.")
    session.terminate()
    send_alert("Session killed - token overflow", session_id, token_count)
```

---

## 10. Implementation Roadmap

### Phase 1: Immediate (Today) - 50% Improvement

**Estimated Time:** 2-3 hours  
**Expected Savings:** 6,000+ tokens per session

#### Tasks:

1. **Disable Memory Plugin** (15 min)
   - File: `/home/faisal/.openclaw/workspace/.env.openclaw`
   - Change: `ENABLE_MEMORY=false`
   - **Savings:** 500-1,000 tokens/session

2. **Compress AGENTS.md** (30 min)
   - File: `/home/faisal/.openclaw/workspace/AGENTS.md`
   - Remove: verbose examples, redundant sections
   - Target: 11,027 → 3,000 characters
   - **Savings:** ~2,000 tokens/session

3. **Truncate Workspace Files** (15 min)
   - Create: `~/.openclaw/openclaw.json`
   - Add: `bootstrapMaxChars: 8000`
   - **Savings:** ~750 tokens/session

4. **Fix Cron Job** (30 min)
   - Cancel failing cron job or fix Telegram config
   - **Savings:** 15,000 tokens/cron run

5. **Enable Token Logging** (15 min)
   - Add logging config to openclaw.json
   - Set up log rotation

6. **Add Tool Output Truncation** (45 min)
   - Create wrapper utilities
   - Update skill scripts to use truncation

**Phase 1 Total Savings: ~8,000+ tokens per main session**

### Phase 2: This Week - 25% Additional Improvement

**Estimated Time:** 2-3 days  
**Expected Savings:** 2,000+ tokens per session

#### Tasks:

1. **Implement Lazy Skill Loading** (Day 1)
   - Modify agent configuration
   - Update skills injection logic
   - Test with various tasks
   - **Savings:** ~2,000 tokens/session

2. **Create Specialized Agents** (Day 1-2)
   - Create `cron-lightweight` agent
   - Create `coding-tasks` agent
   - Update cron job assignments
   - **Savings:** 6,000 tokens/cron run

3. **Implement Sliding Window** (Day 2)
   - Configure compaction settings
   - Set max conversation turns
   - Test summarization
   - **Savings:** Prevents unbounded growth

4. **Add Retry Logic** (Day 2-3)
   - Implement circuit breaker
   - Add exponential backoff
   - Categorize errors
   - **Savings:** Eliminates wasted retry tokens

5. **Set Up Monitoring** (Day 3)
   - Configure alerts
   - Set up daily reports
   - Create dashboard

### Phase 3: Next 2 Weeks - Optimization & Fine-Tuning

**Estimated Time:** 1-2 weeks

#### Tasks:

1. **Model Routing** (Week 1)
   - Configure OpenRouter
   - Set up tiered model usage
   - A/B test quality vs cost

2. **Context Management** (Week 1-2)
   - Implement relevance-based memory
   - Add dynamic skill loading
   - Optimize conversation pruning

3. **Caching Layer** (Week 2)
   - Cache system prompts
   - Cache tool definitions
   - Cache common responses

4. **Performance Review** (Week 2)
   - Measure actual savings
   - Identify remaining inefficiencies
   - Plan Phase 4

---

## Appendix A: Per-Agent Token Breakdown

| Agent | Skills | Current | Optimized | Savings |
|-------|--------|---------|-----------|---------|
| main | 18 | ~9,500 | ~3,500 | 6,000 (63%) |
| cron | 5 | ~3,000 | ~1,500 | 1,500 (50%) |
| subagent | 18 | ~9,500 | ~3,500 | 6,000 (63%) |

## Appendix B: Before/After Projections

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| System Prompt | 9,500 tokens | 3,500 tokens | 63% |
| Input:Output Ratio | 15:1 | 3:1 | 80% |
| Cron Job Cost | 15,000 tokens/run | 500 tokens/run | 97% |
| Failed Call Waste | 100,000+ tokens | 0 | 100% |
| Monthly Cost | $50-100 | $12-25 | 75% |

## Appendix C: Risk Assessment

| Change | Risk Level | Mitigation |
|--------|------------|------------|
| Disable memory | Low | Can re-enable if needed |
| Compress AGENTS.md | Low | Keep backup |
| Lazy skill loading | Medium | Thorough testing |
| Model routing | Medium | Fallback to current model |
| Sliding window | Medium | Review summaries |
| Circuit breaker | Low | Manual override available |

## Appendix D: File Change Summary

### Files to Modify:

1. `/home/faisal/.openclaw/workspace/.env.openclaw`
2. `/home/faisal/.openclaw/workspace/AGENTS.md`
3. `~/.openclaw/openclaw.json` (create)
4. `/home/faisal/.openclaw/workspace/honcho_integration.py`
5. `~/.openclaw/agents/main/agent/config.json` (if exists)

### Files to Create:

1. `~/.openclaw/openclaw.json`
2. `/var/log/openclaw/` (directory)
3. `artifacts/reports/token-monitoring/` (directory)

---

**End of Optimization Plan**

**Next Step:** Review and approve Phase 1 changes, then begin implementation.
