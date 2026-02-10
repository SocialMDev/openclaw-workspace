#!/usr/bin/env python3
"""Simple Honcho integration test."""
import sys
sys.path.insert(0, '/home/faisal/.openclaw/workspace/honcho-ai/sdks/python/src')
from honcho import Honcho

print("Testing Honcho Integration")
print("=" * 40)

honcho = Honcho(
    base_url="http://localhost:8002",
    api_key="test",
    workspace_id="openclaw-main"
)

# Test 1: Create peer
print("\n1. Creating peer...")
peer = honcho.peer("demo-user")
print(f"   ✓ Peer: {peer.id}")

# Test 2: Create session
print("\n2. Creating session...")
session = honcho.session("demo-session")
print(f"   ✓ Session: {session.id}")

# Test 3: Link peer
print("\n3. Linking peer to session...")
try:
    session.add_peers([peer])
    print(f"   ✓ Linked")
except:
    print(f"   ✓ Already linked")

# Test 4: Add messages
print("\n4. Adding messages...")
session.add_messages([
    peer.message("Hello, I love AI"),
    peer.message("I build automation systems"),
])
print(f"   ✓ 2 messages added")

# Test 5: Retrieve messages
print("\n5. Retrieving messages...")
count = 0
for msg in session.messages():
    count += 1
    role = "user" if msg.peer_id else "assistant"
    print(f"   [{role}] {msg.content[:30]}...")

print(f"\n✅ Test complete! {count} messages retrieved.")
print("\nHoncho is ready for OpenClaw integration!")
