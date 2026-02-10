#!/usr/bin/env python3
"""
Twitter/X Thread Scraper using Playwright
Scrapes main tweet + all replies in the thread
"""

from playwright.sync_api import sync_playwright
import json
import time

# Your Twitter cookies from earlier
cookies_str = 'd_prefs=MjoxLGNvbnNlbnRfdmVyc2lvbjoyLHRleHRfdmVyc2lvbjoxMDAw; __cuid=a55a8855d2e44711919c27fc933a8e8b; dnt=1; personalization_id="v1_H2h/nF/JL692eZve5U/qjQ=="; g_state={"i_l":0,"i_ll":1770227285515,"i_b":"KT88xKBMx/SHoXlJe33MRafsMbFoAQVwNt/vlYdnHns","i_e":{"enable_itp_optimization":1}}; ads_prefs="HBESAAA="; guest_id_ads=v1%3A177025143212666750; guest_id_marketing=v1%3A177025143212666750; guest_id=v1%3A177025143212666750; twid=u%3D1562799790961729537; ct0=6b8c12c916a61259574f110f790375ffb46387998935e4d1cfd9a7167e3985a492060234ede77092f57a857aa2d363b39dad0cb26731c997c6d15de206d7c2c0483d0e9a2051e5b00440422a3cb5398f; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; lang=en'

def parse_cookies(cookie_string):
    """Parse cookie string into list of dicts for Playwright"""
    cookies = []
    for item in cookie_string.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            value = value.strip().strip('"')
            cookies.append({
                'name': key.strip(),
                'value': value,
                'domain': '.x.com',
                'path': '/'
            })
    return cookies

def scrape_thread(url):
    """Scrape main tweet + thread replies"""
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
            
            # Wait for content to load
            page.wait_for_selector('article', timeout=15000)
            
            # Scroll down to load more replies
            print("Scrolling to load replies...")
            for i in range(5):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(2)
            
            # Extract all tweets in thread
            tweets = page.query_selector_all('article')
            
            print(f"\n{'='*80}")
            print(f"FOUND {len(tweets)} TWEETS IN THREAD")
            print(f"{'='*80}\n")
            
            thread_data = []
            
            for idx, tweet in enumerate(tweets, 1):
                try:
                    # Try to get tweet text
                    text_elem = tweet.query_selector('[data-testid="tweetText"]')
                    text = text_elem.inner_text() if text_elem else "No text"
                    
                    # Try to get author
                    author_elem = tweet.query_selector('[data-testid="User-Name"]')
                    author = author_elem.inner_text() if author_elem else "Unknown"
                    
                    # Try to get timestamp
                    time_elem = tweet.query_selector('time')
                    timestamp = time_elem.get_attribute('datetime') if time_elem else ""
                    
                    # Try to get stats (likes, retweets, etc)
                    stats = {}
                    try:
                        replies = tweet.query_selector('[data-testid="reply"]')
                        retweets = tweet.query_selector('[data-testid="retweet"]')
                        likes = tweet.query_selector('[data-testid="like"]')
                        
                        stats['replies'] = replies.inner_text() if replies else "0"
                        stats['retweets'] = retweets.inner_text() if retweets else "0"
                        stats['likes'] = likes.inner_text() if likes else "0"
                    except:
                        pass
                    
                    tweet_data = {
                        'number': idx,
                        'author': author.replace('\n', ' - '),
                        'text': text,
                        'timestamp': timestamp,
                        'stats': stats
                    }
                    thread_data.append(tweet_data)
                    
                    print(f"\n--- TWEET #{idx} ---")
                    print(f"Author: {author.replace(chr(10), ' - ')}")
                    print(f"Time: {timestamp}")
                    print(f"Text: {text[:200]}...")
                    if stats:
                        print(f"Stats: {stats}")
                    
                except Exception as e:
                    print(f"Error processing tweet #{idx}: {e}")
            
            # Save full thread data
            with open('thread_data.json', 'w', encoding='utf-8') as f:
                json.dump(thread_data, f, indent=2, ensure_ascii=False)
            print(f"\n{'='*80}")
            print(f"Full thread data saved to: thread_data.json")
            
            # Save screenshot
            page.screenshot(path='thread_screenshot.png', full_page=True)
            print(f"Full page screenshot saved: thread_screenshot.png")
            
            # Save text version
            with open('thread_text.txt', 'w', encoding='utf-8') as f:
                f.write(f"TWITTER THREAD: {url}\n")
                f.write(f"{'='*80}\n\n")
                for tweet in thread_data:
                    f.write(f"Tweet #{tweet['number']}\n")
                    f.write(f"Author: {tweet['author']}\n")
                    f.write(f"Time: {tweet['timestamp']}\n")
                    f.write(f"Text:\n{tweet['text']}\n")
                    if tweet['stats']:
                        f.write(f"Stats: {tweet['stats']}\n")
                    f.write(f"{'-'*80}\n\n")
            print(f"Text version saved: thread_text.txt")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path='thread_error.png')
            print("Error screenshot saved: thread_error.png")
        
        browser.close()

if __name__ == "__main__":
    tweet_url = "https://x.com/alexfinn/status/2019816560190521563"
    scrape_thread(tweet_url)
