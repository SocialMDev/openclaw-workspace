#!/usr/bin/env python3
"""
Long-runner state management.
Get, set, and manipulate workflow state.
"""
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

WORKFLOWS_DIR = Path("workflows")

def get_state_file(workflow: str = None) -> Path:
    """Find state file for workflow."""
    if workflow:
        return WORKFLOWS_DIR / workflow / "state.json"
    
    # Auto-detect from current directory or most recent
    workflows = list(WORKFLOWS_DIR.iterdir()) if WORKFLOWS_DIR.exists() else []
    if workflows:
        # Get most recently modified
        latest = max(workflows, key=lambda p: (p / "state.json").stat().st_mtime if (p / "state.json").exists() else 0)
        return latest / "state.json"
    
    raise FileNotFoundError("No workflow found. Run init first.")

def load_state(state_file: Path) -> dict:
    """Load state from file."""
    with open(state_file) as f:
        return json.load(f)

def save_state(state_file: Path, state: dict):
    """Save state to file."""
    state["last_updated"] = datetime.now().isoformat()
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

def set_value(key: str, value: str, workflow: str = None):
    """Set a state value."""
    state_file = get_state_file(workflow)
    state = load_state(state_file)
    
    # Try to parse as JSON (int, bool, etc.)
    try:
        parsed = json.loads(value)
        state["data"][key] = parsed
    except json.JSONDecodeError:
        state["data"][key] = value
    
    save_state(state_file, state)
    print(f"Set {key} = {value}")

def get_value(key: str, workflow: str = None):
    """Get a state value."""
    state_file = get_state_file(workflow)
    state = load_state(state_file)
    
    value = state["data"].get(key)
    if value is not None:
        print(value)
    else:
        print(f"Key '{key}' not found", file=sys.stderr)
        sys.exit(1)

def increment(key: str, amount: int = 1, workflow: str = None):
    """Increment a numeric state value."""
    state_file = get_state_file(workflow)
    state = load_state(state_file)
    
    current = state["data"].get(key, 0)
    if not isinstance(current, (int, float)):
        print(f"Cannot increment non-numeric value: {key}", file=sys.stderr)
        sys.exit(1)
    
    state["data"][key] = current + amount
    save_state(state_file, state)
    print(f"Incremented {key}: {current} -> {state['data'][key]}")

def list_state(workflow: str = None):
    """List all state values."""
    state_file = get_state_file(workflow)
    state = load_state(state_file)
    
    print(f"Workflow: {state['workflow_name']}")
    print(f"Phase: {state['current_phase']}")
    print(f"Step: {state['step_number']}")
    print("")
    print("Data:")
    for key, value in state["data"].items():
        print(f"  {key}: {value}")

def export_state(workflow: str = None):
    """Export full state as JSON."""
    state_file = get_state_file(workflow)
    state = load_state(state_file)
    print(json.dumps(state, indent=2))

def import_state(file_path: str, workflow: str = None):
    """Import state from JSON file."""
    state_file = get_state_file(workflow)
    
    with open(file_path) as f:
        new_state = json.load(f)
    
    save_state(state_file, new_state)
    print(f"Imported state from {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Manage workflow state")
    parser.add_argument("--workflow", help="Workflow name (auto-detect if omitted)")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Set
    set_parser = subparsers.add_parser("set", help="Set a value")
    set_parser.add_argument("key", help="Key name")
    set_parser.add_argument("value", help="Value to set")
    
    # Get
    get_parser = subparsers.add_parser("get", help="Get a value")
    get_parser.add_argument("key", help="Key name")
    
    # Increment
    inc_parser = subparsers.add_parser("increment", help="Increment a numeric value")
    inc_parser.add_argument("key", help="Key name")
    inc_parser.add_argument("amount", type=int, default=1, nargs="?", help="Amount to increment")
    
    # List
    subparsers.add_parser("list", help="List all state")
    
    # Export
    subparsers.add_parser("export", help="Export state as JSON")
    
    # Import
    import_parser = subparsers.add_parser("import", help="Import state from JSON")
    import_parser.add_argument("file", help="JSON file path")
    
    args = parser.parse_args()
    
    if args.command == "set":
        set_value(args.key, args.value, args.workflow)
    elif args.command == "get":
        get_value(args.key, args.workflow)
    elif args.command == "increment":
        increment(args.key, args.amount, args.workflow)
    elif args.command == "list":
        list_state(args.workflow)
    elif args.command == "export":
        export_state(args.workflow)
    elif args.command == "import":
        import_state(args.file, args.workflow)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
