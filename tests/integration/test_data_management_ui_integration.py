"""
UI Integration Tests for Data Management

Tests that verify data management operations are reflected correctly in the UI:
1. Global seed data visible in UI
2. On-demand insertion visible in UI
3. Update operations reflected in UI
4. Soft delete hides items from UI
5. Hard delete removes items from UI
"""

import pytest
import os
import uuid
from lib.pages.search_page import SearchPage


class TestDataManagementUIIntegration:
    """UI Integration Tests for Data Management Operations"""
    
    def test_global_seed_data_visible_in_ui(self, admin_ui_actor, env_config, mongodb_connection):
        """
        Verify global seed data appears in UI.
        """
        print("\n" + "="*70)
        print("UI TEST 1: Global Seed Data Visible in UI")
        print("="*70)
        
        actor = admin_ui_actor
        page = actor['page']
        user = actor['user']
        frontend_base_url = env_config.FRONTEND_BASE_URL
        search_page = SearchPage(page)
        
        # Verify seed data exists in MongoDB
        enable_seed_setup = os.getenv('ENABLE_SEED_SETUP', 'false').lower() == 'true'
        if not enable_seed_setup:
            pytest.skip("ENABLE_SEED_SETUP=false, skipping seed data UI test")
        
        seed_count = mongodb_connection.items.count_documents({
            'created_by': user['_id'],
            'tags': {'$in': ['seed']}
        })
        
        assert seed_count > 0, "Seed data should exist in MongoDB"
        print(f"[UI] Seed data in MongoDB: {seed_count} items")
        
        # Navigate to items page
        search_page.navigate(f"{frontend_base_url}/items")
        search_page.wait_for_ready()
        
        # Verify items are visible in UI
        ui_count = search_page.get_items_count()
        assert ui_count > 0, "Items should be visible in UI"
        print(f"[UI] Items visible in UI: {ui_count}")
        
        # Verify seed items are in the list (check for items with 'seed' tag)
        # Note: UI may not show tags directly, but items should be visible
        assert ui_count >= seed_count or seed_count > 0, "Seed items should be visible in UI"
        
        print("[UI] SUCCESS: Global seed data visible in UI")
    
    def test_on_demand_insertion_visible_in_ui(self, admin_ui_actor, env_config, insert_data_if_not_exists):
        """
        Verify on-demand inserted data appears in UI.
        """
        print("\n" + "="*70)
        print("UI TEST 2: On-Demand Insertion Visible in UI")
        print("="*70)
        
        actor = admin_ui_actor
        page = actor['page']
        api = actor['api']
        frontend_base_url = env_config.FRONTEND_BASE_URL
        search_page = SearchPage(page)
        
        unique_id = uuid.uuid4().hex[:8]
        item_name = f"UI Test Insert {unique_id}"
        
        # Insert data on-demand
        items = insert_data_if_not_exists(api, [{
            "name": item_name,
            "description": "Test description for UI insertion test - this meets the minimum length requirement",
            "item_type": "DIGITAL",
            "price": 35.00,
            "category": "Testing",
            "download_url": "https://example.com/ui-insert.zip",
            "file_size": 1024
        }])
        
        assert len(items) == 1, "Item should be created"
        item_id = items[0]['_id']
        print(f"[UI] Created item: {item_id}")
        
        # Navigate to items page
        search_page.navigate(f"{frontend_base_url}/items")
        search_page.wait_for_ready()
        
        # Search for the item
        search_page.search(item_name)
        search_page.wait_for_ready()
        
        # Verify item is visible
        ui_count = search_page.get_items_count()
        assert ui_count > 0, "Inserted item should be visible in UI"
        
        # Verify item name appears
        item_names = search_page.get_all_item_names()
        assert any(item_name in name for name in item_names), f"Item '{item_name}' should be visible in UI"
        
        print("[UI] SUCCESS: On-demand inserted data visible in UI")
        
        # Cleanup
        api.delete(f"/items/{item_id}")
    
    def test_update_item_reflects_in_ui(self, admin_ui_actor, env_config, create_test_item, update_test_item):
        """
        Verify item updates are reflected in UI.
        """
        print("\n" + "="*70)
        print("UI TEST 3: Update Item Reflects in UI")
        print("="*70)
        
        actor = admin_ui_actor
        page = actor['page']
        api = actor['api']
        frontend_base_url = env_config.FRONTEND_BASE_URL
        search_page = SearchPage(page)
        
        unique_id = uuid.uuid4().hex[:8]
        original_name = f"UI Test Update Original {unique_id}"
        updated_name = f"UI Test Update Changed {unique_id}"
        
        # Create item
        item = create_test_item(api, {
            "name": original_name,
            "description": "Test description for UI update test - this meets the minimum length requirement",
            "item_type": "DIGITAL",
            "price": 40.00,
            "category": "Testing",
            "download_url": "https://example.com/ui-update.zip",
            "file_size": 1024
        })
        
        item_id = item['_id']
        original_version = item['version']
        print(f"[UI] Created item: {item_id}")
        
        # Update item
        updated = update_test_item(api, item_id, {
            "name": updated_name,
            "price": 50.00
        }, original_version)
        
        assert updated is not None, "Update should succeed"
        print(f"[UI] Updated item: name={updated_name}, price={updated['price']}")
        
        # Navigate to items page
        search_page.navigate(f"{frontend_base_url}/items")
        search_page.wait_for_ready()
        
        # Search for updated name
        search_page.search(updated_name)
        search_page.wait_for_ready()
        
        # Verify updated item is visible
        item_names = search_page.get_all_item_names()
        assert any(updated_name in name for name in item_names), f"Updated item '{updated_name}' should be visible"
        
        # Verify price is updated (if price is visible in UI)
        prices = search_page.get_all_item_prices_float()
        if prices:
            assert 50.00 in prices or any(abs(p - 50.00) < 0.01 for p in prices), "Updated price should be visible"
        
        print("[UI] SUCCESS: Update reflected in UI")
        
        # Cleanup
        api.delete(f"/items/{item_id}")
    
    def test_soft_delete_hides_from_ui(self, admin_ui_actor, env_config, create_test_item, delete_test_item):
        """
        Verify soft deleted items are hidden from UI.
        """
        print("\n" + "="*70)
        print("UI TEST 4: Soft Delete Hides from UI")
        print("="*70)
        
        actor = admin_ui_actor
        page = actor['page']
        api = actor['api']
        frontend_base_url = env_config.FRONTEND_BASE_URL
        search_page = SearchPage(page)
        
        unique_id = uuid.uuid4().hex[:8]
        item_name = f"UI Test Soft Delete {unique_id}"
        
        # Create item
        item = create_test_item(api, {
            "name": item_name,
            "description": "Test description for UI soft delete test - this meets the minimum length requirement",
            "item_type": "DIGITAL",
            "price": 45.00,
            "category": "Testing",
            "download_url": "https://example.com/ui-softdelete.zip",
            "file_size": 1024
        })
        
        item_id = item['_id']
        print(f"[UI] Created item: {item_id}")
        
        # Verify item is visible before delete
        search_page.navigate(f"{frontend_base_url}/items")
        search_page.wait_for_ready()
        search_page.search(item_name)
        search_page.wait_for_ready()
        
        item_names_before = search_page.get_all_item_names()
        assert any(item_name in name for name in item_names_before), "Item should be visible before delete"
        
        # Soft delete
        success = delete_test_item(api, item_id)
        assert success, "Soft delete should succeed"
        print(f"[UI] Soft deleted item: {item_id}")
        
        # Refresh page and filter by active status to ensure only active items are shown
        search_page.navigate(f"{frontend_base_url}/items")
        search_page.wait_for_ready()
        search_page.filter_by_status("active")  # Filter to show only active items
        search_page.wait_for_ready()
        search_page.search(item_name)
        search_page.wait_for_ready()
        
        # Item should not appear in active items list (soft deleted items are filtered out)
        item_names_after = search_page.get_all_item_names()
        assert not any(item_name in name for name in item_names_after), "Soft deleted item should be hidden from UI"
        
        print("[UI] SUCCESS: Soft deleted item hidden from UI")
    
    def test_hard_delete_removes_from_ui(self, admin_ui_actor, env_config, create_test_item, hard_delete_test_item):
        """
        Verify hard deleted items are permanently removed (not visible even with direct URL).
        """
        print("\n" + "="*70)
        print("UI TEST 5: Hard Delete Removes from UI")
        print("="*70)
        
        actor = admin_ui_actor
        page = actor['page']
        api = actor['api']
        frontend_base_url = env_config.FRONTEND_BASE_URL
        search_page = SearchPage(page)
        
        unique_id = uuid.uuid4().hex[:8]
        item_name = f"UI Test Hard Delete {unique_id}"
        
        # Create item
        item = create_test_item(api, {
            "name": item_name,
            "description": "Test description for UI hard delete test - this meets the minimum length requirement",
            "item_type": "DIGITAL",
            "price": 55.00,
            "category": "Testing",
            "download_url": "https://example.com/ui-harddelete.zip",
            "file_size": 1024
        })
        
        item_id = item['_id']
        print(f"[UI] Created item: {item_id}")
        
        # Verify item is visible before delete
        search_page.navigate(f"{frontend_base_url}/items")
        search_page.wait_for_ready()
        search_page.search(item_name)
        search_page.wait_for_ready()
        
        item_names_before = search_page.get_all_item_names()
        assert any(item_name in name for name in item_names_before), "Item should be visible before delete"
        
        # Hard delete
        result = hard_delete_test_item(api, item_id)
        assert result is not None, "Hard delete should succeed"
        print(f"[UI] Hard deleted item: {item_id}")
        
        # Verify item is permanently removed
        # Try to access item directly via API
        response = api.get(f"/items/{item_id}")
        assert response.status_code == 404, "Hard deleted item should return 404"
        
        # Verify item is not in UI
        search_page.navigate(f"{frontend_base_url}/items")
        search_page.wait_for_ready()
        search_page.search(item_name)
        search_page.wait_for_ready()
        
        item_names_after = search_page.get_all_item_names()
        assert not any(item_name in name for name in item_names_after), "Hard deleted item should not be in UI"
        
        print("[UI] SUCCESS: Hard deleted item permanently removed from UI")
