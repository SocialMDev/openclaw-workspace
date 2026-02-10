#!/usr/bin/env python3
"""
Twitter/X Scraper using Selenium
Uses cookies to access authenticated content
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Your Twitter cookies from earlier
cookies_str = 'd_prefs=MjoxLGNvbnNlbnRfdmVyc2lvbjoyLHRleHRfdmVyc2lvbjoxMDAw; __cuid=a55a8855d2e44711919c27fc933a8e8b; dnt=1; personalization_id="v1_H2h/nF/JL692eZve5U/qjQ=="; g_state={"i_l":0,"i_ll":1770227285515,"i_b":"KT88xKBMx/SHoXlJe33MRafsMbFoAQVwNt/vlYdnHns","i_e":{"enable_itp_optimization":1}}; ads_prefs="HBESAAA="; guest_id_ads=v1%3A177025143212666750; guest_id_marketing=v1%3A177025143212666750; guest_id=v1%3A177025143212666750; twid=u%3D1562799790961729537; ct0=6b8c12c916a61259574f110f790375ffb46387998935e4d1cfd9a7167e3985a492060234ede77092f57a857aa2d363b39dad0cb26731c997c6d15de206d7c2c0483d0e9a2051e5b00440422a3cb5398f; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; lang=en'

def parse_cookies(cookie_string):
    """Parse cookie string into list of dicts for Selenium"""
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

def scrape_tweet(url):
    """Scrape a specific tweet using Selenium"""
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Use Playwright's Chromium if available, otherwise system chromium
    chrome_options.binary_location = '/home/faisal/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome'
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to X first to set domain
        driver.get('https://x.com')
        time.sleep(2)
        
        # Add cookies
        cookies = parse_cookies(cookies_str)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                pass  # Some cookies might fail
        
        # Navigate to tweet
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for tweet to load
        wait = WebDriverWait(driver, 15)
        tweet_article = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
        
        # Extract data
        try:
            tweet_text = driver.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text
        except:
            tweet_text = "Could not extract tweet text"
        
        try:
            author = driver.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]').text
        except:
            author = "Unknown"
        
        print(f"\n{'='*60}")
        print(f"Author: {author}")
        print(f"{'='*60}")
        print(f"Tweet:\n{tweet_text}")
        print(f"{'='*60}")
        
        # Save screenshot
        driver.save_screenshot('tweet_selenium.png')
        print("\nScreenshot saved: tweet_selenium.png")
        
    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot('error_selenium.png')
        print("Error screenshot saved: error_selenium.png")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    tweet_url = "https://x.com/alexfinn/status/2019816560190521563"
    scrape_tweet(tweet_url)
