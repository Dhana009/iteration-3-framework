
import json
import os
from pathlib import Path
from lib.users import UserLease, STATE_PATH, CONFIG_PATH, LOCK_PATH

def test_user_lease_mechanics():
    print(">>> Starting UserLease Mechanics Verification")
    
    # 0. Setup: ensure clean state
    if STATE_PATH.exists():
        os.remove(STATE_PATH)
    
    lease = UserLease("worker_test_mech")
    
    # Check 1: State file should be auto-created on init
    assert STATE_PATH.exists(), "State file was not lazy-created on init"
    with open(STATE_PATH) as f:
        data = json.load(f)
        assert data == {}, "State file should be empty initially"
    print("[PASS] State file lazy creation")

    # Check 2: Acquire
    print(">>> Acquiring ADMIN...")
    user = lease.acquire("ADMIN")
    assert user is not None
    assert user['email'] == "admin1@test.com" # Assuming default config
    
    # Verify State File Content
    with open(STATE_PATH) as f:
        state = json.load(f)
        assert "admin1@test.com" in state
        assert state["admin1@test.com"] == "worker_test_mech"
    print("[PASS] Acquisition correctly updated state file")

    # Check 3: Release
    print(">>> Releasing...")
    lease.release()
    
    # Verify State File Cleared
    with open(STATE_PATH) as f:
        state = json.load(f)
        assert "admin1@test.com" not in state
    print("[PASS] Release correctly cleared state file")

    print(">>> ALL CHECKS PASSED")

if __name__ == "__main__":
    try:
        test_user_lease_mechanics()
    except AssertionError as e:
        print(f"!!! VERIFICATION FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"!!! ERROR: {e}")
        exit(1)
