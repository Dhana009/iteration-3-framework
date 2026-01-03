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
from fixtures.seed import check_and_heal_seed
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
