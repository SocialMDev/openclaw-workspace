# Email Integration Setup
# This script helps set up OAuth access for Gmail and Microsoft Exchange

import os
import json
from pathlib import Path

# Configuration directory
CONFIG_DIR = Path.home() / ".openclaw" / "email_config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

GMAIL_CONFIG_FILE = CONFIG_DIR / "gmail_credentials.json"
OUTLOOK_CONFIG_FILE = CONFIG_DIR / "outlook_credentials.json"

print("📧 Email Integration Setup")
print("=" * 60)
print()
print("This will set up secure OAuth access for:")
print("  • Gmail (Google Workspace / Personal)")
print("  • Microsoft Exchange / Outlook")
print()
print("Using OAuth means:")
print("  ✅ No passwords stored")
print("  ✅ Secure token-based access")
print("  ✅ You control permissions")
print("  ✅ Can revoke access anytime")
print()

# Gmail Setup
print("=" * 60)
print("🔵 GMAIL SETUP")
print("=" * 60)
print()
print("To access Gmail, you need to create OAuth credentials:")
print()
print("1. Go to: https://console.cloud.google.com/")
print("2. Create a new project (or use existing)")
print("3. Enable the Gmail API:")
print("   - APIs & Services > Library")
print("   - Search 'Gmail API' and enable it")
print("4. Create OAuth credentials:")
print("   - APIs & Services > Credentials")
print("   - Click 'Create Credentials' > 'OAuth client ID'")
print("   - Application type: 'Desktop app'")
print("   - Name: 'OpenClaw Email'")
print("5. Download the JSON file")
print()
print(f"6. Save it to: {GMAIL_CONFIG_FILE}")
print()

# Check if Gmail config exists
if GMAIL_CONFIG_FILE.exists():
    print(f"✅ Gmail config found at: {GMAIL_CONFIG_FILE}")
else:
    print(f"⏳ Waiting for Gmail config...")
    print(f"   Save credentials to: {GMAIL_CONFIG_FILE}")

print()

# Outlook/Exchange Setup
print("=" * 60)
print("🟠 MICROSOFT EXCHANGE / OUTLOOK SETUP")
print("=" * 60)
print()
print("To access Exchange/Outlook, you need Azure AD app:")
print()
print("1. Go to: https://portal.azure.com/")
print("2. Navigate to: Azure Active Directory > App registrations")
print("3. Click 'New registration'")
print("4. Configure:")
print("   - Name: 'OpenClaw Email'")
print("   - Supported account types: 'Accounts in any organizational directory'")
print("   - Redirect URI: 'http://localhost:8080/callback'")
print("5. Click 'Register'")
print("6. Note the Application (client) ID")
print("7. Go to 'Certificates & secrets' > 'New client secret'")
print("   - Description: 'OpenClaw Secret'")
print("   - Expires: 24 months")
print("8. Note the secret value (you can't see it again!)")
print("9. Go to 'API permissions' > 'Add permission'")
print("   - Microsoft Graph > Delegated permissions")
print("   - Add: Mail.Read, Mail.Send, User.Read")
print("   - Click 'Grant admin consent' (if you have admin access)")
print()
print("10. Save credentials as JSON:")
print(f"    Location: {OUTLOOK_CONFIG_FILE}")
print()
print("    Format:")
print('''    {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "tenant_id": "your-tenant-id"
    }''')
print()

# Check if Outlook config exists
if OUTLOOK_CONFIG_FILE.exists():
    print(f"✅ Outlook config found at: {OUTLOOK_CONFIG_FILE}")
else:
    print(f"⏳ Waiting for Outlook config...")
    print(f"   Save credentials to: {OUTLOOK_CONFIG_FILE}")

print()
print("=" * 60)
print("📋 NEXT STEPS")
print("=" * 60)
print()
print("1. Set up Gmail OAuth (if needed)")
print("2. Set up Outlook/Exchange OAuth (if needed)")
print("3. Run the authentication script:")
print("   python3 /home/faisal/.openclaw/workspace/email_auth.py")
print()
print("4. Once authenticated, you can:")
print("   • Read emails")
print("   • Send emails")
print("   • Search emails")
print("   • Manage labels/folders")
print()
print("=" * 60)
