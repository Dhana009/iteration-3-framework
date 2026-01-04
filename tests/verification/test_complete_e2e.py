"""
Complete End-to-End Test

Flow:
1. Global seed setup (automatic for 5 users)
2. Verify editor has seed data
3. Create test item via API
4. Verify item exists
5. Delete test item via API
6. Verify item deleted
"""

import pytest


def test_complete_e2e_workflow(
    create_test_item,
    delete_test_item,
    editor_actor
):
    """
    Complete E2E test of seed data and API fixtures
    
    Tests:
    - Global seed setup (automatic)
    - Editor has seed data
    - Create item via API
    - Delete item via API
    """
    
    print("\n" + "="*60)
    print("COMPLETE E2E TEST")
    print("="*60)
    
    api = editor_actor['api']
    
    # Step 1: Verify global seed was created (automatic)
    print("\n[Step 1] Verifying global seed setup...")
    response = api.get('/items')
    assert response.status_code == 200
    
    items = response.json()['data']['items']
    seed_items = [i for i in items if 'seed' in i.get('tags', [])]
    
    print(f"OK Editor has {len(items)} total items")
    print(f"OK Editor has {len(seed_items)} seed items")
    assert len(seed_items) >= 11, "Editor should have at least 11 seed items"
    
    # Step 2: Create test item via API
    print("\n[Step 2] Creating test item via API...")
    test_item = create_test_item(api, {
        "name": "Complete E2E Test Item",
        "description": "This item tests the complete end-to-end workflow",
        "item_type": "DIGITAL",
        "price": 99.99,
        "category": "Testing",
        "download_url": "https://example.com/e2e.zip",
        "file_size": 2048
    })
    
    assert test_item is not None
    assert test_item['name'] == "Complete E2E Test Item"
    assert 'test-data' in test_item['tags']
    item_id = test_item['_id']
    print(f"OK Created: {test_item['name']}")
    print(f"OK Item ID: {item_id}")
    
    # Step 3: Verify item exists
    print("\n[Step 3] Verifying item exists...")
    response = api.get(f"/items/{item_id}")
    assert response.status_code == 200
    
    fetched = response.json()['data']
    assert fetched['_id'] == item_id
    assert fetched['name'] == "Complete E2E Test Item"
    print(f"OK Item verified: {fetched['name']}")
    
    # Step 4: Delete test item
    print("\n[Step 4] Deleting test item...")
    success = delete_test_item(api, item_id)
    assert success
    print(f"OK Deleted: {item_id}")
    
    # Step 5: Verify item deleted
    print("\n[Step 5] Verifying item deleted...")
    response = api.get(f"/items/{item_id}")
    
    if response.status_code == 404:
        print(f"OK Item returns 404 (deleted)")
    elif response.status_code == 200:
        item_data = response.json()['data']
        assert item_data.get('is_active') == False
        print(f"OK Item is inactive (soft deleted)")
    else:
        raise AssertionError(f"Unexpected status: {response.status_code}")
    
    print("\n" + "="*60)
    print("PASS - COMPLETE E2E TEST PASSED")
    print("="*60)
    print("\nVerified:")
    print("  OK Global seed setup (5 users)")
    print("  OK Editor has seed data (11+ items)")
    print("  OK Create item via API")
    print("  OK Verify item exists")
    print("  OK Delete item via API")
    print("  OK Verify item deleted")
    print("\nAll fixtures working correctly!")
