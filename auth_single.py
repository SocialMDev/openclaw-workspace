#!/usr/bin/env python3
"""
Single Account Gmail Authentication
====================================

Authenticates one Gmail account at a time.
Usage: python3 auth_single.py [account_number]

Example:
    python3 auth_single.py 1  # Authenticate account1
    python3 auth_single.py 2  # Authenticate account2
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

    print("=" * 70)
    print(f"Gmail Authentication: {account_name}")
    print("=" * 70)
    print()

    if not creds_path.exists():
        print(f"ERROR: Credentials file not found: {creds_path}")
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
                print(f"Already authenticated: {email}")
                return True

            if creds and creds.expired and creds.refresh_token:
                print("Token expired, refreshing...")
                creds.refresh(Request())
                with open(token_path, 'wb') as f:
                    pickle.dump(creds, f)
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile(userId='me').execute()
                email = profile.get('emailAddress', 'unknown')
                print(f"Token refreshed: {email}")
                return True
        except Exception as e:
            print(f"Existing token invalid: {e}")
            print("Re-authenticating...")
            print()

    # Need to authenticate
    print("Starting OAuth authentication...")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)

    # Use port based on account number to avoid conflicts
    port = 8080 + account_num

    print(f"A local server will start on port {port}.")
    print("A browser window should open automatically.")
    print()
    print("If no browser opens, visit this URL manually:")
    print()

    try:
        creds = flow.run_local_server(
            port=port,
            open_browser=True,
            authorization_prompt_message="",
            success_message="Authentication successful! You can close this tab."
        )
    except Exception as e:
        print(f"Browser-based auth failed: {e}")
        print()
        print("Trying console-based authentication...")
        print()

        # Generate URL manually
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        print("Open this URL in a browser:")
        print()
        print(auth_url)
        print()
        print("After granting access, you'll be redirected to localhost.")
        print("The page may show an error - that's OK.")
        print("Copy the FULL URL from your browser's address bar.")
        print()

        redirect_url = input("Paste the redirect URL here: ").strip()

        if not redirect_url:
            print("No URL provided.")
            return False

        # Extract the code from the URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)

        if 'code' not in params:
            print("Could not find authorization code in URL")
            return False

        code = params['code'][0]
        flow.fetch_token(code=code)
        creds = flow.credentials

    # Save token
    with open(token_path, 'wb') as f:
        pickle.dump(creds, f)

    # Verify
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    email = profile.get('emailAddress', 'unknown')

    print()
    print("=" * 70)
    print(f"SUCCESS: Authenticated as {email}")
    print(f"Token saved to: {token_path}")
    print("=" * 70)
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auth_single.py <account_number>")
        print()
        print("Available accounts:")
        for f in sorted(config_dir.glob("gmail_account*.json")):
            account_name = f.stem.replace("gmail_", "")
            num = account_name.replace("account", "")
            token_path = config_dir / f"gmail_token_{account_name}.pickle"
            status = "authenticated" if token_path.exists() else "needs auth"
            print(f"  {num}: gmail_{account_name}.json ({status})")
        return

    try:
        account_num = int(sys.argv[1])
    except ValueError:
        print(f"Invalid account number: {sys.argv[1]}")
        return

    authenticate(account_num)


if __name__ == "__main__":
    main()
