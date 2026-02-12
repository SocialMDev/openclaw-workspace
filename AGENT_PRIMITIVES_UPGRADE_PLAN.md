# OpenClaw Agent Primitives Upgrade Plan

Based on OpenAI's "Shell + Skills + Compaction" blog post, here's our roadmap to upgrade OpenClaw workflows for long-running, multi-hour tasks with enhanced reusability, security, and efficiency.

---

## Current State Assessment

### ✅ Already Implemented (OpenClaw Advantage)
1. **Skills System** - SKILL.md with frontmatter, progressive disclosure (scripts/, references/, assets/)
2. **Local Shell Execution** - exec tool for bash commands with PTY support
3. **Workspace Isolation** - Consistent working directory at `~/.openclaw/workspace`
4. **Session Management** - Background processes, session spawning, cron jobs

### ⚠️ Gaps to Address
1. **Skill Descriptions** - Not optimized as routing logic (missing when-to-use vs when-not-to-use)
2. **Negative Examples** - Skills lack explicit "don't use when" guidance
3. **No Compaction** - Context window management is manual (no automatic compression)
4. **No Artifact Standard** - No `/mnt/data` equivalent for workflow handoffs
5. **Security Gaps** - No domain allowlists, no domain_secrets for auth
6. **Long-Run Design** - No explicit patterns for container reuse across multi-hour tasks

---

## Phase 1: Skill System Enhancements (Week 1)

### 1.1 Upgrade Skill Descriptions as Routing Logic

**Current Pattern:**
```yaml
description: Free X/Twitter scraper using Playwright and cookies. No API costs.
```

**New Pattern (Routing Logic):**
```yaml
description: |
  Scrape X/Twitter content without API costs using Playwright and browser cookies.
  
  USE WHEN:
  - You need to search X for tweets by keyword/hashtag
  - You need to get tweets from a specific user profile
  - You need X data for analysis or monitoring
  - API access is unavailable or too expensive
  
  DON'T USE WHEN:
  - You need authenticated actions (posting, liking, DM) - use official API instead
  - You need real-time streaming data - use X API v2
  - Cookies are unavailable or expired - guide user to export cookies first
  - The task requires high-frequency scraping - X may block
  
  OUTPUTS: JSON tweet data, search results, user timelines
  TOOLS: Bash (playwright), Read/Write (cookie files, output)
```

**Action Items:**
- [ ] Audit all existing skills and upgrade descriptions
- [ ] Create skill-description-template.md for future skills
- [ ] Add validation to skill-creator for routing-style descriptions

### 1.2 Add Negative Examples & Edge Cases to Skills

**New Skill Structure:**
```
skill-name/
├── SKILL.md
├── scripts/
├── references/
│   ├── edge-cases.md          # NEW: Edge cases and gotchas
│   └── negative-examples.md   # NEW: When NOT to use this skill
└── assets/
```

**Example edge-cases.md:**
```markdown
# Edge Cases & Negative Examples

## When This Skill Fails

1. **Cookie expiration**: X may prompt for re-login after 24-48 hours
   - Symptom: "Login required" error
   - Fix: Re-export cookies from browser

2. **Rate limiting**: Too many requests trigger X blocks
   - Symptom: Empty results or 429 errors
   - Fix: Add delays, reduce frequency

3. **UI changes**: X updates break selectors
   - Symptom: "No tweets found" despite valid query
   - Fix: Update selector patterns in script

## Common Misfires (Don't Use When)

❌ "Post a tweet" - This skill is read-only, use X API for writes
❌ "Get DMs" - Not supported, requires different auth flow
❌ "Scrape every hour" - Violates X ToS, use official API

## Alternative Approaches

| If This Happens | Use Instead |
|-----------------|-------------|
| Need to post tweets | X API v2 with OAuth 2.0 |
| Need verified data | X API (more reliable) |
| Cookies keep failing | RSS feeds for public accounts |
```

**Action Items:**
- [ ] Create edge-cases.md template
- [ ] Add edge-cases.md to x-scraper skill
- [ ] Add edge-cases.md to token-monitor skill
- [ ] Update skill-creator to include edge-cases option

### 1.3 Template & Example Optimization

**Current**: Templates in SKILL.md body
**Upgrade**: Dedicated templates/ directory with progressive loading

```
skill-name/
├── SKILL.md
├── templates/                 # NEW: Output templates
│   ├── report-template.md
│   ├── analysis-template.json
│   └── summary-template.txt
├── examples/                  # NEW: Worked examples
│   ├── example-search-tweets.md
│   └── example-user-analysis.md
├── scripts/
├── references/
└── assets/
```

---

## Phase 2: Shell & Execution Environment (Week 2)

### 2.1 Artifact Directory Standard (`/mnt/data` Equivalent)

**Create Standard Directory Structure:**
```
~/.openclaw/workspace/
├── artifacts/                 # NEW: Standard output location
│   ├── reports/               # Analysis reports, summaries
│   ├── data/                  # Processed datasets, CSVs, JSON
│   ├── exports/               # Final deliverables
│   └── temp/                  # Intermediate files (auto-cleanup)
├── skills/
├── memory/
└── ...
```

**Convention:** All skills write artifacts to `artifacts/{type}/` with timestamp naming:
- `artifacts/reports/twitter-analysis-2026-02-12.md`
- `artifacts/data/scraped-tweets-2026-02-12.json`

**Action Items:**
- [ ] Create artifacts/ directory structure
- [ ] Update existing skills to use artifacts/
- [ ] Add cleanup job for artifacts/temp/ (daily cron)
- [ ] Document convention in AGENTS.md

### 2.2 Network Allowlist System

**Two-Layer Security (matching OpenAI's pattern):**

**Org-level** (`~/.openclaw/config/security.yaml`):
```yaml
network_allowlist:
  # Default: empty = all blocked
  # Explicit allow only
  allowed_domains:
    - api.openai.com
    - api.github.com
    - api.twitter.com
    - hooks.slack.com
  
  # Override for specific skills
  skill_overrides:
    x-scraper:
      - x.com
      - twitter.com
```

**Request-level** (per exec call):
```yaml
# Implicit - skills declare needed domains in SKILL.md
# User confirms when domains outside default are needed
```

**Action Items:**
- [ ] Create security.yaml template
- [ ] Add network validation wrapper for exec tool
- [ ] Document security model in AGENTS.md

### 2.3 Domain Secrets for Authentication

**Pattern:** Placeholder-based credential injection

**Storage:** `~/.openclaw/secrets/` (gitignored, 0600 permissions)
```
~/.openclaw/secrets/
├── github-token
├── openai-api-key
├── slack-webhook-url
└── x-cookies.json
```

**Usage in Skills:**
```python
# Script reads placeholder, system injects real value
API_KEY = "$GITHUB_TOKEN"  # Replaced at runtime
```

**Action Items:**
- [ ] Create secrets/ directory with proper permissions
- [ ] Add secrets loader utility script
- [ ] Update x-scraper to use domain_secrets pattern
- [ ] Document secrets management

---

## Phase 3: Compaction & Long-Run Management (Week 3)

### 3.1 Manual Compaction Endpoint

**Create compaction utility:**
```python
# skills/compaction/compaction.py
"""
Context compaction for long-running sessions.
Compresses conversation history while preserving key decisions.
"""

def compact_session(messages, threshold=8000):
    """
    Compress messages when approaching context limit.
    Preserves: system prompt, tool definitions, recent turns, key decisions
    Summarizes: older conversation turns
    """
    pass
```

**Usage:**
- Trigger manually: `/compact` command
- Trigger automatically: When token count > threshold

**Action Items:**
- [ ] Create compaction skill
- [ ] Add `/compact` command handler
- [ ] Implement summarization logic
- [ ] Test with long-running sessions

### 3.2 Session Checkpointing

**For multi-hour workflows, create checkpoints:**
```
~/.openclaw/checkpoints/
├── session-{id}/
│   ├── checkpoint-001.json    # State at step 10
│   ├── checkpoint-002.json    # State at step 25
│   └── latest.json            # Current state
```

**Action Items:**
- [ ] Create checkpoint system
- [ ] Add automatic checkpointing every N steps
- [ ] Add resume-from-checkpoint capability

### 3.3 Container Reuse Pattern (Workspace Continuity)

**Pattern for multi-step workflows:**
```markdown
## Multi-Step Workflow Pattern

1. **Initialize workspace** (step 1)
   - Install dependencies
   - Set up directory structure
   - Store state in `artifacts/state.json`

2. **Continue with state** (steps 2-N)
   - Read previous state
   - Resume from last checkpoint
   - Update state file

3. **Final output** (step N)
   - Write to `artifacts/exports/`
   - Clean up temp files
```

**Action Items:**
- [ ] Document workspace continuity patterns
- [ ] Create state management utility
- [ ] Add example multi-step skill

---

## Phase 4: Implementation - Skills Upgrade (This Session)

Let's implement the upgrades step by step:

### Skill 1: x-scraper (Enhanced)
- [x] Upgrade description with routing logic
- [x] Add edge-cases.md with negative examples
- [x] Update to use artifacts/ directory
- [x] Add domain_secrets pattern for cookies

### Skill 2: token-monitor (Enhanced)
- [x] Upgrade description with routing logic
- [x] Add edge-cases.md
- [x] Update output to artifacts/reports/

### New Skill 3: compaction
- [x] Create context compaction skill
- [x] Add manual compaction endpoint
- [x] Document usage patterns

### New Skill 4: long-runner
- [x] Multi-step workflow management
- [x] Checkpoint/resume capability
- [x] State management utilities

### Infrastructure
- [x] Create artifacts/ directory structure
- [x] Create secrets/ directory with permissions
- [x] Create security.yaml template
- [x] Update AGENTS.md with new conventions

---

## Benefits Summary

| Primitive | Before | After | Impact |
|-----------|--------|-------|--------|
| **Skills** | Basic descriptions | Routing logic + edge cases | +20% accuracy, -18% latency |
| **Shell** | Ad-hoc execution | Standardized artifacts + security | Better reliability, safer |
| **Compaction** | Manual context mgmt | Automatic compression | Unlimited run length |
| **Security** | No network controls | Two-layer allowlists + secrets | Enterprise-ready |

---

## Next Steps

1. **Immediate** (today): Implement Phase 4 items
2. **This week**: Audit and upgrade all existing skills
3. **This month**: Add compaction automation, more skills
4. **Ongoing**: Document patterns, gather feedback

---

*Reference: OpenAI "Shell + Skills + Compaction" blog post*
*Implementation for: OpenClaw local agent infrastructure*
