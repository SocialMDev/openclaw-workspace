#!/usr/bin/env python3
"""
Context compaction utility for OpenClaw.
Compresses conversation history to prevent token limit exhaustion.
"""
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

ARTIFACTS_DIR = Path("artifacts/compaction")
CHECKPOINTS_DIR = Path("checkpoints")

class ContextCompactor:
    """Compacts conversation context while preserving critical information."""
    
    def __init__(self, keep_recent: int = 5):
        self.keep_recent = keep_recent
        self.summary = []
        
    def analyze_content(self, messages: list[dict]) -> dict:
        """Analyze messages and categorize by importance."""
        analysis = {
            "total_messages": len(messages),
            "system_prompts": [],
            "tool_calls": [],
            "tool_outputs": [],
            "user_messages": [],
            "assistant_messages": [],
            "key_decisions": [],
        }
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "system":
                analysis["system_prompts"].append(msg)
            elif role == "tool":
                if len(content) > 500:
                    analysis["tool_outputs"].append(msg)
                else:
                    analysis["tool_calls"].append(msg)
            elif role == "user":
                analysis["user_messages"].append(msg)
                # Detect key decisions
                if any(kw in content.lower() for kw in ["decide", "choose", "use ", "don't use", "important"]):
                    analysis["key_decisions"].append(msg)
            elif role == "assistant":
                analysis["assistant_messages"].append(msg)
                
        return analysis
    
    def summarize_exchanges(self, messages: list[dict]) -> str:
        """Generate a summary of older exchanges."""
        if not messages:
            return ""
        
        # Extract key actions and outcomes
        actions = []
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            
            if role == "user" and len(content) < 200:
                actions.append(f"User requested: {content[:100]}...")
            elif role == "assistant" and "tool" in content.lower():
                actions.append("Assistant executed tools")
        
        if not actions:
            return f"Session included {len(messages)} exchanges."
        
        return " | ".join(actions[:5])  # Limit to first 5 actions
    
    def compact(self, messages: list[dict]) -> tuple[list[dict], dict]:
        """
        Compact message history.
        
        Returns:
            Tuple of (compacted_messages, metadata)
        """
        if len(messages) <= self.keep_recent + 2:
            return messages, {"compacted": False, "reason": "Too few messages"}
        
        analysis = self.analyze_content(messages)
        
        # Always preserve system prompts
        preserved = [m for m in messages if m.get("role") == "system"]
        
        # Always preserve key decisions
        preserved.extend(analysis["key_decisions"])
        
        # Keep recent messages
        recent = messages[-self.keep_recent:]
        
        # Summarize middle section
        middle_start = len(preserved)
        middle_end = len(messages) - self.keep_recent
        
        if middle_end > middle_start:
            middle_messages = messages[middle_start:middle_end]
            summary = self.summarize_exchanges(middle_messages)
            
            if summary:
                summary_msg = {
                    "role": "system",
                    "content": f"[SESSION SUMMARY]: {summary}",
                    "timestamp": datetime.now().isoformat()
                }
                preserved.append(summary_msg)
        
        # Add recent messages
        compacted = preserved + recent
        
        metadata = {
            "compacted": True,
            "original_count": len(messages),
            "compacted_count": len(compacted),
            "reduction": f"{((len(messages) - len(compacted)) / len(messages) * 100):.1f}%",
            "summary": summary if 'summary' in locals() else "N/A"
        }
        
        return compacted, metadata
    
    def save_checkpoint(self, messages: list[dict], name: Optional[str] = None):
        """Save a checkpoint before compaction."""
        CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = name or f"checkpoint_{timestamp}"
        
        checkpoint_file = CHECKPOINTS_DIR / f"{name}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "message_count": len(messages),
                "messages": messages
            }, f, indent=2)
        
        return checkpoint_file
    
    def save_summary(self, metadata: dict):
        """Save compaction summary to artifacts."""
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        
        summary_file = ARTIFACTS_DIR / "last-summary.md"
        
        content = f"""# Compaction Summary

**Timestamp**: {datetime.now().isoformat()}

## Statistics

- Original messages: {metadata.get('original_count', 'N/A')}
- Compacted messages: {metadata.get('compacted_count', 'N/A')}
- Reduction: {metadata.get('reduction', 'N/A')}

## Summary Content

{metadata.get('summary', 'No summary generated')}

## Checkpoints

Last checkpoint: {list(CHECKPOINTS_DIR.glob('*.json'))[-1] if list(CHECKPOINTS_DIR.glob('*.json')) else 'None'}
"""
        summary_file.write_text(content)
        return summary_file

def main():
    """CLI for compaction utility."""
    if len(sys.argv) < 2:
        print("Usage: compaction.py <command> [args...]")
        print("")
        print("Commands:")
        print("  analyze                  Analyze current session (simulated)")
        print("  compact [--keep-recent N] Compact context")
        print("  checkpoint [name]        Save checkpoint")
        print("  report                   Show last compaction report")
        print("")
        print("Examples:")
        print("  compaction.py analyze")
        print("  compaction.py compact --keep-recent 10")
        print("  compaction.py checkpoint before-major-change")
        sys.exit(1)
    
    command = sys.argv[1]
    compactor = ContextCompactor()
    
    if command == "analyze":
        print("Context Compaction Analysis")
        print("=" * 40)
        print()
        print("This would analyze the current session's token usage.")
        print("In actual implementation, this connects to OpenClaw's session data.")
        print()
        print("Key metrics to track:")
        print("  - Total tokens used")
        print("  - Tokens remaining")
        print("  - Compression opportunity")
        
    elif command == "compact":
        # Parse args
        keep_recent = 5
        if "--keep-recent" in sys.argv:
            idx = sys.argv.index("--keep-recent")
            if idx + 1 < len(sys.argv):
                keep_recent = int(sys.argv[idx + 1])
        
        compactor.keep_recent = keep_recent
        
        # In real implementation, this would fetch actual session messages
        # For now, demonstrate the concept
        print(f"Compaction configured (keep_recent={keep_recent})")
        print()
        print("In actual implementation:")
        print("1. Fetches current session messages")
        print("2. Saves checkpoint")
        print("3. Compacts context")
        print("4. Returns compacted messages to session")
        
    elif command == "checkpoint":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        checkpoint_file = compactor.save_checkpoint([], name)
        print(f"Checkpoint saved: {checkpoint_file}")
        
    elif command == "report":
        summary_file = ARTIFACTS_DIR / "last-summary.md"
        if summary_file.exists():
            print(summary_file.read_text())
        else:
            print("No compaction report found.")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
