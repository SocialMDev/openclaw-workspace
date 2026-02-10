#!/usr/bin/env python3
"""
Manual Gmail Authentication for Headless Environments
======================================================

This script uses a local server but doesn't open the browser automatically.
You'll need to copy the URL and open it in any browser (can be on a different machine
on the same network if you use the machine's IP instead of localhost).
"""

import os
import pickle
import socket
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


def get_local_ip():
    """Get the local IP address for remote browser access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def authenticate_account(creds_path: Path, token_path: Path, account_name: str):
    """Authenticate a single Gmail account."""
    print("-" * 70)
    print(f"Account: {account_name}")
    print("-" * 70)

    # Check if already authenticated
    if token_path.exists():
        try:
            with open(token_path, 'rb') as f:
                creds = pickle.load(f)
            if creds and creds.valid:
                # Test the connection
                try:
                    service = build('gmail', 'v1', credentials=creds)
                    profile = service.users().getProfile(userId='me').execute()
                    email = profile.get('emailAddress', 'unknown')
                    print(f"✅ Already authenticated: {email}")
                    return True
                except Exception as e:
                    print(f"⚠️  Token exists but connection failed: {e}")
            elif creds and creds.expired and creds.refresh_token:
                print("🔄 Token expired, refreshing...")
                try:
                    creds.refresh(Request())
                    with open(token_path, 'wb') as f:
                        pickle.dump(creds, f)
                    # Verify
                    service = build('gmail', 'v1', credentials=creds)
                    profile = service.users().getProfile(userId='me').execute()
                    email = profile.get('emailAddress', 'unknown')
                    print(f"✅ Token refreshed: {email}")
                    return True
                except Exception as e:
                    print(f"⚠️  Refresh failed: {e}")
        except Exception as e:
            print(f"⚠️  Token exists but invalid: {e}")

    # Need fresh authentication
    print()
    print("🔐 OAuth Authentication Required")
    print()

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)

        local_ip = get_local_ip()
        port = 8080 + hash(account_name) % 100  # Different port per account

        print(f"Starting local OAuth server on port {port}...")
        print()
        print("📋 INSTRUCTIONS:")
        print()
        print("   1. Open this URL in ANY browser (even on your phone/laptop):")
        print()

        # Start server without opening browser
        creds = flow.run_local_server(
            port=port,
            open_browser=False,
            authorization_prompt_message=(
                f"   👉 http://localhost:{port}/\n"
                f"      OR: http://{local_ip}:{port}/ (if accessing from another device)\n"
            ),
            success_message="Authentication successful! You can close this tab.",
            timeout_seconds=300  # 5 minute timeout
        )

        # Save token
        with open(token_path, 'wb') as f:
            pickle.dump(creds, f)

        # Verify
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'unknown')

        print()
        print(f"✅ Authentication successful!")
        print(f"   Email: {email}")
        print(f"   Token saved to: {token_path}")
        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False


def main():
    # Find all Gmail credential files
    gmail_files = list(config_dir.glob("gmail_account*.json"))
    gmail_files.sort(key=lambda x: x.name)

    print("=" * 70)
    print("Gmail Manual Authentication (Headless Mode)")
    print("=" * 70)
    print()
    print(f"Found {len(gmail_files)} Gmail account(s) to authenticate:")
    for f in gmail_files:
        account_name = f.stem.replace("gmail_", "")
        token_path = config_dir / f"gmail_token_{account_name}.pickle"
        status = "✅ Token exists" if token_path.exists() else "❌ Needs auth"
        print(f"  • {f.name} -> {status}")
    print()

    results = {}
    for creds_path in gmail_files:
        account_name = creds_path.stem.replace("gmail_", "")
        token_path = config_dir / f"gmail_token_{account_name}.pickle"
        results[account_name] = authenticate_account(creds_path, token_path, account_name)
        print()

    print("=" * 70)
    print("Authentication Summary")
    print("=" * 70)
    print()
    success = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"  Authenticated: {success}/{total} accounts")
    print()
    for account, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {account}")

    if success == total:
        print()
        print("🎉 All accounts authenticated successfully!")
        print()
        print("You can now use the email client:")
        print()
        print("  from email_client import EmailClient")
        print("  client = EmailClient()")
        print("  emails = client.read_emails('account1', limit=10)")


if __name__ == "__main__":
    main()
