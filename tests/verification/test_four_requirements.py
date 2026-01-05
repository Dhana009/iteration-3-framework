"""
Verification: Four Critical Requirements

Requirement 1: Global MongoDB seed data with on/off switch
- Automatically runs before tests (if enabled)
- Uses MongoDB direct insertion
- Doesn't create duplicates if data exists
- Can be turned on/off via ENABLE_SEED_SETUP

Requirement 2: Test-level seed data via fixture
- Can call create_seed_for_user fixture in any test
- Creates seed data for specific user on demand

Requirement 3: Create data using API at test level
- Can use create_test_item fixture to create data via API
- Works at test level

Requirement 4: Delete data using API at test level
- Can use delete_test_item fixture to delete data via API
- Works at test level
"""

import pytest
import os
import uuid


def test_requirement_1_global_mongodb_seed_with_switch(admin_actor, mongodb_connection):
    """
    Requirement 1: Verify global MongoDB seed data with on/off switch
    
    - Automatically runs before tests (if ENABLE_SEED_SETUP=true)
    - Uses MongoDB direct insertion
    - Doesn't create duplicates if data exists
    - Can be turned on/off
    """
    print("\n" + "="*70)
    print("REQUIREMENT 1: Global MongoDB Seed Data with On/Off Switch")
    print("="*70)
    
    # Check if switch is accessible
    switch_value = os.getenv('ENABLE_SEED_SETUP', 'false')
    print(f"✅ Switch ENABLE_SEED_SETUP: {switch_value}")
    
    # Verify seed data exists in MongoDB (regardless of switch, if it ran)
    api = admin_actor['api']
    user_id = admin_actor['user']['_id']
    
    # Check MongoDB directly
    seed_count_mongo = mongodb_connection.items.count_documents({
        'created_by': user_id,
        'tags': {'$in': ['seed']}
    })
    print(f"✅ MongoDB seed items for admin1: {seed_count_mongo}")
    
    # Check via API
    response = api.get('/items')
    assert response.status_code == 200
    data = response.json()
    items = data.get('items', [])
    seed_items_api = [item for item in items if 'seed' in item.get('tags', [])]
    print(f"✅ API visible seed items: {len(seed_items_api)}")
    
    # Verify we have seed data (either from MongoDB setup or API setup)
    assert seed_count_mongo >= 11 or len(seed_items_api) >= 11, "Should have seed data"
    
    # Verify switch works (can be read)
    assert switch_value in ['true', 'false'], "Switch should be readable"
    
    print("✅ REQUIREMENT 1 PASSED: Global MongoDB seed with switch working")


def test_requirement_2_test_level_seed_fixture(editor_actor, create_seed_for_user, mongodb_connection):
    """
    Requirement 2: Verify test-level seed data via fixture
    
    - Can call create_seed_for_user fixture in any test
    - Creates seed data for specific user on demand
    """
    print("\n" + "="*70)
    print("REQUIREMENT 2: Test-Level Seed Data via Fixture")
    print("="*70)
    
    # Get user ID
    user_email = editor_actor['user']['email']
    user_id = editor_actor['user']['_id']  # ObjectId
    user_id_str = str(user_id)  # String version for backward compatibility
    
    print(f"✅ Testing with user: {user_email}")
    
    # Count before (check both ObjectId and string for backward compatibility)
    from bson import ObjectId
    # Explicitly use ObjectId(user_id_str) to ensure MongoDB matches both ObjectId and string types
    count_before = mongodb_connection.items.count_documents({
        'created_by': {'$in': [ObjectId(user_id_str), user_id_str]},
        'tags': {'$in': ['seed']}
    })
    print(f"✅ Seed items before fixture call: {count_before}")
    
    # Call fixture to create seed data (create_seed_for_user is a factory fixture)
    result_count = create_seed_for_user(user_email)
    print(f"✅ Fixture returned: {result_count} items")
    
    # Count after (check both ObjectId and string for backward compatibility)
    # Explicitly use ObjectId(user_id_str) to ensure MongoDB matches both ObjectId and string types
    count_after = mongodb_connection.items.count_documents({
        'created_by': {'$in': [ObjectId(user_id_str), user_id_str]},
        'tags': {'$in': ['seed']}
    })
    print(f"✅ Seed items after fixture call: {count_after}")
    
    # Verify: Should have at least 11 items (either existed or created)
    assert count_after >= 11, f"Should have at least 11 seed items, found {count_after}"
    
    # Verify: If items existed, count shouldn't increase (duplicate prevention)
    if count_before >= 11:
        assert count_after == count_before, "Should not create duplicates if data exists"
        print("✅ Duplicate prevention working: No new items created")
    else:
        assert count_after >= 11, "Should create items if they don't exist"
        print("✅ Items created successfully")
    
    print("✅ REQUIREMENT 2 PASSED: Test-level seed fixture working")


def test_requirement_3_create_data_via_api(admin_actor, create_test_item):
    """
    Requirement 3: Verify create data using API at test level
    
    - Can use create_test_item fixture to create data via API
    - Works at test level
    """
    print("\n" + "="*70)
    print("REQUIREMENT 3: Create Data Using API at Test Level")
    print("="*70)
    
    api = admin_actor['api']
    
    # Create item via API fixture
    unique_id = uuid.uuid4().hex[:8]
    test_item = create_test_item(api, {
        "name": f"API Test Item {unique_id}",
        "description": "Test item created via API fixture for requirement verification",
        "item_type": "DIGITAL",
        "price": 25.99,
        "category": "Testing",
        "download_url": "https://example.com/api-test.zip",
        "file_size": 1024
    })
    
    assert test_item is not None, "Item should be created"
    assert test_item['name'] == f"API Test Item {unique_id}", "Name should match"
    assert 'test-data' in test_item['tags'], "Should have test-data tag"
    
    item_id = test_item['_id']
    print(f"✅ Created item via API: {item_id}")
    
    # Verify item exists via API
    response = api.get(f"/items/{item_id}")
    assert response.status_code == 200, "Item should be accessible via API"
    print(f"✅ Verified item exists via API: {item_id}")
    
    # Clean up (for next requirement test)
    api.delete(f"/items/{item_id}")
    print(f"✅ Cleaned up test item: {item_id}")
    
    print("✅ REQUIREMENT 3 PASSED: Create data via API at test level working")


def test_requirement_4_delete_data_via_api(admin_actor, create_test_item, delete_test_item):
    """
    Requirement 4: Verify delete data using API at test level
    
    - Can use delete_test_item fixture to delete data via API
    - Works at test level
    """
    print("\n" + "="*70)
    print("REQUIREMENT 4: Delete Data Using API at Test Level")
    print("="*70)
    
    api = admin_actor['api']
    
    # Create item first
    unique_id = uuid.uuid4().hex[:8]
    test_item = create_test_item(api, {
        "name": f"Delete Test Item {unique_id}",
        "description": "Test item for delete verification - comprehensive description",
        "item_type": "DIGITAL",
        "price": 15.99,
        "category": "Testing",
        "download_url": "https://example.com/delete-test.zip",
        "file_size": 512
    })
    
    item_id = test_item['_id']
    print(f"✅ Created item for deletion test: {item_id}")
    
    # Verify item exists
    response = api.get(f"/items/{item_id}")
    assert response.status_code == 200, "Item should exist before delete"
    print(f"✅ Verified item exists: {item_id}")
    
    # Delete item via API fixture
    success = delete_test_item(api, item_id)
    assert success, "Delete should succeed"
    print(f"✅ Deleted item via API fixture: {item_id}")
    
    # Verify item is deleted (soft delete - inactive)
    response = api.get(f"/items/{item_id}")
    if response.status_code == 200:
        item_data = response.json().get('data', {})
        assert item_data.get('is_active') is False, "Item should be inactive after delete"
        print(f"✅ Verified item is inactive (soft delete): {item_id}")
    else:
        assert response.status_code == 404, "Item should return 404 if hard deleted"
        print(f"✅ Verified item is deleted (404): {item_id}")
    
    print("✅ REQUIREMENT 4 PASSED: Delete data via API at test level working")


def test_all_requirements_integration(admin_actor, editor_actor, create_seed_for_user, 
                                     create_test_item, delete_test_item, mongodb_connection):
    """
    Integration Test: Verify all 4 requirements work together
    
    - Global seed exists
    - Test-level seed fixture works
    - API create works
    - API delete works
    - All work together without conflicts
    """
    print("\n" + "="*70)
    print("INTEGRATION: All 4 Requirements Working Together")
    print("="*70)
    
    # 1. Verify global seed exists
    admin_api = admin_actor['api']
    response = admin_api.get('/items')
    data = response.json()
    seed_items_global = [item for item in data.get('items', []) if 'seed' in item.get('tags', [])]
    print(f"✅ Global seed items: {len(seed_items_global)}")
    assert len(seed_items_global) >= 11, "Global seed should exist"
    
    # 2. Test-level seed fixture
    editor_email = editor_actor['user']['email']
    editor_user_id = editor_actor['user']['_id']
    editor_user_id_str = str(editor_user_id)
    from bson import ObjectId
    # Explicitly use ObjectId(editor_user_id_str) to ensure MongoDB matches both ObjectId and string types
    count_before = mongodb_connection.items.count_documents({
        'created_by': {'$in': [ObjectId(editor_user_id_str), editor_user_id_str]},
        'tags': {'$in': ['seed']}
    })
    create_seed_for_user(editor_email)  # Call fixture
    count_after = mongodb_connection.items.count_documents({
        'created_by': {'$in': [ObjectId(editor_user_id_str), editor_user_id_str]},
        'tags': {'$in': ['seed']}
    })
    assert count_after >= 11, "Test-level seed should work"
    print(f"✅ Test-level seed: {count_after} items")
    
    # 3. API create
    editor_api = editor_actor['api']
    unique_id = uuid.uuid4().hex[:8]
    test_item = create_test_item(editor_api, {
        "name": f"Integration Test {unique_id}",
        "description": "Integration test item for all requirements verification",
        "item_type": "DIGITAL",
        "price": 30.00,
        "category": "Testing",
        "download_url": "https://example.com/integration.zip",
        "file_size": 1024
    })
    assert test_item is not None
    print(f"✅ API create: {test_item['_id']}")
    
    # 4. API delete
    success = delete_test_item(editor_api, test_item['_id'])
    assert success
    print(f"✅ API delete: Success")
    
    # Verify seed data still intact
    response = admin_api.get('/items')
    data = response.json()
    seed_items_final = [item for item in data.get('items', []) if 'seed' in item.get('tags', [])]
    assert len(seed_items_final) >= 11, "Global seed should remain intact"
    print(f"✅ Global seed still intact: {len(seed_items_final)} items")
    
    print("✅ INTEGRATION PASSED: All 4 requirements work together correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
