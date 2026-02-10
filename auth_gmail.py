#!/usr/bin/env python3
"""
Gmail Account Authentication Helper
====================================

Usage:
    # Step 1: Get the authorization URL
    python3 auth_gmail.py account1 --url

    # Step 2: Open URL in browser, authorize, copy the code

    # Step 3: Complete authentication with the code
    python3 auth_gmail.py account1 --code "4/0ABC..."

Accounts: account1, account2, account3, account4
"""

import sys
import os
import pickle
import argparse
from pathlib import Path

# Setup
sys.path.insert(0, '/home/faisal/.openclaw/workspace')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

config_dir = Path.home() / ".openclaw" / "email_config"


def get_auth_url(account_name: str) -> str:
    """Generate authorization URL for an account."""
    creds_path = config_dir / f"gmail_{account_name}.json"

    if not creds_path.exists():
        raise FileNotFoundError(f"Credentials not found: {creds_path}")

    flow = InstalledAppFlow.from_client_secrets_file(
        str(creds_path),
        SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    return auth_url


def authenticate_with_code(account_name: str, code: str) -> bool:
    """Complete authentication using authorization code."""
    creds_path = config_dir / f"gmail_{account_name}.json"
    token_path = config_dir / f"gmail_token_{account_name}.pickle"

    if not creds_path.exists():
        raise FileNotFoundError(f"Credentials not found: {creds_path}")

    flow = InstalledAppFlow.from_client_secrets_file(
        str(creds_path),
        SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    # Exchange code for token
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Save token
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)

    # Verify
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    email_addr = profile.get('emailAddress', 'unknown')

    print(f"✅ Authenticated: {email_addr}")
    print(f"💾 Token saved: {token_path}")

    return True


def check_status(account_name: str) -> dict:
    """Check authentication status for an account."""
    creds_path = config_dir / f"gmail_{account_name}.json"
    token_path = config_dir / f"gmail_token_{account_name}.pickle"

    status = {
        'account': account_name,
        'credentials_exist': creds_path.exists(),
        'token_exists': token_path.exists(),
        'token_valid': False,
        'email': None
    }

    if token_path.exists():
        try:
            with open(token_path, 'rb') as f:
                creds = pickle.load(f)

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'wb') as f:
                    pickle.dump(creds, f)

            if creds and creds.valid:
                status['token_valid'] = True
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile(userId='me').execute()
                status['email'] = profile.get('emailAddress')
        except Exception as e:
            status['error'] = str(e)

    return status


def main():
    parser = argparse.ArgumentParser(description='Gmail OAuth Authentication Helper')
    parser.add_argument('account', nargs='?', help='Account name (e.g., account1)')
    parser.add_argument('--url', action='store_true', help='Get authorization URL')
    parser.add_argument('--code', type=str, help='Authorization code from Google')
    parser.add_argument('--status', action='store_true', help='Check authentication status')
    parser.add_argument('--all', action='store_true', help='Process all accounts')

    args = parser.parse_args()

    # Status check for all accounts
    if args.status and args.all:
        print("📊 Gmail Authentication Status")
        print("=" * 50)
        for i in range(1, 5):
            account = f"account{i}"
            status = check_status(account)
            if status['token_valid']:
                print(f"✅ {account}: {status['email']}")
            elif status['token_exists']:
                print(f"⚠️  {account}: Token exists but invalid")
            elif status['credentials_exist']:
                print(f"❌ {account}: Not authenticated")
            else:
                print(f"⛔ {account}: No credentials")
        return

    # Get URLs for all accounts
    if args.url and args.all:
        print("🔗 Authorization URLs")
        print("=" * 50)
        for i in range(1, 5):
            account = f"account{i}"
            try:
                url = get_auth_url(account)
                print(f"\n📧 {account}:")
                print(url)
            except Exception as e:
                print(f"\n❌ {account}: {e}")
        return

    # Single account operations
    if not args.account:
        parser.print_help()
        print("\n📋 Available accounts: account1, account2, account3, account4")
        print("\nExamples:")
        print("  python3 auth_gmail.py --status --all    # Check all accounts")
        print("  python3 auth_gmail.py account1 --url    # Get auth URL")
        print("  python3 auth_gmail.py account1 --code 'CODE'  # Complete auth")
        return

    if args.status:
        status = check_status(args.account)
        print(f"Account: {args.account}")
        print(f"  Credentials: {'✅' if status['credentials_exist'] else '❌'}")
        print(f"  Token: {'✅' if status['token_exists'] else '❌'}")
        print(f"  Valid: {'✅' if status['token_valid'] else '❌'}")
        if status.get('email'):
            print(f"  Email: {status['email']}")
        if status.get('error'):
            print(f"  Error: {status['error']}")

    elif args.url:
        url = get_auth_url(args.account)
        print(f"🔗 Authorization URL for {args.account}:\n")
        print(url)
        print(f"\n👉 Open this URL, authorize, then run:")
        print(f"   python3 auth_gmail.py {args.account} --code 'PASTE_CODE_HERE'")

    elif args.code:
        authenticate_with_code(args.account, args.code)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
