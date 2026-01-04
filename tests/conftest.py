import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

# Ensure root dir is in path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from fixtures.users import UserLease
from fixtures.auth import SmartAuth
from fixtures.ui_auth import SmartUIAuth
from fixtures.seed import check_and_heal_seed
from utils.api_client import APIClient
import json
from utils.file_lock import AtomicLock

CONFIG_PATH = ROOT_DIR / 'config' / 'user_pool.json'
LOCK_PATH = ROOT_DIR / 'config' / 'user_pool.lock'

def pytest_sessionstart(session):
    """
    Morning Roll Call: Reset User Pool on Session Start.
    Runs ONLY on the Master node (before workers start).
    Ensures recovery from previous crashes by un-reserving all users.
    """
    if not hasattr(session.config, 'workerinput'):
        # Inline imports for safety
        import json
        from pathlib import Path
        from utils.file_lock import AtomicLock
        
        # Robust path resolution using pytest's rootdir
        root = Path(session.config.rootdir)
        config_path = root / 'config' / 'user_pool.json'
        # AtomicLock expects Union[str, Path], so we can pass Path directly now
        lock_path = root / 'config' / 'user_pool.lock'
        
        if not config_path.exists():
            print(f"[Morning Roll Call] Config not found at {config_path}")
            return
        
        try:
            with AtomicLock(lock_path, timeout_seconds=10):
                with open(config_path, 'r+') as f:
                    pool = json.load(f)
                    reset_count = 0
                    
                    for role in pool:
                        for user in pool[role]:
                            if user.get('reserved_by'):
                                user['reserved_by'] = None
                                reset_count += 1
                    
                    if reset_count > 0:
                        f.seek(0)
                        json.dump(pool, f, indent=4)
                        f.truncate()
                        print(f"[Morning Roll Call] Released {reset_count} stuck users.")
                    else:
                        print("[Morning Roll Call] User pool is clean.")
        except Exception as e:
            print(f"[Morning Roll Call] Error: {e}")


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


# ---------- Page Object Factory ----------

class PageFactory:
    """
    Lazy-loading factory for Page Objects.
    Usage: pages.login_page.do_login()
    """
    def __init__(self, page):
        self.page = page
        self._login_page = None
        self._create_item = None
        # Add future pages here

    @property
    def create_item(self):
        # Lazy import to avoid circular dep
        from tests.pages.create_item_page import CreateItemPage
        if not self._create_item:
            self._create_item = CreateItemPage(self.page)
        return self._create_item

    # Example for Login Page (if we add it later)
    # @property
    # def login(self):
    #     if not self._login_page:
    #         self._login_page = LoginPage(self.page)
    #     return self._login_page


@pytest.fixture
def pages(page):
    """
    Fixture that returns a PageFactory.
    Requires the standard playwright 'page' fixture.
    """
    return PageFactory(page)
