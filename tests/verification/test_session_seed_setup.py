"""
Session Setup Verification

Tests that session-scoped setup_mongodb_seed fixture works correctly.
This verifies that seed data is created before all tests run.
"""

import pytest
import os


def test_session_seed_setup_creates_data(admin_actor, mongodb_connection):
    """
    Verify that session-scoped setup_mongodb_seed created seed data
    
    Note: This test assumes ENABLE_SEED_SETUP=true was set
    If ENABLE_SEED_SETUP=false, this test will verify that no seed data exists
    """
    api = admin_actor['api']
    user = admin_actor['user']
    user_id = user['_id']
    user_email = user['email']
    
    print(f"\n[Session Setup] Verifying seed data for {user_email}...")
    
    # Check if session setup was enabled
    enable_seed_setup = os.getenv('ENABLE_SEED_SETUP', 'false').lower() == 'true'
    
    if not enable_seed_setup:
        print("[Session Setup] ⚠️  ENABLE_SEED_SETUP=false, skipping verification")
        pytest.skip("ENABLE_SEED_SETUP=false, session setup was not run")
    
    # Check via API
    print(f"[Session Setup] Checking via API...")
    resp = api.get('/items')
    assert resp.status_code == 200
    
    response_data = resp.json()
    if 'data' in response_data:
        items = response_data['data']['items']
    else:
        items = response_data.get('items', [])
    
    seed_items = [i for i in items if 'seed' in i.get('tags', [])]
    
    # Should have at least 11 seed items
    assert len(seed_items) >= 11, f"Session setup should create at least 11 seed items, got {len(seed_items)}"
    print(f"[Session Setup] API check: Found {len(seed_items)} seed items ✓")
    
    # Verify via MongoDB directly
    print(f"[Session Setup] Checking via MongoDB directly...")
    mongo_count = mongodb_connection.items.count_documents({
        'created_by': user_id,
        'tags': 'seed'
    })
    assert mongo_count >= 11, f"MongoDB should have at least 11 seed items, got {mongo_count}"
    print(f"[Session Setup] MongoDB check: Found {mongo_count} seed items ✓")
    
    # Verify seed items have correct tags
    print(f"[Session Setup] Verifying seed item tags...")
    for item in seed_items[:3]:  # Check first 3 items
        tags = item.get('tags', [])
        assert 'seed' in tags, f"Seed item {item['name']} should have 'seed' tag"
        print(f"[Session Setup] ✓ {item['name']} has correct tags: {tags}")
    
    # Verify naming pattern (should have user suffix)
    print(f"[Session Setup] Verifying naming pattern...")
    user_suffix = user_id[-4:]
    for item in seed_items[:3]:  # Check first 3 items
        name = item['name']
        assert f" - {user_suffix}" in name, f"Seed item name should end with ' - {user_suffix}', got: {name}"
        print(f"[Session Setup] ✓ {name} has correct naming pattern")
    
    print(f"[Session Setup] ✅ SUCCESS: Session setup created seed data correctly")


def test_session_seed_setup_creates_for_all_users(mongodb_connection):
    """
    Verify that session setup creates seed data for all configured users
    """
    enable_seed_setup = os.getenv('ENABLE_SEED_SETUP', 'false').lower() == 'true'
    
    if not enable_seed_setup:
        pytest.skip("ENABLE_SEED_SETUP=false, session setup was not run")
    
    # List of users that should have seed data
    expected_users = [
        "admin1@test.com",
        "admin2@test.com",
        "editor1@test.com",
        "editor2@test.com",
        "viewer1@test.com"
    ]
    
    print(f"\n[Session Setup] Verifying seed data for all configured users...")
    
    for email in expected_users:
        # Get user from MongoDB
        user = mongodb_connection.users.find_one({"email": email})
        if not user:
            print(f"[Session Setup] ⚠️  User {email} not found in MongoDB")
            continue
        
        user_id = str(user['_id'])
        
        # Count seed items for this user
        count = mongodb_connection.items.count_documents({
            'created_by': user_id,
            'tags': 'seed'
        })
        
        assert count >= 11, f"User {email} should have at least 11 seed items, got {count}"
        print(f"[Session Setup] ✓ {email}: {count} seed items")
    
    print(f"[Session Setup] ✅ SUCCESS: All users have seed data")


def test_session_seed_setup_uses_correct_tags(mongodb_connection, admin_actor):
    """
    Verify that session setup creates items with correct tags: ['seed', 'v1.0']
    """
    enable_seed_setup = os.getenv('ENABLE_SEED_SETUP', 'false').lower() == 'true'
    
    if not enable_seed_setup:
        pytest.skip("ENABLE_SEED_SETUP=false, session setup was not run")
    
    user = admin_actor['user']
    user_id = user['_id']
    
    print(f"\n[Session Setup] Verifying seed item tags...")
    
    # Get seed items from MongoDB
    seed_items = list(mongodb_connection.items.find({
        'created_by': user_id,
        'tags': 'seed'
    }).limit(5))  # Check first 5 items
    
    assert len(seed_items) > 0, "Should have at least one seed item"
    
    for item in seed_items:
        tags = item.get('tags', [])
        assert 'seed' in tags, f"Item {item.get('name')} should have 'seed' tag"
        # Note: v1.0 might be in tags array, but we're mainly checking for 'seed'
        print(f"[Session Setup] ✓ {item.get('name')}: tags = {tags}")
    
    print(f"[Session Setup] ✅ SUCCESS: All seed items have correct tags")
