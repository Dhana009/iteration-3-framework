
import pytest
import os
from lib.seed import SEED_ITEMS
from lib.auth import SmartAuth
from utils.api_client import APIClient

# Feature flag - checked once at module load time
_SEED_ENABLED = os.getenv('ENABLE_API_SEED_SETUP', 'true').lower() == 'true'

@pytest.fixture(scope="session")
def seed_fixture_api(env_config):
    """
    Factory fixture to seed data via API.
    Ensures all backend logic (hooks, timestamps, owner_id) is applied.
    Includes caching to avoid redundant API calls.
    """
    # Session-level cache to track seeded users
    _cache = {}
    
    def _seed(email: str, password: str = "Test123!@#", force_refresh: bool = False):
        # Check cache first (unless force_refresh is True)
        if not force_refresh and email in _cache:
            print(f"\n[Seed] ✅ {email} already seeded (cached: {_cache[email]} items)")
            return _cache[email]
        
        # 1. Authenticate using SmartAuth (like actors_api.py does)
        print(f"\n[Seed] Authenticating as {email}...")
        try:
            auth = SmartAuth(email, password, env_config.API_BASE_URL)
            token, user_data = auth.authenticate()
            if not token:
                print(f"[Seed] ⚠️ Authentication failed for {email}. Skipping seed.")
                return 0
        except Exception as e:
            print(f"[Seed] ⚠️ Authentication error for {email}: {e}")
            return 0
        
        # Create authenticated API client
        api = APIClient(env_config.API_BASE_URL, token=token)
            
        # 2. Check Existing Data
        try:
            response = api.get('/items')
            
            if response.status_code == 200:
                data = response.json()
                # API returns: { "status": "success", "items": [...], "pagination": { "total": 100, ... } }
                total = data.get('pagination', {}).get('total', 0)
                
                if total >= len(SEED_ITEMS):
                    print(f"[Seed] ✅ Data already exists for {email} ({total} items).")
                    _cache[email] = total  # Cache the result
                    return total
            else:
                print(f"[Seed] ⚠️ Failed to check items: {response.status_code}")
        except Exception as e:
            print(f"[Seed] Failed to check items: {e}")
            # Proceed to try creation anyway
            
        # 3. Create Items
        print(f"[Seed] Seeding {len(SEED_ITEMS)} items for {email}...")
        created = 0
        for item in SEED_ITEMS:
            # Prepare payload - add seed tag
            payload = item.copy()
            # Add seed tag to identify seed items
            if 'tags' not in payload:
                payload['tags'] = []
            if 'seed' not in payload['tags']:
                payload['tags'].append('seed')
            if 'v1.0' not in payload['tags']:
                payload['tags'].append('v1.0')
            
            # API handles 'is_active' default, but we can set it explicitly
            if 'is_active' not in payload:
                payload['is_active'] = True
                
            try:
                response = api.post('/items', json=payload)
                
                if response.status_code == 201:
                    data = response.json()
                    if data.get('status') == 'success' and 'data' in data:
                        created += 1
                    else:
                        print(f"[Seed] ⚠️ Unexpected response for {item['name']}: {data}")
                elif response.status_code == 409:
                    # Duplicate item - already exists, count as success
                    print(f"[Seed] ℹ️  Item {item['name']} already exists (409)")
                    created += 1
                elif response.status_code == 403:
                    # Forbidden - user doesn't have permission
                    print(f"[Seed] 🛑 User {email} is not authorized to create items (Role: Viewer?). Skipping.")
                    break
                else:
                    print(f"[Seed] ⚠️ Failed to create {item['name']}: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                # Handle 403 Forbidden (e.g., Viewer role)
                if "403" in str(e) or "Forbidden" in str(e):
                    print(f"[Seed] 🛑 User {email} is not authorized to create items (Role: Viewer?). Skipping.")
                    break
                print(f"[Seed] ❌ Error creating {item['name']}: {e}")
                
        print(f"[Seed] Created {created} items for {email}.")
        _cache[email] = created  # Cache the result
        return created

    return _seed

@pytest.fixture(scope="session", autouse=True)
def setup_api_seed_data(seed_fixture_api):
    """
    Session-scoped autouse fixture to ensure standard users have data.
    Controlled by ENABLE_API_SEED_SETUP environment variable.
    """
    # Feature flag check (uses module-level constant)
    if not _SEED_ENABLED:
        print("\n[API SeedSetup] Skipped (ENABLE_API_SEED_SETUP=false)")
        return
    
    # Seed data for main test actors
    print("\n[API SeedSetup] Setting up API seed data...")
    # Admin
    seed_fixture_api("admin1@test.com")
    
    # Editor
    seed_fixture_api("editor1@test.com")
    
    # Admin 2 (if needed)
    # seed_fixture_api("admin2@test.com")
    
    # Viewer? (Usually read-only, check permission)
    # Trying to seed viewer might fail with 403, logic handles it.
    seed_fixture_api("viewer1@test.com")
