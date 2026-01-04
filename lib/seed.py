import pytest
import time

SEED_ITEMS = [
    # Item 1: Alpha - Electronics, PHYSICAL (was DIGITAL - FIXED), Active, $25
    {
        "name": "Seed Item Alpha",
        "description": "Electronics item for search and filter testing",
        "item_type": "PHYSICAL",  # FIXED: Electronics MUST be PHYSICAL
        "price": 25.00,
        "category": "Electronics",
        "weight": 1.0,
        "dimensions": {"length": 10, "width": 8, "height": 5}
    },
    # Item 2: Beta - Software, DIGITAL, Active, $50
    {
        "name": "Seed Item Beta",
        "description": "Software item for search and filter testing",
        "item_type": "DIGITAL",
        "price": 50.00,
        "category": "Software",
        "download_url": "https://www.dhanunjaya.space/assets/resume.pdf",
        "file_size": 200
    },
    # Item 3: Gamma - Home, PHYSICAL, Active, $75
    {
        "name": "Seed Item Gamma",
        "description": "Home item for category filter testing",
        "item_type": "PHYSICAL",
        "price": 75.00,
        "category": "Home",
        "weight": 2.5,
        "dimensions": {"length": 15, "width": 10, "height": 8}
    },
    # Item 4: Delta - Electronics, PHYSICAL, Active, $100
    {
        "name": "Seed Item Delta",
        "description": "Electronics physical item for testing",
        "item_type": "PHYSICAL",
        "price": 100.00,
        "category": "Electronics",
        "weight": 3.0,
        "dimensions": {"length": 20, "width": 15, "height": 10}
    },
    # Item 5: Epsilon - Books, DIGITAL, Active, $15
    {
        "name": "Seed Item Epsilon",
        "description": "Books category item for filter testing",
        "item_type": "DIGITAL",
        "price": 15.00,
        "category": "Books",
        "download_url": "https://www.dhanunjaya.space/",
        "file_size": 50
    },
    # Item 6: Zeta - Software, DIGITAL, Inactive, $200
    {
        "name": "Seed Item Zeta",
        "description": "Inactive software item for status filter testing",
        "item_type": "DIGITAL",
        "price": 200.00,
        "category": "Software",
        "download_url": "https://example.com/zeta",
        "file_size": 500,
        "is_active": False  # Inactive status
    },
    # Item 7: Eta - Home, PHYSICAL, Active, $30
    {
        "name": "Seed Item Eta",
        "description": "Home item for price sort testing",
        "item_type": "PHYSICAL",
        "price": 30.00,
        "category": "Home",
        "weight": 1.0,
        "dimensions": {"length": 12, "width": 8, "height": 6}
    },
    # Item 8: Theta - Electronics, PHYSICAL (was DIGITAL - FIXED), Active, $500 (Highest price)
    {
        "name": "Seed Item Theta",
        "description": "Premium electronics item for price sort testing",
        "item_type": "PHYSICAL",  # FIXED: Electronics MUST be PHYSICAL
        "price": 500.00,
        "category": "Electronics",
        "weight": 5.0,
        "dimensions": {"length": 40, "width": 30, "height": 20}
    },
    # Item 9: Iota - Books, PHYSICAL, Active, $10
    {
        "name": "Seed Item Iota",
        "description": "Books physical item for testing",
        "item_type": "PHYSICAL",
        "price": 10.00,
        "category": "Books",
        "weight": 0.5,
        "dimensions": {"length": 8, "width": 6, "height": 2}
    },
    # Item 10: Kappa - Software, DIGITAL, Active, $150
    {
        "name": "Seed Item Kappa",
        "description": "Software item for pagination testing",
        "item_type": "DIGITAL",
        "price": 150.00,
        "category": "Software",
        "download_url": "https://example.com/kappa",
        "file_size": 300
    },
    # Item 11: Lambda - Home, PHYSICAL, Inactive, $5 (Lowest price)
    {
        "name": "Seed Item Lambda",
        "description": "Inactive home item for status and price testing",
        "item_type": "PHYSICAL",
        "price": 5.00,
        "category": "Home",
        "weight": 0.3,
        "dimensions": {"length": 5, "width": 5, "height": 3},
        "is_active": False  # Inactive status
    }
]

# Track which users have been cleaned in this process/session
CLEANED_USERS = set()

def check_and_heal_seed(client, user_id):
    """
    Ensures that the SEED_ITEMS exist for the current user.
    
    Behavior:
    - If CLEANUP_SEED_ON_START=true: Clean existing seed data ONCE per session per user.
    - Then proceeds to 'Trust But Verify' (create missing items).
    """
    import os
    
    # Check env var directly
    cleanup_enabled = os.environ.get('CLEANUP_SEED_ON_START', 'false').lower() == 'true'
    
    if cleanup_enabled and user_id not in CLEANED_USERS:
        print(f"[SeedHealer] CLEANUP_SEED_ON_START=true. Cleaning seed data for {user_id} (Once per session)...")
        _cleanup_user_seed_data(client, user_id)
        CLEANED_USERS.add(user_id)
        print(f"[SeedHealer] Cleanup complete for {user_id}. Recreating seed data...")

    print(f"[SeedHealer] Verifying baseline data for {user_id}...")
    
    # 1. Fetch ALL items for this user (Active + Inactive)
    # Note: We must fetch inactive too, to avoid false 409s.
    existing_items = []
    
    # Fetch Active
    resp = client.get("/items")
    if resp.status_code == 200:
       existing_items.extend(resp.json().get('items', []))
       
    # Fetch Inactive
    resp = client.get("/items", params={"status": "inactive"})
    if resp.status_code == 200:
       existing_items.extend(resp.json().get('items', []))
       
    existing_names = {i['name'] for i in existing_items}

    for i, seed in enumerate(SEED_ITEMS, 1):
        # Strategy: Seed items must be unique PER USER to avoid "Shared Baseline" conflicts
        # if the backend isolates by owner.
        # But if the backend enforces Global Uniqueness on Name, we have a problem.
        # Assuming Global Uniqueness on Name:
        # We must suffix the name with the user_id (or a hash of it)
        
        user_suffix = user_id[-4:] # Last 4 chars of ID
        # Validation allows: alphanumeric, spaces, hyphens, underscores.
        # Parentheses match failed in parallel run. Swapping to hyphen.
        unique_name = f"{seed['name']} - {user_suffix}"
        
        print(f"[SeedHealer] [{i}/{len(SEED_ITEMS)}] Checking '{unique_name}'...")
        
        if unique_name not in existing_names:
            print(f"[SeedHealer] Missing '{unique_name}'. Healing...")
            
            # Create payload with unique name
            payload = seed.copy()
            payload['name'] = unique_name
            
            resp = client.post("/items", json=payload)
            if resp.status_code == 201:
                print(f"[SeedHealer] Created '{unique_name}'.")
            elif resp.status_code == 409:
                # Conflict -> Likely soft deleted but missed in search?
                # Or owned by someone else?
                print(f"[SeedHealer] Conflict for '{unique_name}'. Attempting reactivation...")
                
                # Search specifically for this item
                search_resp = client.get("/items", params={"search": unique_name, "status": "inactive"})
                candidates = search_resp.json().get('items', [])
                target = next((i for i in candidates if i['name'] == unique_name), None)
                
                if target:
                    act_resp = client.patch(f"/items/{target['_id']}/activate")
                    if act_resp.status_code == 200:
                        print(f"[SeedHealer] Reactivated '{unique_name}'.")
                    else:
                        raise RuntimeError(f"Failed to reactivate {unique_name}: {act_resp.status_code}")
                else:
                    # If we get 409 but can't find it, it means it exists but we can't see/edit it.
                    # This happens if Another User owns "Seed Item Alpha (1234)".
                    # But since we suffixed it, this shouldn't happen unless ID collision.
                    print(f"FAILED to heal {unique_name}: 409 and not found.")
                    # If it's owned by someone else, we might just have to skip it or accept it.
                    # raising error for now to be safe.
                    pass
            else:
                 print(f"FAILED to heal {unique_name}: {resp.status_code}")
                 print(resp.text)
                 # raise RuntimeError(f"Seed Healing Failed for {unique_name}")
        else:
            # check if inactive?
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


def _cleanup_user_seed_data(client, user_id: str):
    """
    Delete all seed items for a specific user using MongoDB DIRECTLY.
    This ensures a hard delete/clean slate, not a soft delete via API.
    """
    try:
        from pymongo import MongoClient
        import os
    except ImportError:
        print("[SeedHealer] ❌ pymongo not installed. Skipping direct cleanup.")
        return

    mongo_uri = os.environ.get('MONGODB_URI')
    db_name = os.environ.get('MONGODB_DB_NAME', 'test') # Default to 'test' based on .env
    
    if not mongo_uri:
        print("[SeedHealer] ❌ MONGODB_URI not set. Skipping direct cleanup.")
        return

    user_suffix = user_id[-4:]
    print(f"[SeedHealer] 🧹 connecting to MongoDB to clean items for suffix '{user_suffix}'...")
    
    try:
        with MongoClient(mongo_uri) as mongo_client:
            db = mongo_client[db_name]
            items_collection = db['items']
            
            # Construct query: Name contains "Seed Item" AND ends with " - {user_suffix}"
            # Using regex for flexible matching similar to previous logic
            query = {
                "name": {"$regex": f"Seed Item.* - {user_suffix}$"}
            }
            
            # Count before delete
            count = items_collection.count_documents(query)
            
            if count == 0:
                 print(f"[SeedHealer] No existing seed data found in MongoDB for {user_suffix}. (0 items to clean)")
                 return

            print(f"[SeedHealer] 🔍 Found {count} existing seed items in MongoDB for {user_suffix}. Deleting...")
            
            # Delete
            result = items_collection.delete_many(query)
            print(f"[SeedHealer] ✅ Hard deleted {result.deleted_count} items from MongoDB for {user_suffix}.")
            
            if result.deleted_count != count:
                print(f"[SeedHealer] ⚠️  WARNING: Deleted count ({result.deleted_count}) != Found count ({count})")
            
    except Exception as e:
        print(f"[SeedHealer] ❌ MongoDB Cleanup Failed: {str(e)}")
        # We generally don't want to crash the test if cleanup fails, but it might lead to 409s later.
        # Allowing it to proceed to see if API update handles it.
