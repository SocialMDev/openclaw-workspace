#!/usr/bin/env python3
"""
Multi-Account Email Authentication (Headless-Safe)
===================================================

This script authenticates your Gmail accounts using console-based OAuth.
It prints a URL that you open in your browser, then you paste back the auth code.

Usage:
    uv run python email_auth_console.py
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, '/home/faisal/.openclaw/workspace')

print("=" * 70)
print("📧 OpenClaw Multi-Account Email Authentication")
print("=" * 70)
print()

# Check if dependencies are installed
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import pickle
    print("✅ Google API libraries loaded")
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("\nInstalling...")
    os.system("pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client --user")
    print("\nPlease run this script again.")
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

# Configuration directory
config_dir = Path.home() / ".openclaw" / "email_config"
config_dir.mkdir(parents=True, exist_ok=True)

print(f"📁 Config directory: {config_dir}")
print()

# Find all Gmail credential files
gmail_files = list(config_dir.glob("gmail_credentials*.json")) + list(config_dir.glob("gmail_account*.json"))
gmail_files = [f for f in gmail_files if "token" not in f.name]

if not gmail_files:
    print("❌ No Gmail credential files found!")
    print(f"\nPlease save your OAuth credential files to:")
    print(f"   {config_dir}")
    print("\nWith names like:")
    print("   • gmail_account1.json")
    print("   • gmail_account2.json")
    print("   • gmail_credentials.json")
    sys.exit(1)

print(f"🔍 Found {len(gmail_files)} Gmail account(s):")
for f in sorted(gmail_files):
    print(f"   • {f.name}")
print()

# Authenticate each account
for creds_path in sorted(gmail_files):
    # Determine account name
    if creds_path.name == "gmail_credentials.json":
        account_name = "gmail"
    elif creds_path.name.startswith("gmail_account"):
        account_name = creds_path.stem.replace("gmail_", "").lower()
    else:
        account_name = creds_path.stem.replace("gmail_credentials_", "").lower()
    
    token_path = config_dir / f"gmail_token_{account_name}.pickle"
    
    print(f"\n{'=' * 70}")
    print(f"🔐 Account: {account_name}")
    print(f"{'=' * 70}")
    
    # Check if already authenticated
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        if creds and creds.valid:
            print(f"✅ Already authenticated (token valid)")
            continue
        elif creds and creds.expired and creds.refresh_token:
            print(f"🔄 Refreshing token...")
            creds.refresh(Request())
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
            print(f"✅ Token refreshed!")
            continue
    
    # Need to authenticate
    print(f"\n🌐 Opening OAuth flow...")
    print(f"   Credential file: {creds_path.name}")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)

        print("\n" + "-" * 70)
        print("INSTRUCTIONS:")
        print("1. A URL will be shown below")
        print("2. Open it in your browser and sign in")
        print("3. Grant the requested permissions")
        print("4. The script will automatically detect when you're done")
        print("-" * 70)
        print()

        # Use local server with open_browser=False so we don't need a display
        # The server will wait for the OAuth callback
        creds = flow.run_local_server(
            port=0,  # Use any available port
            open_browser=False,  # Don't try to open browser automatically
            authorization_prompt_message="Open this URL in your browser:\n{url}",
            success_message="Authentication successful! You can close this window.",
            timeout_seconds=300  # 5 minute timeout
        )

        # Save token
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

        print(f"\n✅ Authentication successful!")
        print(f"💾 Token saved: {token_path.name}")

        # Verify by getting user profile
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email_addr = profile.get('emailAddress', 'unknown')
        print(f"📧 Connected as: {email_addr}")

    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 70)
print("🎉 All Accounts Authenticated!")
print("=" * 70)
print()
print("You can now use the email client:")
print()
print("  from email_client import EmailClient")
print("  client = EmailClient()")
print("  emails = client.read_emails('account1', limit=10)")
print()

# List all tokens
token_files = list(config_dir.glob("gmail_token_*.pickle"))
if token_files:
    print("📋 Token files created:")
    for tf in sorted(token_files):
        size = tf.stat().st_size
        print(f"   • {tf.name} ({size} bytes)")
