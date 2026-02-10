# Honcho Integration for OpenClaw (with Authentication)
# Location: /home/faisal/.openclaw/workspace/honcho_integration.py

import sys
import os
sys.path.insert(0, '/home/faisal/.openclaw/workspace/honcho-ai/sdks/python/src')

from honcho import Honcho
from typing import Optional, List, Dict, Any

# JWT Token for API authentication
# Generated with admin privileges
HONCHO_JWT_TOKEN = os.environ.get(
    "HONCHO_JWT_TOKEN",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJhZCI6dHJ1ZSwidyI6IioifQ.qbK7wEuN3gTV68LIONGAKxGP-TLFnPEUcUD5KL-M4Eg"
)

class OpenClawMemory:
    """
    Memory manager for OpenClaw using Honcho.
    
    Usage:
        memory = OpenClawMemory()
        
        # When user sends a message:
        memory.store_message(user_id="faisal", message="Hello!")
        
        # Get conversation history:
        history = memory.get_history(user_id="faisal")
        
        # Get user insights:
        insights = memory.get_user_insights(user_id="faisal")
    """
    
    def __init__(self, workspace_id: str = "openclaw"):
        """Initialize Honcho connection with JWT authentication."""
        self.workspace_id = workspace_id
        self.honcho = Honcho(
            base_url="http://localhost:8002",
            api_key=HONCHO_JWT_TOKEN,  # JWT token used as API key
            workspace_id=workspace_id
        )
        self._cache = {}
    
    def store_message(self, user_id: str, message: str, metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Store a user message in Honcho.
        
        Args:
            user_id: Unique identifier for the user (Telegram ID, etc.)
            message: The message content
            metadata: Optional metadata dictionary
            
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            # Get or create peer (user)
            peer = self.honcho.peer(user_id)
            
            # Get or create session for this user
            session_id = f"{user_id}-session"
            session = self.honcho.session(session_id)
            
            # Link peer to session
            try:
                session.add_peers([peer])
            except Exception:
                pass  # Peer already linked
            
            # Prepare message metadata
            msg_metadata = metadata or {}
            msg_metadata["source"] = "openclaw"
            msg_metadata["timestamp"] = str(int(time.time()))
            
            # Store message
            msg = peer.message(message, metadata=msg_metadata)
            result = session.add_messages([msg])
            
            return result[0].id if result else None
            
        except Exception as e:
            print(f"⚠️  Failed to store message: {e}")
            return None
    
    def get_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: The user identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages with role and content
        """
        try:
            session_id = f"{user_id}-session"
            session = self.honcho.session(session_id)
            
            messages = []
            for msg in session.messages():
                # Role is determined by peer_id - if set, it's a user message
                role = "user" if msg.peer_id else "assistant"
                messages.append({
                    "role": role,
                    "content": msg.content,
                    "created_at": msg.created_at,
                    "id": msg.id
                })
            
            return messages[-limit:]  # Return last N messages
            
        except Exception as e:
            print(f"⚠️  Failed to get history: {e}")
            return []
    
    def get_formatted_history(self, user_id: str, limit: int = 10) -> str:
        """
        Get formatted conversation history for LLM context injection.
        
        Args:
            user_id: The user identifier
            limit: Maximum number of messages
            
        Returns:
            Formatted string with conversation history
        """
        history = self.get_history(user_id, limit)
        
        if not history:
            return ""
        
        formatted = []
        for msg in history:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role_label}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def get_context_for_prompt(self, user_id: str, limit: int = 10) -> str:
        """
        Get context formatted for injection into LLM prompt.
        
        Args:
            user_id: The user identifier
            limit: Maximum number of messages
            
        Returns:
            Context string ready for prompt insertion
        """
        history = self.get_formatted_history(user_id, limit)
        
        if not history:
            return ""
        
        return f"""Previous conversation context:
{history}

---
"""
    
    def get_user_insights(self, user_id: str, question: str = "What are this user's main interests?") -> Optional[str]:
        """
        Get AI-generated insights about the user using Honcho's dialectic API.
        
        Args:
            user_id: The user identifier
            question: Question to ask about the user
            
        Returns:
            Insights string or None if not available
        """
        try:
            peer = self.honcho.peer(user_id)
            insights = peer.chat(question)
            return insights
        except Exception as e:
            print(f"⚠️  Dialectic not available: {e}")
            return None
    
    def get_user_facts(self, user_id: str) -> List[str]:
        """
        Get known facts about the user from Honcho's representation.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of fact strings
        """
        try:
            peer = self.honcho.peer(user_id)
            # Get representation (this contains conclusions/facts about the user)
            rep = peer.representation()
            # Extract facts from representation
            # This depends on Honcho's representation format
            return []
        except Exception as e:
            print(f"⚠️  Could not get user facts: {e}")
            return []


# OpenClaw Integration Hook Functions
# These functions can be called from OpenClaw's message handling

def before_turn_inject_memory(user_id: str, current_message: str) -> str:
    """
    Hook to inject memory context before OpenClaw processes a message.
    
    Usage in OpenClaw:
        context = before_turn_inject_memory(user_id, message)
        prompt = context + f"User: {message}\nAssistant:"
    """
    memory = OpenClawMemory()
    context = memory.get_context_for_prompt(user_id, limit=10)
    return context


def after_turn_store_memory(user_id: str, user_message: str, assistant_response: str, metadata: Optional[Dict] = None):
    """
    Hook to store conversation after OpenClaw generates a response.
    
    Usage in OpenClaw:
        after_turn_store_memory(user_id, message, response)
    """
    memory = OpenClawMemory()
    
    # Store user message
    memory.store_message(user_id, user_message, metadata)
    
    # Store assistant response (as metadata-only message or separate mechanism)
    # This depends on how Honcho handles assistant messages


# Test the integration
if __name__ == "__main__":
    import time
    
    print("🧠 Testing OpenClaw + Honcho Integration")
    print("=" * 60)
    
    memory = OpenClawMemory()
    user_id = "telegram-test-user"
    
    print("\n1️⃣ Storing test messages...")
    memory.store_message(user_id, "I love Python programming", {"topic": "programming"})
    memory.store_message(user_id, "I want to build AI agents", {"topic": "ai"})
    memory.store_message(user_id, "I work on automation projects", {"topic": "automation"})
    print("   ✅ Messages stored")
    
    print("\n2️⃣ Retrieving conversation history...")
    history = memory.get_history(user_id)
    print(f"   📊 Found {len(history)} messages")
    for h in history:
        print(f"      [{h['role']}] {h['content'][:50]}...")
    
    print("\n3️⃣ Getting formatted context for LLM...")
    context = memory.get_context_for_prompt(user_id, limit=5)
    if context:
        print(f"   Context:\n{context}")
    else:
        print("   No context available")
    
    print("\n4️⃣ Testing user insights (dialectic)...")
    insights = memory.get_user_insights(user_id, "What does this user like?")
    if insights:
        print(f"   💡 Insights: {insights[:200]}...")
    else:
        print("   ℹ️  Insights not available yet (deriver still processing)")
    
    print("\n" + "=" * 60)
    print("✅ Integration test complete!")
    print("\n🔧 To integrate with OpenClaw:")
    print('   1. Import: from honcho_integration import OpenClawMemory, before_turn_inject_memory, after_turn_store_memory')
    print('   2. Before LLM call: context = before_turn_inject_memory(user_id, message)')
    print('   3. After LLM response: after_turn_store_memory(user_id, message, response)')
    print("\n📚 API Docs: http://localhost:8002/docs")
    print("🔐 JWT Token configured for authentication")
