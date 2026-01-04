"""
Verification Script: Capacity Limit
Reason: Verify that we CRASH immediately when the user pool is exhausted.
Scenario:
- Pool has 1 ADMIN.
- We spawn 2 workers requesting ADMIN.
- Expected: 1 Success, 1 Failure (RuntimeError).
"""
import sys
import sys
import os
import json
import multiprocessing
import time
from pathlib import Path
from fixtures.users import UserLease

# Setup Paths
ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = ROOT_DIR / 'config' / 'user_pool.json'

def run_worker(worker_id, should_fail=False):
    lease = UserLease(worker_id=f"worker_{worker_id}")
    try:
        user = lease.acquire("ADMIN")
        time.sleep(2) # Hold it
        lease.release()
        return "SUCCESS"
    except RuntimeError as e:
        return f"FAILED: {e}"
    except Exception as e:
        return f"ERROR: {e}"

def test_capacity_limit_verification():
    # 1. Modify User Pool to only have 1 ADMIN for this test
    print("Setting up constrained user pool...")
    original_pool = None
    with open(CONFIG_PATH, 'r') as f:
        original_pool = json.load(f)
        
    test_pool = original_pool.copy()
    test_pool["ADMIN"] = [test_pool["ADMIN"][0]] # Keep only 1
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(test_pool, f)
        
    try:
        # 2. Spawn 2 processes
        with multiprocessing.Pool(processes=2) as pool:
            results = pool.map(run_worker, [1, 2])
            
        print("Results:", results)
        
        # 3. Validate
        successes = [r for r in results if r == "SUCCESS"]
        failures = [r for r in results if "INFRASTRUCTURE_ERROR" in r]
        
        if len(successes) == 1 and len(failures) == 1:
            print("VERIFICATION SUCCESS: System failed fast on pool exhaustion.")
        else:
            print("VERIFICATION FAILURE: Did not see expected 1 Success + 1 Failure.")
            
    finally:
        # Restore Config
        with open(CONFIG_PATH, 'w') as f:
            json.dump(original_pool, f, indent=4)
        # Clear locks if needed (handled by logic)

if __name__ == "__main__":
    run_verification()
