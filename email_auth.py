#!/usr/bin/env python3
"""
Multi-Account Email Authentication Script
=========================================

Run this to authenticate with all configured Gmail and Outlook accounts.
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, '/home/faisal/.openclaw/workspace')

print("📧 OpenClaw Multi-Account Email Authentication")
print("=" * 60)
print()

# Check if dependencies are installed
try:
    from email_client import EmailClient
    print("✅ Email client module loaded")
except ImportError as e:
    print(f"❌ Error loading email client: {e}")
    print("\nInstalling dependencies...")
    os.system("pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client msal requests --user")
    print("\nPlease run this script again.")
    sys.exit(1)

# Check configuration directory
config_dir = Path.home() / ".openclaw" / "email_config"
config_dir.mkdir(parents=True, exist_ok=True)

print(f"📁 Configuration directory: {config_dir}")
print()

# Find all Gmail credential files
gmail_files = list(config_dir.glob("gmail_credentials*.json")) + list(config_dir.glob("gmail_account*.json"))
outlook_files = list(config_dir.glob("outlook_credentials*.json"))

# Filter out token files
gmail_files = [f for f in gmail_files if "token" not in f.name]
outlook_files = [f for f in outlook_files if "token" not in f.name]

print(f"🔍 Found {len(gmail_files)} Gmail credential file(s):")
for f in gmail_files:
    print(f"   • {f.name}")

print(f"\n🔍 Found {len(outlook_files)} Outlook credential file(s):")
for f in outlook_files:
    print(f"   • {f.name}")

print()
print("=" * 60)

if not gmail_files and not outlook_files:
    print("\n⚠️  No credentials found!")
    print("\nTo set up email access:")
    print("1. Download OAuth credentials from Google Cloud Console")
    print("2. Save credential files to the config directory:")
    print(f"   {config_dir}")
    print("\n   Naming convention:")
    print("   • gmail_account1.json, gmail_account2.json, etc.")
    print("   • OR: gmail_credentials.json, gmail_credentials_work.json, etc.")
    print("\n3. Run this script again to authenticate")
    sys.exit(1)

print("\n🔄 Initializing email clients...")
print("   (This will open browser windows for OAuth authentication)")
print("   You'll need to authenticate each account separately.")
print()

try:
    client = EmailClient()
    
    # List all loaded accounts
    providers = client.list_providers()
    gmail_accounts = list(client.gmail_clients.keys())
    outlook_accounts = list(client.outlook_clients.keys())
    
    if gmail_accounts:
        print(f"\n✅ Gmail accounts ready:")
        for acc in gmail_accounts:
            print(f"   • {acc}")
    
    if outlook_accounts:
        print(f"\n✅ Outlook accounts ready:")
        for acc in outlook_accounts:
            print(f"   • {acc}")
    
    if not gmail_accounts and not outlook_accounts:
        print("\n⚠️  No accounts were loaded. Check the error messages above.")
        sys.exit(1)
    
    # Test reading emails from each account
    print("\n🧪 Testing email access...")
    
    for account_name in gmail_accounts:
        try:
            emails = client.read_emails(account_name, limit=1)
            if emails:
                print(f"   ✅ {account_name}: Connected ({len(emails)} email(s) found)")
            else:
                print(f"   ✅ {account_name}: Connected (inbox empty or no access)")
        except Exception as e:
            print(f"   ⚠️  {account_name}: Connection issue - {e}")
    
    for account_name in outlook_accounts:
        try:
            emails = client.read_emails(account_name, limit=1)
            if emails:
                print(f"   ✅ {account_name}: Connected ({len(emails)} email(s) found)")
            else:
                print(f"   ✅ {account_name}: Connected (inbox empty or no access)")
        except Exception as e:
            print(f"   ⚠️  {account_name}: Connection issue - {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Email authentication complete!")
    print("\nYou can now use the email client:")
    print()
    print("  from email_client import EmailClient")
    print("  client = EmailClient()")
    print()
    print("  # Read from specific account:")
    for acc in gmail_accounts[:2]:
        print(f"  emails = client.read_emails('{acc}', limit=10)")
    print()
    print("  # Send from specific account:")
    for acc in gmail_accounts[:1]:
        print(f"  client.send_email('{acc}', 'to@example.com', 'Subject', 'Body')")
    print()
        
except Exception as e:
    print(f"\n❌ Authentication failed: {e}")
    import traceback
    traceback.print_exc()
