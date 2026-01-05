"""
Simple E2E Test - API Fixtures Only

Tests API fixtures without seed conflicts:
1. Create test item via API
2. Verify item exists
3. Delete test item via API
4. Verify item deleted
5. Delete all items for viewer1 (cleanup endpoint)
"""

import pytest
import os
import uuid


def test_api_fixtures_e2e(
    create_test_item,
    delete_test_item,
    delete_user_items,
    editor_actor,
    env_config
):
    """
    E2E test for API fixtures only
    """
    
    print("\n" + "="*60)
    print("E2E Test - API Fixtures")
    print("="*60)
    
    api = editor_actor['api']
    
    # Step 1: Create test item via API
    print("\n[Step 1] Creating test item via API...")
    unique_suffix = uuid.uuid4().hex[:6]
    test_item = create_test_item(api, {
        "name": f"API Test Item - {unique_suffix}",
        "description": "Test item created via API fixture for E2E testing",
        "item_type": "DIGITAL",
        "price": 29.99,
        "category": f"Testing {unique_suffix}",
        "download_url": "https://example.com/test.zip",
        "file_size": 512
    })
    
    assert test_item is not None
    assert test_item['name'] == f"API Test Item - {unique_suffix}"
    assert 'test-data' in test_item['tags']
    item_id = test_item['_id']
    print(f"OK Created item: {test_item['name']} (ID: {item_id})")
    
    # Step 2: Verify item exists
    print("\n[Step 2] Verifying item exists...")
    response = api.get(f"/items/{item_id}")
    assert response.status_code == 200
    fetched_item = response.json()['data']
    assert fetched_item['_id'] == item_id
    print(f"OK Item exists: {fetched_item['name']}")
    
    # Step 3: Delete test item
    print("\n[Step 3] Deleting test item...")
    success = delete_test_item(api, item_id)
    assert success
    print(f"OK Deleted item: {item_id}")
    
    # Step 4: Verify item deleted
    print("\n[Step 4] Verifying item deleted...")
    response = api.get(f"/items/{item_id}")
    # After soft delete, item should be 404 or inactive
    if response.status_code == 404:
        print(f"OK Item returns 404 (not found)")
    elif response.status_code == 200:
        item_data = response.json().get('data', {})
        assert item_data.get('is_active') == False, "Item should be inactive after delete"
        print(f"OK Item is inactive")
    else:
        raise AssertionError(f"Unexpected status code: {response.status_code}")
    
    # Step 5: Test cleanup endpoint
    print("\n[Step 5] Testing cleanup endpoint for viewer1...")
    
    result = delete_user_items("viewer1@test.com")
    
    # Result may be True (deleted) or False (no items/user not found)
    print(f"OK Cleanup endpoint called (result: {result})")
    
    print("\n" + "="*60)
    print("PASS All API Fixtures Working")
    print("="*60)
    print("\nVerified:")
    print("  OK Create test item via API")
    print("  OK Verify item exists")
    print("  OK Delete test item via API")
    print("  OK Verify item deleted")
    print("  OK Cleanup endpoint callable")
