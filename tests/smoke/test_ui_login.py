import pytest
from playwright.sync_api import Page, expect

def test_admin_dashboard_access(admin_actor, page: Page, env_config):
    """
    Scenario:
    1. Infrastructure: Get Valid Token for Admin (from Smart Gate).
    2. Logic: Inject Token -> Navigate to Dashboard (Bypass Login Form).
    3. Verify: We are logged in.
    """
    frontend_url = env_config.FRONTEND_BASE_URL
    user = admin_actor['user']
    token = admin_actor['token']
    
    print(f"\n[UI] Launching Browser for {user['email']}...")
    
    # 1. Inject Auth (Bypass Login Screen)
    # Go to base first
    page.goto(frontend_url) 
    
    # Inject Token into LocalStorage
    print(f"[UI] Injecting Token: {token[:10]}...")
    import json
    user_json = json.dumps(user)
    
    page.evaluate(f"""() => {{
        window.localStorage.setItem('token', '{token}');
        window.localStorage.setItem('user', JSON.stringify({user_json}));
    }}""")
    
    # 2. Navigate to Dashboard/Items
    print("[UI] Navigating to /items...")
    target_url = f"{frontend_url}/items"
    page.goto(target_url)
    
    # 3. Verify
    print(f"[UI] Current URL: {page.url}")
    # Simple check: we shouldn't be redirected back to login
    # And URL should contain /items
    # Ensure strict match if we trust environment 
    # But safe check:
    expect(page).to_have_url(f"{frontend_url}/items")
    
    # Slow down so user can see it
    page.wait_for_timeout(3000) 
