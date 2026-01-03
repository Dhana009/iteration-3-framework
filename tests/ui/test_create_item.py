import pytest
import uuid
import json
from playwright.sync_api import Page, expect

@pytest.mark.parametrize("load_index", range(1)) # Stress Test: Increase range(1) to range(N) for load.
@pytest.mark.parametrize("actor_fixture", ["admin_ui_actor", "editor_ui_actor"])
def test_create_item_ui_flow(actor_fixture, load_index, request, page: Page):
    """
    Flow 2: Create Item (UI) + Teardown (API)
    Runs for both ADMIN and EDITOR.
    'load_index' is used to multiply the tests for parallel stress testing.
    """
    # Dynamically get the fixture based on name
    actor = request.getfixturevalue(actor_fixture)
    
    user = actor['user']
    api = actor['api']
    # NOTE: We must use the page from the actor (authenticated context), 
    # NOT the default 'page' fixture which is fresh/unauthenticated!
    # However, request.getfixturevalue might instantiate it.
    # Actually, the actor fixture YIELDS the actor dict which contains 'page'.
    page = actor['page']
    
    # 1. Generate Ephemeral Data
    unique_id = uuid.uuid4().hex[:8]
    item_name = f"UI Test Item {unique_id}"
    
    # Define Cleanup Closure
    def cleanup():
        print(f"\n[Teardown] Searching for {item_name} to delete...")
        search_resp = api.get("/items", params={"search": item_name})
        if search_resp.status_code == 200:
            items = search_resp.json().get('items', [])
            target = next((i for i in items if i['name'] == item_name), None)
            if target:
                print(f"[Teardown] Deleting {target['_id']}...")
                api.delete(f"/items/{target['_id']}")
            else:
                print("[Teardown] Not found (Clean).")
        else:
            print(f"[Teardown] Search failed: {search_resp.status_code}")
            
    # Register Teardown
    request.addfinalizer(cleanup)
    
    print(f"\n[UI] Starting Flow 2 for {item_name}...")

    # 2. Login & Navigate (Reuse Strategy)
    # The 'page' is already logged in via storageState.
    # We just explicitly go to the Create page.
    print("[UI] Navigating to Create Page (Authenticated Context)...")
    page.goto("https://testing-box.vercel.app/items/create")
    page.wait_for_load_state("domcontentloaded")
    
    # Verify we didn't bounce to login
    if "login" in page.url:
         raise RuntimeError("SmartUIAuth Failed: Redirected to Login")
    page.wait_for_load_state("domcontentloaded")
    
    # 3. Fill Form
    print("[UI] Filling Form...")
    # Selectors from 07-FLOW2-UI-SELECTORS.md
    page.get_by_test_id("item-name").fill(item_name)
    page.get_by_test_id("item-description").fill(f"Description for {unique_id}")
    page.get_by_test_id("item-price").fill("10.99")
    page.get_by_test_id("item-category").fill("Software")
    
    # Select Type (Triggers Conditional Fields)
    page.get_by_test_id("item-type").select_option("DIGITAL")
    page.get_by_test_id("digital-fields").wait_for(state="visible")
    
    # Fill Digital Fields
    page.get_by_test_id("item-download-url").fill("https://example.com/file.zip")
    page.get_by_test_id("item-file-size").fill("1024")
    
    # 4. Submit
    print("[UI] Submitting...")
    page.get_by_test_id("create-item-submit").click()
    
    # 5. Verify Success
    # Toast check
    toast = page.get_by_test_id("toast-success")
    expect(toast).to_be_visible(timeout=10000)
    expect(toast).to_contain_text("Item created")
    
    # Verify Redirect
    expect(page).to_have_url("https://testing-box.vercel.app/items")
    print("[UI] SUCCESS: Toast verified and redirected.")
    
    # Execute Cleanup (Handled by finalizer)
    pass
