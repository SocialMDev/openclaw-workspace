# 🤖 OpenClaw - AI Assistant with Persistent Memory

Complete AI assistant system with persistent memory using Honcho (self-hosted, cheap API via OpenRouter).

## ✅ What's Set Up

| Component | Status | URL |
|-----------|--------|-----|
| Honcho Memory | ✅ Running | http://localhost:8002 |
| OpenClaw API | ✅ Ready | http://localhost:8080 |
| PostgreSQL | ✅ Connected | localhost:5432 |

## 🚀 Quick Start

### Option 1: Run CLI
```bash
cd /home/faisal/.openclaw/workspace
python3 main.py
```

### Option 2: Run API Server
```bash
cd /home/faisal/.openclaw/workspace
./start.sh
```

Then test:
```bash
curl -X POST http://localhost:8080/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user1", "message": "Hello!"}'
```

### Option 3: Use as Library
```python
from main import OpenClaw

openclaw = OpenClaw()
response = openclaw.chat("user123", "Hello!")
print(response)
```

## 📁 Files

| File | Purpose |
|------|---------|
| `main.py` | Main OpenClaw application (CLI + Library) |
| `api_server.py` | HTTP API server |
| `start.sh` | Start all services |
| `honcho_integration.py` | Memory integration module |
| `openclaw_agent.py` | Advanced agent class |
| `.env.openclaw` | Configuration |
| `openclaw.service` | SystemD service file |

## 💰 Costs

- **Infrastructure**: $0 (your server)
- **PostgreSQL**: $0 (already running)
- **OpenRouter API**: ~$20-40/month
- **Total**: **~$20-40/month**

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/chat` | POST | Send message |
| `/history/<user>` | GET | Get history |
| `/info/<user>` | GET | User info |
| `/clear/<user>` | POST | Clear history |

## 📝 Example Usage

### CLI
```
$ python3 main.py

🤖 OpenClaw - AI Assistant with Memory
==================================================

👤 You: I love Python
🤖 OpenClaw: Hello! I see you're interested in: I love Python...

👤 You: history
📜 History (2 messages):
   🧑 I love Python...
```

### HTTP API
```bash
# Chat
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "message": "Hello!"}'

# Get history
curl http://localhost:8080/history/user1

# Get user info
curl http://localhost:8080/info/user1

# Clear history
curl -X POST http://localhost:8080/clear/user1
```

### Python Library
```python
from main import OpenClaw

# Initialize
openclaw = OpenClaw()

# Chat
response = openclaw.chat("user123", "Hello!")

# Get history
history = openclaw.get_history("user123")

# Get user info
info = openclaw.get_user_info("user123")

# Clear history
openclaw.clear_history("user123")
```

## 🎯 Features

- ✅ Persistent conversation memory per user
- ✅ Context-aware responses
- ✅ Message history tracking
- ✅ RESTful API
- ✅ CLI interface
- ✅ Python library
- ✅ Self-hosted (no vendor lock-in)
- ✅ Cheap API costs via OpenRouter

## 🔌 SystemD Service (Optional)

```bash
# Install service
sudo cp openclaw.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable openclaw
sudo systemctl start openclaw

# Check status
sudo systemctl status openclaw
```

## 📊 Architecture

```
User → OpenClaw API → Honcho → PostgreSQL
              ↓
         OpenRouter (LLM)
```

## 🛠️ Configuration

Edit `.env.openclaw`:
```env
HONCHO_BASE_URL=http://localhost:8002
HONCHO_API_KEY=openclaw-local-dev
HONCHO_WORKSPACE=openclaw
OPENROUTER_API_KEY=your-key
```

## 📝 Logs

- Honcho: `/tmp/honcho.log`
- OpenClaw API: `/tmp/openclaw-api.log`

## 🎉 You're Ready!

Everything is set up and working. Start using OpenClaw with:

```bash
./start.sh
```

Or:

```bash
python3 main.py
```

---

**Built with:** Python + Honcho + PostgreSQL + OpenRouter
