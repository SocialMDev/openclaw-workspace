---
name: x-scraper
description: |
  Scrape X/Twitter content without API costs using Playwright and browser cookies.
  
  USE WHEN:
  - You need to search X for tweets by keyword, hashtag, or topic
  - You need to get tweets from a specific user profile (public accounts)
  - You need X data for analysis, monitoring, or research
  - API access is unavailable, rate-limited, or too expensive
  - You have valid browser cookies exported from an X session
  
  DON'T USE WHEN:
  - You need to post tweets, like, retweet, or DM (this skill is read-only)
  - You need authenticated user actions - use official X API v2 instead
  - You need real-time streaming data - use X API streaming endpoints
  - You don't have valid cookies or can't export them from a browser
  - The task requires high-frequency scraping (>1 request/minute) - X may block
  - You need data from private/protected accounts - only public data accessible
  
  OUTPUTS: JSON tweet data, CSV exports, search results, user timelines
  TOOLS: Bash (playwright, python), Read/Write (cookies, artifacts)
  ARTIFACTS: Writes to artifacts/data/ with timestamp
---

# X/Twitter Scraper

Free X/Twitter scraping without API costs using Playwright and browser cookies.

## Quick Start

```bash
# Search for tweets
python3 skills/x-scraper/x_scraper.py search "OpenClaw" --limit 20

# Get tweets from a user
python3 skills/x-scraper/x_scraper.py user faisalnd --limit 20

# Save to artifacts (default)
python3 skills/x-scraper/x_scraper.py search "AI news" --output artifacts/data/
```

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install playwright
   playwright install chromium
   ```

2. **Configure cookies (choose one method):**
   
   **Method A: Direct file (legacy)**
   - Export cookies from browser using Cookie-Editor extension
   - Save to: `~/.openclaw/cookies/x_cookies.json`
   
   **Method B: Secrets manager (recommended)**
   ```bash
   # Save cookies as a secret
   python3 skills/secrets-manager/secrets.py set x-cookies "$(cat x_cookies.json)"
   ```

3. **Verify setup:**
   ```bash
   python3 skills/x-scraper/x_scraper.py search "test" --limit 5
   ```

## Usage Patterns

### Search Tweets
```bash
# Basic search
python3 skills/x-scraper/x_scraper.py search "OpenClaw"

# With options
python3 skills/x-scraper/x_scraper.py search "AI news" --limit 50 --json

# Save to specific location
python3 skills/x-scraper/x_scraper.py search "bitcoin" --output artifacts/data/btc-tweets.json
```

### Get User Tweets
```bash
# Recent tweets from a user
python3 skills/x-scraper/x_scraper.py user faisalnd --limit 20

# With JSON output
python3 skills/x-scraper/x_scraper.py user elonmusk --json --output artifacts/data/elon.json
```

## Natural Language Commands

The skill handles queries like:
- "Search X for tweets about OpenClaw"
- "Get recent tweets from @faisalnd"
- "Find tweets about AI in the last week"
- "Scrape X for posts about cryptocurrency and save to artifacts"

## Output Format

Default output directory: `artifacts/data/`

**JSON format:**
```json
{
  "query": "OpenClaw",
  "tweets": [
    {
      "id": "1234567890",
      "text": "Tweet content here...",
      "author": "username",
      "created_at": "2026-02-12T10:00:00Z",
      "likes": 42,
      "retweets": 10
    }
  ],
  "metadata": {
    "scraped_at": "2026-02-12T10:30:00Z",
    "count": 20
  }
}
```

## Features

- ✅ **No API costs** - uses browser automation
- ✅ **Cookie-based auth** - uses your existing session
- ✅ **Search tweets** - by keyword/hashtag
- ✅ **User profiles** - get tweets from specific users
- ✅ **JSON output** - for programmatic use
- ✅ **Artifacts integration** - writes to standardized output directory
- ✅ **Secrets support** - secure credential management

## References

- **Edge Cases & Troubleshooting**: See [edge-cases.md](edge-cases.md)
- **Cookie Format**: See [references/cookie-format.md](references/cookie-format.md)

## Security & Ethics

- **Rate limiting**: Built-in delays to avoid blocks
- **Respectful**: Follow X's robots.txt and terms of service
- **Privacy**: Only access public data, not protected accounts
- **Session security**: Cookies stored securely, not in context
