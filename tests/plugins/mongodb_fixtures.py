"""
Reusable MongoDB Fixtures for Test Data Management

Purpose: Provide factory fixtures for MongoDB operations (create/delete seed data)
"""

import pytest
import os
from datetime import datetime
from pymongo import MongoClient
from typing import Callable


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
    Factory fixture: Create seed data for specific user
    
    Returns:
        Function that creates seed data for a user email
        
    Usage:
        # Use default seed items
        count = create_seed_for_user("editor1@test.com")
        
        # Use custom seed items
        custom_items = [...]
        count = create_seed_for_user("admin1@test.com", seed_items=custom_items)
    """
    from lib.seed import SEED_ITEMS
    from pymongo.errors import BulkWriteError
    from typing import Optional, List, Dict, Any

    def _create(user_email: str, seed_items: Optional[List[Dict[str, Any]]] = None) -> int:
        """
        Create seed data for a user
        
        Args:
            user_email: User email address
            seed_items: Optional list of seed items. If None, uses default SEED_ITEMS
        
        Returns:
            Number of seed items created/existing
        """
        # Use provided seed_items or fallback to default
        items_to_use = seed_items if seed_items is not None else SEED_ITEMS
        
        # Get user ID from MongoDB
        user = mongodb_connection.users.find_one({"email": user_email})
        if not user:
            raise ValueError(f"User not found: {user_email}")
        
        user_id = str(user['_id'])
        
        # Optimized Check: Limit query to verify if enough items exist
        # Fetch just enough to confirm we have the required amount
        existing_items = list(mongodb_connection.items.find({
            'created_by': user_id,
            'tags': {'$in': ['seed']}
        }).limit(len(items_to_use) + 1))
        
        if len(existing_items) >= len(items_to_use):
             # If we hit the limit, there might be more items. Get exact count for accuracy.
             if len(existing_items) > len(items_to_use):
                 true_count = mongodb_connection.items.count_documents({
                    'created_by': user_id,
                    'tags': {'$in': ['seed']}
                 })
                 print(f"[MongoDB] Seed data already exists for {user_email} ({true_count} items)")
                 return true_count
             
             # Otherwise we have exactly the count we found
             print(f"[MongoDB] Seed data already exists for {user_email} (found {len(existing_items)} items)")
             return len(existing_items)
        
        # Prepare seed items with list comprehension
        user_id_suffix = user_id[-4:]
        items_to_insert = [
            {
                **item,
                'name': f"{item['name']} - {user_id_suffix}",
                'created_by': user_id,
                'tags': ['seed', 'v1.0'],
                'is_active': item.get('is_active', True), # Default to Active if not specified
                'normalizedName': f"{item['name']} - {user_id_suffix}".lower(),
                'normalizedCategory': item['category'].lower() if 'category' in item else None,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            for item in items_to_use
        ]
        
        # Bulk insert
        try:
            result = mongodb_connection.items.insert_many(items_to_insert, ordered=False)
            count = len(result.inserted_ids)
            print(f"[MongoDB] Created {count} seed items for {user_email}")
            return count
        except BulkWriteError as e:
             # Handle partial insertions (some duplicates)
            count = e.details['nInserted']
            print(f"[MongoDB] Partial seed creation for {user_email} ({count} new items)")
            print(f"[MongoDB] Write Errors: {e.details.get('writeErrors')}")
            
            # Verify final state
            final_count = mongodb_connection.items.count_documents({
                'created_by': user_id,
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
            print(f"[Cleanup] ✅ Deleted: {deleted.get('items', 0)} items, "
                  f"{deleted.get('files', 0)} files, "
                  f"{deleted.get('bulk_jobs', 0)} jobs")
            return True
        else:
            print(f"[Cleanup] ⚠️  Failed: {response.status_code}")
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
            print(f"[Cleanup] ✅ Deleted: {deleted.get('items', 0)} items, "
                  f"{deleted.get('files', 0)} files")
            print(f"[Cleanup] ✅ Preserved: user, bulk_jobs, activity_logs, otps")
            return True
        else:
            print(f"[Cleanup] ⚠️  Failed: {response.status_code}")
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
