"""
Reusable API Fixtures for Test Data Management

Purpose: Provide factory fixtures for API operations (create/delete test items)
"""

import pytest
from typing import Callable, Dict, Any


@pytest.fixture
def create_test_item() -> Callable:
    """
    Factory fixture: Create test item via API
    
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
def delete_test_item() -> Callable:
    """
    Factory fixture: Delete test item via API (soft delete)
    
    Returns:
        Function that deletes a test item
        
    Usage:
        success = delete_test_item(api_client, item_id)
    """
    def _delete(api_client, item_id: str) -> bool:
        response = api_client.delete(f'/items/{item_id}')
        
        if response.status_code == 200:
            print(f"[API] Deleted test item: {item_id}")
            return True
        else:
            print(f"[API] ⚠️  Failed to delete item {item_id}: {response.status_code}")
            return False
    
    return _delete


@pytest.fixture
def create_multiple_test_items() -> Callable:
    """
    Factory fixture: Create multiple test items via API
    
    Returns:
        Function that creates multiple test items
        
    Usage:
        items = create_multiple_test_items(api_client, [
            {"name": "Item 1", ...},
            {"name": "Item 2", ...}
        ])
    """
    def _create_many(api_client, items_data: list) -> list:
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
                print(f"[API] ⚠️  Failed to create item: {response.status_code}")
        
        print(f"[API] Created {len(created_items)}/{len(items_data)} test items")
        return created_items
    
    return _create_many
