#!/usr/bin/env python3
"""
Twitter/X Scraper using Playwright
Uses cookies to access authenticated content
"""

from playwright.sync_api import sync_playwright
import json

# Your Twitter cookies from earlier
cookies_str = 'd_prefs=MjoxLGNvbnNlbnRfdmVyc2lvbjoyLHRleHRfdmVyc2lvbjoxMDAw; __cuid=a55a8855d2e44711919c27fc933a8e8b; dnt=1; personalization_id="v1_H2h/nF/JL692eZve5U/qjQ=="; g_state={"i_l":0,"i_ll":1770227285515,"i_b":"KT88xKBMx/SHoXlJe33MRafsMbFoAQVwNt/vlYdnHns","i_e":{"enable_itp_optimization":1}}; ads_prefs="HBESAAA="; guest_id_ads=v1%3A177025143212666750; guest_id_marketing=v1%3A177025143212666750; guest_id=v1%3A177025143212666750; twid=u%3D1562799790961729537; ct0=6b8c12c916a61259574f110f790375ffb46387998935e4d1cfd9a7167e3985a492060234ede77092f57a857aa2d363b39dad0cb26731c997c6d15de206d7c2c0483d0e9a2051e5b00440422a3cb5398f; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; lang=en'

def parse_cookies(cookie_string):
    """Parse cookie string into list of dicts for Playwright"""
    cookies = []
    for item in cookie_string.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            # Clean up value
            value = value.strip().strip('"')
            cookies.append({
                'name': key.strip(),
                'value': value,
                'domain': '.x.com',
                'path': '/'
            })
    return cookies

def scrape_tweet(url):
    """Scrape a specific tweet using Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        # Add cookies
        cookies = parse_cookies(cookies_str)
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            print(f"Navigating to: {url}")
            page.goto(url, wait_until='networkidle')
            
            # Wait for tweet content to load
            page.wait_for_selector('article', timeout=10000)
            
            # Extract tweet text
            tweet_text = page.inner_text('article [data-testid="tweetText"]')
            author = page.inner_text('article [data-testid="User-Name"]')
            
            print(f"\n{'='*60}")
            print(f"Author: {author}")
            print(f"{'='*60}")
            print(f"Tweet:\n{tweet_text}")
            print(f"{'='*60}")
            
            # Save screenshot
            page.screenshot(path='tweet_playwright.png')
            print("\nScreenshot saved: tweet_playwright.png")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path='error_playwright.png')
            print("Error screenshot saved: error_playwright.png")
        
        browser.close()

if __name__ == "__main__":
    # Replace with the tweet URL you want to scrape
    tweet_url = "https://x.com/alexfinn/status/2019816560190521563"
    scrape_tweet(tweet_url)
