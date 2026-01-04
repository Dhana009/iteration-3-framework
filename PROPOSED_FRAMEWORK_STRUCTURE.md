# Production-Ready Playwright Framework - Proposed Structure

## Executive Summary

This structure combines the team's data-driven approach with battle-tested components from the current implementation. It addresses parallel execution, user management, authentication caching, and seed data optimization.

---

## Complete Folder Structure

```
framework/
├── tests/                          # Test Layer
│   ├── smoke/                      # Smoke tests
│   │   ├── test_crud_flow.py
│   │   └── test_ui_login.py
│   ├── ui/                         # UI feature tests
│   │   ├── test_search_discovery.py
│   │   └── test_create_item.py
│   ├── api/                        # API tests (yes, we test APIs)
│   │   └── test_api_endpoints.py
│   ├── verification/               # Framework verification tests
│   │   ├── test_capacity_limit.py
│   │   └── test_auth_smart_gate.py
│   ├── conftest.py                 # Main fixtures + pytest hooks
│   └── pytest.ini                  # Pytest configuration
│
├── lib/                            # Business Logic Layer (Services)
│   ├── pages/                      # Page Object Model
│   │   ├── base_page.py
│   │   ├── login_page.py
│   │   └── dashboard_page.py
│   ├── auth.py                     # SmartAuth (API token caching)
│   ├── ui_auth.py                  # SmartUIAuth (browser state caching)
│   ├── users.py                    # UserLease (user pool management)
│   └── seed.py                     # Seed data management
│
├── config/                         # Configuration Layer
│   ├── environments/               # Environment configs
│   │   ├── .env.local
│   │   ├── .env.staging
│   │   └── .env.production
│   ├── user_pool.json              # User credentials (static)
│   ├── user_state.json             # User reservations (dynamic)
│   └── seed_state.json             # Seed verification tracking (dynamic)
│
├── data/                           # Data Layer
│   ├── test_data/                  # Test data files
│   │   ├── json/
│   │   │   ├── users.json
│   │   │   ├── items.json
│   │   │   └── search_queries.json
│   │   ├── csv/
│   │   │   └── test_scenarios.csv
│   │   └── excel/
│   │       └── test_data.xlsx
│   ├── providers/                  # Data providers
│   │   ├── data_loader.py
│   │   ├── json_provider.py
│   │   ├── csv_provider.py
│   │   └── excel_provider.py
│   └── seed/                       # Seed data definitions
│       ├── seed_items.py           # SEED_ITEMS constant
│       └── seed_version.py         # SEED_DATA_VERSION constant
│
├── utils/                          # Utilities Layer
│   ├── api_client.py               # Generic HTTP client
│   ├── file_lock.py                # AtomicLock for concurrency
│   ├── wait_helpers.py             # Custom wait utilities
│   └── assertion_helpers.py        # Custom assertions
│
├── state/                          # Runtime State Storage
│   ├── admin1@test.com.json        # API token cache
│   ├── editor1@test.com.json       # API token cache
│   └── admin1@test.com_storage.json # Browser state cache
│
├── reports/                        # Test Artifacts
│   ├── allure-results/             # Allure report data
│   ├── screenshots/                # Failure screenshots
│   ├── videos/                     # Test recordings
│   └── logs/                       # Execution logs
│
├── .github/                        # CI/CD
│   └── workflows/
│       └── playwright.yml          # GitHub Actions workflow
│
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration (root)
└── README.md                       # Framework documentation
```

---

## Layer Responsibilities

### **1. Test Layer (`tests/`)**

**Purpose:** Test cases organized by type and scope

**Structure:**
- `smoke/` - Critical path tests (run first)
- `ui/` - UI feature tests (data-driven)
- `api/` - API tests (yes, we test APIs)
- `verification/` - Framework self-tests
- `conftest.py` - **ALL fixtures + pytest hooks**

**Key Components in conftest.py:**
```python
# Pytest Hooks
def pytest_sessionstart(session):
    """Morning Roll Call - Reset user state"""
    # Clear user_state.json
    # Optional: Clear seed_state.json if CLEANUP_SEED_ON_START=true

# Core Fixtures
@pytest.fixture(scope="session")
def env_config():
    """Load environment configuration"""

@pytest.fixture(scope="session")
def user_lease():
    """User pool management"""
    return UserLease(worker_id=...)

# Authentication Fixtures
@pytest.fixture
def auth_context(user_lease, env_config):
    """Authenticated API client + user"""
    user = user_lease.acquire(role)
    auth = SmartAuth(user['email'], user['password'], base_url)
    token, user_data = auth.authenticate()
    api = APIClient(base_url, token)
    yield {'api': api, 'user': user_data, 'token': token}
    user_lease.release()

# Actor Fixtures (High-Level)
@pytest.fixture
def admin_actor(auth_context, ensure_seed_data):
    """Admin with API access + seed data"""
    return auth_context

@pytest.fixture
def admin_ui_actor(user_lease, browser, env_config):
    """Admin with browser + authenticated session"""
    user = user_lease.acquire("ADMIN")
    ui_auth = SmartUIAuth(user['email'], user['password'], browser, base_url)
    storage_state = ui_auth.get_storage_state()
    context = browser.new_context(storage_state=storage_state)
    page = context.new_page()
    yield {'page': page, 'user': user, 'context': context}
    context.close()
    user_lease.release()

# Seed Data Fixtures
@pytest.fixture(scope="session")
def ensure_seed_data(auth_context):
    """Verify/create seed data for user"""
    from lib.seed import check_and_heal_seed
    check_and_heal_seed(auth_context['api'], auth_context['user']['_id'])
```

**Dependencies:** lib/, config/, data/, utils/

---

### **2. Business Logic Layer (`lib/`)**

**Purpose:** Core business logic and reusable components

**Components:**

**`lib/pages/` - Page Object Model**
- `base_page.py` - Common page methods
- `login_page.py` - Login page interactions
- `dashboard_page.py` - Dashboard interactions
- Feature-specific pages

**`lib/auth.py` - SmartAuth (API)**
```python
class SmartAuth:
    """
    Traffic Control for API Authentication
    - Caches tokens in state/ directory
    - Validates token before reuse (GET /auth/me)
    - Re-authenticates if expired
    """
    LOGIN_ENDPOINT = "/auth/login"
    ME_ENDPOINT = "/auth/me"
```

**`lib/ui_auth.py` - SmartUIAuth (Browser)**
```python
class SmartUIAuth:
    """
    Traffic Control for UI Authentication
    - Caches browser state (cookies, localStorage)
    - Validates state before reuse (navigate to /dashboard)
    - Re-authenticates if expired
    """
```

**`lib/users.py` - UserLease**
```python
class UserLease:
    """
    User Pool Management
    - Exclusive user access (prevents parallel conflicts)
    - Fail-fast when pool exhausted
    - Atomic locking via file_lock.py
    - Separate state (user_state.json) from config (user_pool.json)
    """
```

**`lib/seed.py` - Seed Data Management**
```python
SEED_DATA_VERSION = "v1.0"  # From data/seed/seed_version.py
SEED_ITEMS = [...]           # From data/seed/seed_items.py

def check_and_heal_seed(client, user_id):
    """
    Verify/create seed data for user
    - Check seed_state.json for cached verification
    - If verified + version matches → Skip
    - If not verified or version mismatch → Verify database
    - Try-create pattern (handle 409 gracefully)
    - Update seed_state.json with version
    """
```

**Dependencies:** utils/, config/, data/seed/

---

### **3. Configuration Layer (`config/`)**

**Purpose:** Environment settings and runtime state

**Files:**

**Static Configuration:**
- `environments/.env.{env}` - Environment-specific settings
- `user_pool.json` - User credentials (read-only)

**Dynamic State:**
- `user_state.json` - Active user reservations (read-write, locked)
- `seed_state.json` - Seed verification tracking (read-write)

**Structure of seed_state.json:**
```json
{
  "global_version": "v1.0",
  "users": {
    "admin1@test.com": {
      "verified": true,
      "data_version": "v1.0",
      "last_verified": "2026-01-04T22:00:00",
      "items_count": 11
    },
    "editor1@test.com": {
      "verified": true,
      "data_version": "v1.0",
      "last_verified": "2026-01-04T22:05:00",
      "items_count": 11
    }
  }
}
```

**Dependencies:** None (base layer)

---

### **4. Data Layer (`data/`)**

**Purpose:** Test data and seed data management

**Structure:**

**`data/test_data/` - Test Data Files**
- JSON, CSV, Excel files for data-driven tests
- Used with `@pytest.mark.parametrize`

**`data/providers/` - Data Loaders**
- Abstract data loading from different formats
- Return test data sets for parametrization

**`data/seed/` - Seed Data Definitions**
- `seed_items.py` - SEED_ITEMS constant (11 baseline items)
- `seed_version.py` - SEED_DATA_VERSION constant

**Example Usage:**
```python
# In test
from data.providers import json_provider

@pytest.mark.parametrize("user_data", json_provider.load("users.json"))
def test_login_multiple_users(user_data):
    # Test logic runs for each user in users.json
```

**Dependencies:** None (data only)

---

### **5. Utilities Layer (`utils/`)**

**Purpose:** Reusable helper functions

**Components:**

**`utils/api_client.py` - Generic HTTP Client**
```python
class APIClient:
    """
    Pure transport layer (no domain logic)
    - get(), post(), put(), patch(), delete()
    - Session management
    - Token injection
    """
```

**`utils/file_lock.py` - AtomicLock**
```python
class AtomicLock:
    """
    File-based locking for parallel safety
    - Wraps filelock.FileLock
    - Short timeout (fail-fast)
    - Used by UserLease and seed management
    """
```

**`utils/wait_helpers.py` - Custom Waits**
**`utils/assertion_helpers.py` - Custom Assertions**

**Dependencies:** None (utilities)

---

### **6. State Layer (`state/`)**

**Purpose:** Runtime state storage (gitignored)

**Files:**
- `{email}.json` - API token cache (from SmartAuth)
- `{email}_storage.json` - Browser state cache (from SmartUIAuth)

**Lifecycle:**
- Created on first authentication
- Reused until expired
- Validated before reuse
- Deleted on expiry

**Dependencies:** None (storage only)

---

### **7. Reports Layer (`reports/`)**

**Purpose:** Test execution artifacts

**Structure:**
- `allure-results/` - Allure report data
- `screenshots/` - Failure screenshots
- `videos/` - Test recordings
- `logs/` - Execution logs

**Dependencies:** None (output only)

---

## Key Architectural Decisions

### **Decision 1: Service Layer Exists (as `lib/`)**

**Rationale:**
- auth.py, users.py, seed.py provide business logic
- Not just page interactions
- Calling it `lib/` is fine (clear purpose)

**Alternative considered:** Rename to `services/` (more explicit)

---

### **Decision 2: API Layer is Multi-Purpose**

**Clarification:**
- **Primary:** Seed data setup (via lib/seed.py)
- **Secondary:** API testing (tests/api/)
- **Tertiary:** Support operations (minimal)

**Not just "supporting layer" - it's a testing target too**

---

### **Decision 3: Fixtures in tests/conftest.py**

**Rationale:**
- Standard pytest location
- Contains ALL fixtures (browser, auth, seed, actors)
- Contains pytest hooks (sessionstart, etc.)
- No separate "core/browser/browser_factory.py" (over-engineering)

---

### **Decision 4: State Files in config/**

**Rationale:**
- `user_state.json` and `seed_state.json` are configuration state
- Co-located with `user_pool.json` (related files together)
- Separate `state/` directory is for auth caches (different purpose)

---

### **Decision 5: Seed Data Split**

**Structure:**
- `data/seed/seed_items.py` - Data definitions
- `data/seed/seed_version.py` - Version constant
- `lib/seed.py` - Business logic (verify/create)
- `config/seed_state.json` - Verification tracking

**Rationale:** Separation of data, logic, and state

---

## Critical Components (Must Have)

### **1. User Pool Management** ✅
- `lib/users.py` - UserLease class
- `config/user_pool.json` - Credentials
- `config/user_state.json` - Reservations
- `utils/file_lock.py` - AtomicLock

**Why:** Prevents parallel tests from using same user

---

### **2. Smart Authentication** ✅
- `lib/auth.py` - API token caching
- `lib/ui_auth.py` - Browser state caching
- `state/` - Token/state storage

**Why:** Eliminates redundant logins (90% time saved)

---

### **3. Seed Data Optimization** ✅
- `config/seed_state.json` - Verification tracking
- `data/seed/seed_version.py` - Version management
- `lib/seed.py` - Try-create pattern

**Why:** Eliminates redundant database checks

---

### **4. Pytest Hooks** ✅
- `tests/conftest.py::pytest_sessionstart` - Morning Roll Call
- Resets user_state.json on session start
- Optional: Resets seed_state.json if flag set

**Why:** Recovers from crashed tests (clears stale locks)

---

## Data-Driven Testing Pattern

### **NOT BDD** ✅
- No Gherkin, no feature files, no step definitions
- Pure pytest with `@pytest.mark.parametrize`

### **Data Sources**
```python
# JSON
@pytest.mark.parametrize("user", json_provider.load("users.json"))

# CSV
@pytest.mark.parametrize("scenario", csv_provider.load("scenarios.csv"))

# Excel
@pytest.mark.parametrize("data", excel_provider.load("test_data.xlsx", sheet="Login"))
```

### **Example Test**
```python
@pytest.mark.parametrize("user_data", json_provider.load("users.json"))
def test_login_multiple_users(page, user_data):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(user_data['email'], user_data['password'])
    assert login_page.is_logged_in()
```

---

## Parallel Execution

### **Configuration (pytest.ini)**
```ini
[pytest]
addopts = -n auto --dist loadscope
```

### **Isolation Mechanisms**
1. **User Pool:** Each worker gets exclusive user (UserLease)
2. **Browser:** Each worker gets isolated browser context
3. **State:** File locking prevents state corruption
4. **Seed Data:** User-specific (no conflicts)

---

## Dependency Flow

```
Tests (conftest.py)
  ↓
lib/ (auth, users, seed, pages)
  ↓
utils/ (api_client, file_lock)
  ↓
data/ (providers, seed definitions)
  ↓
config/ (env settings, state files)
```

**Rule:** Each layer only imports from layers below it

---

## Migration from Current Structure

### **Minimal Changes Needed:**

**Keep as-is:**
- `lib/` (already correct)
- `tests/` (already correct)
- `config/` (already correct)
- `utils/` (already correct)

**Add:**
- `config/seed_state.json` (new file)
- `data/seed/seed_version.py` (new file)
- `data/providers/` (new directory)
- `data/test_data/` (new directory)

**Enhance:**
- `lib/seed.py` (add state tracking + versioning)
- `tests/conftest.py` (ensure hooks present)

**Total effort:** 2-3 days

---

## Comparison: Proposed vs Team's Proposal

| Aspect | Team Proposal | This Proposal | Winner |
|--------|---------------|---------------|--------|
| User Pool | ❌ Missing | ✅ Included | **This** |
| Smart Auth | ❌ Missing | ✅ Included | **This** |
| Seed Optimization | ❌ Missing | ✅ Included | **This** |
| Data-Driven | ✅ Good | ✅ Same | **Tie** |
| Layer Separation | ✅ Good | ✅ Same | **Tie** |
| Pytest Hooks | ❌ Missing | ✅ Included | **This** |
| Migration Path | ❌ Unclear | ✅ Clear | **This** |
| Production-Ready | ⚠️ Gaps | ✅ Complete | **This** |

---

## Recommendation

**Adopt this structure** because:
1. ✅ Includes all battle-tested components
2. ✅ Minimal migration from current implementation
3. ✅ Addresses parallel execution correctly
4. ✅ Optimizes authentication and seed data
5. ✅ Clear dependency flow
6. ✅ Production-ready (no critical gaps)

**Team's proposal is good foundation, but missing critical components for production use.**

---

## Next Steps

1. **Review with team** - Get feedback on this structure
2. **Answer backend questions** - Get API clarifications for seed optimization
3. **Implement seed optimization** - Add state tracking + versioning
4. **Add data providers** - Implement JSON/CSV/Excel loaders
5. **Migrate gradually** - No big-bang rewrite, incremental improvements

---

## Questions for Team

1. **Agree on structure?** Any concerns with this proposal?
2. **Service layer naming?** Keep `lib/` or rename to `services/`?
3. **Browser factory?** Keep fixtures in conftest.py or extract factory class?
4. **Timeline?** When to implement data providers and seed optimization?

---

**This structure is production-ready and builds on proven patterns from current implementation.**
