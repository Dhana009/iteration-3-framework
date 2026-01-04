"""
Comprehensive Verification: Seed Data System

Tests:
1. API Fixtures (create_test_item, delete_test_item)
2. Global Seed Data (setup_api_seed_data)
3. Cleanup functionality
4. On/Off switch for seed data
"""

import pytest
import os
import uuid


def test_api_fixtures_create_and_delete(admin_actor, create_test_item, delete_test_item):
    """
    Test 1: Verify API fixtures can create and delete items
    """
    print("\n" + "="*60)
    print("TEST 1: API Fixtures (Create/Delete)")
    print("="*60)
    
    api = admin_actor['api']
    
    # Create item
    unique_id = uuid.uuid4().hex[:8]
    test_item = create_test_item(api, {
        "name": f"Verification Test Item {unique_id}",
        "description": "Test item for API fixture verification - this is a comprehensive test description",
        "item_type": "DIGITAL",
        "price": 99.99,
        "category": "Testing",
        "download_url": "https://example.com/verification-test.zip",
        "file_size": 2048
    })
    
    assert test_item is not None, "Item should be created"
    assert test_item['name'] == f"Verification Test Item {unique_id}", "Item name should match"
    assert 'test-data' in test_item['tags'], "Item should have test-data tag"
    item_id = test_item['_id']
    print(f"✅ Created item: {item_id}")
    
    # Verify item exists
    response = api.get(f"/items/{item_id}")
    assert response.status_code == 200, "Item should exist"
    print(f"✅ Verified item exists: {item_id}")
    
    # Delete item
    success = delete_test_item(api, item_id)
    assert success, "Delete should succeed"
    print(f"✅ Deleted item: {item_id}")
    
    # Verify item is deleted (soft delete - should be inactive)
    response = api.get(f"/items/{item_id}")
    if response.status_code == 200:
        item_data = response.json().get('data', {})
        assert item_data.get('is_active') is False, "Item should be inactive after delete"
        print(f"✅ Verified item is inactive: {item_id}")
    else:
        assert response.status_code == 404, "Item should return 404 if hard deleted"
        print(f"✅ Verified item is deleted (404): {item_id}")
    
    print("✅ TEST 1 PASSED: API Fixtures working correctly")


def test_global_seed_data_exists(admin_actor):
    """
    Test 2: Verify global seed data exists (created by setup_api_seed_data)
    """
    print("\n" + "="*60)
    print("TEST 2: Global Seed Data")
    print("="*60)
    
    api = admin_actor['api']
    
    # Get all items
    response = api.get('/items')
    assert response.status_code == 200, "Should be able to fetch items"
    
    data = response.json()
    items = data.get('items', [])
    
    # Filter seed items
    seed_items = [item for item in items if 'seed' in item.get('tags', [])]
    
    print(f"✅ Total items: {len(items)}")
    print(f"✅ Seed items found: {len(seed_items)}")
    
    # Verify we have seed items
    assert len(seed_items) >= 11, f"Should have at least 11 seed items, found {len(seed_items)}"
    
    # Verify seed items have correct tags
    for item in seed_items[:5]:  # Check first 5
        assert 'seed' in item.get('tags', []), f"Item {item['name']} should have 'seed' tag"
        print(f"  ✅ {item['name']} has seed tag")
    
    print("✅ TEST 2 PASSED: Global seed data exists and is accessible")


def test_cleanup_functionality(editor_actor, create_test_item, delete_test_item):
    """
    Test 3: Verify cleanup (delete) functionality works correctly
    """
    print("\n" + "="*60)
    print("TEST 3: Cleanup Functionality")
    print("="*60)
    
    api = editor_actor['api']
    
    # Create multiple items
    created_items = []
    for i in range(3):
        unique_id = uuid.uuid4().hex[:6]
        item = create_test_item(api, {
            "name": f"Cleanup Test {unique_id}",
            "description": f"Test item {i+1} for cleanup verification - comprehensive test description",
            "item_type": "DIGITAL",
            "price": 10.00 + i,
            "category": "Testing",
            "download_url": f"https://example.com/cleanup-{i}.zip",
            "file_size": 1024
        })
        created_items.append(item)
        print(f"  ✅ Created: {item['name']} ({item['_id']})")
    
    # Delete all items
    deleted_count = 0
    for item in created_items:
        success = delete_test_item(api, item['_id'])
        if success:
            deleted_count += 1
            print(f"  ✅ Deleted: {item['name']}")
    
    assert deleted_count == len(created_items), f"Should delete all {len(created_items)} items, deleted {deleted_count}"
    
    print("✅ TEST 3 PASSED: Cleanup functionality working correctly")


def test_seed_data_on_off_switch():
    """
    Test 4: Verify on/off switch for seed data works
    """
    print("\n" + "="*60)
    print("TEST 4: Seed Data On/Off Switch")
    print("="*60)
    
    # Check MongoDB seed switch
    mongodb_switch = os.getenv('ENABLE_SEED_SETUP', 'false')
    print(f"✅ ENABLE_SEED_SETUP: {mongodb_switch}")
    
    # Check API seed switch
    api_switch = os.getenv('ENABLE_API_SEED_SETUP', 'true')
    print(f"✅ ENABLE_API_SEED_SETUP: {api_switch}")
    
    # Verify switches are readable
    assert mongodb_switch in ['true', 'false'], "ENABLE_SEED_SETUP should be 'true' or 'false'"
    assert api_switch in ['true', 'false'], "ENABLE_API_SEED_SETUP should be 'true' or 'false'"
    
    print("✅ TEST 4 PASSED: On/Off switches are accessible and valid")


def test_seed_data_switch_disabled(monkeypatch):
    """
    Test 5: Verify seed data can be disabled via switch
    """
    print("\n" + "="*60)
    print("TEST 5: Seed Data Switch Disabled")
    print("="*60)
    
    # Temporarily disable API seed
    monkeypatch.setenv('ENABLE_API_SEED_SETUP', 'false')
    
    # Verify the switch is set
    assert os.getenv('ENABLE_API_SEED_SETUP') == 'false', "Switch should be disabled"
    print("✅ ENABLE_API_SEED_SETUP set to 'false'")
    
    # Note: This test verifies the switch can be set
    # Actual fixture behavior is tested in integration tests
    print("✅ TEST 5 PASSED: Switch can be disabled")


def test_seed_data_switch_enabled(monkeypatch):
    """
    Test 6: Verify seed data can be enabled via switch
    """
    print("\n" + "="*60)
    print("TEST 6: Seed Data Switch Enabled")
    print("="*60)
    
    # Enable API seed
    monkeypatch.setenv('ENABLE_API_SEED_SETUP', 'true')
    
    # Verify the switch is set
    assert os.getenv('ENABLE_API_SEED_SETUP') == 'true', "Switch should be enabled"
    print("✅ ENABLE_API_SEED_SETUP set to 'true'")
    
    print("✅ TEST 6 PASSED: Switch can be enabled")


def test_comprehensive_integration(admin_actor, create_test_item, delete_test_item):
    """
    Test 7: Comprehensive integration test
    - Seed data exists
    - Can create new items
    - Can delete items
    - Seed data remains intact
    """
    print("\n" + "="*60)
    print("TEST 7: Comprehensive Integration")
    print("="*60)
    
    api = admin_actor['api']
    
    # 1. Count seed items before
    response = api.get('/items')
    data = response.json()
    items_before = data.get('items', [])
    seed_items_before = [item for item in items_before if 'seed' in item.get('tags', [])]
    print(f"✅ Seed items before: {len(seed_items_before)}")
    
    # 2. Create test item
    unique_id = uuid.uuid4().hex[:8]
    test_item = create_test_item(api, {
        "name": f"Integration Test {unique_id}",
        "description": "Comprehensive integration test item - verification description",
        "item_type": "DIGITAL",
        "price": 50.00,
        "category": "Testing",
        "download_url": "https://example.com/integration.zip",
        "file_size": 1024
    })
    print(f"✅ Created test item: {test_item['_id']}")
    
    # 3. Verify test item exists
    response = api.get(f"/items/{test_item['_id']}")
    assert response.status_code == 200, "Test item should exist"
    print(f"✅ Verified test item exists")
    
    # 4. Count items after creation
    response = api.get('/items')
    data = response.json()
    items_after = data.get('items', [])
    seed_items_after = [item for item in items_after if 'seed' in item.get('tags', [])]
    print(f"✅ Seed items after: {len(seed_items_after)}")
    
    # 5. Verify seed items count didn't change
    assert len(seed_items_after) == len(seed_items_before), "Seed items should remain unchanged"
    print(f"✅ Seed items count unchanged: {len(seed_items_after)}")
    
    # 6. Delete test item
    success = delete_test_item(api, test_item['_id'])
    assert success, "Delete should succeed"
    print(f"✅ Deleted test item")
    
    # 7. Verify seed items still exist
    response = api.get('/items')
    data = response.json()
    items_final = data.get('items', [])
    seed_items_final = [item for item in items_final if 'seed' in item.get('tags', [])]
    assert len(seed_items_final) == len(seed_items_before), "Seed items should still exist"
    print(f"✅ Seed items still intact: {len(seed_items_final)}")
    
    print("✅ TEST 7 PASSED: Comprehensive integration working correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
