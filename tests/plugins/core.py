import pytest
from lib.users import UserLease
from lib.auth import SmartAuth
from utils.api_client import APIClient

@pytest.fixture(scope="session")
def worker_id_val(worker_id):
    """
    Expose xdist worker_id or default to master.
    """
    return worker_id

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
def auth_context(user_lease, env_config):
    """
    Authenticates the leased user using Smart Gate logic.
    Returns {token, user, api}
    """
    if not user_lease.user:
        # If no user leased yet (e.g. called directly without acquire), 
        # we might need to acquire one? 
        # But usually user_lease is just the mechanics.
        # Tests using auth_context assume they got a user.
        # Actually, user_lease is the LEASE MANAGER. 
        # Typically the test calls user_lease.acquire().
        # But if auth_context is autouse or requested, it needs a user.
        # Simplest: auth_context acquires "default" user if none?
        # Let's stick to explicit acquiring if possible, BUT:
        # ensure_seed_data in `lib/seed.py` asks for `auth_context`.
        # So auth_context MUST acquire a user if one isn't active.
        # For simplicity, let's acquire "ADMIN" or just a user.
        # BUT: parallel tests need unique users.
        pass

    # NOTE: The previous pattern was:
    # 1. user_lease fixture yields the manager.
    # 2. test calls lease.acquire().
    # 3. auth_context usage implies we want an auto-authenticated user.
    # Let's assume auth_context acquires a generic VIEWER or defaults?
    # Or, does it check if user_lease object has an active user?
    # The UserLease class manages state.
    
    # If we look at previous `conftest.py` logic (which I don't have handy right now but can infer):
    # It likely expected `user_lease` to be used. 
    # Let's implement robustly.
    
    # Strategy: acquire a EDITOR/VIEWER if not specified?
    # Better: auth_context acquires "EDITOR" by default for seed verification tests.
    
    user = user_lease.acquire("EDITOR") # Default role
    
    email = user['email']
    password = user['password']
    base_url = env_config.API_BASE_URL
    
    auth = SmartAuth(email, password, base_url)
    token, user_data = auth.authenticate()
    
    return {
        "token": token, 
        "user": user_data, 
        "api": APIClient(base_url, token=token)
    }
