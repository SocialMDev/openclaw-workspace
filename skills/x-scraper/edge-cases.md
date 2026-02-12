# Edge Cases & Negative Examples

## When This Skill Fails

### 1. Cookie Expiration (Most Common)
**Symptom**: "Login required" error or redirect to login page
**Cause**: X session expires after 24-48 hours or after browser logout
**Fix**: 
1. Log into X in your browser
2. Export fresh cookies using Cookie-Editor extension
3. Update the cookie file or secret

### 2. Rate Limiting / Blocking
**Symptom**: Empty results, 429 errors, or "Something went wrong" messages
**Cause**: X detected automated access and temporarily blocked
**Fix**:
- Add longer delays between requests (modify script)
- Reduce request frequency
- Use residential proxy (advanced)
- Wait 15-30 minutes before retrying

### 3. UI Changes (Layout Breaks)
**Symptom**: "No tweets found" despite valid query, or parsing errors
**Cause**: X updated their HTML structure
**Fix**: 
- Check if selectors in script still match current X layout
- Update CSS selectors in `x_scraper.py`
- Check X's current HTML structure

### 4. Account Lockout
**Symptom**: "Account temporarily locked" or CAPTCHA challenges
**Cause**: X detected suspicious activity from the session
**Fix**:
- Log into X manually in browser
- Complete any security challenges
- Re-export cookies after confirming account is unlocked

### 5. Protected Accounts
**Symptom**: "User not found" or empty timeline for existing user
**Cause**: Account is private/protected
**Fix**: 
- This skill only works with public accounts
- Use official X API if you need protected account access

## Common Misfires (Don't Use When)

❌ **"Post a tweet"** - This skill is read-only. Use X API v2 for writes.

❌ **"Like/retweet this tweet"** - Requires authenticated API calls. Use X API.

❌ **"Get my DMs"** - Not supported. Requires different auth flow and API permissions.

❌ **"Scrape X every 5 minutes"** - Violates X ToS and will get blocked. Use official API for monitoring.

❌ **"Get tweet analytics"** - Not supported. Use X Analytics API.

❌ **"Download all tweets from 2010-2024"** - Large historical scraping will trigger blocks. Use X API for bulk historical data.

## Alternative Approaches

| If You Need... | Use Instead |
|----------------|-------------|
| Post/like/retweet | X API v2 with OAuth 2.0 |
| Real-time monitoring | X API streaming endpoints |
| Historical bulk data | X Academic/Enterprise API |
| Verified reliable data | X API (more stable than scraping) |
| RSS feed for public account | X RSS feeds (if available) |
| Analytics data | X Analytics API |

## Troubleshooting Guide

### Debug Mode
```bash
# Run with visible browser (non-headless)
python3 skills/x-scraper/x_scraper.py search "test" --no-headless
```

### Check Cookie Validity
```bash
# Test if cookies work
curl -b "$(python3 skills/secrets-manager/secrets.py get x-cookies)" https://x.com/home
```

### Verify Playwright Installation
```bash
playwright install chromium
playwright chromium --version
```

## Performance Notes

- **Typical latency**: 5-15 seconds per request
- **Rate limit**: Keep under 10 requests/minute to avoid blocks
- **Memory**: Playwright uses ~200MB RAM per instance
- **Concurrent requests**: Not recommended - X will block
