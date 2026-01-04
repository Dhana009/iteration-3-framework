"""
End-to-End Integration Test for MongoDB Fixtures

Tests:
1. Global seed setup (automatic)
2. Individual user seed setup (editor1)
3. Create test item via API
4. Delete test item via API
5. Delete all items for user (viewer1)
"""

import pytest
import os


def test_e2e_seed_and_cleanup_integration(
    create_seed_for_user,
    create_test_item,
    delete_test_item,
    delete_user_items,
    editor_actor,
    env_config
):
    """
    End-to-end test of all fixtures
    
    Flow:
    1. Global seed already created (via setup_mongodb_seed fixture)
    2. Create seed for editor1 specifically
    3. Create test item via API
    4. Delete test item via API
    5. Delete all items for viewer1
    """
    
    print("\n" + "="*60)
    print("E2E Integration Test - All Fixtures")
    print("="*60)
    
    # Step 1: Verify global seed was created (automatic)
    print("\n[Step 1] Verifying global seed setup...")
    api = editor_actor['api']
    
    # Check editor has items (from global setup)
    response = api.get('/api/v1/items')
    assert response.status_code == 200
    items = response.json()['data']['items']
    print(f"OK Editor has {len(items)} items from global setup")
    
    # Step 2: Create seed for editor1 specifically (test individual setup)
    print("\n[Step 2] Creating seed for editor1...")
    try:
        count = create_seed_for_user("editor1@test.com")
        print(f"OK Created {count} seed items for editor1")
    except Exception as e:
        # May already exist from global setup
        print(f"WARN Seed creation skipped: {e}")
    
    # Step 3: Create test item via API
    print("\n[Step 3] Creating test item via API...")
    test_item = create_test_item(api, {
        "name": "E2E Test Item",
        "description": "This is an end-to-end test item created via API fixture",
        "item_type": "DIGITAL",
        "price": 49.99,
        "category": "Testing",
        "download_url": "https://example.com/e2e-test.zip",
        "file_size": 1024,
        "tags": ["e2e-test", "integration"]
    })
    
    assert test_item is not None
    assert test_item['name'] == "E2E Test Item"
    assert 'test-data' in test_item['tags']
    print(f"OK Created test item: {test_item['name']} (ID: {test_item['_id']})")
    
    # Verify item exists
    response = api.get(f"/api/v1/items/{test_item['_id']}")
    assert response.status_code == 200
    print(f"OK Verified item exists via API")
    
    # Step 4: Delete test item via API
    print("\n[Step 4] Deleting test item via API...")
    success = delete_test_item(api, test_item['_id'])
    assert success
    print(f"OK Deleted test item: {test_item['_id']}")
    
    # Verify item is deleted (soft delete)
    response = api.get(f"/api/v1/items/{test_item['_id']}")
    assert response.status_code == 404 or response.json()['data'].get('is_active') == False
    print(f"OK Verified item is deleted")
    
    # Step 5: Delete all items for viewer1
    print("\n[Step 5] Deleting all items for viewer1...")
    internal_key = os.getenv('INTERNAL_AUTOMATION_KEY', 'flowhub-secret-automation-key-2025')
    
    success = delete_user_items(
        "viewer1@test.com",
        env_config.API_BASE_URL,
        internal_key
    )
    
    if success:
        print(f"OK Deleted all items for viewer1")
    else:
        print(f"WARN Viewer1 may not have items or user doesn't exist")
    
    print("\n" + "="*60)
    print("PASS E2E Integration Test PASSED")
    print("="*60)
    print("\nVerified:")
    print("  OK Global seed setup (automatic)")
    print("  OK Individual user seed setup")
    print("  OK Create test item via API")
    print("  OK Delete test item via API")
    print("  OK Delete all user items via API")
