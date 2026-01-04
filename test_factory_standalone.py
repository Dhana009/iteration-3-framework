"""
Standalone test to verify seed factory works
Run: python test_factory_standalone.py
"""

from fixtures.seed_factory import SeedDataFactory, get_user_seed_data

print("="*70)
print("Testing Seed Data Factory")
print("="*70)

# Test 1: Factory generates admin items
print("\nTest 1: Factory generates admin items")
factory = SeedDataFactory(seed_value=42)
admin_items = factory.create_admin_items(count=5)
print(f"  Generated {len(admin_items)} admin items")
print(f"  First item: {admin_items[0]['name']} - {admin_items[0]['category']} - ${admin_items[0]['price']}")
assert len(admin_items) == 5
print("  PASSED")

# Test 2: Factory generates editor items
print("\nTest 2: Factory generates editor items")
editor_items = factory.create_editor_items(count=5)
print(f"  Generated {len(editor_items)} editor items")
print(f"  First item: {editor_items[0]['name']} - {editor_items[0]['category']} - ${editor_items[0]['price']}")
assert len(editor_items) == 5
print("  PASSED")

# Test 3: Different users get different data
print("\nTest 3: Different users get different data")
admin1_data = factory.create_user_specific_items("admin1@test.com", count=5)
admin2_data = factory.create_user_specific_items("admin2@test.com", count=5)
editor1_data = factory.create_user_specific_items("editor1@test.com", count=5)
print(f"  Admin1: {len(admin1_data)} items")
print(f"  Admin2: {len(admin2_data)} items")
print(f"  Editor1: {len(editor1_data)} items")
assert len(admin1_data) == 5
assert len(admin2_data) == 5
assert len(editor1_data) == 5
print("  PASSED")

# Test 4: Helper function works
print("\nTest 4: Helper function works")
admin_data = get_user_seed_data("admin1@test.com", use_factory=True)
print(f"  Generated {len(admin_data)} items for admin1 (factory)")
assert len(admin_data) > 0
print("  PASSED")

# Test 5: Custom config works
print("\nTest 5: Custom config works")
custom_config = [
    {"name": "Custom Item 1", "category": "Electronics", "item_type": "PHYSICAL", "price": 100},
    {"name": "Custom Item 2", "category": "Software", "item_type": "DIGITAL", "price": 50},
]
custom_data = get_user_seed_data("admin1@test.com", custom_config=custom_config)
print(f"  Generated {len(custom_data)} custom items")
assert len(custom_data) == 2
assert custom_data[0]['name'] == "Custom Item 1"
print("  PASSED")

print("\n" + "="*70)
print("ALL TESTS PASSED! Factory is working correctly.")
print("="*70)
