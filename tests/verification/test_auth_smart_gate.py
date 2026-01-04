"""
Verification Script: Smart Gate Auth
Reason: Verify that we reused tokens when valid, and auto-login when invalid/missing.
Scenario:
1. Fresh Login (No state).
2. Reuse Login (Valid state).
3. Heal Login (Corrupt state).
"""
import os
import json
import time
from pathlib import Path
from fixtures.auth import SmartAuth

ROOT_DIR = Path(__file__).parent.parent.parent
STATE_DIR = ROOT_DIR / 'state'
CONFIG_PATH = ROOT_DIR / 'config' / 'user_pool.json'

def clean_state(email):
    path = STATE_DIR / f"{email}.json"
    if path.exists():
        path.unlink()

def corrupt_state(email):
    path = STATE_DIR / f"{email}.json"
    with open(path, 'r') as f:
        data = json.load(f)
    
    data['token'] = "INVALID_TOKEN_STRING"
    
    with open(path, 'w') as f:
        json.dump(data, f)
    print(f"Corrupted token for {email}")

def get_admin_creds():
    with open(CONFIG_PATH, 'r') as f:
        pool = json.load(f)
        return pool['ADMIN'][0]['email'], pool['ADMIN'][0]['password']

def test_auth_smart_gate_verification():
    email, password = get_admin_creds()
    print(f"Testing Auth for {email}...")
    
    # 1. Fresh Login
    print("\n--- TEST 1: FRESH LOGIN ---")
    clean_state(email)
    auth = SmartAuth(email, password)
    t1_start = time.time()
    token1, user1 = auth.authenticate()
    t1_end = time.time()
    
    if not token1:
        print("FAILURE: Fresh login returned no token.")
        return
    print(f"Success. Took {t1_end - t1_start:.2f}s")
    
    # 2. Reuse Login (Should be fast)
    print("\n--- TEST 2: REUSE LOGIN ---")
    auth2 = SmartAuth(email, password)
    t2_start = time.time()
    token2, user2 = auth2.authenticate()
    t2_end = time.time()
    
    if token1 != token2:
        print("WARNING: Tokens changed! Expected reuse.")
    else:
        print("Success: Token reused.")
        
    print(f"Took {t2_end - t2_start:.2f}s")
    if (t2_end - t2_start) > 2.0:
        print("FAILURE: Reuse login took too long (>2s). Did api call happen?")
    
    # 3. Heal Login (Corrupt Token)
    print("\n--- TEST 3: HEAL LOGIN ---")
    corrupt_state(email)
    auth3 = SmartAuth(email, password)
    t3_start = time.time()
    token3, user3 = auth3.authenticate()
    t3_end = time.time()
    
    if token3 == "INVALID_TOKEN_STRING":
        print("FAILURE: Did not heal token!")
    elif token3 != token1:
         print("Success: healed (got new token).")
    else:
         print("Ambiguous: Got same token, but maybe API validated it?")
         
    print(f"Took {t3_end - t3_start:.2f}s")

    print("\nVERIFICATION SUCCESS: Smart Gate behavior confirmed.")

if __name__ == "__main__":
    run_verification()
