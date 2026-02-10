#!/usr/bin/env python3
"""
Gmail Multi-Account Verification Script
========================================

Run this after uploading token files to verify all accounts work.

Usage:
    python3 verify_gmail.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, '/home/faisal/.openclaw/workspace')

print("=" * 70)
print("📧 Gmail Multi-Account Verification")
print("=" * 70)
print()

# Check dependencies
try:
    from email_client import EmailClient
    print("✅ Email client module loaded")
except ImportError as e:
    print(f"❌ Error loading email client: {e}")
    print("\nInstalling dependencies...")
    os.system("pip3 install google-auth google-auth-oauthlib google-api-python-client --user")
    sys.exit(1)

config_dir = Path.home() / ".openclaw" / "email_config"

# Check for credential and token files
cred_files = list(config_dir.glob("gmail_account*.json"))
token_files = list(config_dir.glob("gmail_token_*.pickle"))

print(f"📁 Config directory: {config_dir}")
print(f"   Found {len(cred_files)} credential file(s)")
print(f"   Found {len(token_files)} token file(s)")
print()

if not cred_files:
    print("❌ No credential files found!")
    sys.exit(1)

if not token_files:
    print("❌ No token files found!")
    print("\n⚠️  You need to authenticate first:")
    print("   1. Run authentication on your local computer with browser")
    print("   2. Upload the .pickle token files to the server")
    sys.exit(1)

# Initialize client
print("🔄 Initializing email client...")
try:
    client = EmailClient()
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    sys.exit(1)

# Get all loaded accounts
all_accounts = list(client.gmail_clients.keys())

if not all_accounts:
    print("❌ No Gmail accounts loaded!")
    print("   Check that token files match credential files.")
    sys.exit(1)

print(f"✅ Loaded {len(all_accounts)} account(s): {', '.join(all_accounts)}")
print()

# Test each account
print("=" * 70)
print("🧪 Testing Email Access")
print("=" * 70)

results = []
for account in sorted(all_accounts):
    print(f"\n🔐 Account: {account}")
    print("-" * 50)
    
    try:
        # Try to read emails
        emails = client.read_emails(account, limit=5)
        
        if emails:
            print(f"   ✅ SUCCESS - Found {len(emails)} email(s)")
            print(f"   📨 Latest email:")
            print(f"      From: {emails[0].sender[:50]}")
            print(f"      Subject: {emails[0].subject[:60]}")
            print(f"      Date: {emails[0].date.strftime('%Y-%m-%d %H:%M')}")
            results.append((account, True, len(emails)))
        else:
            print(f"   ⚠️  CONNECTED - No emails found (inbox may be empty)")
            results.append((account, True, 0))
            
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        results.append((account, False, 0))

# Summary
print()
print("=" * 70)
print("📊 Summary")
print("=" * 70)

success_count = sum(1 for _, status, _ in results if status)
total_count = len(results)

for account, status, count in results:
    status_icon = "✅" if status else "❌"
    print(f"   {status_icon} {account:15} {'OK' if status else 'FAILED'} ({count} emails)")

print()
print(f"Result: {success_count}/{total_count} accounts working")

if success_count == total_count:
    print("\n🎉 All Gmail accounts are ready to use!")
    print("\nExample usage:")
    print("  from email_client import EmailClient")
    print("  client = EmailClient()")
    for acc in sorted(all_accounts)[:2]:
        print(f"  emails = client.read_emails('{acc}', limit=10)")
    sys.exit(0)
else:
    print("\n⚠️  Some accounts failed. Check errors above.")
    sys.exit(1)
