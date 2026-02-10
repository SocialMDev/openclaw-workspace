#!/usr/bin/env python3
"""
Local Gmail Authentication - Run on YOUR COMPUTER
=================================================

This authenticates Gmail accounts on your local machine (with browser),
then you upload the generated token files to the server.

Steps:
1. Save credential files to ~/.openclaw/email_config/ on YOUR COMPUTER
2. Run this script - browser windows will open
3. Log in to each Gmail account
4. Upload the generated .pickle files to your server
"""

import os
import sys
import pickle
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Installing dependencies...")
    os.system("pip3 install google-auth google-auth-oauthlib google-api-python-client")
    print("Run again.")
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send', 
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

config_dir = Path.home() / ".openclaw" / "email_config"
config_dir.mkdir(parents=True, exist_ok=True)

gmail_files = list(config_dir.glob("gmail_*.json"))
gmail_files = [f for f in gmail_files if "token" not in f.name]

print("=" * 60)
print("Gmail Authentication - Local Machine")
print("=" * 60)
print(f"\nConfig dir: {config_dir}")
print(f"Found {len(gmail_files)} account(s)\n")

for f in gmail_files:
    print(f"  • {f.name}")

for creds_path in sorted(gmail_files):
    account = creds_path.stem.replace("gmail_", "").lower()
    token_path = config_dir / f"gmail_token_{account}.pickle"
    
    print(f"\n{'=' * 60}")
    print(f"Account: {account}")
    print(f"{'=' * 60}")
    
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        if creds and creds.valid:
            print("✅ Already authenticated")
            continue
    
    print("🌐 Opening browser for authentication...")
    
    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    creds = flow.run_local_server(port=0)
    
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"✅ Saved: {token_path.name}")

print("\n" + "=" * 60)
print("Upload these files to your server:")
tokens = list(config_dir.glob("gmail_token_*.pickle"))
for t in tokens:
    print(f"  scp {t} your-server:~/.openclaw/email_config/")
print("=" * 60)
