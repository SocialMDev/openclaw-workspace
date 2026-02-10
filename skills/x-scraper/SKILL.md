---
name: x-scraper
description: Free X/Twitter scraper using Playwright and cookies. No API costs.
version: 1.0.0
author: OpenClaw
tools: [Bash, Read, Write]
---

# X/Twitter Scraper

Scrape X/Twitter without API costs using Playwright and browser cookies.

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install playwright
   playwright install chromium
   ```

2. **Place your cookies:**
   - Export cookies from your browser (using Cookie-Editor or similar)
   - Save to: `~/.openclaw/cookies/x_cookies.json`

3. **Verify cookies work:**
   ```bash
   python3 skills/x-scraper/x_scraper.py search "OpenClaw" --limit 5
   ```

## Usage

### Search tweets
```bash
# Search for tweets
python3 skills/x-scraper/x_scraper.py search "query" --limit 20

# Output as JSON
python3 skills/x-scraper/x_scraper.py search "query" --json
```

### Get user tweets
```bash
# Get tweets from specific user
python3 skills/x-scraper/x_scraper.py user faisalnd --limit 20
```

## Natural Language Commands

- "Search X for tweets about OpenClaw"
- "Get recent tweets from @faisalnd"
- "Find tweets about AI in the last week"
- "Scrape X for posts about cryptocurrency"

## Features

- ✅ **No API costs** - uses browser automation
- ✅ **Cookie-based auth** - uses your existing session
- ✅ **Search tweets** - by keyword/hashtag
- ✅ **User profiles** - get tweets from specific users
- ✅ **JSON output** - for programmatic use
- ✅ **Headless** - runs in background

## Limitations

- ⚠️ **Requires valid cookies** - X may ask to re-login periodically
- ⚠️ **Rate limited** - X may block if too many requests
- ⚠️ **Fragile** - breaks if X changes their UI
- ⚠️ **Ethical** - respect robots.txt and terms of service

## Cookie Format

Cookies should be in Netscape/JSON format:
```json
[
  {
    "name": "auth_token",
    "value": "your_token_here",
    "domain": ".x.com",
    "path": "/"
  }
]
```

## Troubleshooting

**Login required error:**
- Cookies expired, re-export from browser
- X detected automation, add delays

**No tweets found:**
- Check if query returns results on X website
- X may be serving different HTML

**Blocked by X:**
- Add longer delays between requests
- Use residential proxy
- Reduce request frequency
