
import pytest
from lib.seed import SEED_ITEMS

def test_api_fixtures_functional(admin_actor, editor_actor):
    """
    Verify that API actors (fixtures) are correctly initialized and can make authenticated calls.
    """
    # Verify Admin
    print("\n[Verify] Checking Admin API Actor...")
    admin_api = admin_actor['api']
    resp = admin_api.get('/auth/me')
    assert resp.status_code == 200, f"Admin API failed: {resp.status_code}"
    # API returns: {"status": "success", "data": {...}}
    data = resp.json()
    user_data = data.get('data', {})
    assert user_data.get('email') == admin_actor['user']['email']
    print("[Verify] ✅ Admin API working.")

    # Verify Editor
    print("\n[Verify] Checking Editor API Actor...")
    editor_api = editor_actor['api']
    resp = editor_api.get('/auth/me')
    assert resp.status_code == 200, f"Editor API failed: {resp.status_code}"
    print("[Verify] ✅ Editor API working.")


def test_seed_data_presence(setup_api_seed_data, editor_actor):
    """
    Verify that Global Seed Data (autouse fixture) has correctly populated the database.
    Checks visibility for Editor.
    """
    print("\n[Verify] Checking Global Seed Data...")
    api = editor_actor['api']
    
    # Check item count
    resp = api.get('/items')
    assert resp.status_code == 200
    data = resp.json()
    items = data.get('items', [])
    total = data.get('pagination', {}).get('total', 0)
    
    # We expect at least SEED_ITEMS count (11)
    seed_count = len(SEED_ITEMS)
    assert total >= seed_count, f"Expected at least {seed_count} items, found {total}"
    
    # Verify specific seed item exists
    found_alpha = any('Seed Item Alpha' in item['name'] for item in items)
    assert found_alpha, "Seed Item Alpha not found in Editor view"
    
    print(f"[Verify] ✅ Seed Data Check: Found {total} items. 'Seed Item Alpha' visible.")


def test_cleanup_mechanism(admin_actor):
    """
    Verify that cleanup logic (creating and deleting an item) works as expected.
    """
    print("\n[Verify] Testing Cleanup Mechanism...")
    api = admin_actor['api']
    
    # 1. Create User-Specific Ephemeral Item
    import uuid
    unique_id = uuid.uuid4().hex[:8]
    payload = {
        "name": f"Ephemeral Cleanup Test Item {unique_id}",
        "description": "To be deleted - comprehensive test description for cleanup verification",
        "item_type": "PHYSICAL",
        "price": 10.0,
        "category": "Testing",
        "weight": 1.0, 
        "dimensions": {"length":1, "width":1, "height":1}
    }
    resp = api.post('/items', json=payload)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text[:200]}"
    item_id = resp.json()['data']['_id']
    print(f"[Verify] Created item {item_id}")
    
    # 2. Verify Existence
    resp_check = api.get(f'/items/{item_id}')
    assert resp_check.status_code == 200
    
    # 3. Perform Cleanup (Delete)
    resp_del = api.delete(f'/items/{item_id}')
    assert resp_del.status_code == 200 or resp_del.status_code == 204
    print(f"[Verify] Deleted item {item_id}")
    
    # 4. Verify Gone (soft delete - item should be inactive)
    resp_gone = api.get(f'/items/{item_id}')
    if resp_gone.status_code == 404:
        print("[Verify] ✅ Cleanup confirmed: Item gone (404).")
    elif resp_gone.status_code == 200:
        item_data = resp_gone.json().get('data', {})
        assert item_data.get('is_active') is False, "Item should be inactive after delete"
        print("[Verify] ✅ Cleanup confirmed: Item is inactive (soft delete).")
    else:
        raise AssertionError(f"Unexpected status code: {resp_gone.status_code}")

def test_on_off_switch_configuration(request):
    """
    Verify 'seed_fixtures' plugin registration.
    """
    print("\n[Verify] Checking Seeding Switch (Configuration)...")
    plugin_manager = request.config.pluginmanager
    
    has_seed_plugin = plugin_manager.hasplugin("tests.plugins.seed_fixtures")
    assert has_seed_plugin, "Seed fixtures plugin NOT registered"
    
    print(f"[Verify] ✅ Seed Plugin Active: {has_seed_plugin}")
