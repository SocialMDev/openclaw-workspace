#!/usr/bin/env python3
"""
X/Twitter Scraper Skill for OpenClaw
=====================================

Scrapes X/Twitter without API costs using Playwright.
Uses existing cookies for authentication.

Author: OpenClaw
Version: 1.0.0
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Check if playwright is installed
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed")
    print("\nInstall with:")
    print("  pip3 install playwright")
    print("  playwright install chromium")
    sys.exit(1)

class XTScraper:
    """X/Twitter scraper using Playwright."""
    
    def __init__(self, cookies_path: Optional[str] = None):
        self.cookies_path = cookies_path or Path.home() / ".openclaw" / "cookies" / "x_cookies.json"
        self.base_url = "https://x.com"
        
    async def load_cookies(self, context):
        """Load cookies from file if exists."""
        if Path(self.cookies_path).exists():
            with open(self.cookies_path) as f:
                cookies = json.load(f)
                await context.add_cookies(cookies)
            print(f"✅ Loaded cookies from {self.cookies_path}")
            return True
        else:
            print(f"⚠️  No cookies found at {self.cookies_path}")
            print("   You'll need to login manually first")
            return False
    
    async def save_cookies(self, context):
        """Save cookies to file."""
        cookies = await context.cookies()
        Path(self.cookies_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.cookies_path, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"💾 Saved cookies to {self.cookies_path}")
    
    async def search_tweets(self, query: str, limit: int = 20) -> List[Dict]:
        """Search tweets by query."""
        tweets = []
        
        async with async_playwright() as p:
            # Launch with stealth args to avoid detection
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
            )
            
            # Load cookies
            has_cookies = await self.load_cookies(context)
            
            page = await context.new_page()
            
            # Bypass automation detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                window.chrome = { runtime: {} };
            """)
            
            # Navigate to search
            search_url = f"https://x.com/search?q={query}&f=live"
            print(f"🔍 Searching: {query}")
            await page.goto(search_url, wait_until='domcontentloaded')
            
            # Wait for tweets to load (up to 30 seconds)
            print("⏳ Waiting for content to load...")
            try:
                await page.wait_for_selector('article[data-testid="tweet"]', timeout=30000)
                print("✅ Tweets loaded!")
            except:
                print("⚠️  Timeout waiting for tweets, checking anyway...")
            
            await asyncio.sleep(5)  # Extra wait for dynamic content
            
            # Check if login required
            if "login" in page.url or await page.query_selector('input[name="text"]'):
                print("❌ Login required!")
                print("   Please login manually first and save cookies")
                await browser.close()
                return []
            
            # Debug: save screenshot
            await page.screenshot(path='/tmp/x_search.png', full_page=True)
            print(f"📸 Screenshot saved: /tmp/x_search.png")
            
            # Debug: check page content
            page_content = await page.content()
            print(f"📄 Page content length: {len(page_content)} chars")
            
            # Check for tweet selectors
            tweet_selectors = await page.query_selector_all('article[data-testid="tweet"]')
            print(f"🔍 Found {len(tweet_selectors)} tweet elements")
            
            # Extract tweets
            tweet_selectors = await page.query_selector_all('article[data-testid="tweet"]')
            
            for i, tweet in enumerate(tweet_selectors[:limit]):
                try:
                    # Extract tweet data
                    text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                    text = await text_elem.inner_text() if text_elem else ""
                    
                    user_elem = await tweet.query_selector('[data-testid="User-Name"]')
                    user = await user_elem.inner_text() if user_elem else "Unknown"
                    
                    time_elem = await tweet.query_selector('time')
                    time_str = await time_elem.get_attribute('datetime') if time_elem else ""
                    
                    # Stats
                    stats = {}
                    for stat in ['reply', 'retweet', 'like']:
                        stat_elem = await tweet.query_selector(f'[data-testid="{stat}"]')
                        if stat_elem:
                            stat_text = await stat_elem.inner_text()
                            stats[stat] = stat_text
                    
                    tweets.append({
                        'id': i,
                        'user': user.replace('\n', ' '),
                        'text': text,
                        'time': time_str,
                        'stats': stats
                    })
                    
                except Exception as e:
                    print(f"⚠️  Error extracting tweet {i}: {e}")
                    continue
            
            await browser.close()
        
        return tweets
    
    async def get_user_tweets(self, username: str, limit: int = 20) -> List[Dict]:
        """Get tweets from specific user."""
        tweets = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            await self.load_cookies(context)
            
            page = await context.new_page()
            profile_url = f"https://x.com/{username}"
            
            print(f"👤 Getting tweets from: @{username}")
            await page.goto(profile_url, wait_until='networkidle')
            await asyncio.sleep(3)
            
            # Scroll to load more tweets
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
            
            # Extract tweets
            tweet_selectors = await page.query_selector_all('article[data-testid="tweet"]')
            
            for i, tweet in enumerate(tweet_selectors[:limit]):
                try:
                    text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                    text = await text_elem.inner_text() if text_elem else ""
                    
                    time_elem = await tweet.query_selector('time')
                    time_str = await time_elem.get_attribute('datetime') if time_elem else ""
                    
                    tweets.append({
                        'id': i,
                        'username': username,
                        'text': text,
                        'time': time_str
                    })
                    
                except Exception as e:
                    print(f"⚠️  Error: {e}")
                    continue
            
            await browser.close()
        
        return tweets

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='X/Twitter Scraper')
    parser.add_argument('action', choices=['search', 'user'], help='Action to perform')
    parser.add_argument('query', help='Search query or username')
    parser.add_argument('--limit', type=int, default=20, help='Number of tweets to fetch')
    parser.add_argument('--cookies', help='Path to cookies file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    scraper = XTScraper(cookies_path=args.cookies)
    
    if args.action == 'search':
        tweets = asyncio.run(scraper.search_tweets(args.query, args.limit))
    else:  # user
        tweets = asyncio.run(scraper.get_user_tweets(args.query, args.limit))
    
    if args.json:
        print(json.dumps(tweets, indent=2, ensure_ascii=False))
    else:
        print(f"\n📊 Found {len(tweets)} tweets\n")
        for tweet in tweets:
            print(f"@{tweet.get('username', tweet.get('user', 'Unknown'))}")
            print(f"📝 {tweet['text'][:200]}...")
            print(f"⏰ {tweet['time']}")
            if 'stats' in tweet:
                print(f"📈 {tweet['stats']}")
            print("-" * 50)
