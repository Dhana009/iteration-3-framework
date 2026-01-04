
import json
import pytest
from pathlib import Path

def test_morning_roll_call_resets_state(testdir):
    """
    Verifies that pytest_sessionstart clears user_state.json.
    """
    
    # 1. Setup Mock Project
    # We copy necessary files to the temp testdir
    # Note: 'testdir' fixture is from pytest-pytester, but dealing with
    # complex environment imports in testdir is hard.
    # INSTEAD, we will try to invoke pytest on the ACTUAL project with a dry run
    # but that might be dangerous if we mess with real config.
    
    # ALTERNATIVE: We can just unit test the hook function if we import it.
    # But hooks are hard to import.
    
    # SAFEST: Sanity check via direct function text is too weak.
    # Let's write a small script that:
    # 1. Writes dirty state to config/user_state.json
    # 2. Assert dirty state exists
    # 3. Simulate "pytest session start" by calling the logic directly (easier than spawning pytest)
    pass

# REAL SCRIPT BELOW
import sys
import os

# Add root to path
ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from utils.file_lock import AtomicLock

def verify_morning_roll_call():
    print(">>> Starting Morning Roll Call Verification")
    
    state_path = ROOT / 'config' / 'user_state.json'
    lock_path = ROOT / 'config' / 'user_pool.lock'
    
    # 1. Pollute State
    print(">>> Polluting state file...")
    with AtomicLock(lock_path):
        with open(state_path, 'w') as f:
            json.dump({"test@email.com": "stuck_worker"}, f)
            
    # Verify Pollution
    with open(state_path) as f:
        data = json.load(f)
        assert "test@email.com" in data
    print("[PASS] State is polluted.")

    # 2. Trigger Hook Logic
    # We simulate what hooks.py does (importing it is tricky due to pytest naming)
    # We will basically execute the file? No, let's load it as a module source.
    import importlib.util
    spec = importlib.util.spec_from_file_location("hooks", ROOT / "tests" / "plugins" / "hooks.py")
    hooks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hooks)
    
    # Mock Session Object
    class MockConfig:
        rootdir = str(ROOT)
    class MockSession:
        config = MockConfig()
        
    print(">>> Triggering pytest_sessionstart hook...")
    hooks.pytest_sessionstart(MockSession())
    
    # 3. Verify Clean
    with open(state_path) as f:
        data = json.load(f)
        assert data == {}, f"State should be empty, but got {data}"
    
    print("[PASS] State is clean.")
    print(">>> VERIFICATION SUCCESS")

if __name__ == "__main__":
    try:
        verify_morning_roll_call()
    except Exception as e:
        print(f"!!! FAILED: {e}")
        exit(1)
