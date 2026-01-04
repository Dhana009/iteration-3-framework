import pytest
import os
from lib.users import UserLease
from lib.auth import SmartAuth
from lib.seed import check_and_heal_seed
from utils.api_client import APIClient

@pytest.fixture(scope="session", autouse=True)
def setup_mongodb_seed(env_config, create_seed_for_user):
    """
    Set up baseline seed data via MongoDB before all tests
    Runs ONCE at session start (if ENABLE_SEED_SETUP=true)
    """
    # Feature flag check
    if os.getenv('ENABLE_SEED_SETUP', 'false').lower() != 'true':
        print("\n[SeedSetup] Skipped (ENABLE_SEED_SETUP=false)")
        return
    
    # List of users to setup seed data for
    user_emails = [
        "admin1@test.com",
        "admin2@test.com",
        "editor1@test.com",
        "editor2@test.com",
        "viewer1@test.com"
    ]
    
    print("\n[SeedSetup] Setting up MongoDB seed data...")
    total_items = 0
    
    for email in user_emails:
        try:
            count = create_seed_for_user(email)
            total_items += count
        except ValueError as e:
            print(f"[SeedSetup] ⚠️  Skipping {email}: {e}")
        except Exception as e:
            print(f"[SeedSetup] ❌ Error for {email}: {e}")
    
    print(f"[SeedSetup] ✅ Total: {total_items} items created for {len(user_emails)} users")

# OLD FIXTURE - DISABLED (replaced by setup_mongodb_seed)
# Kept for backward compatibility if needed
@pytest.fixture(scope="session")  # Removed autouse=True
def ensure_admin_global_seed(worker_id_val, env_config):
    """
    OLD: Session-scoped fixture to ensure Admin's global seed data exists.
    
    NOTE: This is now DISABLED (autouse=True removed).
    The new setup_mongodb_seed fixture handles seed data creation.
    This fixture is kept for backward compatibility if explicitly called.
    """
    print("\n[GlobalSeed-OLD] Running old seed healer (should not see this)...")
    
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
        
        print(f"[GlobalSeed-OLD] Admin seed verified for {admin_user['email']}")
    finally:
        # 4. Release admin
        lease.release()
