#!/usr/bin/env python3
"""
Gmail OAuth Device Flow - For Headless Servers
==============================================

Uses Google's OAuth 2.0 for TVs and Limited-Input Devices.

How it works:
1. Script requests a device code from Google
2. Script shows you a URL and a user code
3. You open the URL on your phone/computer and enter the code
4. Script polls Google until you complete the auth
5. Token is saved and ready to use

Usage:
    python3 email_auth_device_flow.py

Requirements:
    pip3 install requests
"""

import sys
import os
import json
import time
import pickle
from pathlib import Path
import requests

print("=" * 70)
print("📧 Gmail OAuth Device Flow - Headless Server Authentication")
print("=" * 70)
print()

# OAuth 2.0 Device Flow endpoints
DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# Gmail scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels"
]

def authenticate_account(creds_path, token_path):
    """Authenticate a single Gmail account using device flow."""
    
    # Load client credentials
    with open(creds_path) as f:
        client_config = json.load(f)
    
    # Handle different JSON formats
    if 'installed' in client_config:
        client_id = client_config['installed']['client_id']
        client_secret = client_config['installed']['client_secret']
    elif 'web' in client_config:
        client_id = client_config['web']['client_id']
        client_secret = client_config['web']['client_secret']
    else:
        client_id = client_config['client_id']
        client_secret = client_config['client_secret']
    
    print(f"\n{'=' * 70}")
    print(f"🔐 Step 1: Requesting device code...")
    print(f"{'=' * 70}")
    
    # Step 1: Request device and user codes
    response = requests.post(
        DEVICE_CODE_URL,
        data={
            'client_id': client_id,
            'scope': ' '.join(SCOPES)
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get device code: {response.text}")
        return False
    
    device_data = response.json()
    device_code = device_data['device_code']
    user_code = device_data['user_code']
    verification_url = device_data['verification_url']
    expires_in = device_data['expires_in']
    interval = device_data['interval']
    
    print(f"\n✅ Device code received!")
    print(f"\n{'=' * 70}")
    print(f"📱 Step 2: Authorize with your phone/computer")
    print(f"{'=' * 70}")
    print(f"\n1. Go to this URL on your phone or computer:")
    print(f"   👉 {verification_url}")
    print(f"\n2. Enter this code when prompted:")
    print(f"   ┌─────────────────────────────────────┐")
    print(f"   │                                     │")
    print(f"   │      {user_code:^30}      │")
    print(f"   │                                     │")
    print(f"   └─────────────────────────────────────┘")
    print(f"\n3. Sign in to Gmail and click 'Allow'")
    print(f"\n⏳ Waiting for authorization (expires in {expires_in} seconds)...")
    print(f"\n{'=' * 70}")
    
    # Step 2: Poll for token
    start_time = time.time()
    while time.time() - start_time < expires_in:
        time.sleep(interval)
        
        token_response = requests.post(
            TOKEN_URL,
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'device_code': device_code,
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
            }
        )
        
        token_data = token_response.json()
        
        if 'error' in token_data:
            error = token_data['error']
            if error == 'authorization_pending':
                print("   ⏳ Waiting for you to authorize...")
                continue
            elif error == 'slow_down':
                interval += 5
                continue
            elif error == 'expired_token':
                print("❌ Authorization expired. Please try again.")
                return False
            elif error == 'access_denied':
                print("❌ Authorization denied by user.")
                return False
            else:
                print(f"❌ Error: {error}")
                continue
        
        # Success!
        if 'access_token' in token_data:
            print(f"\n✅ Authorization successful!")
            
            # Create credentials object compatible with Google API
            from google.oauth2.credentials import Credentials
            
            creds = Credentials(
                token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                token_uri=TOKEN_URL,
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES
            )
            
            # Save token
            with open(token_path, 'wb') as f:
                pickle.dump(creds, f)
            
            print(f"💾 Token saved to: {token_path.name}")
            return True
    
    print("❌ Authorization timed out.")
    return False

# Main script
config_dir = Path.home() / ".openclaw" / "email_config"
config_dir.mkdir(parents=True, exist_ok=True)

print(f"📁 Config directory: {config_dir}")

# Find credential files
gmail_files = list(config_dir.glob("gmail_credentials*.json")) + list(config_dir.glob("gmail_account*.json"))
gmail_files = [f for f in gmail_files if "token" not in f.name]

if not gmail_files:
    print("❌ No Gmail credential files found!")
    print(f"\nPlease save your OAuth credential files to:")
    print(f"   {config_dir}")
    print("\nWith names like:")
    print("   • gmail_account1.json")
    print("   • gmail_account2.json")
    sys.exit(1)

print(f"\n🔍 Found {len(gmail_files)} account(s) to authenticate:")
for f in sorted(gmail_files):
    print(f"   • {f.name}")

# Authenticate each account
success_count = 0
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
            with open(token_path, 'rb') as f:
                from google.oauth2.credentials import Credentials
                creds = pickle.load(f)
            if creds and creds.valid:
                print(f"✅ Already authenticated!")
                success_count += 1
                continue
        except:
            pass
    
    # Authenticate
    if authenticate_account(creds_path, token_path):
        success_count += 1

# Summary
print(f"\n{'=' * 70}")
print(f"🎉 Authentication Complete: {success_count}/{len(gmail_files)} accounts")
print(f"{'=' * 70}")

token_files = list(config_dir.glob("gmail_token_*.pickle"))
if token_files:
    print(f"\n📋 Active tokens:")
    for tf in sorted(token_files):
        print(f"   ✅ {tf.name}")
    print(f"\nYou can now use the email client!")
else:
    print("\n⚠️  No tokens created. Check errors above.")
