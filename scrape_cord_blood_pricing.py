#!/usr/bin/env python3
"""
Scrape cord blood bank pricing from US providers
"""

from playwright.sync_api import sync_playwright
import json

banks = [
    {
        "name": "ViaCord",
        "url": "https://www.viacord.com/pricing",
        "fallback_url": "https://www.viacord.com/cord-blood-banking-options"
    },
    {
        "name": "CBR (Cord Blood Registry)",
        "url": "https://www.cordblood.com/pricing",
        "fallback_url": "https://www.cordblood.com/pricing-plans"
    },
    {
        "name": "Americord",
        "url": "https://www.americordblood.com/pricing",
        "fallback_url": "https://www.americordblood.com/cord-blood/"
    },
    {
        "name": "StemCyte",
        "url": "https://www.stemcyte.com/cord-blood-banking-cost",
        "fallback_url": "https://www.stemcyte.com/private-cord-blood-banking"
    }
]

def scrape_bank(page, bank):
    """Scrape pricing from a single bank"""
    print(f"\n{'='*60}")
    print(f"Checking: {bank['name']}")
    print(f"{'='*60}")
    
    try:
        # Try primary URL
        page.goto(bank['url'], timeout=30000)
        page.wait_for_load_state('networkidle')
        
        # Get all text content
        content = page.inner_text('body')
        
        # Look for pricing keywords
        lines = content.split('\n')
        pricing_info = []
        
        for line in lines:
            line = line.strip()
            # Look for price patterns ($X,XXX or $X,Xxx)
            if '$' in line and any(c.isdigit() for c in line):
                if any(keyword in line.lower() for keyword in [
                    'price', 'cost', 'plan', 'blood', 'tissue', 'lifetime', 
                    'storage', 'annual', 'year', 'month', 'payment'
                ]):
                    if len(line) < 200:  # Keep it concise
                        pricing_info.append(line)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_pricing = []
        for line in pricing_info:
            if line not in seen and len(seen) < 10:
                seen.add(line)
                unique_pricing.append(line)
        
        result = {
            "bank": bank['name'],
            "url": bank['url'],
            "found": len(unique_pricing) > 0,
            "pricing_snippets": unique_pricing[:10],
            "full_content_preview": content[:500] if not unique_pricing else ""
        }
        
        for line in unique_pricing[:5]:
            print(f"  💰 {line}")
        
        if not unique_pricing:
            print(f"  ⚠️  No pricing found on page (may need login or different page)")
            
        return result
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {
            "bank": bank['name'],
            "url": bank['url'],
            "error": str(e),
            "found": False
        }

def main():
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        for bank in banks:
            result = scrape_bank(page, bank)
            results.append(result)
            page.wait_for_timeout(2000)  # Be nice to servers
        
        browser.close()
    
    # Save results
    with open('cord_blood_pricing.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "✅ Found pricing" if r['found'] else "❌ No pricing found"
        print(f"{r['bank']}: {status}")
    print(f"\nDetailed results saved to: cord_blood_pricing.json")

if __name__ == "__main__":
    main()
