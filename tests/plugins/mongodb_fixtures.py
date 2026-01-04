"""
Reusable MongoDB Fixtures for Test Data Management

Purpose: Provide factory fixtures for MongoDB operations (create/delete seed data)
"""

import pytest
import os
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
        count = create_seed_for_user("editor1@test.com")
    """
    def _create(user_email: str) -> int:
        from lib.seed import SEED_ITEMS
        
        # Get user ID from MongoDB
        user = mongodb_connection.users.find_one({"email": user_email})
        if not user:
            raise ValueError(f"User not found: {user_email}")
        
        user_id = str(user['_id'])
        
        # CHECK: Do seed items already exist for this user?
        existing_seed_count = mongodb_connection.items.count_documents({
            'created_by': user_id,
            'tags': 'seed'
        })
        
        if existing_seed_count >= len(SEED_ITEMS):
            print(f"[MongoDB] Seed data already exists for {user_email} ({existing_seed_count} items)")
            return existing_seed_count
        
        # Prepare seed items with created_by and tags
        # Make items unique per user by adding user ID suffix
        user_id_suffix = user_id[-4:]  # Last 4 chars of user ID
        items_to_insert = []
        for item in SEED_ITEMS:
            item_copy = item.copy()
            # Add user suffix to name for uniqueness
            item_copy['name'] = f"{item['name']} - {user_id_suffix}"
            item_copy['created_by'] = user_id
            item_copy['tags'] = ['seed', 'v1.0']
            items_to_insert.append(item_copy)
        
        # Bulk insert
        try:
            result = mongodb_connection.items.insert_many(items_to_insert, ordered=False)
            count = len(result.inserted_ids)
            print(f"[MongoDB] Created {count} seed items for {user_email}")
            return count
        except Exception as e:
            # If some items already exist, count what we have
            final_count = mongodb_connection.items.count_documents({
                'created_by': user_id,
                'tags': 'seed'
            })
            print(f"[MongoDB] Seed setup complete for {user_email} ({final_count} items, some may have existed)")
            return final_count
    
    return _create


@pytest.fixture
def delete_user_data() -> Callable:
    """
    Factory fixture: Delete all data for user via backend API
    
    Returns:
        Function that deletes user data
        
    Usage:
        success = delete_user_data("editor1@test.com", base_url, internal_key)
    """
    def _delete(user_email: str, base_url: str, internal_key: str) -> bool:
        import requests
        
        # Get MongoDB connection
        uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DB_NAME')
        
        client = MongoClient(uri)
        db = client[db_name]
        
        try:
            # Get user ID
            user = db.users.find_one({"email": user_email})
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
                
        finally:
            client.close()
    
    return _delete


@pytest.fixture
def delete_user_items() -> Callable:
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
        
        # Get MongoDB connection
        uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DB_NAME')
        
        client = MongoClient(uri)
        db = client[db_name]
        
        try:
            # Get user ID
            user = db.users.find_one({"email": user_email})
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
                preserved = result.get('preserved', {})
                print(f"[Cleanup] ✅ Deleted: {deleted.get('items', 0)} items, "
                      f"{deleted.get('files', 0)} files")
                print(f"[Cleanup] ✅ Preserved: user, bulk_jobs, activity_logs, otps")
                return True
            else:
                print(f"[Cleanup] ⚠️  Failed: {response.status_code}")
                return False
                
        finally:
            client.close()
    
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
