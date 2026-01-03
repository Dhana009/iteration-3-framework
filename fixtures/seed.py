import pytest
import time

SEED_ITEMS = [
    {
        "name": "Seed Item Alpha",
        "description": "Critical baseline item. Do not delete.",
        "item_type": "DIGITAL",
        "price": 10.00,
        "category": "Software",
        "download_url": "https://example.com/alpha",
        "file_size": 100
    },
    {
        "name": "Seed Item Beta",
        "description": "Critical baseline item. Do not delete.",
        "item_type": "PHYSICAL",
        "price": 20.00,
        "category": "Home",
        "weight": 1.5,
        "dimensions": {"length": 10, "width": 10, "height": 10}
    }
]

def check_and_heal_seed(client, user_id):
    """
    Ensures that the SEED_ITEMS exist for the current user.
    Uses 'Trust But Verify'.
    """
    print(f"[SeedHealer] Verifying baseline data for {user_id}...")
    
    # 1. Fetch Existing (Active Only)
    resp = client.get("/items", params={"limit": 100, "status": "active"})
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to list items: {resp.status_code}")
        
    items = resp.json().get("items", [])
    existing_names = {i['name'] for i in items}
    
    # 2. Check & Heal
    for seed in SEED_ITEMS:
        if seed['name'] not in existing_names:
            print(f"[SeedHealer] Missing '{seed['name']}'. Healing...")
            resp = client.post("/items", json=seed)
            if resp.status_code == 201:
                print(f"[SeedHealer] Created '{seed['name']}'.")
            elif resp.status_code == 409:
                # Conflict -> Likely soft deleted. Find and Activate.
                print(f"[SeedHealer] Conflict for '{seed['name']}'. Attempting reactivation...")
                # Search including inactive
                search_resp = client.get("/items", params={"search": seed['name'], "status": "inactive"})
                candidates = search_resp.json().get('items', [])
                target = next((i for i in candidates if i['name'] == seed['name']), None)
                
                if target:
                    act_resp = client.patch(f"/items/{target['_id']}/activate")
                    if act_resp.status_code == 200:
                        print(f"[SeedHealer] Reactivated '{seed['name']}'.")
                    else:
                        raise RuntimeError(f"Failed to reactivate {seed['name']}: {act_resp.status_code}")
                else:
                    print(f"FAILED to heal {seed['name']}: 409 but not found in inactive list.")
                    raise RuntimeError(f"Seed Healing Failed for {seed['name']}")
            else:
                 print(f"FAILED to heal {seed['name']}: {resp.status_code}")
                 print(resp.text)
                 raise RuntimeError(f"Seed Healing Failed for {seed['name']}")
        else:
            # Optimal: Do nothing
            pass

@pytest.fixture
def ensure_seed_data(auth_context):
    """
    Fixture that guarantees the user has their 'Desk' setup.
    """
    client = auth_context['api']
    user_id = auth_context['user']['_id']
    
    check_and_heal_seed(client, user_id)
    return True
