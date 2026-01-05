"""
MongoDB Direct Seeding Fixtures - GLOBAL LEVEL ONLY

IMPORTANT: These fixtures are for GLOBAL-LEVEL seeding that runs ONCE before all tests.
They are NOT for on-demand seeding during individual tests.

Architecture:
- create_seed_for_user: Used by global setup_mongodb_seed fixture
  - Purpose: Direct MongoDB insertion for global baseline data
  - Scope: Called during session setup, not during tests
  - Data Source: Uses SeedDataFactory (role-specific generation)
  
For on-demand data insertion with flexible payloads, use insert_data_if_not_exists from seed_fixtures.py instead.
"""

import pytest
import os
from pymongo import MongoClient
from typing import Callable

# Import ItemBuilder for transformation
from lib.builders.item_builder import ItemBuilder


@pytest.fixture(scope="session")
def mongodb_connection():
    """
    Session-scoped MongoDB connection
    Reusable across all tests
    
    Yields:
        MongoDB database instance
    """
    uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME')
    
    if not uri or not db_name:
        raise ValueError("MONGODB_URI and MONGODB_DB_NAME must be set in environment")
    
    print(f"\n[MongoDB] Connecting to: {db_name}")
    
    client = MongoClient(uri)
    db = client[db_name]
    
    yield db
    
    client.close()
    print(f"[MongoDB] Connection closed")


@pytest.fixture(scope="session")
def create_seed_for_user(mongodb_connection) -> Callable:
    """
    GLOBAL SETUP ONLY: Factory fixture for MongoDB direct seeding.
    
    This fixture is used by setup_mongodb_seed for GLOBAL-LEVEL seeding.
    It is NOT intended for on-demand seeding during tests.
    
    Purpose:
        - Direct MongoDB insertion (fast, bypasses API validation)
        - Used during session setup to create baseline seed data
        - Generates role-specific data via SeedDataFactory
    
    When to use:
        - Called automatically by setup_mongodb_seed fixture (global setup)
        - NOT for test-level seeding (use seed_fixture_api instead)
    
    Responsibility: MongoDB operations only (insertion, duplicate checking)
    Data generation is handled by SeedDataFactory (separate responsibility)
    
    Returns:
        Function that creates seed data for a user email
        
    Usage (internal):
        count = create_seed_for_user("editor1@test.com")
        Note: This is called by setup_mongodb_seed, not directly in tests.
    """
    from pymongo.errors import BulkWriteError
    from fixtures.seed_factory import get_user_seed_data

    def _create(user_email: str) -> int:
        """
        GLOBAL SETUP ONLY: Create seed data for a user via MongoDB direct insertion.
        
        This function is called by setup_mongodb_seed during global setup.
        It is NOT intended for on-demand seeding during tests.
        
        Args:
            user_email: User email address
        
        Returns:
            Number of seed items created/existing
            
        Note:
            Data generation is delegated to SeedDataFactory.
            This function only handles MongoDB persistence.
            For on-demand seeding with flexible payloads, use seed_fixture_api instead.
        """
        # Data generation responsibility: Use factory to get seed data
        items_to_use = get_user_seed_data(user_email, use_factory=True)
        
        # Get user ID from MongoDB
        user = mongodb_connection.users.find_one({"email": user_email})
        if not user:
            raise ValueError(f"User not found: {user_email}")
        
        user_id = str(user['_id'])
        user_object_id = user['_id']  # Keep ObjectId for MongoDB queries
        
        # Optimized Check: Limit query to verify if enough items exist
        # Fetch just enough to confirm we have the required amount
        # Check for both String ID (legacy) and ObjectId (new builder)
        from bson import ObjectId
        existing_items = list(mongodb_connection.items.find({
            'created_by': {'$in': [user_id, user_object_id]},
            'tags': {'$in': ['seed']}
        }).limit(len(items_to_use) + 1))
        
        existing_count = len(existing_items)
        if existing_count >= len(items_to_use):
            # Seed data exists - return approximate count (exact count not needed)
            print(f"[MongoDB] Seed data already exists for {user_email} ({existing_count}+ items)")
            return existing_count
        
        # Prepare seed items for insertion using ItemBuilder
        try:
            items_to_insert = ItemBuilder.build_many(items_to_use, user_id)
        except Exception as e:
            raise RuntimeError(
                f"ItemBuilder failed to transform seed items for {user_email}. "
                f"This indicates an issue with the ItemBuilder. "
                f"Original error: {type(e).__name__}: {str(e)}"
            ) from e
        
        # Bulk insert
        try:
            result = mongodb_connection.items.insert_many(items_to_insert, ordered=False)
            count = len(result.inserted_ids)
            print(f"[MongoDB] Created {count} seed items for {user_email}")
            return count
        except BulkWriteError as e:
            # Handle partial insertions (some duplicates or validation errors)
            count = e.details.get('nInserted', 0)
            errors = e.details.get('writeErrors', [])
            
            if errors:
                print(f"[MongoDB] WARNING: Partial seed creation for {user_email}: {count} inserted, {len(errors)} failed")
                # Show first 3 errors for debugging
                for err in errors[:3]:
                    msg = err.get('errmsg', 'Unknown error')
                    print(f"  - {msg}")
                if len(errors) > 3:
                    print(f"  ... and {len(errors) - 3} more errors")
            else:
                print(f"[MongoDB] Partial seed creation for {user_email} ({count} new items)")
            
            # Verify final state (check both string and ObjectId for backward compatibility)
            final_count = mongodb_connection.items.count_documents({
                'created_by': {'$in': [user_object_id, user_id]},
                'tags': {'$in': ['seed']}
            })
            return final_count
        except Exception as e:
            print(f"[MongoDB] Error creating seed for {user_email}: {e}")
            raise
    
    return _create


@pytest.fixture(scope="session")
def delete_user_data(mongodb_connection) -> Callable:
    """
    Factory fixture: Delete all data for user via backend API
    
    Returns:
        Function that deletes user data
        
    Usage:
        success = delete_user_data("editor1@test.com", base_url, internal_key)
    """
    def _delete(user_email: str, base_url: str, internal_key: str) -> bool:
        import requests
        
        # Reuse existing connection
        user = mongodb_connection.users.find_one({"email": user_email})
        if not user:
            print(f"[Cleanup] User not found: {user_email}")
            return False
            
        user_id = str(user['_id'])
            
        # Call backend cleanup endpoint
        url = f"{base_url}/api/v1/internal/users/{user_id}/data"
        headers = {'x-internal-key': internal_key}
        
        print(f"[Cleanup] Deleting data for {user_email}...")
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            deleted = result.get('deleted', {})
            print(f"[Cleanup] Deleted: {deleted.get('items', 0)} items, "
                  f"{deleted.get('files', 0)} files, "
                  f"{deleted.get('bulk_jobs', 0)} jobs")
            return True
        else:
            print(f"[Cleanup] WARNING: Failed: {response.status_code}")
            return False
    
    return _delete


@pytest.fixture(scope="session")
def delete_user_items(mongodb_connection) -> Callable:
    """
    Factory fixture: Delete only items for user via backend API
    (Preserves bulk jobs, activity logs, OTPs, user record)
    
    Returns:
        Function that deletes user items
        
    Usage:
        success = delete_user_items("editor1@test.com", base_url, internal_key)
    """
    def _delete_items(user_email: str, base_url: str, internal_key: str) -> bool:
        import requests
        
        # Reuse existing connection
        user = mongodb_connection.users.find_one({"email": user_email})
        if not user:
            print(f"[Cleanup] User not found: {user_email}")
            return False
            
        user_id = str(user['_id'])
            
        # Call items-only cleanup endpoint
        url = f"{base_url}/api/v1/internal/users/{user_id}/items"
        headers = {'x-internal-key': internal_key}
        
        print(f"[Cleanup] Deleting items for {user_email}...")
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            deleted = result.get('deleted', {})
            print(f"[Cleanup] Deleted: {deleted.get('items', 0)} items, "
                  f"{deleted.get('files', 0)} files")
            print(f"[Cleanup] Preserved: user, bulk_jobs, activity_logs, otps")
            return True
        else:
            print(f"[Cleanup] WARNING: Failed: {response.status_code}")
            return False
    
    return _delete_items


@pytest.fixture(scope="session")
def get_user_id_from_email(mongodb_connection) -> Callable:
    """
    Helper fixture: Get user ObjectId from email
    
    Returns:
        Function that returns user ID for email
        
    Usage:
        user_id = get_user_id_from_email("admin1@test.com")
    """
    def _get_id(user_email: str) -> str:
        user = mongodb_connection.users.find_one({"email": user_email})
        if not user:
            raise ValueError(f"User not found: {user_email}")
        return str(user['_id'])
    
    return _get_id
