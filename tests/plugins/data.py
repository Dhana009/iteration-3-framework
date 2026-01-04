import pytest
import os
from lib.users import UserLease
from lib.auth import SmartAuth
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

# OLD FIXTURE REMOVED - Replaced by setup_mongodb_seed
# The old API-based seed healing approach has been replaced with MongoDB direct insertion
