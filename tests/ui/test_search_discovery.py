import pytest
import re
from tests.pages.search_page import SearchPage

def test_viewer_can_view_items_list(viewer_ui_actor):
    """
    Flow 3: Viewer - Read-Only Access
    """
    actor = viewer_ui_actor
    page = actor['page']
    user = actor['user']
    
    search_page = SearchPage(page)
    
    print(f"\n[Flow3-Viewer] Testing read-only access for {user['email']}...")
    
    # 1. Navigate
    print("[Flow3-Viewer] Navigating to /items...")
    search_page.navigate("https://testing-box.vercel.app/items")
    search_page.wait_for_ready()
    
    # 2. Verify items visible
    count = search_page.get_items_count()
    assert count > 0, "Viewer should see items in the list"
    print(f"[Flow3-Viewer] Verified {count} items visible.")
    
    # 3. Verify NO Edit/Delete buttons visible
    # Get ID of first item to check buttons
    first_row = page.locator(search_page.ITEM_ROW_PREFIX).first
    if first_row.is_visible():
        item_id = first_row.get_attribute('data-testid').replace('item-row-', '')
        
        assert not search_page.is_edit_button_visible(item_id), "Viewer should NOT see Edit button"
        assert not search_page.is_delete_button_visible(item_id), "Viewer should NOT see Delete button"
        
        print("[Flow3-Viewer] Verified: No Edit/Delete buttons visible (read-only).")
    
    print("[Flow3-Viewer] SUCCESS.")


def test_editor_search_by_name(editor_ui_actor):
    """
    Flow 3: Editor - Search Functionality
    """
    actor = editor_ui_actor
    page = actor['page']
    
    search_page = SearchPage(page)
    
    print(f"\n[Flow3-Editor-Search] Testing search...")
    
    search_page.navigate("https://testing-box.vercel.app/items")
    search_page.wait_for_ready()
    
    # Search
    term = "Alpha"
    print(f"[Flow3-Editor-Search] Searching for: {term}")
    search_page.search(term)
    
    # Verify
    count = search_page.get_items_count()
    assert count >= 1, f"Should find at least 1 item matching '{term}'"
    
    names = search_page.get_all_item_names()
    assert "Alpha" in names[0], f"First item should contain 'Alpha', got: {names[0]}"
    
    print(f"[Flow3-Editor-Search] SUCCESS: Found {count} items.")


def test_editor_filter_by_status_active(editor_ui_actor):
    """
    Flow 3: Editor - Filter by Status (Active)
    """
    actor = editor_ui_actor
    page = actor['page']
    
    search_page = SearchPage(page)
    
    print(f"\n[Flow3-Editor-Filter] Testing status filter (active)...")
    
    search_page.navigate("https://testing-box.vercel.app/items")
    search_page.wait_for_ready()
    
    # Filter
    search_page.filter_by_status("active")
    
    # Verify
    count = search_page.get_items_count()
    assert count > 0, f"Should show at least 1 active item"
    
    statuses = search_page.get_all_item_statuses()
    for status in statuses:
        assert "Active" in status, "All items should be Active"
    
    print(f"[Flow3-Editor-Filter] SUCCESS: Filtered to {count} active items.")


def test_editor_filter_by_status_inactive(editor_ui_actor):
    """
    Flow 3: Editor - Filter by Status (Inactive)
    """
    actor = editor_ui_actor
    page = actor['page']
    search_page = SearchPage(page)
    
    print(f"\n[Flow3-Editor-Filter] Testing status filter (inactive)...")
    
    search_page.navigate("https://testing-box.vercel.app/items")
    search_page.wait_for_ready()
    
    search_page.filter_by_status("inactive")
    
    count = search_page.get_items_count()
    assert count > 0, f"Should show at least 1 inactive item"
    
    statuses = search_page.get_all_item_statuses()
    for status in statuses:
        assert "Inactive" in status, "All items should be Inactive"
    
    print(f"[Flow3-Editor-Filter] SUCCESS: Filtered to {count} inactive items.")


def test_editor_filter_by_category(editor_ui_actor):
    """
    Flow 3: Editor - Filter by Category
    """
    actor = editor_ui_actor
    page = actor['page']
    search_page = SearchPage(page)
    
    print(f"\n[Flow3-Editor-Filter] Testing category filter (Electronics)...")
    
    search_page.navigate("https://testing-box.vercel.app/items")
    search_page.wait_for_ready()
    
    search_page.filter_by_category("Electronics")
    
    count = search_page.get_items_count()
    assert count > 0, "Should show at least 1 Electronics item"
    
    categories = search_page.get_all_item_categories()
    for cat in categories:
        assert "Electronics" in cat, "All items should be Electronics"
    
    print(f"[Flow3-Editor-Filter] SUCCESS: Filtered to {count} Electronics items.")


def test_editor_sort_by_price_ascending(editor_ui_actor):
    """
    Flow 3: Editor - Sort by Price (Ascending)
    """
    actor = editor_ui_actor
    page = actor['page']
    search_page = SearchPage(page)
    
    print(f"\n[Flow3-Editor-Sort] Testing price sort (ascending)...")
    
    search_page.navigate("https://testing-box.vercel.app/items")
    search_page.wait_for_ready()
    
    search_page.sort_by_price()
    
    prices = search_page.get_all_item_prices_float()
    assert len(prices) >= 2, "Need at least 2 items to test sort"
    
    # Lambda ($5) vs Theta ($500) ideally
    assert prices[0] <= prices[-1], f"First price ({prices[0]}) > Last price ({prices[-1]})"
    
    print(f"[Flow3-Editor-Sort] SUCCESS: Sorted ${prices[0]} to ${prices[-1]}.")


def test_editor_pagination(editor_ui_actor):
    """
    Flow 3: Editor - Pagination
    """
    actor = editor_ui_actor
    page = actor['page']
    search_page = SearchPage(page)
    
    print(f"\n[Flow3-Editor-Pagination] Testing pagination...")
    
    search_page.navigate("https://testing-box.vercel.app/items")
    search_page.wait_for_ready()
    
    # Change limit
    search_page.set_pagination_limit("10")
    
    # Check Page 1
    info = search_page.get_pagination_info()
    assert "1 to 10" in info, f"Page 1 info mismatch: {info}"
    
    # Next Page
    clicked = search_page.go_to_next_page()
    if not clicked:
        print("[Flow3-Editor-Pagination] WARNING: Next button disabled.")
        return

    # Check Page 2
    info_p2 = search_page.get_pagination_info()
    # Should say "11 to 11" (if 11 items total) or similar
    match = re.search(r'(\d+) to', info_p2)
    if match:
        start = int(match.group(1))
        assert start == 11, f"Page 2 should start at 11, got {start}"
    
    count_p2 = search_page.get_items_count()
    assert count_p2 > 0, "Page 2 should show items"
    
    print(f"[Flow3-Editor-Pagination] SUCCESS: Page 2 verified.")


def test_admin_full_discovery_flow(admin_ui_actor):
    """
    Flow 3: Admin - Combined Discovery Flow
    """
    actor = admin_ui_actor
    page = actor['page']
    search_page = SearchPage(page)
    
    print(f"\n[Flow3-Admin-Combined] Testing full discovery flow...")
    
    search_page.navigate("https://testing-box.vercel.app/items")
    search_page.wait_for_ready()
    
    initial = search_page.get_items_count()
    assert initial > 0
    
    # 1. Search
    search_page.search("Electronics")
    search_count = search_page.get_items_count()
    assert search_count <= initial
    
    # 2. Filter Active
    search_page.filter_by_status("active")
    filtered_count = search_page.get_items_count()
    for badge in search_page.get_all_item_statuses():
        assert "Active" in badge
        
    # 3. Sort Price
    search_page.sort_by_price()
    prices = search_page.get_all_item_prices_float()
    if len(prices) >= 2:
        assert prices[0] <= prices[-1]
        
    # 4. Clear
    search_page.clear_filters()
    
    # Verify cleared state
    assert page.get_by_test_id("filter-status").input_value() == "all"
    assert page.get_by_test_id("item-search").input_value() == ""
    
    print("[Flow3-Admin-Combined] SUCCESS.")

