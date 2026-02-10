#!/usr/bin/env python3
"""
OpenClaw Agent with Honcho Memory Integration
==============================================

This is a complete OpenClaw agent implementation with persistent memory
using Honcho (self-hosted, ~$20-40/month via OpenRouter).

Features:
- Persistent conversation memory per user
- Context-aware responses using conversation history
- User insights via dialectic reasoning (optional)
- Cheap API costs via OpenRouter
"""

import sys
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add Honcho SDK to path
sys.path.insert(0, '/home/faisal/.openclaw/workspace/honcho-ai/sdks/python/src')
from honcho import Honcho

# Optional: Add your LLM client here
# from your_llm_client import LLMClient


class OpenClawAgent:
    """
    OpenClaw Agent with Honcho Memory.
    
    Usage:
        agent = OpenClawAgent()
        
        # Handle user message
        response = agent.handle_message(
            user_id="faisal",
            message="I love AI automation"
        )
        print(response)
        
        # Get user insights
        insights = agent.get_user_summary("faisal")
        print(insights)
    """
    
    def __init__(
        self,
        workspace_id: str = "openclaw",
        base_url: str = "http://localhost:8002",
        api_key: str = "openclaw-local-dev"
    ):
        """
        Initialize the OpenClaw agent with Honcho memory.
        
        Args:
            workspace_id: Honcho workspace ID
            base_url: Honcho API URL
            api_key: Honcho API key (auth disabled in local setup)
        """
        print("🚀 Initializing OpenClaw Agent with Honcho Memory...")
        
        # Initialize Honcho memory
        self.memory = Honcho(
            base_url=base_url,
            api_key=api_key,
            workspace_id=workspace_id
        )
        
        # Initialize your LLM here
        # self.llm = LLMClient()
        
        print(f"   ✅ Connected to Honcho at {base_url}")
        print(f"   ✅ Workspace: {workspace_id}")
    
    def handle_message(self, user_id: str, message: str) -> str:
        """
        Handle a user message with memory context.
        
        This method:
        1. Stores the user message
        2. Retrieves conversation history
        3. Builds context-aware prompt
        4. Gets LLM response
        5. Returns response
        
        Args:
            user_id: Unique user identifier
            message: User's message
            
        Returns:
            Assistant's response
        """
        # Step 1: Store user message
        self._store_message(user_id, message)
        
        # Step 2: Get conversation context
        context = self._get_conversation_context(user_id)
        
        # Step 3: Build prompt with context
        prompt = self._build_prompt(context, message)
        
        # Step 4: Get LLM response
        # response = self.llm.generate(prompt)
        # For demo, we'll use a simple echo
        response = self._generate_response(prompt, message)
        
        return response
    
    def _store_message(self, user_id: str, message: str) -> None:
        """
        Store a user message in Honcho memory.
        
        Args:
            user_id: User identifier
            message: Message content
        """
        # Get or create peer (user)
        peer = self.memory.peer(user_id)
        
        # Get or create session
        session_id = f"{user_id}-session"
        session = self.memory.session(session_id)
        
        # Link peer to session (ignore if already linked)
        try:
            session.add_peers([peer])
        except Exception:
            pass
        
        # Store message
        session.add_messages([peer.message(message)])
    
    def _get_conversation_context(
        self,
        user_id: str,
        limit: int = 10
    ) -> str:
        """
        Get formatted conversation history for context.
        
        Args:
            user_id: User identifier
            limit: Number of messages to retrieve
            
        Returns:
            Formatted conversation history
        """
        session_id = f"{user_id}-session"
        session = self.memory.session(session_id)
        
        messages = []
        for msg in session.messages():
            # Determine role from peer_id
            role = "User" if msg.peer_id else "Assistant"
            messages.append(f"{role}: {msg.content}")
        
        # Return last N messages
        return "\n".join(messages[-limit:])
    
    def _build_prompt(self, context: str, message: str) -> str:
        """
        Build prompt with conversation context.
        
        Args:
            context: Previous conversation
            message: Current user message
            
        Returns:
            Complete prompt for LLM
        """
        if context:
            return f"""Previous conversation:
{context}

User: {message}
Assistant:"""
        else:
            return f"User: {message}\nAssistant:"
    
    def _generate_response(self, prompt: str, original_message: str) -> str:
        """
        Generate response using LLM.
        
        Replace this with your actual LLM call.
        
        Args:
            prompt: Full prompt with context
            original_message: Original user message
            
        Returns:
            Generated response
        """
        # TODO: Replace with your LLM
        # return self.llm.generate(prompt)
        
        # Demo response
        return f"I remember our conversation! You said: '{original_message}'. How can I help you with that?"
    
    def get_user_summary(self, user_id: str) -> str:
        """
        Get summary of user's conversation history.
        
        Args:
            user_id: User identifier
            
        Returns:
            User summary
        """
        session_id = f"{user_id}-session"
        session = self.memory.session(session_id)
        
        message_count = sum(1 for _ in session.messages())
        
        if message_count == 0:
            return f"User {user_id} has no conversation history yet."
        
        return f"User {user_id} has sent {message_count} messages."
    
    def get_user_insights(self, user_id: str) -> Optional[str]:
        """
        Get AI-generated insights about the user.
        
        Requires deriver to be running for dialectic reasoning.
        
        Args:
            user_id: User identifier
            
        Returns:
            Insights or None if unavailable
        """
        try:
            peer = self.memory.peer(user_id)
            insights = peer.chat("What are this user's main interests and goals?")
            return insights
        except Exception as e:
            return f"Insights not available (deriver not running): {e}"
    
    def clear_user_history(self, user_id: str) -> bool:
        """
        Clear a user's conversation history.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if cleared
        """
        try:
            # In Honcho, you can create a new session
            # to effectively "clear" history
            session_id = f"{user_id}-session-new-{datetime.now().timestamp()}"
            session = self.memory.session(session_id)
            peer = self.memory.peer(user_id)
            session.add_peers([peer])
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False


# Demo / Test
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 OpenClaw Agent with Honcho Memory - Demo")
    print("=" * 60)
    
    # Initialize agent
    agent = OpenClawAgent()
    
    # Test user
    user_id = "demo-user-123"
    
    print("\n📨 Simulating conversation...")
    print("-" * 60)
    
    # Simulate conversation
    messages = [
        "Hello! I love working with AI.",
        "I want to build automation systems.",
        "My goal is to save time with AI agents.",
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n💬 Message {i}:")
        print(f"   User: {msg}")
        
        response = agent.handle_message(user_id, msg)
        print(f"   Assistant: {response}")
    
    print("\n" + "-" * 60)
    print("📊 User Summary:")
    print(f"   {agent.get_user_summary(user_id)}")
    
    print("\n🧠 User Insights (if deriver running):")
    insights = agent.get_user_insights(user_id)
    if insights and not insights.startswith("Insights not available"):
        print(f"   {insights[:200]}...")
    else:
        print(f"   {insights}")
    
    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("\n💡 To use in production:")
    print("   1. Replace _generate_response() with your LLM")
    print("   2. Import this class in your OpenClaw main")
    print("   3. Call handle_message() for each user message")
    print("=" * 60)
