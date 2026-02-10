#!/usr/bin/env python3
"""
Manual OAuth Flow for Headless Servers
========================================

Since this is a headless server without a browser, we'll use the manual OAuth flow:
1. Script generates an authorization URL
2. You open the URL in your browser
3. You authorize the app
4. You copy the authorization code
5. Paste it back to complete authentication

Usage:
    python3 email_auth_manual.py
"""

import sys
import os
import json
from pathlib import Path
from urllib.parse import urlencode

# Add paths
sys.path.insert(0, '/home/faisal/.openclaw/workspace')

print("=" * 70)
print("📧 Gmail Manual OAuth Authentication")
print("=" * 70)
print()
print("This script will help you authenticate Gmail accounts on a headless server.")
print("You'll need to copy/paste authorization codes from your browser.")
print()

# Check dependencies
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    import pickle
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("\nPlease install:")
    print("  pip3 install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'  # Out-of-band / manual flow

config_dir = Path.home() / ".openclaw" / "email_config"
config_dir.mkdir(parents=True, exist_ok=True)

# Find all Gmail credential files
gmail_files = list(config_dir.glob("gmail_credentials*.json")) + list(config_dir.glob("gmail_account*.json"))
gmail_files = [f for f in gmail_files if "token" not in f.name]

if not gmail_files:
    print("❌ No credential files found in:", config_dir)
    sys.exit(1)

print(f"Found {len(gmail_files)} account(s) to authenticate:\n")
for f in sorted(gmail_files):
    print(f"  • {f.name}")
print()

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
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            if creds and creds.valid:
                print(f"✅ Already authenticated!")
                continue
            elif creds and creds.expired and creds.refresh_token:
                print(f"🔄 Refreshing token...")
                creds.refresh(Request())
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print(f"✅ Token refreshed!")
                continue
        except Exception as e:
            print(f"⚠️  Existing token invalid: {e}")
    
    # Load client config
    with open(creds_path) as f:
        client_config = json.load(f)
    
    # Create flow
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    # Generate authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print(f"\n1️⃣  Open this URL in your browser:\n")
    print(f"   {auth_url}")
    print(f"\n   (Right-click to copy, then paste in your browser)")
    print()
    
    # Get authorization code from user
    print("2️⃣  After authorizing, you'll get a code.")
    print("3️⃣  Paste the code here and press Enter:\n")
    
    try:
        auth_code = input("   Authorization code: ").strip()
    except EOFError:
        print("\n❌ Cannot read input in non-interactive mode.")
        print("\n💡 SOLUTION: Run this script with an interactive terminal:")
        print("   ssh -t your-server 'cd ~/.openclaw/workspace && python3 email_auth_manual.py'")
        print("\n   Or use: script -q -c 'python3 email_auth_manual.py'")
        sys.exit(1)
    
    if not auth_code:
        print("❌ No code provided. Skipping...")
        continue
    
    try:
        # Exchange code for credentials
        print("\n🔄 Exchanging code for tokens...")
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save token
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ Success! Token saved: {token_path.name}")
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nCommon issues:")
        print("  • Code expired - generate a new one")
        print("  • Wrong Google Cloud project - check credentials file")
        print("  • App not verified - use test users in Google Cloud Console")

print()
print("=" * 70)
print("🎉 Authentication Process Complete!")
print("=" * 70)
print()

# Summary
token_files = list(config_dir.glob("gmail_token_*.pickle"))
if token_files:
    print("📋 Active tokens:")
    for tf in sorted(token_files):
        print(f"   ✅ {tf.name}")
    print()
    print("You can now use the email client:")
    print("  from email_client import EmailClient")
    print("  client = EmailClient()")
    print("  emails = client.read_emails('account1', limit=10)")
else:
    print("⚠️  No tokens were created. Check the errors above.")
