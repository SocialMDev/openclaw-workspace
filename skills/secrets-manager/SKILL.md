---
name: secrets-manager
description: |
  Securely manage API keys, tokens, and credentials without exposing them in the context window.
  
  USE WHEN:
  - You need to store an API key securely (GitHub, OpenAI, Slack, etc.)
  - You need to inject credentials into commands without exposing them
  - You're setting up a new integration that requires authentication
  - You need to list or manage existing stored secrets
  
  DON'T USE WHEN:
  - You just need to read a public file - use Read tool directly
  - The credential is temporary/session-only - pass it directly instead
  - You're in a shared/multi-user environment where secrets shouldn't persist
  
  SECURITY NOTES:
  - Secrets are stored with 0600 permissions (owner-only access)
  - Directory has 0700 permissions
  - Placeholders like $GITHUB_TOKEN are replaced at execution time
  - Secret values never appear in conversation context
  
  OUTPUTS: Secure credential storage, placeholder injection
  TOOLS: Bash (secrets.py script)
---

# Secrets Manager

Secure credential management for OpenClaw agents.

## Quick Start

```bash
# Store a secret
python3 skills/secrets-manager/secrets.py set github-token ghp_xxxxxxxx

# List stored secrets (names only, not values)
python3 skills/secrets-manager/secrets.py list

# Inject placeholders in a command
python3 skills/secrets-manager/secrets.py inject 'Authorization: Bearer $GITHUB_TOKEN'
```

## Usage in Scripts

```python
import sys
sys.path.insert(0, 'skills/secrets-manager')
from secrets import get_secret

token = get_secret('github-token')
# Use token for API calls
```

## Placeholder Format

Secrets are referenced by placeholder:
- File: `github-token` → Placeholder: `$GITHUB_TOKEN`
- File: `openai-api-key` → Placeholder: `$OPENAI_API_KEY`
- File: `slack-webhook` → Placeholder: `$SLACK_WEBHOOK`

Pattern: `$` + uppercase with underscores

## Security Model

1. **Storage**: `~/.openclaw/secrets/` (0700 permissions)
2. **Files**: Individual files per secret (0600 permissions)
3. **No context exposure**: Values never loaded into conversation
4. **Runtime injection**: Replaced only at execution time

## Common Secrets

| Service | Secret Name | Placeholder |
|---------|-------------|-------------|
| GitHub | github-token | $GITHUB_TOKEN |
| OpenAI | openai-api-key | $OPENAI_API_KEY |
| Slack | slack-webhook-url | $SLACK_WEBHOOK_URL |
| X/Twitter | x-cookies | $X_COOKIES |

## Edge Cases

**Permission errors**: If you see "overly permissive permissions" warnings:
```bash
chmod 700 ~/.openclaw/secrets
chmod 600 ~/.openclaw/secrets/*
```

**Secret not found**: Placeholders remain unchanged if secret doesn't exist

**Backup**: Secrets are NOT backed up - keep master copies elsewhere
