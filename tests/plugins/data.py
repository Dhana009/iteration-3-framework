import pytest
import os
from fixtures.seed_factory import get_user_seed_data

@pytest.fixture(scope="session", autouse=True)
def setup_mongodb_seed(create_seed_for_user):
    """
    Set up baseline seed data via MongoDB before all tests
    Runs ONCE at session start (if ENABLE_SEED_SETUP=true)
    
    Uses test data factory to generate user-specific seed data.
    Each user can have different seed data based on their role or custom configuration.
    
    Optimized for memory efficiency: Generates seed data on-demand (lazy evaluation)
    instead of pre-generating all data upfront.
    """
    # Feature flag check FIRST (O(1) - early exit optimization)
    if os.getenv('ENABLE_SEED_SETUP', 'false').lower() != 'true':
        print("\n[SeedSetup] Skipped (ENABLE_SEED_SETUP=false)")
        return
    
    # Single source of truth: user list (O(n) space, n=5)
    users = [
        "admin1@test.com",
        "admin2@test.com",
        "editor1@test.com",
        "editor2@test.com",
        "viewer1@test.com"
    ]
    
    # Optional: Custom configurations for specific users
    # If a user is not in this dict, factory will be used automatically (lazy evaluation)
    # This preserves flexibility while defaulting to efficient on-demand generation
    CUSTOM_CONFIGS = {
        # Example custom config (currently unused, but available for future use):
        # "admin1@test.com": get_user_seed_data("admin1@test.com", custom_config=[
        #     {"name": "Custom Item 1", "category": "Electronics", "item_type": "PHYSICAL", "price": 100},
        #     {"name": "Custom Item 2", "category": "Software", "item_type": "DIGITAL", "price": 50},
        # ]),
    }
    
    print("\n[SeedSetup] Setting up MongoDB seed data using factory...")
    total_items = 0
    
    # Lazy evaluation: Generate seed data on-demand (O(n*m) time, O(m) space per iteration)
    for email in users:  # O(n) iterations
        try:
            # Check for custom config first (O(1) lookup)
            if email in CUSTOM_CONFIGS:
                seed_items = CUSTOM_CONFIGS[email]
            else:
                # Lazy generation: Only generate when needed (O(m) time, O(m) space)
                seed_items = get_user_seed_data(email, use_factory=True)
            
            # Create seed data in MongoDB (O(m) time, O(1) space)
            count = create_seed_for_user(email, seed_items=seed_items)
            total_items += count
            
            # seed_items goes out of scope here, memory freed (streaming approach)
            
        except ValueError as e:
            # User not found - skip gracefully
            print(f"[SeedSetup] ⚠️  Skipping {email}: {e}")
        except Exception as e:
            # Other errors - log and continue
            print(f"[SeedSetup] ❌ Error for {email}: {e}")
    
    print(f"[SeedSetup] SUCCESS: Total: {total_items} items created for {len(users)} users")

# OLD FIXTURE REMOVED - Replaced by setup_mongodb_seed
# The old API-based seed healing approach has been replaced with MongoDB direct insertion
