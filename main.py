#!/usr/bin/env python3
"""
OpenClaw - Main Application
===========================

Complete AI assistant with persistent memory via Honcho.

Features:
- Persistent conversation memory per user
- Context-aware responses
- Cheap API costs via OpenRouter
- Self-hosted (no vendor lock-in)

Usage:
    python main.py
    
Or as a module:
    from main import OpenClaw
    openclaw = OpenClaw()
    response = openclaw.chat("faisal", "Hello!")
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add Honcho SDK to path
sys.path.insert(0, '/home/faisal/.openclaw/workspace/honcho-ai/sdks/python/src')

try:
    from honcho import Honcho
    HONCHO_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import Honcho: {e}")
    HONCHO_AVAILABLE = False


class OpenClaw:
    """
    OpenClaw AI Assistant with Persistent Memory.
    
    This is the main class for the OpenClaw system. It provides:
    - User memory management via Honcho
    - Context-aware conversations
    - Message history tracking
    - User insights (with dialectic)
    
    Example:
        >>> openclaw = OpenClaw()
        >>> response = openclaw.chat("user123", "Hello!")
        >>> print(response)
        Hello! How can I help you today?
        
        >>> # Later...
        >>> response = openclaw.chat("user123", "What did I say before?")
        >>> print(response)
        You said "Hello!" earlier.
    """
    
    def __init__(
        self,
        honcho_url: str = "http://localhost:8002",
        honcho_key: str = "openclaw-local-dev",
        workspace: str = "openclaw"
    ):
        """
        Initialize OpenClaw.
        
        Args:
            honcho_url: Honcho API URL
            honcho_key: Honcho API key
            workspace: Workspace ID for isolation
        """
        logger.info("🚀 Initializing OpenClaw...")
        
        self.honcho_url = honcho_url
        self.honcho_key = honcho_key
        self.workspace = workspace
        
        # Initialize Honcho
        if HONCHO_AVAILABLE:
            try:
                self.memory = Honcho(
                    base_url=honcho_url,
                    api_key=honcho_key,
                    workspace_id=workspace
                )
                logger.info(f"   ✅ Connected to Honcho at {honcho_url}")
                logger.info(f"   ✅ Workspace: {workspace}")
            except Exception as e:
                logger.error(f"   ❌ Failed to connect to Honcho: {e}")
                self.memory = None
        else:
            logger.warning("   ⚠️  Honcho not available - running without memory")
            self.memory = None
        
        # Message cache for quick access
        self._message_cache: Dict[str, List[Dict]] = {}
        
        logger.info("✅ OpenClaw ready!")
    
    def chat(self, user_id: str, message: str) -> str:
        """
        Process a user message and return a response.
        
        This is the main entry point for conversations. It:
        1. Stores the user message
        2. Retrieves conversation context
        3. Generates a context-aware response
        4. Returns the response
        
        Args:
            user_id: Unique user identifier
            message: User's message
            
        Returns:
            Assistant's response
            
        Example:
            >>> openclaw = OpenClaw()
            >>> openclaw.chat("user1", "I love Python")
            "That's great! Python is a powerful language for automation."
        """
        logger.info(f"💬 Message from {user_id}: {message[:50]}...")
        
        # Store user message
        self._store_message(user_id, message)
        
        # Get context
        context = self._get_context(user_id)
        
        # Generate response
        response = self._generate_response(user_id, message, context)
        
        logger.info(f"🤖 Response: {response[:50]}...")
        
        return response
    
    def _store_message(self, user_id: str, message: str) -> None:
        """
        Store a message in Honcho memory.
        
        Args:
            user_id: User identifier
            message: Message content
        """
        if not self.memory:
            logger.debug("Memory not available, skipping storage")
            return
        
        try:
            # Get or create peer
            peer = self.memory.peer(user_id)
            
            # Get or create session
            session_id = f"{user_id}-session"
            session = self.memory.session(session_id)
            
            # Link peer to session
            try:
                session.add_peers([peer])
            except Exception:
                pass  # Already linked
            
            # Store message
            session.add_messages([peer.message(message)])
            logger.debug(f"Stored message for {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to store message: {e}")
    
    def _get_context(self, user_id: str, limit: int = 10) -> str:
        """
        Get conversation context for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum messages to retrieve
            
        Returns:
            Formatted conversation history
        """
        if not self.memory:
            return ""
        
        try:
            session_id = f"{user_id}-session"
            session = self.memory.session(session_id)
            
            messages = []
            for msg in session.messages():
                role = "User" if msg.peer_id else "Assistant"
                messages.append(f"{role}: {msg.content}")
            
            # Return last N messages
            context = "\n".join(messages[-limit:])
            logger.debug(f"Retrieved {len(messages)} messages for context")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return ""
    
    def _generate_response(
        self,
        user_id: str,
        message: str,
        context: str
    ) -> str:
        """
        Generate a response based on message and context.
        
        This is where you'd integrate your LLM.
        
        Args:
            user_id: User identifier
            message: Current message
            context: Conversation history
            
        Returns:
            Generated response
        """
        # TODO: Replace with your LLM
        # For now, a simple contextual response
        
        if context:
            # We have history - reference it
            return (
                f"I remember our conversation! You said things like: "
                f"'{context.split(chr(10))[-1][:50]}...' "
                f"Now you're asking about: {message[:50]}"
            )
        else:
            # First message
            return f"Hello! I see you're interested in: {message[:50]}. Tell me more!"
    
    def get_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get message history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum messages
            
        Returns:
            List of message dicts
        """
        if not self.memory:
            return []
        
        try:
            session_id = f"{user_id}-session"
            session = self.memory.session(session_id)
            
            messages = []
            for msg in session.messages():
                messages.append({
                    "role": "user" if msg.peer_id else "assistant",
                    "content": msg.content,
                    "created_at": str(msg.created_at)
                })
            
            return messages[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get information about a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User info dict
        """
        history = self.get_history(user_id)
        
        return {
            "user_id": user_id,
            "message_count": len(history),
            "first_seen": history[0]["created_at"] if history else None,
            "last_active": history[-1]["created_at"] if history else None,
        }
    
    def clear_history(self, user_id: str) -> bool:
        """
        Clear a user's conversation history.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if cleared
        """
        if not self.memory:
            return False
        
        try:
            # Create new session to clear history
            session_id = f"{user_id}-session-{int(datetime.now().timestamp())}"
            session = self.memory.session(session_id)
            peer = self.memory.peer(user_id)
            session.add_peers([peer])
            
            logger.info(f"Cleared history for {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False


# CLI Interface
def main():
    """Run OpenClaw CLI."""
    print("=" * 60)
    print("🤖 OpenClaw - AI Assistant with Memory")
    print("=" * 60)
    
    # Initialize
    openclaw = OpenClaw()
    
    print("\n💡 Commands:")
    print("   Type your message to chat")
    print("   'history' - show your conversation history")
    print("   'info' - show your user info")
    print("   'clear' - clear your history")
    print("   'quit' - exit")
    print("-" * 60)
    
    # Use a default user for CLI
    user_id = "cli-user"
    
    while True:
        try:
            # Get input
            message = input(f"\n👤 You: ").strip()
            
            if not message:
                continue
            
            # Handle commands
            if message.lower() == 'quit':
                print("\n👋 Goodbye!")
                break
            
            elif message.lower() == 'history':
                history = openclaw.get_history(user_id)
                print(f"\n📜 History ({len(history)} messages):")
                for h in history[-10:]:
                    role = "🧑" if h["role"] == "user" else "🤖"
                    print(f"   {role} {h['content'][:60]}...")
                continue
            
            elif message.lower() == 'info':
                info = openclaw.get_user_info(user_id)
                print(f"\nℹ️  User Info:")
                for key, value in info.items():
                    print(f"   {key}: {value}")
                continue
            
            elif message.lower() == 'clear':
                if openclaw.clear_history(user_id):
                    print("\n🗑️  History cleared!")
                else:
                    print("\n❌ Failed to clear history")
                continue
            
            # Process message
            response = openclaw.chat(user_id, message)
            print(f"🤖 OpenClaw: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
