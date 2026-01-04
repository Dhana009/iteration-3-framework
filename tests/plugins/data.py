import pytest
from lib.users import UserLease
from lib.auth import SmartAuth
from lib.seed import check_and_heal_seed
from utils.api_client import APIClient

@pytest.fixture(scope="session", autouse=True)
def ensure_admin_global_seed(worker_id_val, env_config):
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
        base_url = env_config.API_BASE_URL
        auth = SmartAuth(admin_user['email'], admin_user['password'], base_url)
        token, user_data = auth.authenticate()
        api = APIClient(base_url, token=token)
        
        # 3. Heal seed data
        check_and_heal_seed(api, user_data['_id'])
        
        print(f"[GlobalSeed] Admin seed verified for {admin_user['email']}")
    finally:
        # 4. Release admin
        lease.release()
