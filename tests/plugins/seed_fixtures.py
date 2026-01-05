"""
API-Based Data Insertion - Simple Insert If Not Exists

IMPORTANT: This module provides simple data insertion with duplicate checking.
No seed data concepts - just payload insertion with existence check.

Purpose:
    - Insert data if not exists for authenticated user
    - Check duplicates by name (efficient indexed query)
    - Simple payload insertion without seed tags or versioning

Usage:
    insert_data_if_not_exists(api_client, items_payload)
"""

import pytest
from typing import List, Dict, Any, Set


@pytest.fixture(scope="session")
def insert_data_if_not_exists():
    """
    Factory fixture: Insert data if not exists (simple duplicate check by name).
    
    Time Complexity: O(n) where n = number of items
    Space Complexity: O(m) where m = number of existing item names (for duplicate check)
    
    Algorithm:
    1. Fetch existing items by name (single query per unique name) - O(n) queries
    2. Filter out items that already exist - O(n) time
    3. Insert only new items - O(k) where k = new items
    
    Optimizations:
    - Uses indexed search query (name search is indexed)
    - Batches duplicate checks by unique names
    - Only inserts items that don't exist
    
    Returns:
        Function that inserts items if they don't exist for the authenticated user
        
    Usage:
        items = insert_data_if_not_exists(api_client, [
            {"name": "Item 1", "item_type": "DIGITAL", ...},
            {"name": "Item 2", "item_type": "PHYSICAL", ...}
        ])
    """
    def _insert(api_client, items_payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Insert items if they don't exist for the authenticated user.
        
        Duplicate Detection:
        - Checks by item name (case-sensitive)
        - Uses GET /items?search=name for efficient indexed query
        - Only inserts items that don't exist
        
        Args:
            api_client: Authenticated APIClient instance
            items_payload: List of item dictionaries to insert
            
        Returns:
            List of successfully created items
        """
        if not items_payload:
            return []
        
        # Step 1: Get existing item names for current user (O(n) queries, but indexed)
        # Optimization: Batch check by collecting unique names first
        unique_names: Set[str] = {item.get('name') for item in items_payload if item.get('name')}
        existing_names: Set[str] = set()
        
        # Check each unique name (indexed query - O(log m) per query where m = total items)
        for name in unique_names:
            try:
                response = api_client.get('/items', params={'search': name, 'limit': 1})
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    # Check if any item with this exact name exists
                    if items and any(item.get('name') == name for item in items):
                        existing_names.add(name)
            except Exception as e:
                print(f"[Insert] Error checking for item '{name}': {e}")
                # Continue - will attempt insert and handle 409 if duplicate
        
        # Step 2: Filter items that don't exist (O(n) time, O(n) space)
        items_to_insert = [
            item for item in items_payload 
            if item.get('name') not in existing_names
        ]
        
        if not items_to_insert:
            print(f"[Insert] All {len(items_payload)} items already exist")
            return []
        
        # Step 3: Insert new items (O(k) where k = new items)
        created_items = []
        for item in items_to_insert:
            try:
                # Don't modify original payload - create copy
                payload = item.copy()
                
                response = api_client.post('/items', json=payload)
                
                if response.status_code == 201:
                    data = response.json()
                    if data.get('status') == 'success' and 'data' in data:
                        created_items.append(data['data'])
                        print(f"[Insert] Created: {item.get('name', 'unknown')}")
                    else:
                        print(f"[Insert] Unexpected response for {item.get('name', 'unknown')}")
                elif response.status_code == 409:
                    # Duplicate detected (race condition or name collision)
                    print(f"[Insert] Item '{item.get('name', 'unknown')}' already exists (409)")
                elif response.status_code == 400:
                    # Validation error - log the actual error message
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', 'Unknown validation error')
                        print(f"[Insert] Validation error for '{item.get('name', 'unknown')}': {error_msg}")
                    except:
                        print(f"[Insert] Validation error for '{item.get('name', 'unknown')}': {response.status_code} - {response.text[:200]}")
                elif response.status_code == 403:
                    print(f"[Insert] Permission denied for item '{item.get('name', 'unknown')}'")
                    break  # Stop if user lacks permission
                else:
                    print(f"[Insert] Failed to create '{item.get('name', 'unknown')}': {response.status_code} - {response.text[:200]}")
            except Exception as e:
                print(f"[Insert] Error creating '{item.get('name', 'unknown')}': {e}")
        
        print(f"[Insert] Created {len(created_items)}/{len(items_payload)} items")
        return created_items
    
    return _insert
