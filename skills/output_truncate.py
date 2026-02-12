#!/usr/bin/env python3
"""
Tool output truncation utilities for OpenClaw token optimization.
Truncate tool outputs to prevent context bloat.
"""
import sys
import json
from typing import Optional

# Default maximum output tokens per tool type
DEFAULT_LIMITS = {
    "web_fetch": 1000,
    "exec": 500,
    "read": 1000,
    "browser": 2000,
    "web_search": 1000,
    "default": 1000
}

def truncate_output(output: str, max_tokens: int, tool_name: str = "default") -> str:
    """
    Truncate tool output to max tokens.
    
    Args:
        output: Raw tool output
        max_tokens: Maximum tokens allowed
        tool_name: Name of the tool (for tool-specific handling)
    
    Returns:
        Truncated output with indicator
    """
    if not output:
        return output
    
    # Approximate tokens: ~4 characters per token
    max_chars = max_tokens * 4
    
    if len(output) <= max_chars:
        return output
    
    # Truncate and add indicator
    truncated = output[:max_chars]
    removed_chars = len(output) - max_chars
    removed_tokens = removed_chars // 4
    
    return f"{truncated}\n\n... [truncated {removed_tokens} tokens ({removed_chars} chars)]"

def is_error_page(content: str) -> bool:
    """Detect if content is an error page."""
    error_indicators = [
        "404 Not Found",
        "500 Internal Server Error",
        "Error:</strong>",
        "Page not found",
        "<!DOCTYPE html>",  # Likely HTML error page
        "<html", 
        "</html>"
    ]
    content_lower = content[:5000].lower()  # Check first 5000 chars
    return any(indicator.lower() in content_lower for indicator in error_indicators)

def process_web_fetch(content: str, url: str = "") -> str:
    """Process web_fetch output - extract text, truncate HTML."""
    if is_error_page(content):
        return f"Error: Page at {url} returned error or HTML content (not text)."
    
    return truncate_output(content, DEFAULT_LIMITS["web_fetch"], "web_fetch")

def process_exec_output(output: str, command: str = "") -> str:
    """Process exec output - truncate long listings."""
    # Special handling for common commands
    if command.startswith("ls") and len(output) > 2000:
        lines = output.split("\n")
        if len(lines) > 50:
            truncated_lines = lines[:50]
            remaining = len(lines) - 50
            return "\n".join(truncated_lines) + f"\n... [{remaining} more lines]"
    
    if command.startswith("find") and len(output) > 3000:
        lines = output.split("\n")
        if len(lines) > 100:
            truncated_lines = lines[:100]
            remaining = len(lines) - 100
            return "\n".join(truncated_lines) + f"\n... [{remaining} more results]"
    
    return truncate_output(output, DEFAULT_LIMITS["exec"], "exec")

def process_read_output(content: str, file_path: str = "") -> str:
    """Process read output - truncate large files."""
    # Check if it's a code file and very large
    if len(content) > 10000:
        lines = content.split("\n")
        if len(lines) > 200:
            # Show first 100 and last 100 lines with ellipsis
            first_100 = "\n".join(lines[:100])
            last_100 = "\n".join(lines[-100:])
            skipped = len(lines) - 200
            return f"{first_100}\n\n... [{skipped} lines skipped] ...\n\n{last_100}"
    
    return truncate_output(content, DEFAULT_LIMITS["read"], "read")

def process_browser_output(content: str) -> str:
    """Process browser snapshot output."""
    # Browser output is often very verbose
    return truncate_output(content, DEFAULT_LIMITS["browser"], "browser")

def main():
    """CLI for output truncation."""
    if len(sys.argv) < 3:
        print("Usage: output_truncate.py <tool_name> <file_path> [max_tokens]")
        print("  tool_name: web_fetch, exec, read, browser, web_search")
        print("  file_path: Path to file containing tool output")
        print("  max_tokens: Optional override for token limit")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    file_path = sys.argv[2]
    max_tokens = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_LIMITS.get(tool_name, 1000)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Process based on tool type
    processors = {
        "web_fetch": process_web_fetch,
        "exec": process_exec_output,
        "read": process_read_output,
        "browser": process_browser_output,
        "web_search": lambda x: truncate_output(x, max_tokens, "web_search")
    }
    
    processor = processors.get(tool_name, lambda x: truncate_output(x, max_tokens, tool_name))
    result = processor(content)
    
    print(result)

if __name__ == "__main__":
    main()
