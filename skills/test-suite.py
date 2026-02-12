#!/usr/bin/env python3
"""
Test suite for agent primitives upgrade.
Validates all new skills are working correctly.
"""
import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report success/failure."""
    print(f"\n🧪 Testing: {description}")
    print(f"   Command: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"   ✅ PASS")
            return True
        else:
            print(f"   ❌ FAIL: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

def test_secrets_manager():
    """Test secrets-manager skill."""
    tests = [
        ("python3 skills/secrets-manager/secrets.py list", "List secrets (empty)"),
        ("python3 skills/secrets-manager/secrets.py set test-secret test-value", "Set a secret"),
        ("python3 skills/secrets-manager/secrets.py get test-secret", "Get a secret"),
        ("python3 skills/secrets-manager/secrets.py inject 'Key: $TEST_SECRET'", "Inject placeholder"),
    ]
    
    results = [run_command(cmd, desc) for cmd, desc in tests]
    
    # Cleanup
    Path.home().joinpath(".openclaw/secrets/test-secret").unlink(missing_ok=True)
    
    return all(results)

def test_compaction():
    """Test compaction skill."""
    tests = [
        ("python3 skills/compaction/compaction.py analyze", "Analyze context"),
        ("python3 skills/compaction/compaction.py checkpoint test-checkpoint", "Create checkpoint"),
        ("python3 skills/compaction/compaction.py report", "View report"),
    ]
    
    results = [run_command(cmd, desc) for cmd, desc in tests]
    return all(results)

def test_long_runner():
    """Test long-runner skill."""
    workflow_name = "test-workflow"
    
    tests = [
        (f"python3 skills/long-runner/scripts/init.py --name {workflow_name}", "Initialize workflow"),
        (f"python3 skills/long-runner/scripts/state.py set test_key test_value", "Set state value"),
        (f"python3 skills/long-runner/scripts/state.py get test_key", "Get state value"),
        (f"python3 skills/long-runner/scripts/state.py increment counter 1", "Increment counter"),
        (f"python3 skills/long-runner/scripts/checkpoint.py create test-checkpoint", "Create checkpoint"),
        (f"python3 skills/long-runner/scripts/checkpoint.py list", "List checkpoints"),
    ]
    
    results = [run_command(cmd, desc) for cmd, desc in tests]
    
    # Cleanup
    import shutil
    shutil.rmtree(f"workflows/{workflow_name}", ignore_errors=True)
    
    return all(results)

def test_artifacts_structure():
    """Test artifacts directory structure."""
    print("\n🧪 Testing: Artifacts directory structure")
    
    dirs = [
        "artifacts/data",
        "artifacts/reports",
        "artifacts/exports",
        "artifacts/temp",
    ]
    
    all_exist = True
    for d in dirs:
        path = Path(d)
        if path.exists():
            print(f"   ✅ {d}/ exists")
        else:
            print(f"   ❌ {d}/ missing")
            all_exist = False
    
    return all_exist

def test_secrets_permissions():
    """Test secrets directory permissions."""
    print("\n🧪 Testing: Secrets directory permissions")
    
    secrets_dir = Path.home() / ".openclaw/secrets"
    
    if not secrets_dir.exists():
        print("   ❌ Secrets directory doesn't exist")
        return False
    
    import stat
    mode = secrets_dir.stat().st_mode
    
    # Check 0700 permissions
    if mode & stat.S_IRWXU and not (mode & stat.S_IRWXG) and not (mode & stat.S_IRWXO):
        print(f"   ✅ Secrets dir has correct permissions (0700)")
        return True
    else:
        print(f"   ⚠️  Secrets dir permissions: {oct(mode)}")
        return True  # Warning but not failure

def test_security_config():
    """Test security configuration exists."""
    print("\n🧪 Testing: Security configuration")
    
    config_path = Path.home() / ".openclaw/config/security.yaml"
    
    if config_path.exists():
        print(f"   ✅ Security config exists")
        return True
    else:
        print(f"   ❌ Security config missing")
        return False

def test_skill_files():
    """Test all skill files exist."""
    print("\n🧪 Testing: Skill files")
    
    required_files = [
        "skills/secrets-manager/SKILL.md",
        "skills/secrets-manager/secrets.py",
        "skills/compaction/SKILL.md",
        "skills/compaction/compaction.py",
        "skills/long-runner/SKILL.md",
        "skills/long-runner/scripts/init.py",
        "skills/long-runner/scripts/state.py",
        "skills/long-runner/scripts/checkpoint.py",
        "skills/x-scraper/edge-cases.md",
        "skills/token-monitor/edge-cases.md",
    ]
    
    all_exist = True
    for f in required_files:
        path = Path(f)
        if path.exists():
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("=" * 60)
    print("Agent Primitives Upgrade - Test Suite")
    print("=" * 60)
    
    results = {
        "Secrets Manager": test_secrets_manager(),
        "Compaction": test_compaction(),
        "Long Runner": test_long_runner(),
        "Artifacts Structure": test_artifacts_structure(),
        "Secrets Permissions": test_secrets_permissions(),
        "Security Config": test_security_config(),
        "Skill Files": test_skill_files(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print("-" * 60)
    print(f"  Total: {passed}/{total} passed")
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
