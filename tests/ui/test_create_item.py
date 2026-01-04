import pytest
import uuid
from playwright.sync_api import Page
from tests.pages.create_item_page import CreateItemPage

@pytest.mark.parametrize("load_index", range(1)) # Stress Test: Increase range(1) to range(N) for load.
@pytest.mark.parametrize("actor_fixture", ["admin_ui_actor", "editor_ui_actor"])
def test_create_digital_item(actor_fixture, load_index, request):
    """
    Flow 2: Create DIGITAL Item (Software category)
    Uses POM (CreateItemPage) for interactions.
    """
    actor = request.getfixturevalue(actor_fixture)
    api = actor['api']
    page = actor['page'] # Authenticated page
    
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
    create_page.navigate("https://testing-box.vercel.app/items/create")
    if "login" in page.url:
         raise RuntimeError("SmartUIAuth Failed: Redirected to Login")
    
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
def test_create_physical_item(actor_fixture, load_index, request):
    """
    Flow 2: Create PHYSICAL Item (Electronics category)
    """
    actor = request.getfixturevalue(actor_fixture)
    api = actor['api']
    page = actor['page']
    
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

    create_page.navigate("https://testing-box.vercel.app/items/create")
    
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
def test_create_service_item(actor_fixture, load_index, request):
    """
    Flow 2: Create SERVICE Item (Services category)
    """
    actor = request.getfixturevalue(actor_fixture)
    api = actor['api']
    page = actor['page']
    
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

    create_page.navigate("https://testing-box.vercel.app/items/create")
    
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

