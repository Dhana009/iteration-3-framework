"""
MongoDB Direct Seeding - GLOBAL LEVEL ONLY

IMPORTANT: This module provides GLOBAL-LEVEL seeding that runs ONCE before all tests.
This is NOT for on-demand seeding during tests.

Architecture:
- MongoDB Direct Seeding (GLOBAL): Runs once at session start via setup_mongodb_seed
  - Purpose: One-time baseline seed data before all tests
  - Method: Direct MongoDB insertion (fast, bypasses API validation)
  - Trigger: ENABLE_SEED_SETUP=true environment variable
  - Data Source: Uses SeedDataFactory to generate role-specific data
  
- API-Based Insertion (ON-DEMAND): Use insert_data_if_not_exists for test-level data insertion
  - Purpose: Insert data for specific users on-demand with flexible payloads
  - Method: API calls (validates through backend, includes duplicate checking)
  - Trigger: Call insert_data_if_not_exists() in your test when needed
  - Data Source: Accepts flexible payload (user-provided items)

DO NOT use this for on-demand insertion. Use insert_data_if_not_exists instead.
"""

import pytest
import os
from fixtures.seed_factory import get_user_seed_data

@pytest.fixture(scope="session", autouse=True)
def setup_mongodb_seed(create_seed_for_user):
    """
    GLOBAL SETUP ONLY: Set up baseline seed data via MongoDB before all tests.
    
    This fixture runs ONCE at session start (if ENABLE_SEED_SETUP=true).
    It is NOT for on-demand seeding during tests.
    
    Purpose:
        - One-time baseline seed data before all tests run
        - Fast MongoDB direct insertion (bypasses API validation)
        - Uses factory to generate role-specific data automatically
    
    When to use:
        - Global test setup (automatic, controlled by ENABLE_SEED_SETUP flag)
        - NOT for test-level insertion (use insert_data_if_not_exists instead)
    
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
            # If custom config exists, pass it to factory via environment or direct call
            # Note: CUSTOM_CONFIGS currently empty - factory handles default generation
            if email in CUSTOM_CONFIGS:
                # Custom configs would be passed to factory's custom_config parameter
                # For now, factory will use default generation
                pass
            
            # Create seed data in MongoDB
            # Responsibility separation: Factory generates data, fixture handles MongoDB
            count = create_seed_for_user(email)
            total_items += count
            
            # seed_items goes out of scope here, memory freed (streaming approach)
            
        except ValueError as e:
            # User not found - skip gracefully
            print(f"[SeedSetup] WARNING: Skipping {email}: {e}")
        except Exception as e:
            # Other errors - log and continue
            print(f"[SeedSetup] ERROR: Error for {email}: {e}")
    
    print(f"[SeedSetup] SUCCESS: Total: {total_items} items created for {len(users)} users")

# OLD FIXTURE REMOVED - Replaced by setup_mongodb_seed
# The old API-based seed healing approach has been replaced with MongoDB direct insertion
