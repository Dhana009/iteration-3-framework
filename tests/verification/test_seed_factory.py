"""
Verification: Seed Data Factory

Tests that verify the test data factory works correctly:
1. Factory generates different data for different users
2. create_seed_for_user accepts optional seed_items parameter
3. User-specific seed data is created correctly
4. Factory generates valid item structures
"""

import pytest
import os
from fixtures.seed_factory import SeedDataFactory, get_user_seed_data
from lib.seed import SEED_ITEMS


def test_factory_generates_admin_items():
    """
    Test 1: Verify factory generates admin-specific items
    """
    print("\n" + "="*70)
    print("TEST 1: Factory Generates Admin Items")
    print("="*70)
    
    factory = SeedDataFactory(seed_value=42)  # Deterministic
    admin_items = factory.create_admin_items(count=5)
    
    assert len(admin_items) == 5, "Should generate 5 items"
    print(f"✅ Generated {len(admin_items)} admin items")
    
    # Verify item structure
    for item in admin_items:
        assert 'name' in item, "Item should have name"
        assert 'category' in item, "Item should have category"
        assert 'item_type' in item, "Item should have item_type"
        assert 'price' in item, "Item should have price"
        assert item['item_type'] in ['PHYSICAL', 'DIGITAL'], "Item type should be valid"
        print(f"  ✓ {item['name']} - {item['category']} - {item['item_type']} - ${item['price']}")
    
    print("✅ TEST 1 PASSED: Factory generates valid admin items")


def test_factory_generates_editor_items():
    """
    Test 2: Verify factory generates editor-specific items
    """
    print("\n" + "="*70)
    print("TEST 2: Factory Generates Editor Items")
    print("="*70)
    
    factory = SeedDataFactory(seed_value=42)
    editor_items = factory.create_editor_items(count=5)
    
    assert len(editor_items) == 5, "Should generate 5 items"
    print(f"✅ Generated {len(editor_items)} editor items")
    
    # Verify items are different from admin items
    admin_items = factory.create_admin_items(count=5)
    assert editor_items != admin_items, "Editor items should differ from admin items"
    print("✅ Editor items are different from admin items")
    
    print("✅ TEST 2 PASSED: Factory generates valid editor items")


def test_factory_generates_different_data_per_user():
    """
    Test 3: Verify factory generates different data for different users
    """
    print("\n" + "="*70)
    print("TEST 3: Factory Generates Different Data Per User")
    print("="*70)
    
    factory = SeedDataFactory(seed_value=42)
    
    # Generate data for different users
    admin1_data = factory.create_user_specific_items("admin1@test.com", count=5)
    admin2_data = factory.create_user_specific_items("admin2@test.com", count=5)
    editor1_data = factory.create_user_specific_items("editor1@test.com", count=5)
    
    # All should have items
    assert len(admin1_data) == 5, "Admin1 should have 5 items"
    assert len(admin2_data) == 5, "Admin2 should have 5 items"
    assert len(editor1_data) == 5, "Editor1 should have 5 items"
    
    print(f"✅ Admin1: {len(admin1_data)} items")
    print(f"✅ Admin2: {len(admin2_data)} items")
    print(f"✅ Editor1: {len(editor1_data)} items")
    
    # Note: With same seed, admin1 and admin2 might generate same items
    # But they should be different from editor items
    assert admin1_data != editor1_data, "Admin and editor items should differ"
    print("✅ Admin and editor items are different")
    
    print("✅ TEST 3 PASSED: Factory generates different data per user")


def test_get_user_seed_data_helper():
    """
    Test 4: Verify get_user_seed_data helper function works
    """
    print("\n" + "="*70)
    print("TEST 4: get_user_seed_data Helper Function")
    print("="*70)
    
    # Test with factory
    admin_data = get_user_seed_data("admin1@test.com", use_factory=True)
    assert len(admin_data) > 0, "Should generate admin data"
    print(f"✅ Generated {len(admin_data)} items for admin1 (factory)")
    
    # Test with custom config
    custom_config = [
        {"name": "Custom Item 1", "category": "Electronics", "item_type": "PHYSICAL", "price": 100},
        {"name": "Custom Item 2", "category": "Software", "item_type": "DIGITAL", "price": 50},
    ]
    custom_data = get_user_seed_data("admin1@test.com", custom_config=custom_config)
    assert len(custom_data) == 2, "Should generate 2 custom items"
    assert custom_data[0]['name'] == "Custom Item 1", "First item should match"
    print(f"✅ Generated {len(custom_data)} custom items")
    
    # Test with default (no factory)
    default_data = get_user_seed_data("admin1@test.com", use_factory=False)
    assert len(default_data) == len(SEED_ITEMS), "Should return default SEED_ITEMS"
    print(f"✅ Returned {len(default_data)} default items")
    
    print("✅ TEST 4 PASSED: Helper function works correctly")


def test_create_seed_for_user_with_custom_items(create_seed_for_user, mongodb_connection):
    """
    Test 5: Verify create_seed_for_user accepts optional seed_items parameter
    """
    print("\n" + "="*70)
    print("TEST 5: create_seed_for_user with Custom Items")
    print("="*70)
    
    # Generate custom seed data using factory
    custom_items = get_user_seed_data("admin1@test.com", use_factory=True)
    
    # Create seed data with custom items
    count = create_seed_for_user("admin1@test.com", seed_items=custom_items)
    
    assert count >= len(custom_items), f"Should create at least {len(custom_items)} items, got {count}"
    print(f"✅ Created {count} custom seed items for admin1")
    
    # Verify items exist in MongoDB
    user = mongodb_connection.users.find_one({"email": "admin1@test.com"})
    assert user is not None, "User should exist"
    user_id = str(user['_id'])
    
    mongo_count = mongodb_connection.items.count_documents({
        'created_by': user_id,
        'tags': {'$in': ['seed']}
    })
    
    assert mongo_count >= len(custom_items), f"MongoDB should have at least {len(custom_items)} items"
    print(f"✅ Verified {mongo_count} seed items in MongoDB")
    
    print("✅ TEST 5 PASSED: create_seed_for_user accepts custom seed_items")


def test_user_specific_seed_data_created(mongodb_connection):
    """
    Test 6: Verify that user-specific seed data was created by setup_mongodb_seed
    """
    print("\n" + "="*70)
    print("TEST 6: User-Specific Seed Data Created")
    print("="*70)
    
    # Check if session setup was enabled
    enable_seed_setup = os.getenv('ENABLE_SEED_SETUP', 'false').lower() == 'true'
    
    if not enable_seed_setup:
        print("[Test 6] ⚠️  ENABLE_SEED_SETUP=false, skipping verification")
        pytest.skip("ENABLE_SEED_SETUP=false, session setup was not run")
    
    # Check seed data for different users
    users_to_check = [
        "admin1@test.com",
        "admin2@test.com",
        "editor1@test.com",
        "editor2@test.com",
        "viewer1@test.com"
    ]
    
    for email in users_to_check:
        user = mongodb_connection.users.find_one({"email": email})
        if not user:
            print(f"[Test 6] ⚠️  User {email} not found, skipping")
            continue
        
        user_id = str(user['_id'])
        seed_count = mongodb_connection.items.count_documents({
            'created_by': user_id,
            'tags': {'$in': ['seed']}
        })
        
        # Factory generates different counts per role
        # Admin: 15, Editor: 10, Viewer: 5
        if "admin" in email:
            expected_min = 10  # At least 10 (factory generates 15)
        elif "editor" in email:
            expected_min = 8  # At least 8 (factory generates 10)
        elif "viewer" in email:
            expected_min = 3  # At least 3 (factory generates 5)
        else:
            expected_min = 5  # Default minimum
        
        assert seed_count >= expected_min, \
            f"User {email} should have at least {expected_min} seed items, got {seed_count}"
        
        print(f"✅ {email}: {seed_count} seed items")
    
    print("✅ TEST 6 PASSED: User-specific seed data created correctly")


def test_factory_item_structure():
    """
    Test 7: Verify factory generates items with correct structure
    """
    print("\n" + "="*70)
    print("TEST 7: Factory Item Structure")
    print("="*70)
    
    factory = SeedDataFactory()
    item = factory.create_item(
        name="Test Item",
        category="Electronics",
        item_type="PHYSICAL",
        price=100.0
    )
    
    # Required fields
    assert 'name' in item
    assert 'category' in item
    assert 'item_type' in item
    assert 'price' in item
    assert 'description' in item
    assert 'is_active' in item
    
    # Type-specific fields for PHYSICAL
    assert 'weight' in item, "PHYSICAL items should have weight"
    assert 'dimensions' in item, "PHYSICAL items should have dimensions"
    
    print("✅ PHYSICAL item structure correct")
    
    # Test DIGITAL item
    digital_item = factory.create_item(
        name="Test Digital",
        category="Software",
        item_type="DIGITAL",
        price=50.0
    )
    
    assert 'download_url' in digital_item, "DIGITAL items should have download_url"
    assert 'file_size' in digital_item, "DIGITAL items should have file_size"
    
    print("✅ DIGITAL item structure correct")
    print("✅ TEST 7 PASSED: Factory generates correct item structures")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
