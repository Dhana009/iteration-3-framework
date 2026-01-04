"""
Verification Script: Seed Healing
Reason: Verify that if we delete a seed item, the system automatically put it back.
"""
import os
import sys
import time
from pathlib import Path
from fixtures.auth import SmartAuth
from fixtures.seed import check_and_heal_seed, SEED_ITEMS
from utils.api_client import APIClient
import json

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = ROOT_DIR / 'config' / 'user_pool.json'

def get_admin_creds():
    with open(CONFIG_PATH, 'r') as f:
        pool = json.load(f)
        return pool['ADMIN'][0]['email'], pool['ADMIN'][0]['password']

def test_seed_healing_verification():
    email, password = get_admin_creds()
    print(f"Testing Seed Healer for {email}...")
    
    # 1. Login
    auth = SmartAuth(email, password)
    token, user = auth.authenticate()
    client = APIClient(token=token)
    user_id = user['_id']
    
    # 2. Ensure Initial State (Heal)
    print("\n--- STEP 1: INITIAL HEAL ---")
    check_and_heal_seed(client, user_id)
    
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
         # Note: Soft delete means it might still be there but inactive. 
         # API might return it. 
         # Our Seed Logic checks 'existing_names' from list.
         # List endpoint usually filters inactive properly or likely returns them.
         # Let's check if the Healer ignores deleted items or not.
         print("Warning: Item might still be visible (Soft Delete).")
    
    # 5. Heal Again
    print("\n--- STEP 3: RE-HEAL ---")
    check_and_heal_seed(client, user_id)
    
    # 6. Verify Restoration
    resp = client.get("/items", params={"search": "Seed Item Alpha"})
    items = resp.json().get('items', [])
    # We might have duplicates if soft deleted items are ignored by list but exist in DB?
    # Or simple name match.
    # We look for ACTIVE item.
    active_target = next((i for i in items if i['name'] == "Seed Item Alpha" and i.get('is_active') != False), None)

    if active_target:
        print(f"VERIFICATION SUCCESS: Item restored with ID {active_target['_id']}")
        if active_target['_id'] != target['_id']:
            print("(Confirmed it is a NEW item, as expected)")
    else:
        print("FAILURE: Item was not restored.")

if __name__ == "__main__":
    run_verification()
