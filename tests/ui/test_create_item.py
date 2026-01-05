import pytest
import uuid
import os
from playwright.sync_api import Page
from lib.pages.create_item_page import CreateItemPage

@pytest.mark.parametrize("load_index", range(1)) 
@pytest.mark.parametrize("actor_fixture", ["admin_ui_actor", "editor_ui_actor"])
def test_create_digital_item(actor_fixture, load_index, request, env_config, 
                            create_test_item, delete_test_item, insert_data_if_not_exists,
                            update_test_item, mongodb_connection):
    """
    Flow 2: Create DIGITAL Item (Software category)
    Uses POM (CreateItemPage) for interactions.
    Integrates with new data management fixtures:
    - Verifies global seed data exists
    - Uses insert_data_if_not_exists for test-specific data
    - Uses update_test_item for updates
    - Uses delete operations for cleanup
    """
    actor = request.getfixturevalue(actor_fixture)
    api = actor['api']
    page = actor['page'] # Authenticated page
    user = actor['user']
    frontend_base_url = env_config.FRONTEND_BASE_URL
    
    # --- Verify Global Seed Data Exists ---
    print("\n[Flow 2] Verifying global seed data exists...")
    enable_seed_setup = os.getenv('ENABLE_SEED_SETUP', 'false').lower() == 'true'
    if enable_seed_setup:
        seed_count = mongodb_connection.items.count_documents({
            'created_by': user['_id'],
            'tags': {'$in': ['seed']}
        })
        print(f"[Flow 2] Global seed data: {seed_count} items for {user['email']}")
        assert seed_count > 0, "Global seed data should exist when ENABLE_SEED_SETUP=true"
    else:
        print("[Flow 2] Global seed data disabled (ENABLE_SEED_SETUP=false)")
    # ----------------------------------------
    
    # --- Integration: On-Demand Data Insertion ---
    print("\n[Flow 2] Using insert_data_if_not_exists for test-specific data...")
    unique_id = uuid.uuid4().hex[:8]
    test_items = insert_data_if_not_exists(api, [{
        "name": f"Flow2 Test Data {unique_id}",
        "description": "Test data for Flow 2 integration - this meets the minimum length requirement",
        "item_type": "DIGITAL",
        "price": 5.00,
        "category": "Testing",
        "download_url": "https://example.com/flow2-test.zip",
        "file_size": 512
    }])
    
    if test_items:
        test_item_id = test_items[0]['_id']
        test_item_version = test_items[0]['version']
        print(f"[Flow 2] Created test data item: {test_item_id}")
        
        # Test update operation
        updated = update_test_item(api, test_item_id, {"price": 7.50}, test_item_version)
        if updated:
            print(f"[Flow 2] Updated test data item: price = {updated['price']}")
        
        # Cleanup test data
        delete_test_item(api, test_item_id)
        print("[Flow 2] Cleaned up test data")
    # ----------------------------------------------
    
    # Initialize POM
    create_page = CreateItemPage(page)
    
    # 1. Generate Ephemeral Data
    unique_id = uuid.uuid4().hex[:8]
    item_name = f"POM Test Digital {unique_id}"
    
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
    request.addfinalizer(cleanup)
    
    print(f"\n[UI] Starting Flow 2 (POM) for {item_name}...")

    # 2. Navigate
    print("[UI] Navigating to Create Page...")
    create_page.navigate(f"{frontend_base_url}/items/create")
    if "login" in page.url:
         raise RuntimeError("SmartUIAuth Failed: Redirected to Login")
    
    print("[UI] Waiting for page ready...")
    create_page.wait_for_ready()
    
    # 3. Form Interaction via POM
    print("[UI] Filling Form via POM...")
    create_page.fill_common_fields(
        name=item_name,
        description=f"POM Desc {unique_id}",
        price="10.99",
        category="Software"
    )
    
    create_page.select_type("DIGITAL")
    create_page.fill_digital_fields(
        url="https://example.com/pom-file.zip",
        size="2048"
    )
    
    print("[UI] Submitting...")
    create_page.submit()
    
    # 4. Verify
    create_page.verify_success()
    print("[UI] SUCCESS.")


@pytest.mark.parametrize("load_index", range(1))
@pytest.mark.parametrize("actor_fixture", ["admin_ui_actor", "editor_ui_actor"])
def test_create_physical_item(actor_fixture, load_index, request, env_config):
    """
    Flow 2: Create PHYSICAL Item (Electronics category)
    """
    actor = request.getfixturevalue(actor_fixture)
    api = actor['api']
    page = actor['page']
    frontend_base_url = env_config.FRONTEND_BASE_URL
    
    create_page = CreateItemPage(page)
    
    unique_id = uuid.uuid4().hex[:8]
    item_name = f"POM Test Physical {unique_id}"
    
    def cleanup():
        search_resp = api.get("/items", params={"search": item_name})
        if search_resp.status_code == 200:
            items = search_resp.json().get('items', [])
            target = next((i for i in items if i['name'] == item_name), None)
            if target:
                api.delete(f"/items/{target['_id']}")
    request.addfinalizer(cleanup)
    
    print(f"\n[UI-Physical] Starting Flow 2 (POM) for {item_name}...")

    create_page.navigate(f"{frontend_base_url}/items/create")
    
    create_page.fill_common_fields(
        name=item_name,
        description=f"POM Physical {unique_id}",
        price="100.00",
        category="Electronics"
    )
    
    create_page.select_type("PHYSICAL")
    create_page.fill_physical_fields(
        weight="2.5",
        length="20",
        width="15",
        height="10"
    )
    
    create_page.submit()
    create_page.verify_success()
    print("[UI-Physical] SUCCESS.")


@pytest.mark.parametrize("load_index", range(1))
@pytest.mark.parametrize("actor_fixture", ["admin_ui_actor", "editor_ui_actor"])
def test_create_service_item(actor_fixture, load_index, request, env_config):
    """
    Flow 2: Create SERVICE Item (Services category)
    """
    actor = request.getfixturevalue(actor_fixture)
    api = actor['api']
    page = actor['page']
    frontend_base_url = env_config.FRONTEND_BASE_URL
    
    create_page = CreateItemPage(page)
    
    unique_id = uuid.uuid4().hex[:8]
    item_name = f"POM Test Service {unique_id}"
    
    def cleanup():
        search_resp = api.get("/items", params={"search": item_name})
        if search_resp.status_code == 200:
            items = search_resp.json().get('items', [])
            target = next((i for i in items if i['name'] == item_name), None)
            if target:
                api.delete(f"/items/{target['_id']}")
    request.addfinalizer(cleanup)
    
    print(f"\n[UI-Service] Starting Flow 2 (POM) for {item_name}...")

    create_page.navigate(f"{frontend_base_url}/items/create")
    
    create_page.fill_common_fields(
        name=item_name,
        description=f"POM Service {unique_id}",
        price="75.00",
        category="Services"
    )
    
    create_page.select_type("SERVICE")
    create_page.fill_service_fields(duration="8")
    
    create_page.submit()
    create_page.verify_success()
    print("[UI-Service] SUCCESS.")
