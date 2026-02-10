#!/usr/bin/env python3
"""
Twitter/X Scraper using Requests + BeautifulSoup
Basic version - may not work for JavaScript-heavy content
"""

import requests
from bs4 import BeautifulSoup

# Your Twitter cookies from earlier
cookies_str = 'd_prefs=MjoxLGNvbnNlbnRfdmVyc2lvbjoyLHRleHRfdmVyc2lvbjoxMDAw; __cuid=a55a8855d2e44711919c27fc933a8e8b; dnt=1; personalization_id="v1_H2h/nF/JL692eZve5U/qjQ=="; g_state={"i_l":0,"i_ll":1770227285515,"i_b":"KT88xKBMx/SHoXlJe33MRafsMbFoAQVwNt/vlYdnHns","i_e":{"enable_itp_optimization":1}}; ads_prefs="HBESAAA="; guest_id_ads=v1%3A177025143212666750; guest_id_marketing=v1%3A177025143212666750; guest_id=v1%3A177025143212666750; twid=u%3D1562799790961729537; ct0=6b8c12c916a61259574f110f790375ffb46387998935e4d1cfd9a7167e3985a492060234ede77092f57a857aa2d363b39dad0cb26731c997c6d15de206d7c2c0483d0e9a2051e5b00440422a3cb5398f; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; lang=en'

def parse_cookies(cookie_string):
    """Parse cookie string into dict for requests"""
    cookies = {}
    for item in cookie_string.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip().strip('"')
    return cookies

def scrape_tweet(url):
    """Scrape a tweet using requests + BeautifulSoup"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://x.com/',
    }
    
    cookies = parse_cookies(cookies_str)
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, cookies=cookies, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Size: {len(response.text)} bytes")
        
        # Save raw HTML for inspection
        with open('tweet_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Raw HTML saved: tweet_response.html")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract tweet text
        # Note: X/Twitter heavily relies on JS, so this might not work well
        tweet_text_div = soup.find('div', {'data-testid': 'tweetText'})
        if tweet_text_div:
            print(f"\n{'='*60}")
            print(f"Tweet Text:\n{tweet_text_div.get_text()}")
            print(f"{'='*60}")
        else:
            print("\nNote: Could not extract tweet text with BeautifulSoup alone.")
            print("X/Twitter requires JavaScript rendering. Use Playwright or Selenium instead.")
            print("\nSaved HTML for manual inspection.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    tweet_url = "https://x.com/alexfinn/status/2019816560190521563"
    scrape_tweet(tweet_url)
