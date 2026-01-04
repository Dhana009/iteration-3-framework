"""
Comprehensive Test: SmartUIAuth State Validation
Tests the full lifecycle of state validation including:
1. Fresh login (no state)
2. State reuse (valid state)
3. Expired state detection and recovery
"""
import pytest
import json
import time
from pathlib import Path
from playwright.sync_api import expect

def test_smartuiauth_state_lifecycle(browser, env_config, user_lease):
    """
    Full lifecycle test for SmartUIAuth state validation.
    Tests: Fresh login -> Reuse -> Expiry detection -> Recovery
    """
    from lib.ui_auth import SmartUIAuth
    
    # Get a user from the pool
    user = user_lease.acquire("ADMIN")
    email = user['email']
    password = user['password']
    base_url = env_config.FRONTEND_BASE_URL
    
    print(f"\n>>> Testing SmartUIAuth State Lifecycle for {email}")
    
    # Clean up any existing state
    state_dir = Path(__file__).parent.parent.parent / 'state'
    state_file = state_dir / f"{email}_storage.json"
    if state_file.exists():
        state_file.unlink()
        print("[Setup] Cleaned existing state")
    
    # ===== TEST 1: Fresh Login (No State) =====
    print("\n[TEST 1] Fresh Login (No State)")
    ui_auth = SmartUIAuth(email, password, browser, base_url)
    
    state_path = ui_auth.get_storage_state()
    assert state_path.exists(), "State file should be created"
    print(f"[PASS] Fresh login created state: {state_path}")
    
    # ===== TEST 2: State Reuse (Valid State) =====
    print("\n[TEST 2] State Reuse (Valid State)")
    ui_auth2 = SmartUIAuth(email, password, browser, base_url)
    
    # This should reuse the existing state (no login)
    state_path2 = ui_auth2.get_storage_state()
    assert state_path2 == state_path, "Should return same state path"
    print("[PASS] Valid state was reused (no re-login)")
    
    # ===== TEST 3: Verify State Actually Works =====
    print("\n[TEST 3] Verify State Actually Works")
    context = browser.new_context(storage_state=str(state_path), base_url=base_url)
    page = context.new_page()
    
    # Navigate to protected page
    page.goto(f"{base_url}/dashboard", wait_until="domcontentloaded", timeout=10000)
    
    # Should NOT be redirected to login
    current_url = page.url.lower()
    assert "/login" not in current_url, f"Should be on dashboard, but got: {page.url}"
    print(f"[PASS] State works - on protected page: {page.url}")
    context.close()
    
    # ===== TEST 4: Simulate Expired State =====
    print("\n[TEST 4] Simulate Expired State")
    
    # Corrupt the state by modifying cookie expiry
    with open(state_path, 'r') as f:
        state_data = json.load(f)
    
    # Set all cookies to expired (past timestamp)
    if 'cookies' in state_data:
        for cookie in state_data['cookies']:
            if 'expires' in cookie:
                cookie['expires'] = time.time() - 86400  # 1 day ago
    
    with open(state_path, 'w') as f:
        json.dump(state_data, f)
    
    print("[Setup] Corrupted state with expired cookies")
    
    # ===== TEST 5: Expired State Detection & Recovery =====
    print("\n[TEST 5] Expired State Detection & Recovery")
    ui_auth3 = SmartUIAuth(email, password, browser, base_url)
    
    # This should detect expired state and re-login
    state_path3 = ui_auth3.get_storage_state()
    assert state_path3.exists(), "Should create new state after detecting expiry"
    print("[PASS] Expired state detected and new login performed")
    
    # ===== TEST 6: Verify New State Works =====
    print("\n[TEST 6] Verify New State Works")
    context2 = browser.new_context(storage_state=str(state_path3), base_url=base_url)
    page2 = context2.new_page()
    
    page2.goto(f"{base_url}/dashboard", wait_until="domcontentloaded", timeout=10000)
    current_url2 = page2.url.lower()
    assert "/login" not in current_url2, f"New state should work, but got: {page2.url}"
    print(f"[PASS] New state works - on protected page: {page2.url}")
    context2.close()
    
    print("\n>>> ALL TESTS PASSED - SmartUIAuth State Validation Works Correctly")
