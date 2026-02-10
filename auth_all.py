#!/usr/bin/env python3
"""
Gmail Authentication - All Accounts
====================================

This script authenticates all configured Gmail accounts sequentially.
It will start a local server for each account and open a browser window.

For headless environments, you can:
1. Run this on a machine with a browser, OR
2. Use SSH port forwarding: ssh -L 8081:localhost:8081 -L 8082:localhost:8082 user@server
   Then open the URLs in your local browser

Usage: python3 auth_all.py
"""

import sys
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

config_dir = Path.home() / ".openclaw" / "email_config"


def authenticate(account_num: int):
    """Authenticate a single Gmail account."""
    account_name = f"account{account_num}"
    creds_path = config_dir / f"gmail_{account_name}.json"
    token_path = config_dir / f"gmail_token_{account_name}.pickle"

    print()
    print("-" * 70)
    print(f"Account {account_num}: {account_name}")
    print("-" * 70)

    if not creds_path.exists():
        print(f"  Credentials file not found, skipping")
        return False

    # Check existing token
    if token_path.exists():
        try:
            with open(token_path, 'rb') as f:
                creds = pickle.load(f)

            if creds and creds.valid:
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile(userId='me').execute()
                email = profile.get('emailAddress', 'unknown')
                print(f"  Already authenticated: {email}")
                return True

            if creds and creds.expired and creds.refresh_token:
                print("  Token expired, refreshing...")
                creds.refresh(Request())
                with open(token_path, 'wb') as f:
                    pickle.dump(creds, f)
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile(userId='me').execute()
                email = profile.get('emailAddress', 'unknown')
                print(f"  Token refreshed: {email}")
                return True
        except Exception as e:
            print(f"  Existing token invalid, re-authenticating...")

    # Need to authenticate
    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    port = 8080 + account_num

    print(f"  Starting local server on port {port}...")
    print(f"  Waiting for browser authentication...")

    try:
        creds = flow.run_local_server(
            port=port,
            open_browser=True,
            authorization_prompt_message="",
            success_message="Authentication successful! You can close this tab."
        )

        # Save token
        with open(token_path, 'wb') as f:
            pickle.dump(creds, f)

        # Verify
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'unknown')

        print(f"  SUCCESS: {email}")
        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def main():
    print("=" * 70)
    print("Gmail Authentication - All Accounts")
    print("=" * 70)
    
    # Find all accounts
    accounts = []
    for f in sorted(config_dir.glob("gmail_account*.json")):
        account_name = f.stem.replace("gmail_", "")
        num = int(account_name.replace("account", ""))
        accounts.append(num)
    
    print(f"Found {len(accounts)} account(s) to authenticate")
    
    results = {}
    for num in accounts:
        results[num] = authenticate(num)
    
    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    success = sum(1 for v in results.values() if v)
    print(f"  Authenticated: {success}/{len(results)}")
    print()
    
    for num, status in results.items():
        icon = "OK" if status else "FAIL"
        print(f"  account{num}: {icon}")
    
    if success == len(results):
        print()
        print("All accounts authenticated successfully!")
        print()
        print("Test with:")
        print("  python3 -c \"from email_client import EmailClient; c = EmailClient(); print(c.gmail_clients.keys())\"")


if __name__ == "__main__":
    main()
