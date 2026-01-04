"""
Editor Test with New Fixtures

Tests:
1. Setup seed data for editor
2. Verify seed data exists
3. Create item via API
4. Delete item via API
"""

import pytest


def test_editor_seed_setup(create_seed_for_user, editor_actor):
    """
    Test: Setup seed data for editor and verify
    """
    print("\n[Test] Setting up seed data for editor1...")
    
    # Note: Seed may already exist from global setup
    # This tests the fixture can be called for specific user
    try:
        count = create_seed_for_user("editor1@test.com")
        print(f"OK Created {count} seed items for editor1")
    except Exception as e:
        print(f"INFO Seed already exists: {e}")
    
    # Verify editor has seed items
    api = editor_actor['api']
    response = api.get('/items')
    assert response.status_code == 200
    
    response_data = response.json()
    
    # Handle different response structures
    if 'data' in response_data:
        items = response_data['data']['items']
    else:
        # Direct items array
        items = response_data.get('items', [])
    
    seed_items = [i for i in items if 'seed' in i.get('tags', [])]
    
    print(f"OK Editor has {len(items)} total items")
    print(f"OK Editor has {len(seed_items)} seed items")
    assert len(seed_items) >= 11, "Editor should have at least 11 seed items"


def test_editor_create_and_delete_with_fixtures(
    create_test_item,
    delete_test_item,
    editor_actor
):
    """
    Test: Create and delete item using new fixtures
    """
    api = editor_actor['api']
    
    print("\n[Test] Creating item via fixture...")
    
    # Create item
    item = create_test_item(api, {
        "name": "Editor Test Item",
        "description": "Item created by editor using new fixture",
        "item_type": "DIGITAL",
        "price": 49.99,
        "category": "Testing",
        "download_url": "https://example.com/editor-test.zip",
        "file_size": 1024
    })
    
    assert item is not None
    assert item['name'] == "Editor Test Item"
    assert 'test-data' in item['tags']
    item_id = item['_id']
    print(f"OK Created item: {item['name']} (ID: {item_id})")
    
    # Verify item exists
    print("\n[Test] Verifying item exists...")
    response = api.get(f"/items/{item_id}")
    assert response.status_code == 200
    fetched = response.json()['data']
    assert fetched['_id'] == item_id
    print(f"OK Item verified: {fetched['name']}")
    
    # Delete item
    print("\n[Test] Deleting item via fixture...")
    success = delete_test_item(api, item_id)
    assert success
    print(f"OK Item deleted: {item_id}")
    
    # Verify deletion
    print("\n[Test] Verifying deletion...")
    response = api.get(f"/items/{item_id}")
    
    if response.status_code == 404:
        print(f"OK Item returns 404 (deleted)")
    elif response.status_code == 200:
        item_data = response.json()['data']
        assert item_data.get('is_active') == False
        print(f"OK Item is inactive (soft deleted)")
    
    print("\nPASS All fixture operations successful!")
