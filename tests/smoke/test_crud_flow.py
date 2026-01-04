import pytest
import uuid

def test_crud_lifecycle_admin(admin_actor):
    """
    Scenario:
    1. Infrastructure: Leases ADMIN, Authenticates, Ensures Seed Data.
    2. Logic: Create Item -> Verify -> Delete.
    """
    client = admin_actor['api']
    item_name = f"Smoke Test Item {uuid.uuid4().hex[:6]}"
    
    # 1. CREATE
    payload = {
        "name": item_name,
        "description": "Transient smoke test item",
        "item_type": "DIGITAL",
        "price": 5.00,
        "category": "Software",
        "download_url": "https://example.com/smoke",
        "file_size": 1024
    }
    print(f"\n[Smoke] Creating {item_name}...")
    resp = client.post("/items", json=payload)
    assert resp.status_code == 201, f"Create failed: {resp.text}"
    item_id = resp.json()['data']['_id']
    
    # 2. READ & VERIFY
    print(f"[Smoke] Verifying {item_id}...")
    resp = client.get(f"/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()['data']['name'] == item_name
    
    # 3. DELETE
    print(f"[Smoke] Deleting {item_id}...")
    resp = client.delete(f"/items/{item_id}")
    assert resp.status_code == 200
    
    # 4. VERIFY DELETION (Soft Delete check)
    resp = client.get(f"/items/{item_id}")
    if resp.status_code == 200:
        data = resp.json().get('data', {})
        assert data.get('is_active') is False or data.get('deleted_at'), "Item should be inactive/deleted"
    else:
        # 404 is also acceptable depending on API implementation details for deleted items
        assert resp.status_code == 404

    print("\n[Smoke] SUCCESS: Infinite Reliability Achieved.")


def test_crud_with_fixtures(admin_actor, create_test_item, delete_test_item):
    """
    NEW: Test using new fixtures
    
    Demonstrates:
    1. Create item via create_test_item fixture
    2. Verify item exists
    3. Delete item via delete_test_item fixture
    4. Verify deletion
    """
    client = admin_actor['api']
    
    print("\n[Smoke-Fixtures] Creating item via fixture...")
    
    # 1. CREATE using fixture (with unique name to avoid 409)
    item = create_test_item(client, {
        "name": f"Smoke Test with Fixture {uuid.uuid4().hex[:6]}",
        "description": "Testing new fixture integration in smoke tests",
        "item_type": "DIGITAL",
        "price": 9.99,
        "category": "Testing",
        "download_url": "https://example.com/fixture-test",
        "file_size": 512
    })
    
    assert item is not None
    assert 'test-data' in item['tags']
    item_id = item['_id']
    print(f"[Smoke-Fixtures] Created: {item['name']} (ID: {item_id})")
    
    # 2. VERIFY
    print(f"[Smoke-Fixtures] Verifying {item_id}...")
    resp = client.get(f"/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()['data']['_id'] == item_id
    
    # 3. DELETE using fixture
    print(f"[Smoke-Fixtures] Deleting via fixture...")
    success = delete_test_item(client, item_id)
    assert success
    
    # 4. VERIFY DELETION
    print(f"[Smoke-Fixtures] Verifying deletion...")
    resp = client.get(f"/items/{item_id}")
    if resp.status_code == 200:
        assert resp.json()['data'].get('is_active') is False
    else:
        assert resp.status_code == 404
    
    print("\n[Smoke-Fixtures] SUCCESS: New fixtures working in smoke tests!")
