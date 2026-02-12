#!/usr/bin/env python3
"""
Long-runner checkpoint management.
Create, list, and restore checkpoints.
"""
import json
import shutil
import sys
import argparse
from datetime import datetime
from pathlib import Path

WORKFLOWS_DIR = Path("workflows")
CHECKPOINTS_DIR = Path("checkpoints")

def get_workflow_dir(workflow: str = None) -> Path:
    """Find workflow directory."""
    if workflow:
        return WORKFLOWS_DIR / workflow
    
    workflows = list(WORKFLOWS_DIR.iterdir()) if WORKFLOWS_DIR.exists() else []
    if workflows:
        latest = max(workflows, key=lambda p: (p / "state.json").stat().st_mtime if (p / "state.json").exists() else 0)
        return latest
    
    raise FileNotFoundError("No workflow found.")

def create_checkpoint(name: str = None, description: str = None, workflow: str = None):
    """Create a checkpoint."""
    workflow_dir = get_workflow_dir(workflow)
    state_file = workflow_dir / "state.json"
    
    if not state_file.exists():
        print("No state file found. Is this workflow initialized?", file=sys.stderr)
        sys.exit(1)
    
    with open(state_file) as f:
        state = json.load(f)
    
    # Generate checkpoint name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    step_num = state.get("step_number", 0)
    checkpoint_name = name or f"step-{step_num}_{timestamp}"
    
    # Collect artifacts
    artifacts = []
    outputs_dir = workflow_dir / "outputs"
    if outputs_dir.exists():
        artifacts = [str(p.relative_to(workflow_dir)) for p in outputs_dir.iterdir() if p.is_file()]
    
    # Also collect from global artifacts
    global_artifacts = []
    for subdir in ["data", "reports", "exports"]:
        art_dir = Path("artifacts") / subdir
        if art_dir.exists():
            global_artifacts.extend([str(p) for p in art_dir.iterdir() if p.is_file()])
    
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "workflow_name": state["workflow_name"],
        "step_number": step_num,
        "step_name": state.get("current_phase", "unknown"),
        "description": description or f"Checkpoint at step {step_num}",
        "state": state,
        "artifacts": artifacts,
        "global_artifacts": global_artifacts
    }
    
    # Save to workflow checkpoints
    checkpoint_file = workflow_dir / "checkpoints" / f"{checkpoint_name}.json"
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    # Also save as "latest"
    latest_file = workflow_dir / "checkpoints" / "latest.json"
    with open(latest_file, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    # Backup to global checkpoints
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = CHECKPOINTS_DIR / f"{state['workflow_name']}-{checkpoint_name}.json"
    with open(backup_file, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    print(f"Created checkpoint: {checkpoint_name}")
    print(f"  Workflow: {state['workflow_name']}")
    print(f"  Step: {step_num} ({state.get('current_phase', 'unknown')})")
    print(f"  Artifacts: {len(artifacts)} local, {len(global_artifacts)} global")
    
    return checkpoint_file

def list_checkpoints(workflow: str = None):
    """List all checkpoints for a workflow."""
    workflow_dir = get_workflow_dir(workflow)
    checkpoints_dir = workflow_dir / "checkpoints"
    
    if not checkpoints_dir.exists():
        print("No checkpoints found.")
        return
    
    checkpoints = sorted(checkpoints_dir.glob("*.json"))
    
    print(f"Checkpoints for {workflow_dir.name}:")
    print("")
    
    for cp_file in checkpoints:
        with open(cp_file) as f:
            cp = json.load(f)
        
        marker = " ← LATEST" if cp_file.name == "latest.json" else ""
        print(f"  {cp_file.stem}{marker}")
        print(f"    Step: {cp.get('step_number', 'N/A')} - {cp.get('step_name', 'unknown')}")
        print(f"    Time: {cp.get('timestamp', 'unknown')[:19]}")
        if cp.get('description'):
            print(f"    Desc: {cp['description'][:60]}...")
        print("")

def cleanup_checkpoints(keep: int = 5, workflow: str = None):
    """Clean up old checkpoints, keeping only N most recent."""
    workflow_dir = get_workflow_dir(workflow)
    checkpoints_dir = workflow_dir / "checkpoints"
    
    if not checkpoints_dir.exists():
        return
    
    # Get all checkpoints except "latest.json"
    checkpoints = [f for f in checkpoints_dir.glob("*.json") if f.name != "latest.json"]
    checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    to_delete = checkpoints[keep:]
    
    for f in to_delete:
        f.unlink()
        print(f"Removed: {f.name}")
    
    print(f"Kept {min(keep, len(checkpoints))} checkpoints")

def main():
    parser = argparse.ArgumentParser(description="Manage workflow checkpoints")
    parser.add_argument("--workflow", help="Workflow name (auto-detect if omitted)")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Create
    create_parser = subparsers.add_parser("create", help="Create a checkpoint")
    create_parser.add_argument("name", nargs="?", help="Checkpoint name")
    create_parser.add_argument("--description", help="Checkpoint description")
    
    # List
    subparsers.add_parser("list", help="List checkpoints")
    
    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old checkpoints")
    cleanup_parser.add_argument("--keep", type=int, default=5, help="Number to keep")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_checkpoint(args.name, args.description, args.workflow)
    elif args.command == "list":
        list_checkpoints(args.workflow)
    elif args.command == "cleanup":
        cleanup_checkpoints(args.keep, args.workflow)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
