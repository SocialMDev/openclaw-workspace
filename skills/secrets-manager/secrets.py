#!/usr/bin/env python3
"""
Secrets management utility for OpenClaw.
Loads domain secrets securely without exposing credentials to context window.
"""
import os
import sys
import stat
from pathlib import Path

SECRETS_DIR = Path.home() / ".openclaw" / "secrets"

def ensure_secrets_dir():
    """Create secrets directory with proper permissions."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    # Restrict to owner only (0700)
    os.chmod(SECRETS_DIR, stat.S_IRWXU)

def get_secret(name: str) -> str | None:
    """
    Load a secret by name.
    
    Args:
        name: Secret file name (e.g., 'github-token', 'openai-api-key')
    
    Returns:
        Secret value or None if not found
    """
    ensure_secrets_dir()
    secret_path = SECRETS_DIR / name
    
    if not secret_path.exists():
        return None
    
    # Check permissions - should be owner-readable only
    mode = secret_path.stat().st_mode
    if mode & stat.S_IRWXG or mode & stat.S_IRWXO:
        print(f"WARNING: {secret_path} has overly permissive permissions", file=sys.stderr)
    
    return secret_path.read_text().strip()

def set_secret(name: str, value: str) -> None:
    """
    Store a secret securely.
    
    Args:
        name: Secret file name
        value: Secret value
    """
    ensure_secrets_dir()
    secret_path = SECRETS_DIR / name
    
    secret_path.write_text(value)
    # Owner read/write only (0600)
    os.chmod(secret_path, stat.S_IRUSR | stat.S_IWUSR)
    
    print(f"Secret '{name}' stored securely at {secret_path}")

def list_secrets() -> list[str]:
    """List all stored secret names (not values)."""
    ensure_secrets_dir()
    return [f.name for f in SECRETS_DIR.iterdir() if f.is_file()]

def inject_placeholders(text: str) -> str:
    """
    Replace placeholders like $SECRET_NAME with actual secret values.
    
    Args:
        text: Text containing placeholders
    
    Returns:
        Text with placeholders replaced
    """
    import re
    
    pattern = r'\$([A-Z_][A-Z0-9_]*)'
    
    def replace_match(match):
        secret_name = match.group(1).lower().replace('_', '-')
        value = get_secret(secret_name)
        if value is None:
            return match.group(0)  # Keep original if not found
        return value
    
    return re.sub(pattern, replace_match, text)

def main():
    """CLI for secrets management."""
    if len(sys.argv) < 2:
        print("Usage: secrets.py <command> [args...]")
        print("")
        print("Commands:")
        print("  list                    List all stored secrets")
        print("  get <name>              Get a secret value")
        print("  set <name> <value>      Store a secret")
        print("  inject <text>           Replace $PLACEHOLDERS in text")
        print("")
        print("Examples:")
        print("  secrets.py set github-token ghp_xxxxxxxx")
        print("  secrets.py inject 'Authorization: Bearer $GITHUB_TOKEN'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        secrets = list_secrets()
        if secrets:
            print("Stored secrets:")
            for s in secrets:
                print(f"  - {s}")
        else:
            print("No secrets stored.")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: secrets.py get <name>")
            sys.exit(1)
        value = get_secret(sys.argv[2])
        if value:
            print(value)
        else:
            print(f"Secret '{sys.argv[2]}' not found", file=sys.stderr)
            sys.exit(1)
    
    elif command == "set":
        if len(sys.argv) < 4:
            print("Usage: secrets.py set <name> <value>")
            sys.exit(1)
        set_secret(sys.argv[2], sys.argv[3])
    
    elif command == "inject":
        if len(sys.argv) < 3:
            print("Usage: secrets.py inject '<text with $PLACEHOLDERS>'")
            sys.exit(1)
        print(inject_placeholders(sys.argv[2]))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
