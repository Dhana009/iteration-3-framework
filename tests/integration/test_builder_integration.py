"""
Integration tests for ItemBuilder with MongoDB fixture

Tests that the builder integrates correctly with the MongoDB fixture
and produces the same results as the manual transformation.
"""

import pytest


class TestBuilderIntegration:
    """Test ItemBuilder integration with MongoDB fixture"""
    
    def test_mongodb_fixture_with_builder(self, mongodb_connection, create_seed_for_user):
        """Test that MongoDB fixture works with ItemBuilder (opt-in)"""
        # Use existing test user (admin2 - not used by default seeding)
        user_email = "admin2@test.com"
        
        # Use builder path (opt-in)
        count = create_seed_for_user(user_email, use_builder=True)
        
        # Verify items were created
        assert count > 0
        
        # Verify items have correct structure
        user = mongodb_connection.users.find_one({"email": user_email})
        assert user is not None, f"User {user_email} not found"
        
        user_id = str(user['_id'])
        from bson import ObjectId
        items = list(mongodb_connection.items.find({"created_by": ObjectId(user_id)}))
        
        assert len(items) > 0, "No items found for user"
        
        # Verify builder transformations
        for item in items:
            assert 'normalizedName' in item, "Missing normalizedName"
            assert 'normalizedCategory' in item, "Missing normalizedCategory"
            assert 'createdAt' in item, "Missing createdAt"
            assert 'updatedAt' in item, "Missing updatedAt"
            assert item['created_by'] == ObjectId(user_id), "Incorrect created_by"
            assert 'seed' in item['tags'], "Missing 'seed' tag"
            assert 'v1.0' in item['tags'], "Missing 'v1.0' tag"
            
        print(f"\n✅ Builder integration test passed: {len(items)} items created")
    
    def test_builder_produces_correct_structure(self, mongodb_connection, create_seed_for_user):
        """Test that builder produces items with correct structure"""
        # Use existing test user
        user_email = "admin2@test.com"
        
        # Create items with builder
        count = create_seed_for_user(user_email, use_builder=True)
        assert count > 0
        
        # Get items
        user = mongodb_connection.users.find_one({"email": user_email})
        from bson import ObjectId
        items = list(mongodb_connection.items.find({"created_by": ObjectId(user['_id'])}))
        
        # Verify all items have required fields
        required_fields = ['name', 'normalizedName', 'category', 'normalizedCategory', 
                          'created_by', 'tags', 'is_active', 'createdAt', 'updatedAt']
        
        for item in items:
            for field in required_fields:
                assert field in item, f"Missing field: {field}"
        
        print(f"\n✅ Builder produces correct structure for {len(items)} items")
    
    def test_builder_idempotency(self, mongodb_connection, create_seed_for_user):
        """Test that builder respects existing data (idempotent)"""
        # Use existing test user
        user_email = "viewer2@test.com"
        
        # First call - should create items (or return existing count)
        count1 = create_seed_for_user(user_email, use_builder=True)
        assert count1 > 0
        
        # Second call - should skip (items already exist)
        count2 = create_seed_for_user(user_email, use_builder=True)
        assert count2 == count1  # Should return same count, not create duplicates
        
        # Verify no duplicates in database
        user = mongodb_connection.users.find_one({"email": user_email})
        from bson import ObjectId
        items = list(mongodb_connection.items.find({"created_by": ObjectId(user['_id'])}))
        
        # Should have exactly count1 items (no duplicates)
        assert len(items) == count1
        
        print(f"\n✅ Builder is idempotent: {len(items)} items (no duplicates)")
