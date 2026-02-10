#!/usr/bin/env python3
"""
ScrapeGraph AI Setup for OpenClaw
==================================

Free alternative to Firecrawl with AI-powered scraping.
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("🕷️  ScrapeGraph AI Setup")
print("=" * 60)
print()

# Check if already installed
try:
    from scrapegraphai.graphs import SmartScraperGraph
    print("✅ ScrapeGraph AI already installed")
except ImportError:
    print("Installing ScrapeGraph AI...")
    os.system("pip3 install scrapegraphai playwright --break-system-packages 2>/dev/null || pip3 install scrapegraphai playwright")
    print("✅ Installation complete")

print()
print("=" * 60)
print("🔑 API Key Setup")
print("=" * 60)
print()
print("Choose your AI provider:")
print()
print("1. OpenAI (gpt-4o-mini) - Reliable, paid")
print("   Get key: https://platform.openai.com/api-keys")
print()
print("2. Groq (llama-3.1-70b) - FAST, free tier")
print("   Get key: https://console.groq.com/keys")
print("   Free: 14,400 requests/day")
print()
print("3. Ollama (local) - Completely free")
print("   Install: curl -fsSL https://ollama.com/install.sh | sh")
print("   Run: ollama run llama3.1")
print()
print("=" * 60)
print("💾 Configuration")
print("=" * 60)
print()

# Create config directory
config_dir = Path.home() / ".openclaw" / "scrapegraph"
config_dir.mkdir(parents=True, exist_ok=True)

env_file = config_dir / ".env"

if env_file.exists():
    print(f"✅ Config exists: {env_file}")
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0]
                print(f"   • {key}=***")
else:
    print("Creating config file...")
    with open(env_file, 'w') as f:
        f.write("# ScrapeGraph AI Configuration\n")
        f.write("# Choose ONE provider and add your key:\n\n")
        f.write("# Option 1: OpenAI\n")
        f.write("# OPENAI_API_KEY=your_key_here\n\n")
        f.write("# Option 2: Groq (RECOMMENDED - free tier)\n")
        f.write("# GROQ_API_KEY=your_key_here\n\n")
        f.write("# Option 3: Ollama (local, free)\n")
        f.write("# OLLAMA_URL=http://localhost:11434\n")
    print(f"✅ Created: {env_file}")
    print()
    print("📝 Edit this file and add your API key:")
    print(f"   nano {env_file}")

print()
print("=" * 60)
print("🚀 Usage Examples")
print("=" * 60)
print()
print("Once configured, use ScrapeGraph like this:")
print()
print("```python")
print("from scrapegraphai.graphs import SmartScraperGraph")
print()
print("graph = SmartScraperGraph(")
print("    prompt='Extract all article titles and links',")
print("    source='https://example.com/blog',")
print("    config={")
print("        'llm': {")
print("            'api_key': 'YOUR_KEY',")
print("            'model': 'gpt-4o-mini'")
print("        },")
print("        'headless': True")
print("    }")
print(")")
print("result = graph.run()")
print("print(result)")
print("```")
print()
print("=" * 60)
print("✨ Features")
print("=" * 60)
print()
print("• Natural language queries (no CSS selectors)")
print("• Multi-page crawling")
print("• Structured JSON output")
print("• Handles JavaScript sites")
print("• Completely FREE (with Groq or Ollama)")
print()
