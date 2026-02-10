#!/usr/bin/env python3
"""
ScrapeGraph AI Example - Scrape Any Website
============================================

Usage:
    python3 scrape_example.py "https://example.com" "extract article titles"
"""

import os
import sys
import json
from pathlib import Path

# Load API key from env
def load_api_key():
    env_file = Path.home() / ".openclaw" / "scrapegraph" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith('GROQ_API_KEY='):
                    return line.split('=')[1].strip().strip('"').strip("'")
                if line.startswith('OPENAI_API_KEY='):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY')

def scrape_with_scrapegraph(url: str, prompt: str, api_key: str = None):
    """Scrape a website using ScrapeGraph AI."""
    
    try:
        from scrapegraphai.graphs import SmartScraperGraph
    except ImportError:
        print("❌ ScrapeGraph not installed")
        print("Run: pip3 install scrapegraphai playwright")
        sys.exit(1)
    
    api_key = api_key or load_api_key()
    
    if not api_key:
        print("❌ No API key found!")
        print("Set GROQ_API_KEY or OPENAI_API_KEY environment variable")
        print("Or create: ~/.openclaw/scrapegraph/.env")
        sys.exit(1)
    
    # Detect provider from key format
    if api_key.startswith('gsk_'):
        provider = 'groq'
        model = 'groq/llama-3.3-70b-versatile'
        print("🤖 Using Groq (free tier)")
    else:
        provider = 'openai'
        model = 'gpt-4o-mini'
        print("🤖 Using OpenAI")
    
    # Configure graph
    config = {
        'llm': {
            'api_key': api_key,
            'model': model,
        },
        'headless': True,
        'verbose': False,
    }
    
    print(f"🔍 Scraping: {url}")
    print(f"📝 Prompt: {prompt}")
    
    try:
        graph = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=config
        )
        
        result = graph.run()
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape website with AI')
    parser.add_argument('url', help='Website URL to scrape')
    parser.add_argument('prompt', help='What to extract (natural language)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    result = scrape_with_scrapegraph(args.url, args.prompt)
    
    if result:
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 60)
            print("📊 Results")
            print("=" * 60)
            print(result)
    else:
        print("Failed to scrape")
        sys.exit(1)
