import pytest
from lib.auth import SmartAuth
from lib.ui_auth import SmartUIAuth
from lib.seed import check_and_heal_seed
from utils.api_client import APIClient

@pytest.fixture(scope="function")
def admin_ui_actor(user_lease, browser, env_config):
    """
    UI-Optimized Fixture:
    1. Leases ADMIN.
    2. Ensures UI Session (SmartUIAuth - Reuse/Login).
    3. Returns {user, page, api}
    """
    lease_user = user_lease.acquire("ADMIN")
    api_url = env_config.API_BASE_URL
    ui_url = env_config.FRONTEND_BASE_URL
    
    # 1. API Auth (for Teardown/Setup) - Fast
    api_auth = SmartAuth(lease_user['email'], lease_user['password'], api_url)
    token, auth_user = api_auth.authenticate()
    api = APIClient(api_url, token=token)
    
    # 2. UI Auth (for Browser) - Reuse State
    ui_auth = SmartUIAuth(lease_user['email'], lease_user['password'], browser, ui_url)
    # Note: SmartUIAuth needs correct URL to login if state uses it.
    state_path = ui_auth.get_storage_state()
    
    # 3. Create Context with State
    context = browser.new_context(storage_state=state_path, base_url=ui_url)
    page = context.new_page()
    
    actor = {
        "user": auth_user,
        "password": lease_user['password'],
        "token": token,
        "api": api,
        "page": page,   # Pre-authenticated page
        "context": context
    }
    
    # Auto-Heal Seed - DISABLED (MongoDB seed setup handles this)
    # check_and_heal_seed(api, auth_user['_id'])
    
    yield actor
    
    # Cleanup
    context.close()

@pytest.fixture(scope="function")
def editor_ui_actor(user_lease, browser, env_config):
    """
    UI-Optimized Fixture for EDITOR:
    1. Leases EDITOR.
    2. Ensures UI Session (SmartUIAuth).
    3. Returns {user, page, api}
    """
    lease_user = user_lease.acquire("EDITOR")
    api_url = env_config.API_BASE_URL
    ui_url = env_config.FRONTEND_BASE_URL
    
    # 1. API Auth (Fast)
    api_auth = SmartAuth(lease_user['email'], lease_user['password'], api_url)
    token, auth_user = api_auth.authenticate()
    api = APIClient(api_url, token=token)
    
    # 2. UI Auth (Reuse State)
    ui_auth = SmartUIAuth(lease_user['email'], lease_user['password'], browser, ui_url)
    state_path = ui_auth.get_storage_state()
    
    # 3. Create Context
    context = browser.new_context(storage_state=state_path, base_url=ui_url)
    page = context.new_page()
    
    actor = {
        "user": auth_user,
        "password": lease_user['password'],
        "token": token,
        "api": api,
        "page": page,
        "context": context
    }
    
    # Auto-Heal Seed - DISABLED (MongoDB seed setup handles this)
    # check_and_heal_seed(api, auth_user['_id'])
    
    yield actor
    
    context.close()

@pytest.fixture(scope="function")
def viewer_ui_actor(user_lease, browser, env_config):
    """
    UI-Optimized Fixture for VIEWER:
    1. Leases VIEWER.
    2. Ensures UI Session (SmartUIAuth).
    3. Returns {user, page, api}
    """
    lease_user = user_lease.acquire("VIEWER")
    api_url = env_config.API_BASE_URL
    ui_url = env_config.FRONTEND_BASE_URL
    
    # 1. API Auth (for verification only)
    api_auth = SmartAuth(lease_user['email'], lease_user['password'], api_url)
    token, auth_user = api_auth.authenticate()
    api = APIClient(api_url, token=token)
    
    # 2. UI Auth (Reuse State)
    ui_auth = SmartUIAuth(lease_user['email'], lease_user['password'], browser, ui_url)
    state_path = ui_auth.get_storage_state()
    
    # 3. Create Context
    context = browser.new_context(storage_state=state_path, base_url=ui_url)
    page = context.new_page()
    
    actor = {
        "user": auth_user,
        "password": lease_user['password'],
        "token": token,
        "api": api,
        "page": page,
        "context": context
    }
    
    # NO SEED HEALING FOR VIEWER (read-only role)
    
    yield actor
    
    context.close()
