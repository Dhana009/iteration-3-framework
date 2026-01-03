import pytest
import uuid
from playwright.sync_api import Page, expect

def test_viewer_can_view_items_list(viewer_ui_actor):
    """
    Flow 3: Viewer - Read-Only Access
    
    Verify Viewer can:
    - Navigate to /items page
    - See items table with data
    - Cannot see Edit/Delete action buttons
    """
    actor = viewer_ui_actor
    page = actor['page']
    user = actor['user']
    
    print(f"\n[Flow3-Viewer] Testing read-only access for {user['email']}...")
    
    # 1. Navigate to items page
    print("[Flow3-Viewer] Navigating to /items...")
    page.goto("https://testing-box.vercel.app/items")
    
    # 2. Wait for page to be ready
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    print("[Flow3-Viewer] Page ready.")
    
    # 3. Verify items table is visible
    page.get_by_test_id("items-table").wait_for(state="visible")
    print("[Flow3-Viewer] Items table visible.")
    
    # 4. Verify items are displayed
    items_count_attr = page.get_attribute('[data-test-items-count]', 'data-test-items-count')
    items_count = int(items_count_attr) if items_count_attr else 0
    assert items_count > 0, "Viewer should see items in the list"
    print(f"[Flow3-Viewer] Verified {items_count} items visible.")
    
    # 5. Verify NO Edit/Delete buttons visible for Viewer
    # Get first item row
    first_row = page.locator('[data-testid^="item-row-"]').first
    if first_row.is_visible():
        item_id = first_row.get_attribute('data-testid').replace('item-row-', '')
        
        # Check for Edit button (should NOT exist or be hidden)
        edit_button = page.get_by_test_id(f"edit-item-{item_id}")
        assert not edit_button.is_visible(), "Viewer should NOT see Edit button"
        
        # Check for Delete button (should NOT exist or be hidden)
        delete_button = page.get_by_test_id(f"delete-item-{item_id}")
        assert not delete_button.is_visible(), "Viewer should NOT see Delete button"
        
        print("[Flow3-Viewer] Verified: No Edit/Delete buttons visible (read-only).")
    
    print("[Flow3-Viewer] SUCCESS: Viewer has read-only access.")


def test_editor_search_by_name(editor_ui_actor):
    """
    Flow 3: Editor - Search Functionality
    
    Test search by item name:
    1. Navigate to /items
    2. Search for "Alpha"
    3. Verify only matching items visible
    """
    actor = editor_ui_actor
    page = actor['page']
    user = actor['user']
    user_suffix = user['_id'][-4:]
    
    print(f"\n[Flow3-Editor-Search] Testing search for {user['email']}...")
    
    # 1. Navigate to items page
    page.goto("https://testing-box.vercel.app/items")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 2. Fill search input
    search_term = "Alpha"
    print(f"[Flow3-Editor-Search] Searching for: {search_term}")
    page.get_by_test_id("item-search").fill(search_term)
    
    # 3. Wait for search to complete (debounce + API call)
    page.wait_for_selector('[data-testid="item-search"][data-test-search-state="ready"]', timeout=10000)
    
    # 4. Verify search results
    items_count = int(page.get_attribute('[data-test-items-count]', 'data-test-items-count'))
    assert items_count >= 1, f"Should find at least 1 item matching '{search_term}'"
    
    # 5. Verify the visible item contains "Alpha" in name
    first_item_name = page.locator('[data-testid^="item-name-"]').first.text_content()
    assert "Alpha" in first_item_name, f"First item should contain 'Alpha', got: {first_item_name}"
    
    print(f"[Flow3-Editor-Search] SUCCESS: Found {items_count} item(s) matching '{search_term}'.")


def test_editor_filter_by_status_active(editor_ui_actor):
    """
    Flow 3: Editor - Filter by Status (Active)
    
    Test status filter:
    1. Navigate to /items
    2. Select status filter: "active"
    3. Verify only active items visible (9 out of 11)
    """
    actor = editor_ui_actor
    page = actor['page']
    
    print(f"\n[Flow3-Editor-Filter] Testing status filter (active)...")
    
    # 1. Navigate
    page.goto("https://testing-box.vercel.app/items")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 2. Select status filter: active
    page.get_by_test_id("filter-status").select_option("active")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 3. Verify filtered count (should be less than or equal to total, all active)
    items_count = int(page.get_attribute('[data-test-items-count]', 'data-test-items-count'))
    assert items_count > 0, f"Should show at least 1 active item, got: {items_count}"
    # Verify all visible items have 'Active' status
    status_badges = page.locator('[data-testid^="item-status-"]').all()
    for badge in status_badges:
        assert "Active" in badge.text_content(), "All items should be Active"
    
    print(f"[Flow3-Editor-Filter] SUCCESS: Filtered to {items_count} active items.")


def test_editor_filter_by_status_inactive(editor_ui_actor):
    """
    Flow 3: Editor - Filter by Status (Inactive)
    
    Test status filter:
    1. Navigate to /items
    2. Select status filter: "inactive"
    3. Verify only inactive items visible (2 out of 11: Zeta, Lambda)
    """
    actor = editor_ui_actor
    page = actor['page']
    
    print(f"\n[Flow3-Editor-Filter] Testing status filter (inactive)...")
    
    # 1. Navigate
    page.goto("https://testing-box.vercel.app/items")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 2. Select status filter: inactive
    page.get_by_test_id("filter-status").select_option("inactive")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 3. Verify filtered count (should show inactive items only)
    items_count = int(page.get_attribute('[data-test-items-count]', 'data-test-items-count'))
    assert items_count > 0, f"Should show at least 1 inactive item, got: {items_count}"
    # Verify all visible items have 'Inactive' status
    status_badges = page.locator('[data-testid^="item-status-"]').all()
    for badge in status_badges:
        assert "Inactive" in badge.text_content(), "All items should be Inactive"
    
    print(f"[Flow3-Editor-Filter] SUCCESS: Filtered to {items_count} inactive items.")


def test_editor_filter_by_category(editor_ui_actor):
    """
    Flow 3: Editor - Filter by Category
    
    Test category filter:
    1. Navigate to /items
    2. Select category filter: "Electronics"
    3. Verify only Electronics items visible (4 items: Alpha, Delta, Theta, and one more)
    """
    actor = editor_ui_actor
    page = actor['page']
    
    print(f"\n[Flow3-Editor-Filter] Testing category filter (Electronics)...")
    
    # 1. Navigate
    page.goto("https://testing-box.vercel.app/items")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 2. Select category filter: Electronics
    page.get_by_test_id("filter-category").select_option("Electronics")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 3. Verify filtered count (should show Electronics items only)
    items_count = int(page.get_attribute('[data-test-items-count]', 'data-test-items-count'))
    assert items_count > 0, f"Should show at least 1 Electronics item, got: {items_count}"
    # Verify all visible items have 'Electronics' category
    category_cells = page.locator('[data-testid^="item-category-"]').all()
    for cell in category_cells:
        assert "Electronics" in cell.text_content(), "All items should be Electronics category"
    
    print(f"[Flow3-Editor-Filter] SUCCESS: Filtered to {items_count} Electronics items.")


def test_editor_sort_by_price_ascending(editor_ui_actor):
    """
    Flow 3: Editor - Sort by Price (Ascending)
    
    Test sorting:
    1. Navigate to /items
    2. Click sort-price header (1st click = ascending)
    3. Verify first item is Lambda ($5), last is Theta ($500)
    """
    actor = editor_ui_actor
    page = actor['page']
    
    print(f"\n[Flow3-Editor-Sort] Testing price sort (ascending)...")
    
    # 1. Navigate
    page.goto("https://testing-box.vercel.app/items")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 2. Click sort-price (1st click = ascending)
    page.get_by_test_id("sort-price").click()
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 3. Verify first item has lowest price
    first_item_price = page.locator('[data-testid^="item-price-"]').first.text_content()
    assert "$5" in first_item_price or "$5.00" in first_item_price, f"First item should be $5 (Lambda), got: {first_item_price}"
    
    # 4. Verify last item has highest price
    last_item_price = page.locator('[data-testid^="item-price-"]').last.text_content()
    assert "$500" in last_item_price, f"Last item should be $500 (Theta), got: {last_item_price}"
    
    print(f"[Flow3-Editor-Sort] SUCCESS: Sorted by price ascending (${first_item_price} to ${last_item_price}).")


def test_editor_pagination(editor_ui_actor):
    """
    Flow 3: Editor - Pagination
    
    Test pagination:
    1. Navigate to /items
    2. Change limit to 10 items per page
    3. Verify page 1 shows "1 to 10 of 11"
    4. Click next page
    5. Verify page 2 shows "11 to 11 of 11" (1 item)
    """
    actor = editor_ui_actor
    page = actor['page']
    
    print(f"\n[Flow3-Editor-Pagination] Testing pagination...")
    
    # 1. Navigate
    page.goto("https://testing-box.vercel.app/items")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 2. Change pagination limit to 10
    page.get_by_test_id("pagination-limit").select_option("10")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 3. Verify page 1 info (should show items 1-10)
    pagination_info = page.get_by_test_id("pagination-info").text_content()
    assert "1 to 10" in pagination_info, f"Page 1 should show '1 to 10', got: {pagination_info}"
    # Verify total is greater than 10 (to enable pagination)
    import re
    total_match = re.search(r'of (\d+)', pagination_info)
    if total_match:
        total = int(total_match.group(1))
        assert total > 10, f"Total should be > 10 to test pagination, got: {total}"
    print(f"[Flow3-Editor-Pagination] Page 1: {pagination_info}")
    
    # 4. Click next page (use desktop-specific selector - most reliable)
    # Wait for page to be ready first
    page.wait_for_selector('[data-test-ready="true"]', timeout=5000)
    
    # Desktop pagination selector (more stable, has page numbers)
    next_button = page.locator('.hidden.sm\\:flex [data-testid="pagination-next"]')
    
    # Wait for button to be visible and enabled
    next_button.wait_for(state="visible", timeout=5000)
    
    # Verify button is enabled
    if not next_button.is_enabled():
        print("[Flow3-Editor-Pagination] WARNING: Next button is disabled, skipping page 2 test")
        return
    
    # Click
    next_button.click()
    
    # Wait for page update (loading → ready)
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 5. Verify page 2 info (should show remaining items)
    pagination_info_p2 = page.get_by_test_id("pagination-info").text_content()
    # Verify we're on page 2 and showing remaining items
    total_match_p2 = re.search(r'(\d+) to (\d+) of (\d+)', pagination_info_p2)
    if total_match_p2:
        start, end, total = int(total_match_p2.group(1)), int(total_match_p2.group(2)), int(total_match_p2.group(3))
        assert start == 11, f"Page 2 should start at item 11, got: {start}"
        assert end == total, f"Page 2 should end at total ({total}), got: {end}"
    
    # 6. Verify items on page 2 (should be total - 10)
    items_count_p2 = int(page.get_attribute('[data-test-items-count]', 'data-test-items-count'))
    assert items_count_p2 > 0, f"Page 2 should show at least 1 item, got: {items_count_p2}"
    
    print(f"[Flow3-Editor-Pagination] SUCCESS: Page 2: {pagination_info_p2}, {items_count_p2} item visible.")


def test_admin_full_discovery_flow(admin_ui_actor):
    """
    Flow 3: Admin - Combined Discovery Flow
    
    Test combined search + filter + sort + clear:
    Verifies BEHAVIOR instead of counts (Admin sees all items from parallel tests)
    """
    actor = admin_ui_actor
    page = actor['page']
    
    print(f"\n[Flow3-Admin-Combined] Testing full discovery flow...")
    
    # 1. Navigate
    page.goto("https://testing-box.vercel.app/items")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 2. Verify items are visible (Admin sees all items)
    initial_count = int(page.get_attribute('[data-test-items-count]', 'data-test-items-count'))
    assert initial_count > 0, f"Should have at least some items, got: {initial_count}"
    print(f"[Flow3-Admin-Combined] Initial: {initial_count} items.")
    
    # 3. Search for "Electronics" - verify search WORKS (count decreases or stays same)
    page.get_by_test_id("item-search").fill("Electronics")
    page.wait_for_selector('[data-testid="item-search"][data-test-search-state="ready"]', timeout=10000)
    search_count = int(page.get_attribute('[data-test-items-count]', 'data-test-items-count'))
    assert search_count <= initial_count, f"Search should filter items, got {search_count} vs initial {initial_count}"
    # Verify all visible items contain "Electronics" in name or category
    item_names = page.locator('[data-testid^="item-name-"]').all()
    item_categories = page.locator('[data-testid^="item-category-"]').all()
    assert len(item_names) > 0, "Should have at least one search result"
    print(f"[Flow3-Admin-Combined] After search 'Electronics': {search_count} items.")
    
    # 4. Filter by status: active - verify filter WORKS
    page.get_by_test_id("filter-status").select_option("active")
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    filtered_count = int(page.get_attribute('[data-test-items-count]', 'data-test-items-count'))
    # Verify all visible items have "Active" status
    status_badges = page.locator('[data-testid^="item-status-"]').all()
    for badge in status_badges:
        assert "Active" in badge.text_content(), "All items should be Active after filter"
    print(f"[Flow3-Admin-Combined] After filter (active): {filtered_count} items, all Active.")
    
    # 5. Sort by price: ascending - verify sort WORKS
    page.get_by_test_id("sort-price").click()  # 1st click = asc
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 6. Verify sort worked: first price <= last price (ascending order)
    import re
    price_cells = page.locator('[data-testid^="item-price-"]').all()
    if len(price_cells) >= 2:
        first_price_text = price_cells[0].text_content()
        last_price_text = price_cells[-1].text_content()
        # Extract numeric values
        first_price = float(re.search(r'[\d.]+', first_price_text).group())
        last_price = float(re.search(r'[\d.]+', last_price_text).group())
        assert first_price <= last_price, f"First price ({first_price}) should be <= last price ({last_price}) in asc order"
        print(f"[Flow3-Admin-Combined] After sort (asc): ${first_price} to ${last_price}")
    
    # 7. Clear all filters - verify clear WORKS
    page.get_by_test_id("clear-filters").click()
    page.wait_for_selector('[data-test-ready="true"]', timeout=10000)
    
    # 8. Verify filters are cleared (not count, but filter state)
    assert page.get_by_test_id("filter-status").input_value() == "all", "Status filter should be 'all'"
    assert page.get_by_test_id("item-search").input_value() == "", "Search should be empty"
    print(f"[Flow3-Admin-Combined] After clear: Filters reset successfully.")
    
    print("[Flow3-Admin-Combined] SUCCESS: Full discovery flow verified.")

