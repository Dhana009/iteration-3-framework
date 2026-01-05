"""
Reusable API Fixtures for Test Data Management

Purpose: Provide factory fixtures for API operations (CRUD operations on test items)

All fixtures are optimized for:
- Time complexity: Minimize API calls
- Space complexity: Avoid unnecessary data storage
- Error handling: Graceful degradation

Available Fixtures:
- create_test_item: Create single item (no duplicate check)
- update_test_item: Update existing item (requires version for optimistic locking)
- delete_test_item: Soft delete single item (sets is_active=false)
- hard_delete_test_item: Hard delete single item (permanent, requires internal key)
- hard_delete_user_items: Hard delete all items for user (permanent, requires internal key)
- hard_delete_user_data: Hard delete all user data (permanent, requires internal key)
- create_multiple_test_items: Create multiple items (no duplicate check)
- insert_data_if_not_exists: Insert items if not exists (from seed_fixtures.py)

Note: For insert with duplicate checking, use insert_data_if_not_exists from seed_fixtures.py
"""

import pytest
import os
from typing import Callable, Dict, Any, List, Optional


@pytest.fixture
def create_test_item() -> Callable:
    """
    Factory fixture: Create test item via API (no duplicate check).
    
    Time Complexity: O(1) - Single API call
    Space Complexity: O(1) - No additional storage
    
    Returns:
        Function that creates a test item
        
    Usage:
        item = create_test_item(api_client, {
            "name": "Test Item",
            "description": "Test description",
            "item_type": "DIGITAL",
            "price": 10.00,
            "category": "Electronics",
            "download_url": "https://example.com/file.zip",
            "file_size": 1024
        })
    """
    def _create(api_client, item_data: Dict[str, Any]) -> Dict[str, Any]:
        # Add test-data tag
        item_data['tags'] = item_data.get('tags', []) + ['test-data']
        
        response = api_client.post('/items', json=item_data)
        
        if response.status_code == 201:
            item = response.json()['data']
            print(f"[API] Created test item: {item['name']} (ID: {item['_id']})")
            return item
        else:
            raise Exception(f"Failed to create item: {response.status_code} - {response.text}")
    
    return _create


@pytest.fixture
def update_test_item() -> Callable:
    """
    Factory fixture: Update existing item via API.
    
    Time Complexity: O(1) - Single API call
    Space Complexity: O(1) - No additional storage
    
    Requires optimistic locking: Must provide current version number.
    
    Returns:
        Function that updates an item
        
    Usage:
        updated_item = update_test_item(api_client, item_id, {
            "name": "Updated Name",
            "price": 199.99
        }, version=1)
    """
    def _update(api_client, item_id: str, update_data: Dict[str, Any], version: int) -> Optional[Dict[str, Any]]:
        """
        Update an existing item.
        
        Args:
            api_client: Authenticated APIClient instance
            item_id: Item ID to update
            update_data: Dictionary of fields to update
            version: Current version number (required for optimistic locking)
        
        Returns:
            Updated item data if successful, None otherwise
        """
        # Include version in update payload (required for optimistic locking)
        payload = update_data.copy()
        payload['version'] = version
        
        response = api_client.put(f'/items/{item_id}', json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'data' in data:
                updated_item = data['data']
                print(f"[API] Updated test item: {updated_item.get('name', item_id)} (version: {updated_item.get('version')})")
                return updated_item
            else:
                print(f"[API] Unexpected response format: {data}")
                return None
        elif response.status_code == 409:
            # Version conflict - item was modified by another user
            error_data = response.json()
            current_version = error_data.get('current_version', 'unknown')
            print(f"[API] Version conflict for item {item_id}. Current version: {current_version}, provided: {version}")
            return None
        elif response.status_code == 404:
            print(f"[API] Item {item_id} not found or not owned by user")
            return None
        else:
            print(f"[API] Failed to update item {item_id}: {response.status_code} - {response.text[:100]}")
            return None
    
    return _update


@pytest.fixture
def delete_test_item() -> Callable:
    """
    Factory fixture: Soft delete test item via API.
    
    Time Complexity: O(1) - Single API call
    Space Complexity: O(1) - No additional storage
    
    Soft delete: Sets is_active=false, deleted_at=timestamp (item remains in DB).
    
    Returns:
        Function that soft deletes a test item
        
    Usage:
        success = delete_test_item(api_client, item_id)
    """
    def _delete(api_client, item_id: str) -> bool:
        response = api_client.delete(f'/items/{item_id}')
        
        if response.status_code == 200:
            print(f"[API] Soft deleted test item: {item_id}")
            return True
        elif response.status_code == 404:
            print(f"[API] Item {item_id} not found or already deleted")
            return False
        elif response.status_code == 409:
            print(f"[API] Item {item_id} already deleted")
            return False
        else:
            print(f"[API] Failed to delete item {item_id}: {response.status_code}")
            return False
    
    return _delete


@pytest.fixture
def hard_delete_test_item() -> Callable:
    """
    Factory fixture: Hard delete (permanent) single item via internal API.
    
    Time Complexity: O(1) - Single API call
    Space Complexity: O(1) - No additional storage
    
    Hard delete: Permanently removes item and associated files from database and filesystem.
    Requires internal automation key.
    
    Returns:
        Function that permanently deletes a test item
        
    Usage:
        result = hard_delete_test_item(api_client, item_id, internal_key)
    """
    def _hard_delete(api_client, item_id: str, internal_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Permanently delete a single item.
        
        Args:
            api_client: APIClient instance (doesn't need auth token for internal endpoints)
            item_id: Item ID to permanently delete
            internal_key: Internal automation key (defaults to INTERNAL_AUTOMATION_KEY env var)
        
        Returns:
            Deletion result with counts if successful, None otherwise
        """
        # Get internal key from parameter or environment
        if internal_key is None:
            internal_key = os.getenv('INTERNAL_AUTOMATION_KEY', 'flowhub-secret-automation-key-2025')
        
        # Use requests directly for internal endpoints (need custom headers)
        import requests
        url = f"{api_client.base_url}/internal/items/{item_id}/permanent"
        headers = {'x-internal-key': internal_key}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                deleted = result.get('deleted', {})
                files_deleted = deleted.get('files_deleted', 0)
                print(f"[API] Hard deleted item {item_id} (files deleted: {files_deleted})")
                return result
            elif response.status_code == 401:
                print(f"[API] Unauthorized: Invalid internal key")
                return None
            elif response.status_code == 404:
                print(f"[API] Item {item_id} not found")
                return None
            else:
                print(f"[API] Failed to hard delete item {item_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"[API] Error hard deleting item {item_id}: {e}")
            return None
    
    return _hard_delete


@pytest.fixture
def hard_delete_user_items() -> Callable:
    """
    Factory fixture: Hard delete all items for a user via internal API.
    
    Time Complexity: O(1) - Single API call (bulk operation)
    Space Complexity: O(1) - No additional storage
    
    Hard delete: Permanently removes all items and associated files for a user.
    Preserves: user record, bulk jobs, activity logs, OTPs.
    Requires internal automation key.
    
    Returns:
        Function that permanently deletes all user items
        
    Usage:
        result = hard_delete_user_items(api_client, user_email, internal_key)
        # OR
        result = hard_delete_user_items(api_client, user_id=user_id, internal_key=key)
    """
    def _hard_delete_items(api_client, user_email: Optional[str] = None, user_id: Optional[str] = None, 
                          internal_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Permanently delete all items for a user.
        
        Args:
            api_client: APIClient instance
            user_email: User email (will be converted to user_id)
            user_id: User ID (ObjectId string) - if provided, user_email is ignored
            internal_key: Internal automation key (defaults to INTERNAL_AUTOMATION_KEY env var)
        
        Returns:
            Deletion result with counts if successful, None otherwise
        """
        # Get internal key
        if internal_key is None:
            internal_key = os.getenv('INTERNAL_AUTOMATION_KEY', 'flowhub-secret-automation-key-2025')
        
        # Get user_id from email if needed (requires MongoDB connection)
        if user_id is None and user_email:
            # Try to get user_id from MongoDB if connection available
            # This is optional - user can also pass user_id directly from actor
            try:
                from pymongo import MongoClient
                uri = os.getenv('MONGODB_URI')
                db_name = os.getenv('MONGODB_DB_NAME', 'test')
                if uri and db_name:
                    client = MongoClient(uri)
                    db = client[db_name]
                    user = db.users.find_one({"email": user_email})
                    client.close()
                    if user:
                        user_id = str(user['_id'])
                    else:
                        raise ValueError(f"User not found: {user_email}")
                else:
                    raise ValueError("MongoDB connection not available. Provide user_id directly from actor['user']['_id']")
            except Exception as e:
                raise ValueError(f"Cannot get user_id from email: {e}. Provide user_id directly from actor['user']['_id']")
        
        if user_id is None:
            raise ValueError("Either user_email or user_id must be provided")
        
        import requests
        url = f"{api_client.base_url}/internal/users/{user_id}/items"
        headers = {'x-internal-key': internal_key}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                deleted = result.get('deleted', {})
                items_deleted = deleted.get('items', 0)
                files_deleted = deleted.get('files', 0)
                print(f"[API] Hard deleted {items_deleted} items and {files_deleted} files for user {user_id}")
                return result
            elif response.status_code == 401:
                print(f"[API] Unauthorized: Invalid internal key")
                return None
            elif response.status_code == 404:
                print(f"[API] User {user_id} not found")
                return None
            else:
                print(f"[API] Failed to hard delete user items: {response.status_code}")
                return None
        except Exception as e:
            print(f"[API] Error hard deleting user items: {e}")
            return None
    
    return _hard_delete_items


@pytest.fixture
def hard_delete_user_data() -> Callable:
    """
    Factory fixture: Hard delete all data for a user via internal API.
    
    Time Complexity: O(1) - Single API call (bulk operation)
    Space Complexity: O(1) - No additional storage
    
    Hard delete: Permanently removes all user data (items, bulk jobs, activity logs, OTPs, files).
    Preserves: user record only.
    Requires internal automation key.
    
    Returns:
        Function that permanently deletes all user data
        
    Usage:
        result = hard_delete_user_data(api_client, user_email, internal_key)
        # OR
        result = hard_delete_user_data(api_client, user_id=user_id, internal_key=key)
    """
    def _hard_delete_data(api_client, user_email: Optional[str] = None, user_id: Optional[str] = None,
                         internal_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Permanently delete all data for a user (complete reset).
        
        Args:
            api_client: APIClient instance
            user_email: User email (will be converted to user_id)
            user_id: User ID (ObjectId string) - if provided, user_email is ignored
            internal_key: Internal automation key (defaults to INTERNAL_AUTOMATION_KEY env var)
        
        Returns:
            Deletion result with counts if successful, None otherwise
        """
        # Get internal key
        if internal_key is None:
            internal_key = os.getenv('INTERNAL_AUTOMATION_KEY', 'flowhub-secret-automation-key-2025')
        
        # Get user_id from email if needed (requires MongoDB connection)
        if user_id is None and user_email:
            # Try to get user_id from MongoDB if connection available
            # This is optional - user can also pass user_id directly from actor
            try:
                from pymongo import MongoClient
                uri = os.getenv('MONGODB_URI')
                db_name = os.getenv('MONGODB_DB_NAME', 'test')
                if uri and db_name:
                    client = MongoClient(uri)
                    db = client[db_name]
                    user = db.users.find_one({"email": user_email})
                    client.close()
                    if user:
                        user_id = str(user['_id'])
                    else:
                        raise ValueError(f"User not found: {user_email}")
                else:
                    raise ValueError("MongoDB connection not available. Provide user_id directly from actor['user']['_id']")
            except Exception as e:
                raise ValueError(f"Cannot get user_id from email: {e}. Provide user_id directly from actor['user']['_id']")
        
        if user_id is None:
            raise ValueError("Either user_email or user_id must be provided")
        
        import requests
        url = f"{api_client.base_url}/internal/users/{user_id}/data"
        headers = {'x-internal-key': internal_key}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                deleted = result.get('deleted', {})
                items_deleted = deleted.get('items', 0)
                files_deleted = deleted.get('files', 0)
                bulk_jobs_deleted = deleted.get('bulk_jobs', 0)
                activity_logs_deleted = deleted.get('activity_logs', 0)
                otps_deleted = deleted.get('otps', 0)
                print(f"[API] Hard deleted all data for user {user_id}: "
                      f"{items_deleted} items, {files_deleted} files, "
                      f"{bulk_jobs_deleted} bulk jobs, {activity_logs_deleted} activity logs, "
                      f"{otps_deleted} OTPs")
                return result
            elif response.status_code == 401:
                print(f"[API] Unauthorized: Invalid internal key")
                return None
            elif response.status_code == 404:
                print(f"[API] User {user_id} not found")
                return None
            else:
                # Log full error response for debugging
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    print(f"[API] Failed to hard delete user data: {response.status_code} - {error_msg}")
                    print(f"[API] Full error response: {error_data}")
                except:
                    print(f"[API] Failed to hard delete user data: {response.status_code} - {response.text[:500]}")
                return None
        except Exception as e:
            print(f"[API] Error hard deleting user data: {e}")
            return None
    
    return _hard_delete_data


@pytest.fixture
def create_multiple_test_items() -> Callable:
    """
    Factory fixture: Create multiple test items via API (no duplicate check).
    
    Time Complexity: O(n) where n = number of items
    Space Complexity: O(n) for storing created items
    
    Returns:
        Function that creates multiple test items
        
    Usage:
        items = create_multiple_test_items(api_client, [
            {"name": "Item 1", ...},
            {"name": "Item 2", ...}
        ])
    """
    def _create_many(api_client, items_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        created_items = []
        
        for item_data in items_data:
            # Add test-data tag
            item_data['tags'] = item_data.get('tags', []) + ['test-data']
            
            response = api_client.post('/items', json=item_data)
            
            if response.status_code == 201:
                item = response.json()['data']
                created_items.append(item)
                print(f"[API] Created test item: {item['name']}")
            else:
                print(f"[API] Failed to create item: {response.status_code}")
        
        print(f"[API] Created {len(created_items)}/{len(items_data)} test items")
        return created_items
    
    return _create_many
