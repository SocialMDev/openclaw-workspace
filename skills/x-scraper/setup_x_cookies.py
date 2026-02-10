#!/usr/bin/env python3
"""
X Cookie Setup Helper
=====================

Helps you set up X/Twitter cookies for scraping.

Usage:
    python3 setup_x_cookies.py
"""

import json
from pathlib import Path

print("=" * 60)
print("🔐 X/Twitter Cookie Setup")
print("=" * 60)
print()

# Cookie directory
cookie_dir = Path.home() / ".openclaw" / "cookies"
cookie_dir.mkdir(parents=True, exist_ok=True)

cookie_file = cookie_dir / "x_cookies.json"

print(f"📁 Cookie location: {cookie_file}")
print()

# Check if cookies exist
if cookie_file.exists():
    print("✅ Cookies already exist!")
    try:
        with open(cookie_file) as f:
            cookies = json.load(f)
        print(f"   Found {len(cookies)} cookie(s)")
        
        # Check for important cookies
        auth_cookie = any(c.get('name') == 'auth_token' for c in cookies)
        if auth_cookie:
            print("   ✅ auth_token found (you're logged in)")
        else:
            print("   ⚠️  auth_token not found (may need re-login)")
            
    except Exception as e:
        print(f"   ❌ Error reading cookies: {e}")
else:
    print("❌ No cookies found!")
    print()
    print("How to export cookies:")
    print("1. Install 'Cookie-Editor' extension in Chrome/Firefox")
    print("2. Login to x.com in your browser")
    print("3. Click Cookie-Editor extension")
    print("4. Click 'Export' → 'JSON' format")
    print("5. Save the file and copy contents")
    print()
    
    # Option to paste cookies
    print("Paste your cookies JSON here (Ctrl+D when done):")
    print("-" * 60)
    
    try:
        cookie_json = ""
        while True:
            try:
                line = input()
                cookie_json += line + "\n"
            except EOFError:
                break
        
        if cookie_json.strip():
            cookies = json.loads(cookie_json)
            with open(cookie_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f"\n✅ Saved {len(cookies)} cookie(s)!")
        else:
            print("\n⚠️  No cookies provided")
            
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

print()
print("=" * 60)
print("Test your setup:")
print(f"  python3 skills/x-scraper/x_scraper.py search 'test' --limit 3")
print("=" * 60)
