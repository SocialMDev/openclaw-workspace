#!/usr/bin/env python3
"""
Gmail Authentication for Headless Servers
==========================================

This script is designed for servers without a browser.
It starts a local OAuth server and prints URLs that you can open in any browser.

Method 1 (Recommended): SSH Port Forwarding
  1. SSH with port forwarding: ssh -L 8081:localhost:8081 user@server
  2. Run this script
  3. Open http://localhost:8081 in your LOCAL browser
  
Method 2: Direct Access
  If your server is accessible on a local network, open the URL directly
  using the server's IP address.

Usage: python3 auth_headless.py [account_number]
       python3 auth_headless.py  # Interactive mode for all accounts
"""

import sys
import os
import socket
import pickle
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
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
    """Get local IP for network access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


class OAuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback."""
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP logs
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1>Authentication Successful!</h1>
                <p>You can close this tab and return to the terminal.</p>
                </body></html>
            """)
        elif 'error' in params:
            self.server.auth_error = params.get('error', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error = params.get('error_description', ['Authentication denied'])[0]
            self.wfile.write(f"""
                <html><body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1>Authentication Failed</h1>
                <p>{error}</p>
                </body></html>
            """.encode())
        else:
            # Initial request - redirect to Google
            if hasattr(self.server, 'auth_url'):
                self.send_response(302)
                self.send_header('Location', self.server.auth_url)
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body>Waiting for OAuth setup...</body></html>")


def authenticate_account(account_num: int):
    """Authenticate a single Gmail account."""
    account_name = f"account{account_num}"
    creds_path = config_dir / f"gmail_{account_name}.json"
    token_path = config_dir / f"gmail_token_{account_name}.pickle"

    print()
    print("=" * 70)
    print(f"Account {account_num}: {account_name}")
    print("=" * 70)

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
            print(f"Token invalid ({e}), re-authenticating...")

    # Start OAuth server
    port = 8080 + account_num
    local_ip = get_local_ip()
    
    server = HTTPServer(('0.0.0.0', port), OAuthHandler)
    server.auth_code = None
    server.auth_error = None
    server.timeout = 300  # 5 minute timeout per request
    
    # Create OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    flow.redirect_uri = f'http://localhost:{port}/'
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    server.auth_url = auth_url
    
    print()
    print("Local OAuth server started on port", port)
    print()
    print("-" * 70)
    print("OPEN ONE OF THESE URLS IN YOUR BROWSER:")
    print("-" * 70)
    print(f"  Local:   http://localhost:{port}/")
    print(f"  Network: http://{local_ip}:{port}/")
    print()
    print("If using SSH, forward the port first:")
    print(f"  ssh -L {port}:localhost:{port} user@server")
    print("-" * 70)
    print()
    print("Waiting for authentication (5 minute timeout)...")
    
    # Handle requests until we get a code or error
    while server.auth_code is None and server.auth_error is None:
        server.handle_request()
    
    if server.auth_error:
        print(f"ERROR: {server.auth_error}")
        return False
    
    # Exchange code for token
    try:
        flow.fetch_token(code=server.auth_code)
        creds = flow.credentials
        
        # Save token
        with open(token_path, 'wb') as f:
            pickle.dump(creds, f)
        
        # Verify
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'unknown')
        
        print()
        print(f"SUCCESS: Authenticated as {email}")
        print(f"Token saved to: {token_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to complete authentication: {e}")
        return False


def main():
    print("=" * 70)
    print("Gmail Authentication for Headless Servers")
    print("=" * 70)
    
    # Find all accounts
    accounts = []
    for f in sorted(config_dir.glob("gmail_account*.json")):
        account_name = f.stem.replace("gmail_", "")
        num = int(account_name.replace("account", ""))
        token_path = config_dir / f"gmail_token_{account_name}.pickle"
        status = "OK" if token_path.exists() else "needs auth"
        accounts.append((num, status))
    
    print()
    print("Found accounts:")
    for num, status in accounts:
        print(f"  {num}: account{num} ({status})")
    print()
    
    if len(sys.argv) > 1:
        # Single account mode
        try:
            num = int(sys.argv[1])
            authenticate_account(num)
        except ValueError:
            print(f"Invalid account number: {sys.argv[1]}")
    else:
        # Interactive mode - authenticate all
        results = {}
        for num, status in accounts:
            if status == "OK":
                # Verify it still works
                results[num] = authenticate_account(num)
            else:
                results[num] = authenticate_account(num)
        
        # Summary
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        success = sum(1 for v in results.values() if v)
        print(f"Authenticated: {success}/{len(results)}")
        for num, ok in results.items():
            print(f"  account{num}: {'OK' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()
