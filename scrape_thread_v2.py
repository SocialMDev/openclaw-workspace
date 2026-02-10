#!/usr/bin/env python3
"""
Twitter/X Thread Scraper v2 - Captures main tweet + replies
More aggressive scrolling and clicking "Show more"
"""

from playwright.sync_api import sync_playwright
import json
import time

cookies_str = 'd_prefs=MjoxLGNvbnNlbnRfdmVyc2lvbjoyLHRleHRfdmVyc2lvbjoxMDAw; __cuid=a55a8855d2e44711919c27fc933a8e8b; dnt=1; personalization_id="v1_H2h/nF/JL692eZve5U/qjQ=="; g_state={"i_l":0,"i_ll":1770227285515,"i_b":"KT88xKBMx/SHoXlJe33MRafsMbFoAQVwNt/vlYdnHns","i_e":{"enable_itp_optimization":1}}; ads_prefs="HBESAAA="; guest_id_ads=v1%3A177025143212666750; guest_id_marketing=v1%3A177025143212666750; guest_id=v1%3A177025143212666750; twid=u%3D1562799790961729537; ct0=6b8c12c916a61259574f110f790375ffb46387998935e4d1cfd9a7167e3985a492060234ede77092f57a857aa2d363b39dad0cb26731c997c6d15de206d7c2c0483d0e9a2051e5b00440422a3cb5398f; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; lang=en'

def parse_cookies(cookie_string):
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

def scrape_thread_with_replies(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        
        cookies = parse_cookies(cookies_str)
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            print(f"Loading: {url}")
            page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait for initial load
            page.wait_for_selector('article', timeout=20000)
            print("Initial page loaded")
            
            # Aggressive scrolling to load replies
            print("Loading replies... (this may take a moment)")
            all_tweets = set()
            last_count = 0
            no_change_count = 0
            
            for scroll_num in range(15):  # More scroll attempts
                # Scroll down
                page.evaluate('window.scrollBy(0, 800)')
                time.sleep(2)
                
                # Try to click "Show more replies" buttons
                try:
                    show_more_buttons = page.query_selector_all('span:text-is("Show more replies")')
                    for btn in show_more_buttons[:3]:  # Click up to 3
                        btn.click()
                        time.sleep(1)
                except:
                    pass
                
                # Try to click "Show additional replies" 
                try:
                    additional_buttons = page.query_selector_all('span:text-is("Show additional replies")')
                    for btn in additional_buttons[:2]:
                        btn.click()
                        time.sleep(1)
                except:
                    pass
                
                # Count current tweets
                current_tweets = page.query_selector_all('article')
                current_count = len(current_tweets)
                
                if current_count > last_count:
                    print(f"  Scroll {scroll_num+1}: Found {current_count} tweets (+{current_count - last_count})")
                    last_count = current_count
                    no_change_count = 0
                else:
                    no_change_count += 1
                    if no_change_count >= 3:  # Stop if no new tweets for 3 scrolls
                        print(f"  No new tweets loaded. Stopping.")
                        break
            
            # Now extract all tweet data
            print(f"\n{'='*80}")
            print(f"EXTRACTING {last_count} TWEETS")
            print(f"{'='*80}\n")
            
            tweets = page.query_selector_all('article')
            thread_data = []
            
            for idx, tweet in enumerate(tweets, 1):
                try:
                    # Get text
                    text_elem = tweet.query_selector('[data-testid="tweetText"]')
                    text = text_elem.inner_text() if text_elem else ""
                    
                    # Get author
                    author_elem = tweet.query_selector('[data-testid="User-Name"]')
                    author = author_elem.inner_text().replace('\n', ' - ') if author_elem else "Unknown"
                    
                    # Check if it's a reply (has reply indicator)
                    is_reply = tweet.query_selector('[data-testid="reply"]') is not None
                    
                    # Get reply indicator if present
                    reply_to = ""
                    try:
                        reply_elem = tweet.query_selector('a[href*="/status/"] span')
                        if reply_elem and "Replying to" in reply_elem.inner_text():
                            reply_to = reply_elem.inner_text()
                    except:
                        pass
                    
                    tweet_data = {
                        'number': idx,
                        'author': author,
                        'text': text,
                        'is_reply': is_reply,
                        'reply_context': reply_to
                    }
                    thread_data.append(tweet_data)
                    
                    # Print summary
                    text_preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"\n--- Tweet #{idx} {'(REPLY)' if is_reply else '(MAIN)'} ---")
                    print(f"Author: {author}")
                    print(f"Text: {text_preview}")
                    
                except Exception as e:
                    print(f"Error on tweet #{idx}: {e}")
            
            # Save results
            with open('full_thread.json', 'w', encoding='utf-8') as f:
                json.dump(thread_data, f, indent=2, ensure_ascii=False)
            
            with open('full_thread.txt', 'w', encoding='utf-8') as f:
                for t in thread_data:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Tweet #{t['number']}\n")
                    f.write(f"Type: {'REPLY' if t['is_reply'] else 'MAIN TWEET'}\n")
                    f.write(f"Author: {t['author']}\n")
                    if t['reply_context']:
                        f.write(f"Context: {t['reply_context']}\n")
                    f.write(f"\n{t['text']}\n")
            
            page.screenshot(path='full_thread.png', full_page=True)
            
            print(f"\n{'='*80}")
            print(f"✅ SAVED:")
            print(f"  - full_thread.json (structured data)")
            print(f"  - full_thread.txt (readable format)")
            print(f"  - full_thread.png (screenshot)")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path='thread_error.png')
        
        browser.close()

if __name__ == "__main__":
    scrape_thread_with_replies("https://x.com/alexfinn/status/2019816560190521563")
