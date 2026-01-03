import sys
import os
import time

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fixtures.users import UserLease
from fixtures.auth import SmartAuth
from fixtures.seed import check_and_heal_seed
from utils.api_client import APIClient

def print_step(step, msg):
    print(f"\n[{step}] {msg}")

def demo_lifecycle():
    print("=== STARTING FRAMEWORK PROOF OF CONCEPT ===")
    
    # 1. LEASING
    print_step("1. LEASING", "Requesting ADMIN user...")
    lease = UserLease("demo_worker")
    try:
        user = lease.acquire("ADMIN")
        print(f"   -> ACQUIRED: {user['email']}")
        
        # 2. AUTHENTICATION
        print_step("2. AUTHENTICATION", "Checking Gate...")
        auth = SmartAuth(user['email'], user['password'])
        t1 = time.time()
        token, auth_user = auth.authenticate()
        t2 = time.time()
        print(f"   -> TOKEN: {token[:10]}... (Took {t2-t1:.2f}s)")
        print(f"   -> USER ID: {auth_user['_id']}")
        
        client = APIClient(token=token)
        
        # 3. SEEDING
        print_step("3. SEEDING", "Checking 'Desk' configuration...")
        check_and_heal_seed(client, auth_user['_id'])
        print("   -> Desk Verified.")
        
        # 4. TEST EXECUTION
        print_step("4. TEST EXECUTION", "Running 'Smoke' Logic...")
        resp = client.post("/items", json={
            "name": f"Demo Item {int(time.time())}",
            "description": "Proof of life",
            "item_type": "DIGITAL",
            "price": 1.00,
            "category": "Software",
            "download_url": "http://demo",
            "file_size": 1
        })
        if resp.status_code == 201:
            print("   -> CREATE: SUCCESS (201)")
            item_id = resp.json()['data']['_id']
            
            # Clean up demo item
            client.delete(f"/items/{item_id}")
            print("   -> CLEANUP: SUCCESS")
        else:
            print(f"   -> CREATE: FAILED {resp.status_code} {resp.text}")

    except Exception as e:
        print(f"!!! CRITICAL FAIL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 5. RELEASE
        print_step("5. RELEASE", "Returning user to pool...")
        lease.release()
        print("   -> RELEASED. Logic Ready for next test.")

if __name__ == "__main__":
    demo_lifecycle()
