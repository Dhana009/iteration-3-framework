import pytest
import os
import sys
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

# Ensure root dir is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from fixtures.users import UserLease
from fixtures.auth import SmartAuth
from fixtures.ui_auth import SmartUIAuth
from fixtures.seed import check_and_heal_seed
from utils.api_client import APIClient

@pytest.fixture(scope="session")
def worker_id_val(worker_id):
    """
    Expose xdist worker_id or default to master.
    """
    return worker_id

@pytest.fixture(scope="session", autouse=True)
def ensure_admin_global_seed(worker_id_val):
    """
    Session-scoped fixture to ensure Admin's global seed data exists.
    Runs ONCE before any tests in the session.
    This creates the 11-item "Infrastructure" seed data for Admin.
    """
    print("\n[GlobalSeed] Ensuring Admin global seed data...")
    
    # 1. Lease admin1 temporarily
    lease = UserLease(worker_id_val)
    admin_user = lease.acquire("ADMIN")
    
    try:
        # 2. Authenticate
        auth = SmartAuth(admin_user['email'], admin_user['password'])
        token, user_data = auth.authenticate()
        api = APIClient(token=token)
        
        # 3. Heal seed data
        check_and_heal_seed(api, user_data['_id'])
        
        print(f"[GlobalSeed] Admin seed verified for {admin_user['email']}")
    finally:
        # 4. Release admin
        lease.release()


@pytest.fixture(scope="function")
def user_lease(worker_id_val):
    """
    Leases a user for the specific test function.
    Releases automatically after test.
    """
    lease = UserLease(worker_id_val)
    yield lease
    lease.release()

@pytest.fixture(scope="function")
def auth_context(user_lease):
    """
    Authenticates the leased user using Smart Gate logic.
    """
    if not user_lease.user:
        # Default to ADMIN if no role specified, or raise error?
        # Better: Test must call user_lease.acquire('ROLE')? 
        # Actually, standard pytest pattern:
        # We need a parametric fixture or just manual acquire in logic?
        # Let's make it simpler: The test requests 'admin_user'.
        pass 
        # See dedicated admin_actor fixture below.
    return None

@pytest.fixture(scope="function")
def admin_actor(user_lease):
    """
    High-level fixture that:
    1. Leases ADMIN
    2. Authenticates
    3. Returns API client
    """
    lease_user = user_lease.acquire("ADMIN")
    auth = SmartAuth(lease_user['email'], lease_user['password'])
    token, auth_user = auth.authenticate()
    
    context = {
        "user": auth_user, # Use backend data (with _id)
        "password": lease_user['password'], # Needed for UI Login
        "token": token,
        "api": APIClient(token=token)
    }
    
    # Auto-Heal Seed
    check_and_heal_seed(context['api'], auth_user['_id'])
    
    return context

@pytest.fixture(scope="function")
def editor_actor(user_lease):
    """
    Same for EDITOR
    """
    lease_user = user_lease.acquire("EDITOR")
    auth = SmartAuth(lease_user['email'], lease_user['password'])
    token, auth_user = auth.authenticate()
    
    context = {
        "user": auth_user,
        "token": token,
        "api": APIClient(token=token)
    }
    
    check_and_heal_seed(context['api'], auth_user['_id'])
    return context

@pytest.fixture(scope="function")
def viewer_actor(user_lease):
    """
    Same for VIEWER
    """
    lease_user = user_lease.acquire("VIEWER")
    auth = SmartAuth(lease_user['email'], lease_user['password'])
    token, auth_user = auth.authenticate()
    
    context = {
        "user": auth_user,
        "token": token,
        "api": APIClient(token=token)
    }
    
    # Viewers typically don't own seed data, but we might verify they see it?
    # No seed healer needed for viewer usually.
    return context

@pytest.fixture(scope="function")
def admin_ui_actor(user_lease, browser):
    """
    UI-Optimized Fixture:
    1. Leases ADMIN.
    2. Ensures UI Session (SmartUIAuth - Reuse/Login).
    3. Returns {user, page, api}
    """
    lease_user = user_lease.acquire("ADMIN")
    
    # 1. API Auth (for Teardown/Setup) - Fast
    api_auth = SmartAuth(lease_user['email'], lease_user['password'])
    token, auth_user = api_auth.authenticate()
    api = APIClient(token=token)
    
    # 2. UI Auth (for Browser) - Reuse State
    ui_auth = SmartUIAuth(lease_user['email'], lease_user['password'], browser)
    state_path = ui_auth.get_storage_state()
    
    # 3. Create Context with State
    context = browser.new_context(storage_state=state_path)
    page = context.new_page()
    
    actor = {
        "user": auth_user,
        "password": lease_user['password'],
        "token": token,
        "api": api,
        "page": page,   # Pre-authenticated page
        "context": context
    }
    
    # Auto-Heal Seed
    check_and_heal_seed(api, auth_user['_id'])
    
    yield actor
    
    # Cleanup
    context.close()

@pytest.fixture(scope="function")
def editor_ui_actor(user_lease, browser):
    """
    UI-Optimized Fixture for EDITOR:
    1. Leases EDITOR.
    2. Ensures UI Session (SmartUIAuth).
    3. Returns {user, page, api}
    """
    lease_user = user_lease.acquire("EDITOR")
    
    # 1. API Auth (Fast)
    api_auth = SmartAuth(lease_user['email'], lease_user['password'])
    token, auth_user = api_auth.authenticate()
    api = APIClient(token=token)
    
    # 2. UI Auth (Reuse State)
    ui_auth = SmartUIAuth(lease_user['email'], lease_user['password'], browser)
    state_path = ui_auth.get_storage_state()
    
    # 3. Create Context
    context = browser.new_context(storage_state=state_path)
    page = context.new_page()
    
    actor = {
        "user": auth_user,
        "password": lease_user['password'],
        "token": token,
        "api": api,
        "page": page,
        "context": context
    }
    
    # Auto-Heal Seed
    check_and_heal_seed(api, auth_user['_id'])
    
    yield actor
    
    context.close()

@pytest.fixture(scope="function")
def viewer_ui_actor(user_lease, browser):
    """
    UI-Optimized Fixture for VIEWER:
    1. Leases VIEWER.
    2. Ensures UI Session (SmartUIAuth).
    3. Returns {user, page, api}
    
    NOTE: No seed data creation for Viewer (read-only role).
    """
    lease_user = user_lease.acquire("VIEWER")
    
    # 1. API Auth (for verification only)
    api_auth = SmartAuth(lease_user['email'], lease_user['password'])
    token, auth_user = api_auth.authenticate()
    api = APIClient(token=token)
    
    # 2. UI Auth (Reuse State)
    ui_auth = SmartUIAuth(lease_user['email'], lease_user['password'], browser)
    state_path = ui_auth.get_storage_state()
    
    # 3. Create Context
    context = browser.new_context(storage_state=state_path)
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

