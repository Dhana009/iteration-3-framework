"""
Verification Script: Seed Healing
Reason: Verify that if we delete a seed item, the system automatically put it back.
"""
import os
import sys
import json
from pathlib import Path
from lib.auth import SmartAuth
from lib.seed import SEED_ITEMS
from utils.api_client import APIClient
from utils.config import ProductionConfig # Default to prod for standalone check

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = ROOT_DIR / 'config' / 'user_pool.json'

def get_admin_creds():
    with open(CONFIG_PATH, 'r') as f:
        pool = json.load(f)
        return pool['ADMIN'][0]['email'], pool['ADMIN'][0]['password']

def test_seed_healing_verification():
    email, password = get_admin_creds()
    print(f"Testing Seed Healer for {email}...")
    
    base_url = ProductionConfig.API_BASE_URL
    
    # 1. Login
    auth = SmartAuth(email, password, base_url)
    token, user = auth.authenticate()
    client = APIClient(base_url, token=token)
    user_id = user['_id']
    
    # 2. Ensure Initial State (Heal)
    print("\n--- STEP 1: INITIAL HEAL ---")
    # check_and_heal_seed(client, user_id)
    print("NOTE: Seed healing disabled (handled by MongoDB fixtures)")
    
    # 3. Verify Existence
    resp = client.get("/items", params={"search": "Seed Item Alpha"})
    items = resp.json().get('items', [])
    target = next((i for i in items if i['name'] == "Seed Item Alpha"), None)
    
    if not target:
        print("FAILURE: Initial heal failed. Item not found.")
        return
        
    print("Initial state verified.")
    
    # 4. Destructive Action (Simulate Data Loss)
    print("\n--- STEP 2: SABOTAGE (DELETE ITEM) ---")
    print(f"Deleting {target['_id']}...")
    del_resp = client.delete(f"/items/{target['_id']}")
    if del_resp.status_code != 200:
        print(f"Failed to delete: {del_resp.status_code}")
        return
        
    # Verify it's gone
    resp = client.get(f"/items/{target['_id']}")
    if resp.status_code != 404 and not resp.json().get('data', {}).get('deleted_at'):
         print("Warning: Item might still be visible (Soft Delete).")
    
    # 5. Heal Again
    print("\n--- STEP 3: RE-HEAL ---")
    # check_and_heal_seed(client, user_id)
    print("NOTE: Seed healing disabled (handled by MongoDB fixtures)")
    
    # 6. Verify Restoration
    resp = client.get("/items", params={"search": "Seed Item Alpha"})
    items = resp.json().get('items', [])
    active_target = next((i for i in items if i['name'] == "Seed Item Alpha" and i.get('is_active') != False), None)

    if active_target:
        print(f"VERIFICATION SUCCESS: Item restored with ID {active_target['_id']}")
    else:
        print("FAILURE: Item was not restored.")

if __name__ == "__main__":
    test_seed_healing_verification()
