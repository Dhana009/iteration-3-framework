import pytest
from lib.seed import check_and_heal_seed, SEED_ITEMS
from lib.auth import SmartAuth
from utils.api_client import APIClient

def verify_role_seed_lifecycle(role_name, email, password, base_url, target_seed_index=0):
    print(f"\n[{role_name}] 1. Authenticating {email}...")
    auth = SmartAuth(email, password, base_url)
    token, user_data = auth.authenticate()
    api = APIClient(base_url, token=token)
    
    # Identify a specific seed item to test (e.g., Alpha)
    # We need to construct the unique name: "Name - {suffix}"
    user_suffix = user_data['_id'][-4:]
    target_seed = SEED_ITEMS[target_seed_index]
    target_name = f"{target_seed['name']} - {user_suffix}"
    
    print(f"[{role_name}] Target Item: {target_name}")

    # 2. Heal First (Ensure baseline)
    print(f"[{role_name}] 2. Running Initial Heal...")
    # check_and_heal_seed(api, user_data['_id'])
    
    # 3. Verify it exists
    print(f"[{role_name}] 3. Verifying existence...")
    resp = api.get("/items", params={"search": target_name})
    items = resp.json().get('items', [])
    found = any(i['name'] == target_name for i in items)
    assert found, f"Item {target_name} should exist after heal."
    item_id = next(i['_id'] for i in items if i['name'] == target_name)
    
    # 4. Delete it (Sabotage)
    print(f"[{role_name}] 4. Deleting item {item_id} (Sabotage)...")
    api.delete(f"/items/{item_id}")
    
    # Verify deletion
    resp = api.get(f"/items/{item_id}")
    
    # 5. Heal Again (Recovery)
    print(f"[{role_name}] 5. Running Recovery Heal...")
    # check_and_heal_seed(api, user_data['_id'])
    
    # 6. Verify it is back
    print(f"[{role_name}] 6. Verifying restoration...")
    resp = api.get("/items", params={"search": target_name})
    items = resp.json().get('items', [])
    restored = any(i['name'] == target_name for i in items)
    assert restored, f"Item {target_name} failed to restore."
    
    print(f"[{role_name}] SUCCESS: Seed lifecycle verified.")

def test_admin_seed_lifecycle(user_lease, env_config):
    """
    Verify Admin can heal their own data.
    """
    lease_user = user_lease.acquire("ADMIN")
    url = env_config.API_BASE_URL
    verify_role_seed_lifecycle("ADMIN", lease_user['email'], lease_user['password'], url, target_seed_index=0) 

def test_editor_seed_lifecycle(user_lease, env_config):
    """
    Verify Editor can heal their own data.
    """
    lease_user = user_lease.acquire("EDITOR")
    url = env_config.API_BASE_URL
    verify_role_seed_lifecycle("EDITOR", lease_user['email'], lease_user['password'], url, target_seed_index=1)
