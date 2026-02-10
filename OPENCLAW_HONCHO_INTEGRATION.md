# OpenClaw + Honcho Integration Guide

## ✅ Integration Complete

Honcho is now integrated with OpenClaw! Here's how to use it.

---

## 🚀 Quick Start

### 1. Import the Memory Module

```python
# In your OpenClaw agent code
import sys
sys.path.insert(0, '/home/faisal/.openclaw/workspace/honcho-ai/sdks/python/src')
from honcho import Honcho
```

### 2. Initialize Memory

```python
honcho = Honcho(
    base_url="http://localhost:8002",
    api_key="openclaw-local-dev",
    workspace_id="openclaw"
)
```

### 3. Store User Messages

```python
def store_user_message(user_id: str, message: str):
    """Store a user message in Honcho memory."""
    peer = honcho.peer(user_id)          # Get/create user
    session = honcho.session(f"{user_id}-session")  # Get/create session
    session.add_peers([peer])            # Link user to session
    session.add_messages([peer.message(message)])   # Store message
```

### 4. Retrieve Context

```python
def get_conversation_context(user_id: str, limit: int = 10) -> str:
    """Get formatted conversation history for LLM."""
    session = honcho.session(f"{user_id}-session")
    
    history = []
    for msg in session.messages():
        role = "User" if msg.peer_id else "Assistant"
        history.append(f"{role}: {msg.content}")
    
    return "\n".join(history[-limit:])
```

---

## 💡 Full OpenClaw Integration Example

```python
import sys
sys.path.insert(0, '/home/faisal/.openclaw/workspace/honcho-ai/sdks/python/src')
from honcho import Honcho

class OpenClawAgentWithMemory:
    def __init__(self):
        self.memory = Honcho(
            base_url="http://localhost:8002",
            api_key="openclaw-local-dev",
            workspace_id="openclaw"
        )
        # self.llm = YourLLMClient()  # Your LLM
    
    def handle_message(self, user_id: str, message: str) -> str:
        # Step 1: Store user message
        self._store_message(user_id, message)
        
        # Step 2: Get conversation context
        context = self._get_context(user_id)
        
        # Step 3: Build prompt with context
        prompt = self._build_prompt(context, message)
        
        # Step 4: Get LLM response
        # response = self.llm.generate(prompt)
        response = f"Echo: {message}"  # Replace with actual LLM
        
        return response
    
    def _store_message(self, user_id: str, message: str):
        """Store message in Honcho."""
        peer = self.memory.peer(user_id)
        session = self.memory.session(f"{user_id}-session")
        try:
            session.add_peers([peer])
        except:
            pass  # Already linked
        session.add_messages([peer.message(message)])
    
    def _get_context(self, user_id: str, limit: int = 10) -> str:
        """Get conversation history."""
        session = self.memory.session(f"{user_id}-session")
        messages = []
        for msg in session.messages():
            role = "User" if msg.peer_id else "Assistant"
            messages.append(f"{role}: {msg.content}")
        return "\n".join(messages[-limit:])
    
    def _build_prompt(self, context: str, message: str) -> str:
        """Build prompt with context."""
        if context:
            return f"Previous conversation:\n{context}\n\nUser: {message}\nAssistant:"
        return f"User: {message}\nAssistant:"
    
    def get_user_insights(self, user_id: str) -> str:
        """Get AI insights about user (requires deriver)."""
        try:
            peer = self.memory.peer(user_id)
            return peer.chat("What are this user's main interests?")
        except:
            return "Insights not available (deriver not running)"

# Usage
agent = OpenClawAgentWithMemory()
response = agent.handle_message("faisal", "I love AI automation")
print(response)
```

---

## 📁 Key Concepts

| Concept | Description |
|---------|-------------|
| **Peer** | A user/entity with memory |
| **Session** | A conversation thread |
| **Message** | Individual message with content |
| **Workspace** | Project/container scope |

---

## 🔧 Testing

Run the test:
```bash
cd /home/faisal/.openclaw/workspace/honcho-ai
uv run python /home/faisal/.openclaw/workspace/test_honcho_simple.py
```

---

## 📊 What You Get

✅ **Persistent Memory** - User conversations stored in PostgreSQL
✅ **Conversation History** - Retrieve past messages for context
✅ **User Insights** - AI-powered understanding (with deriver)
✅ **Scalable** - Self-hosted, no vendor lock-in
✅ **Cheap** - ~$20-40/month via OpenRouter

---

## 🎯 Next Steps

1. **Copy the integration code** into your OpenClaw agent
2. **Replace** `self.llm.generate()` with your actual LLM call
3. **Deploy** and start building with memory!

---

## 💰 Costs

| Item | Monthly |
|------|---------|
| Infrastructure | $0 |
| PostgreSQL | $0 |
| OpenRouter API | ~$20-40 |
| **Total** | **~$20-40** |

---

## 🔗 Files

- `/home/faisal/.openclaw/workspace/honcho_integration.py` - Full integration module
- `/home/faisal/.openclaw/workspace/test_honcho_simple.py` - Simple test
- `/home/faisal/.openclaw/workspace/honcho-ai/` - Honcho server

---

**Ready to use!** 🚀
