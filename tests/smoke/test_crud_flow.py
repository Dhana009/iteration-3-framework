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
