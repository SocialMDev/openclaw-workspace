#!/usr/bin/env python3
"""
Long-runner workflow initialization.
Creates workflow directory structure and initial state.
"""
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

WORKFLOWS_DIR = Path("workflows")

def init_workflow(name: str, venv: bool = False, venv_path: str = None):
    """Initialize a new workflow."""
    workflow_dir = WORKFLOWS_DIR / name
    
    # Create directory structure
    (workflow_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    (workflow_dir / "inputs").mkdir(parents=True, exist_ok=True)
    (workflow_dir / "outputs").mkdir(parents=True, exist_ok=True)
    (workflow_dir / "logs").mkdir(parents=True, exist_ok=True)
    
    # Create initial state
    state = {
        "workflow_name": name,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "current_phase": "initialized",
        "phases_completed": [],
        "step_number": 0,
        "data": {},
        "artifacts": [],
        "config": {
            "venv": venv,
            "venv_path": venv_path
        }
    }
    
    state_file = workflow_dir / "state.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"Initialized workflow: {name}")
    print(f"  Directory: {workflow_dir}")
    print(f"  State file: {state_file}")
    
    if venv:
        print("  Virtual env: Will be created on first use")
    
    return workflow_dir

def main():
    parser = argparse.ArgumentParser(description="Initialize a long-runner workflow")
    parser.add_argument("--name", required=True, help="Workflow name")
    parser.add_argument("--venv", action="store_true", help="Create isolated venv")
    parser.add_argument("--venv-path", help="Use existing venv path")
    parser.add_argument("--import-artifacts", nargs=2, metavar=("FROM", "WORKFLOW"),
                       help="Import artifacts from another workflow")
    
    args = parser.parse_args()
    
    workflow_dir = init_workflow(
        name=args.name,
        venv=args.venv,
        venv_path=args.venv_path
    )
    
    if args.import_artifacts:
        source_workflow = args.import_artifacts[1]
        source_dir = WORKFLOWS_DIR / source_workflow / "outputs"
        if source_dir.exists():
            import shutil
            for f in source_dir.iterdir():
                if f.is_file():
                    shutil.copy(f, workflow_dir / "inputs" / f.name)
                    print(f"  Imported: {f.name}")

if __name__ == "__main__":
    main()
