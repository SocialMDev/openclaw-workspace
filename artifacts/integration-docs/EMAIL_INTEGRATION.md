# 📧 Email Integration for OpenClaw

## Overview

This adds secure email access to OpenClaw using OAuth authentication.

**Supported Providers:**
- ✅ Gmail (Google Workspace / Personal)
- ✅ Microsoft Exchange / Outlook

**Security:**
- 🔐 OAuth2 authentication (no passwords stored)
- 🔒 Secure token-based access
- 🎛️ You control permissions
- 🚫 Can revoke access anytime

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/faisal/.openclaw/workspace/honcho-ai
uv pip install -r /home/faisal/.openclaw/workspace/requirements.email.txt
```

### 2. Set Up OAuth Credentials

**For Gmail:**
1. Go to https://console.cloud.google.com/
2. Create a project → Enable Gmail API
3. Create OAuth credentials (Desktop app)
4. Download JSON file to:
   ```
   ~/.openclaw/email_config/gmail_credentials.json
   ```

**For Outlook/Exchange:**
1. Go to https://portal.azure.com/
2. Azure AD → App registrations → New registration
3. Configure app:
   - Name: "OpenClaw Email"
   - Redirect URI: `http://localhost:8080/callback`
4. Note Application (client) ID
5. Create client secret
6. Add API permissions: Mail.Read, Mail.Send, User.Read
7. Save credentials to:
   ```
   ~/.openclaw/email_config/outlook_credentials.json
   ```
   Format:
   ```json
   {
       "client_id": "your-client-id",
       "client_secret": "your-client-secret",
       "tenant_id": "your-tenant-id"
   }
   ```

### 3. Authenticate

```bash
cd /home/faisal/.openclaw/workspace/honcho-ai
uv run python /home/faisal/.openclaw/workspace/email_auth.py
```

This will open browser windows for OAuth authentication.

### 4. Use Email in OpenClaw

```python
import sys
sys.path.insert(0, '/home/faisal/.openclaw/workspace')
from email_client import EmailClient

# Initialize
client = EmailClient()

# Read emails
emails = client.read_emails('gmail', limit=10)
for email in emails:
    print(f"From: {email.sender}")
    print(f"Subject: {email.subject}")
    print(f"Body: {email.body[:200]}")

# Send email
client.send_email(
    provider='gmail',
    to='recipient@example.com',
    subject='Hello from OpenClaw',
    body='This is a test email'
)

# Search emails
results = client.search_emails('gmail', 'from:boss@company.com')
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `email_setup.py` | Setup instructions |
| `email_auth.py` | Authentication script |
| `email_client.py` | Main email client |
| `requirements.email.txt` | Dependencies |

---

## 🔧 Integration with OpenClaw Agent

```python
import sys
sys.path.insert(0, '/home/faisal/.openclaw/workspace')

from main import OpenClaw
from email_client import EmailClient

class OpenClawWithEmail:
    def __init__(self):
        self.openclaw = OpenClaw()
        self.email = EmailClient()
    
    def handle_message(self, user_id: str, message: str) -> str:
        # Check if user is asking about emails
        if "email" in message.lower() or "inbox" in message.lower():
            # Read recent emails
            emails = self.email.read_emails('gmail', limit=5)
            email_summary = "\n".join([
                f"- {e.subject} from {e.sender}"
                for e in emails[:3]
            ])
            
            return f"Here are your recent emails:\n{email_summary}"
        
        # Otherwise use normal OpenClaw
        return self.openclaw.chat(user_id, message)
```

---

## 📝 Available Methods

### EmailClient

```python
# Read emails
emails = client.read_emails(provider='gmail', limit=10)

# Read with search query (Gmail syntax)
emails = client.read_emails('gmail', query='from:boss@company.com')

# Send email
client.send_email(
    provider='gmail',
    to='recipient@example.com',
    subject='Subject',
    body='Plain text body',
    html_body='<p>HTML body</p>'  # Optional
)

# Search emails
results = client.search_emails('outlook', 'subject:urgent')

# List configured providers
providers = client.list_providers()
```

### Email Object

```python
email.id              # Message ID
email.provider        # 'gmail' or 'outlook'
email.sender          # Sender email
email.recipient       # Recipient email
email.subject         # Subject line
email.body            # Plain text body
email.html_body       # HTML body (if available)
email.date            # datetime object
email.labels          # List of labels/folders
email.is_read         # Boolean
email.has_attachments # Boolean
email.thread_id       # Conversation thread ID
```

---

## 🔐 Security Notes

1. **OAuth Tokens** stored in `~/.openclaw/email_config/`
2. **No passwords** are ever stored
3. **Tokens expire** and refresh automatically
4. **Revoke access** anytime via Google/ Microsoft account settings
5. **Scope-limited** - only requested permissions granted

---

## 🐛 Troubleshooting

### "No email providers configured"
- Run `python3 email_setup.py` for instructions
- Ensure credential files are in the correct location

### "Authentication failed"
- Check that OAuth credentials are correct
- Ensure redirect URIs match
- Try deleting token files and re-authenticating:
  ```bash
  rm ~/.openclaw/email_config/*token*
  python3 email_auth.py
  ```

### "Permission denied"
- For Gmail: Check OAuth consent screen is configured
- For Outlook: Ensure admin consent is granted for organization accounts

---

## 💰 No Additional Cost

Email integration uses your existing:
- Gmail: Free (with rate limits)
- Google Workspace: Included
- Exchange Online: Included
- Outlook.com: Free

Only standard API rate limits apply.

---

## 🎉 Ready to Use!

Once authenticated, OpenClaw can:
- 📨 Read your emails
- 📤 Send emails
- 🔍 Search emails
- 📁 Manage labels/folders

All securely via OAuth!
