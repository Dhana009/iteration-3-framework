
import pytest
from lib.pages.search_page import SearchPage

def test_debug_ui_state(editor_ui_actor, env_config, setup_api_seed_data):
    """
    Debug script to inspect the UI state (visible items, filters).
    Runs with editor access.
    Explicitly depends on setup_api_seed_data to ensure seeding happens.
    """
    actor = editor_ui_actor
    page = actor['page']
    frontend_base_url = env_config.FRONTEND_BASE_URL
    search_page = SearchPage(page)
    
    print(f"\n[DEBUG] Navigating to {frontend_base_url}/items...")
    search_page.navigate(f"{frontend_base_url}/items")
    search_page.wait_for_ready()
    
    # 1. Inspect Visible Items
    print("\n[DEBUG] --- Visible Items ---")
    names = search_page.get_all_item_names()
    print(f"[DEBUG] Count: {len(names)}")
    for name in names:
        print(f"[DEBUG] - {name}")
        
    # 2. Inspect Categories
    print("\n[DEBUG] --- Category Options ---")
    # Get all options from the select element
    options = page.locator(f'[data-testid="{search_page.FILTER_CATEGORY}"] option').all_text_contents()
    print(f"[DEBUG] Options: {options}")
    
    # 3. Inspect Status Options
    print("\n[DEBUG] --- Status Options ---")
    status_opts = page.locator(f'[data-testid="{search_page.FILTER_STATUS}"] option').all_text_contents()
    print(f"[DEBUG] Status Options: {status_opts}")

    # 4. Pagination Info
    print("\n[DEBUG] --- Pagination ---")
    try:
        info = search_page.get_pagination_info()
        print(f"[DEBUG] Info: {info}")
    except:
        print("[DEBUG] Pagination info not found")

    assert True # Always pass, just want output
