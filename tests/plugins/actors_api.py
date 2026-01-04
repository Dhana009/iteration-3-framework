import pytest
from lib.auth import SmartAuth
from lib.seed import check_and_heal_seed
from utils.api_client import APIClient

@pytest.fixture(scope="function")
def admin_actor(user_lease, env_config):
    """
    High-level fixture that:
    1. Leases ADMIN
    2. Authenticates
    3. Returns API client
    """
    lease_user = user_lease.acquire("ADMIN")
    base_url = env_config.API_BASE_URL
    
    auth = SmartAuth(lease_user['email'], lease_user['password'], base_url)
    token, auth_user = auth.authenticate()
    
    context = {
        "user": auth_user, # Use backend data (with _id)
        "password": lease_user['password'], # Needed for UI Login
        "token": token,
        "api": APIClient(base_url, token=token)
    }
    
    # Auto-Heal Seed
    check_and_heal_seed(context['api'], auth_user['_id'])
    
    return context

@pytest.fixture(scope="function")
def editor_actor(user_lease, env_config):
    """
    Same for EDITOR
    """
    lease_user = user_lease.acquire("EDITOR")
    base_url = env_config.API_BASE_URL

    auth = SmartAuth(lease_user['email'], lease_user['password'], base_url)
    token, auth_user = auth.authenticate()
    
    context = {
        "user": auth_user,
        "token": token,
        "api": APIClient(base_url, token=token)
    }
    
    check_and_heal_seed(context['api'], auth_user['_id'])
    return context

@pytest.fixture(scope="function")
def viewer_actor(user_lease, env_config):
    """
    Same for VIEWER
    """
    lease_user = user_lease.acquire("VIEWER")
    base_url = env_config.API_BASE_URL

    auth = SmartAuth(lease_user['email'], lease_user['password'], base_url)
    token, auth_user = auth.authenticate()
    
    context = {
        "user": auth_user,
        "token": token,
        "api": APIClient(base_url, token=token)
    }
    
    # Viewers typically don't own seed data
    return context
