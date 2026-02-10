#!/usr/bin/env python3
"""
OpenClaw Email Integration
==========================

Unified email client for Gmail and Microsoft Exchange/Outlook.

Features:
- Read emails from multiple providers
- Send emails
- Search/filter emails
- Manage labels/folders
- OAuth authentication (secure, no passwords)

Usage:
    from email_client import EmailClient
    
    client = EmailClient()
    
    # Read emails
    emails = client.read_emails(provider="gmail", limit=10)
    
    # Send email
    client.send_email(
        provider="outlook",
        to="recipient@example.com",
        subject="Hello",
        body="Message content"
    )
"""

import os
import sys
import json
import base64
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# Gmail imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

# Outlook/Exchange imports
try:
    import msal
    import requests
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False


@dataclass
class Email:
    """Email message data class."""
    id: str
    provider: str
    sender: str
    recipient: str
    subject: str
    body: str
    html_body: Optional[str]
    date: datetime
    labels: List[str]
    is_read: bool
    has_attachments: bool
    thread_id: Optional[str] = None


class GmailClient:
    """Gmail API client."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.labels'
    ]
    
    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}. "
                        "Run email_setup.py for instructions."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                
                # Try console-based auth first (for headless systems)
                try:
                    creds = flow.run_console()
                except:
                    # Fall back to local server
                    creds = flow.run_local_server(port=0)
            
            # Save token for future runs
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def read_emails(self, limit: int = 10, query: str = "") -> List[Email]:
        """Read emails from Gmail."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=limit,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email = self._parse_message(msg['id'])
                if email:
                    emails.append(email)
            
            return emails
            
        except HttpError as error:
            print(f'Gmail API error: {error}')
            return []
    
    def _parse_message(self, msg_id: str) -> Optional[Email]:
        """Parse Gmail message to Email object."""
        try:
            msg = self.service.users().messages().get(
                userId='me', id=msg_id, format='full'
            ).execute()
            
            headers = msg['payload']['headers']
            
            # Extract headers
            subject = self._get_header(headers, 'Subject')
            sender = self._get_header(headers, 'From')
            recipient = self._get_header(headers, 'To')
            date_str = self._get_header(headers, 'Date')
            
            # Parse date
            try:
                date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            except:
                date = datetime.now()
            
            # Get body
            body, html_body = self._get_body(msg['payload'])
            
            # Get labels
            labels = msg.get('labelIds', [])
            
            return Email(
                id=msg_id,
                provider='gmail',
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body,
                html_body=html_body,
                date=date,
                labels=labels,
                is_read='UNREAD' not in labels,
                has_attachments='parts' in msg['payload'] and len(msg['payload']['parts']) > 1,
                thread_id=msg.get('threadId')
            )
            
        except Exception as e:
            print(f'Error parsing message: {e}')
            return None
    
    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Get header value by name."""
        for header in headers:
            if header['name'] == name:
                return header['value']
        return ''
    
    def _get_body(self, payload: Dict) -> tuple:
        """Extract body text from message payload."""
        body = ''
        html_body = None
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        html_body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body, html_body
    
    def send_email(self, to: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send email via Gmail."""
        try:
            message = self._create_message(to, subject, body, html_body)
            sent = self.service.users().messages().send(
                userId='me', body=message
            ).execute()
            print(f"Email sent! Message Id: {sent['id']}")
            return True
            
        except HttpError as error:
            print(f'Error sending email: {error}')
            return False
    
    def _create_message(self, to: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict:
        """Create email message."""
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['subject'] = subject
        
        # Add plain text part
        message.attach(MIMEText(body, 'plain'))
        
        # Add HTML part if provided
        if html_body:
            message.attach(MIMEText(html_body, 'html'))
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw}
    
    def search_emails(self, query: str, limit: int = 10) -> List[Email]:
        """Search emails using Gmail query syntax."""
        return self.read_emails(limit=limit, query=query)
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark email as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except:
            return False


class OutlookClient:
    """Microsoft Outlook/Exchange client."""
    
    AUTHORITY = "https://login.microsoftonline.com/common"
    SCOPES = ['Mail.Read', 'Mail.Send', 'User.Read', 'offline_access']
    
    def __init__(self, client_id: str, client_secret: str, token_path: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_path = token_path
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Microsoft Graph API."""
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'r') as f:
                token_data = json.load(f)
                self.access_token = token_data.get('access_token')
                expires_at = token_data.get('expires_at', 0)
                
                # Check if token is still valid
                if datetime.now().timestamp() < expires_at:
                    return
        
        # Need to authenticate
        print("Outlook authentication required.")
        print("Please visit the following URL to authenticate:")
        
        # Create MSAL app
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.AUTHORITY,
            client_credential=self.client_secret
        )
        
        # Get authorization URL
        flow = app.initiate_device_flow(scopes=[f"https://graph.microsoft.com/{s}" for s in self.SCOPES])
        print(flow['message'])
        
        # Wait for user to complete authentication
        result = app.acquire_token_by_device_flow(flow)
        
        if 'access_token' in result:
            self.access_token = result['access_token']
            
            # Save token
            token_data = {
                'access_token': result['access_token'],
                'refresh_token': result.get('refresh_token'),
                'expires_at': datetime.now().timestamp() + result.get('expires_in', 3600)
            }
            
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f)
            
            print("✅ Outlook authentication successful!")
        else:
            raise Exception(f"Authentication failed: {result.get('error_description')}")
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make request to Microsoft Graph API."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"https://graph.microsoft.com/v1.0{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 401:
            # Token expired, re-authenticate
            self._authenticate()
            return self._make_request(endpoint, method, data)
        
        response.raise_for_status()
        return response.json()
    
    def read_emails(self, limit: int = 10, folder: str = "inbox") -> List[Email]:
        """Read emails from Outlook."""
        try:
            result = self._make_request(
                f"/me/mailFolders/{folder}/messages?$top={limit}&$orderby=receivedDateTime desc"
            )
            
            emails = []
            for msg in result.get('value', []):
                email = self._parse_message(msg)
                if email:
                    emails.append(email)
            
            return emails
            
        except Exception as e:
            print(f'Outlook API error: {e}')
            return []
    
    def _parse_message(self, msg: Dict) -> Optional[Email]:
        """Parse Outlook message to Email object."""
        try:
            # Parse date
            date_str = msg.get('receivedDateTime', '')
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                date = datetime.now()
            
            # Get sender
            sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
            
            # Get recipients
            to_recipients = msg.get('toRecipients', [])
            recipient = to_recipients[0]['emailAddress']['address'] if to_recipients else ''
            
            # Get body
            body_content = msg.get('body', {}).get('content', '')
            body_type = msg.get('body', {}).get('contentType', 'text')
            
            if body_type == 'html':
                html_body = body_content
                # Simple HTML to text conversion
                import re
                body = re.sub('<[^<]+?>', '', body_content)
            else:
                body = body_content
                html_body = None
            
            return Email(
                id=msg.get('id', ''),
                provider='outlook',
                sender=sender,
                recipient=recipient,
                subject=msg.get('subject', ''),
                body=body,
                html_body=html_body,
                date=date,
                labels=[msg.get('parentFolderId', '')],
                is_read=msg.get('isRead', True),
                has_attachments=msg.get('hasAttachments', False),
                thread_id=msg.get('conversationId')
            )
            
        except Exception as e:
            print(f'Error parsing Outlook message: {e}')
            return None
    
    def send_email(self, to: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send email via Outlook."""
        try:
            email_data = {
                'message': {
                    'subject': subject,
                    'body': {
                        'contentType': 'HTML' if html_body else 'Text',
                        'content': html_body if html_body else body
                    },
                    'toRecipients': [
                        {
                            'emailAddress': {
                                'address': to
                            }
                        }
                    ]
                }
            }
            
            self._make_request('/me/sendMail', method='POST', data=email_data)
            print(f"Email sent to {to}!")
            return True
            
        except Exception as e:
            print(f'Error sending email: {e}')
            return False
    
    def search_emails(self, query: str, limit: int = 10) -> List[Email]:
        """Search emails in Outlook."""
        try:
            # Outlook search uses $search parameter
            result = self._make_request(
                f"/me/messages?$search=\"{query}\"&$top={limit}"
            )
            
            emails = []
            for msg in result.get('value', []):
                email = self._parse_message(msg)
                if email:
                    emails.append(email)
            
            return emails
            
        except Exception as e:
            print(f'Outlook search error: {e}')
            return []


class EmailClient:
    """Unified email client for multiple providers and accounts."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".openclaw" / "email_config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Support multiple accounts per provider
        self.gmail_clients: Dict[str, GmailClient] = {}
        self.outlook_clients: Dict[str, OutlookClient] = {}
        
        # Legacy single clients (for backward compatibility)
        self.gmail_client: Optional[GmailClient] = None
        self.outlook_client: Optional[OutlookClient] = None
        
        self._load_clients()
    
    def _load_clients(self):
        """Load configured email clients (supports multiple accounts)."""
        # Gmail - support multiple accounts
        # Look for both naming patterns: gmail_credentials_*.json and gmail_account*.json
        gmail_creds_pattern = list(self.config_dir.glob("gmail_credentials*.json")) + \
                              list(self.config_dir.glob("gmail_account*.json"))
        
        for creds_path in gmail_creds_pattern:
            # Skip token files
            if "token" in creds_path.name:
                continue
                
            # Determine account name
            if creds_path.name == "gmail_credentials.json":
                account_name = "gmail"  # default account
            elif creds_path.name.startswith("gmail_account"):
                # Extract account name from filename: gmail_account1.json -> account1
                account_name = creds_path.stem.replace("gmail_", "").lower()
            else:
                # Extract account name from filename: gmail_credentials_WORK.json -> work
                account_name = creds_path.stem.replace("gmail_credentials_", "").lower()
                if not account_name:
                    account_name = "gmail"
            
            token_path = self.config_dir / f"gmail_token_{account_name}.pickle"
            
            if GMAIL_AVAILABLE:
                try:
                    client = GmailClient(str(creds_path), str(token_path))
                    self.gmail_clients[account_name] = client
                    
                    # Set as default if it's the primary account
                    if account_name == "gmail":
                        self.gmail_client = client
                    
                    print(f"✅ Gmail client loaded: {account_name}")
                except Exception as e:
                    print(f"⚠️  Gmail client failed ({account_name}): {e}")
        
        # Outlook - support multiple accounts
        outlook_creds_pattern = self.config_dir.glob("outlook_credentials*.json")
        
        for creds_path in outlook_creds_pattern:
            # Skip token files
            if "token" in creds_path.name:
                continue
            
            # Determine account name
            if creds_path.name == "outlook_credentials.json":
                account_name = "outlook"  # default account
            else:
                account_name = creds_path.stem.replace("outlook_credentials_", "").lower()
                if not account_name:
                    account_name = "outlook"
            
            token_path = self.config_dir / f"outlook_token_{account_name}.json"
            
            if OUTLOOK_AVAILABLE:
                try:
                    with open(creds_path) as f:
                        creds = json.load(f)
                    
                    client = OutlookClient(
                        creds['client_id'],
                        creds['client_secret'],
                        str(token_path)
                    )
                    self.outlook_clients[account_name] = client
                    
                    # Set as default if it's the primary account
                    if account_name == "outlook":
                        self.outlook_client = client
                    
                    print(f"✅ Outlook client loaded: {account_name}")
                except Exception as e:
                    print(f"⚠️  Outlook client failed ({account_name}): {e}")
    
    def read_emails(self, provider: str = "gmail", limit: int = 10, **kwargs) -> List[Email]:
        """
        Read emails from specified provider and account.
        
        Args:
            provider: "gmail" or "outlook" (or account name like "work", "personal")
            limit: Maximum number of emails to read
            **kwargs: Additional provider-specific options
                - account: Specific account name (e.g., "work", "personal")
                - query: Search query (Gmail)
                - folder: Folder name (Outlook)
        
        Returns:
            List of Email objects
        """
        account = kwargs.get('account')
        
        # Try to get specific account first
        if account:
            if provider == "gmail" and account in self.gmail_clients:
                return self.gmail_clients[account].read_emails(limit=limit, query=kwargs.get('query', ''))
            elif provider == "outlook" and account in self.outlook_clients:
                return self.outlook_clients[account].read_emails(limit=limit, folder=kwargs.get('folder', 'inbox'))
        
        # Fall back to default account
        if provider == "gmail" and self.gmail_client:
            return self.gmail_client.read_emails(limit=limit, query=kwargs.get('query', ''))
        elif provider == "outlook" and self.outlook_client:
            return self.outlook_client.read_emails(limit=limit, folder=kwargs.get('folder', 'inbox'))
        
        # Try as account name directly
        if provider in self.gmail_clients:
            return self.gmail_clients[provider].read_emails(limit=limit, query=kwargs.get('query', ''))
        elif provider in self.outlook_clients:
            return self.outlook_clients[provider].read_emails(limit=limit, folder=kwargs.get('folder', 'inbox'))
        
        print(f"⚠️  {provider} client not available")
        return []
    
    def send_email(self, provider: str, to: str, subject: str, body: str, **kwargs) -> bool:
        """
        Send email via specified provider and account.
        
        Args:
            provider: "gmail" or "outlook" (or account name like "work", "personal")
            to: Recipient email address
            subject: Email subject
            body: Email body
            **kwargs: Additional options
                - account: Specific account name
                - html_body: HTML version of the email
        
        Returns:
            True if sent successfully
        """
        account = kwargs.get('account')
        html_body = kwargs.get('html_body')
        
        # Try specific account first
        if account:
            if provider == "gmail" and account in self.gmail_clients:
                return self.gmail_clients[account].send_email(to, subject, body, html_body)
            elif provider == "outlook" and account in self.outlook_clients:
                return self.outlook_clients[account].send_email(to, subject, body, html_body)
        
        # Fall back to default
        if provider == "gmail" and self.gmail_client:
            return self.gmail_client.send_email(to, subject, body, html_body)
        elif provider == "outlook" and self.outlook_client:
            return self.outlook_client.send_email(to, subject, body, html_body)
        
        # Try as account name directly
        if provider in self.gmail_clients:
            return self.gmail_clients[provider].send_email(to, subject, body, html_body)
        elif provider in self.outlook_clients:
            return self.outlook_clients[provider].send_email(to, subject, body, html_body)
        
        print(f"⚠️  {provider} client not available")
        return False
    
    def search_emails(self, provider: str, query: str, limit: int = 10) -> List[Email]:
        """Search emails."""
        if provider == "gmail" and self.gmail_client:
            return self.gmail_client.search_emails(query, limit)
        elif provider == "outlook" and self.outlook_client:
            return self.outlook_client.search_emails(query, limit)
        else:
            print(f"⚠️  {provider} client not available")
            return []
    
    def list_providers(self) -> List[str]:
        """List available email providers."""
        providers = []
        if self.gmail_client:
            providers.append("gmail")
        if self.outlook_client:
            providers.append("outlook")
        return providers


# Demo
if __name__ == "__main__":
    print("📧 OpenClaw Email Client")
    print("=" * 60)
    
    client = EmailClient()
    
    providers = client.list_providers()
    if providers:
        print(f"\n✅ Available providers: {', '.join(providers)}")
        
        # Demo: Read recent emails
        for provider in providers:
            print(f"\n📨 Reading {provider} emails...")
            emails = client.read_emails(provider, limit=5)
            print(f"   Found {len(emails)} emails")
            for email in emails[:3]:
                print(f"   • {email.subject[:50]} from {email.sender[:30]}")
    else:
        print("\n⚠️  No email providers configured.")
        print("   Run: python3 email_setup.py")
