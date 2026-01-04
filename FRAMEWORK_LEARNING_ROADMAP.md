# 🎓 Complete Framework Learning Roadmap

## 📊 Learning Progress Overview

### ✅ **COMPLETED TOPICS** (You've Mastered These!)

#### 1. **Infrastructure Layer** ✅
- **File Lock System** (`utils/file_lock.py`)
  - `AtomicLock` class for thread-safe file operations
  - Timeout-based fail-fast mechanism
  - Used for user pool synchronization

- **User Lease System** (`lib/users.py`)
  - `UserLease` class for parallel test user management
  - Worker-based user allocation
  - State file management with atomic locks
  - Auto-release on test completion

#### 2. **Authentication Layer** ✅
- **API Authentication** (`lib/auth.py`)
  - `SmartAuth` class with "Smart Gate" logic
  - Token caching and validation
  - State file persistence (`state/{email}.json`)
  - Automatic token refresh on expiry

- **UI Authentication** (`lib/ui_auth.py`)
  - `SmartUIAuth` class for Playwright sessions
  - Storage state reuse (avoids repeated logins)
  - State validation via protected page check
  - Lazy session creation

---

### 🔄 **CURRENT TOPIC** (In Progress)

#### 3. **Data Management Layer** 🔄
- **Seed Data System** (Learning Now)
  - `lib/seed.py` - Seed item templates (`SEED_ITEMS`)
  - `tests/plugins/data.py` - Global MongoDB seed setup
  - `tests/plugins/mongodb_fixtures.py` - MongoDB factory fixtures
  - `tests/plugins/seed_fixtures.py` - API-based seed setup
  - `fixtures/seed_factory.py` - Dynamic seed data generation
  - Duplicate prevention logic
  - On/off switches (`ENABLE_SEED_SETUP`, `ENABLE_API_SEED_SETUP`)

---

### 📚 **REMAINING TOPICS** (To Learn Next)

#### 4. **Test Infrastructure Layer**
- **Core Fixtures** (`tests/plugins/core.py`)
  - `worker_id_val` - Pytest-xdist worker identification
  - `user_lease` - User leasing fixture
  - `auth_context` - Auto-authentication context

- **Hooks System** (`tests/plugins/hooks.py`)
  - `pytest_sessionstart` - Morning roll call (state reset)
  - Master node coordination
  - Session lifecycle management

- **Configuration System** (`utils/config.py`)
  - Environment-based config (`local`, `production`)
  - `get_config()` function
  - API/UI URL management
  - MongoDB connection settings

#### 5. **API Communication Layer**
- **API Client** (`utils/api_client.py`)
  - Generic HTTP client wrapper
  - Methods: `post()`, `get()`, `put()`, `patch()`, `delete()`
  - Token-based authentication headers
  - URL normalization

- **API Fixtures** (`tests/plugins/api_fixtures.py`)
  - `create_test_item` - Factory for ephemeral test data
  - `delete_test_item` - Cleanup factory
  - `create_multiple_test_items` - Batch creation
  - Test data tagging (`test-data` tag)

#### 6. **Test Actor System**
- **API Actors** (`tests/plugins/actors_api.py`)
  - `admin_actor` - Admin role with API access
  - `editor_actor` - Editor role with API access
  - `viewer_actor` - Viewer role (read-only)
  - Auto-authentication and user leasing

- **UI Actors** (`tests/plugins/actors_ui.py`)
  - `admin_ui_actor` - Admin with browser page
  - `editor_ui_actor` - Editor with browser page
  - `viewer_ui_actor` - Viewer with browser page
  - Pre-authenticated Playwright contexts

#### 7. **Page Object Model (POM)**
- **Base Page** (`lib/pages/base_page.py`)
  - Common page operations
  - Wait strategies
  - Element interaction patterns

- **Page Objects** (`lib/pages/`)
  - `login_page.py` - Login page interactions
  - `create_item_page.py` - Item creation form
  - `search_page.py` - Search and filter UI

- **Page Factory** (`tests/plugins/pages.py`)
  - `PageFactory` class for lazy page loading
  - `pages` fixture for test access
  - Usage: `pages.login.login()`, `pages.search.filter()`

#### 8. **Test Organization**
- **Test Structure**
  - `tests/smoke/` - Smoke tests
  - `tests/ui/` - UI-specific tests
  - `tests/verification/` - System verification tests
  - `tests/pages/` - Page object tests

- **Pytest Configuration** (`tests/conftest.py`)
  - Plugin registration
  - Environment fixtures
  - Browser configuration
  - Command-line options (`--env`)

---

## 🗺️ **Framework Architecture Map**

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST EXECUTION LAYER                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  conftest.py → Plugin Registration → Fixture Chain  │  │
│  │  hooks.py → Session Lifecycle → State Management     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    TEST ACTOR LAYER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  actors_api.py → API Actors (admin/editor/viewer)   │  │
│  │  actors_ui.py → UI Actors (browser + API)           │  │
│  │  core.py → User Lease + Auth Context               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION LAYER                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SmartAuth → API Token Management                    │  │
│  │  SmartUIAuth → Playwright Session Reuse              │  │
│  │  UserLease → Parallel User Allocation                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA MANAGEMENT LAYER                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  seed.py → Seed Templates                             │  │
│  │  data.py → Global Seed Setup                         │  │
│  │  mongodb_fixtures.py → MongoDB Factories             │  │
│  │  seed_fixtures.py → API Seed Setup                   │  │
│  │  api_fixtures.py → Ephemeral Test Data               │  │
│  │  seed_factory.py → Dynamic Seed Generation           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  file_lock.py → Atomic File Locking                  │  │
│  │  api_client.py → HTTP Client Wrapper                 │  │
│  │  config.py → Environment Configuration               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Backend API (MongoDB + Express)                     │  │
│  │  Frontend UI (React + Playwright)                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📖 **Learning Path Sequence**

### **Phase 1: Foundation** ✅ (COMPLETED)
1. ✅ File Lock System
2. ✅ User Lease System
3. ✅ API Authentication (SmartAuth)
4. ✅ UI Authentication (SmartUIAuth)

### **Phase 2: Data Management** 🔄 (IN PROGRESS)
5. 🔄 Seed Data System
   - ✅ Seed templates (`lib/seed.py`)
   - ✅ Global MongoDB seed (`tests/plugins/data.py`)
   - 🔄 MongoDB factory fixtures (`tests/plugins/mongodb_fixtures.py`) ← **YOU ARE HERE**
   - ⏳ API seed fixtures (`tests/plugins/seed_fixtures.py`)
   - ⏳ Seed factory (`fixtures/seed_factory.py`)
   - ⏳ API test fixtures (`tests/plugins/api_fixtures.py`)

### **Phase 3: Test Infrastructure** ⏳ (NEXT)
6. ⏳ Core fixtures (`tests/plugins/core.py`)
7. ⏳ Hooks system (`tests/plugins/hooks.py`)
8. ⏳ Configuration system (`utils/config.py`)

### **Phase 4: Communication** ⏳
9. ⏳ API Client (`utils/api_client.py`)
10. ⏳ API Fixtures (`tests/plugins/api_fixtures.py`)

### **Phase 5: Test Actors** ⏳
11. ⏳ API Actors (`tests/plugins/actors_api.py`)
12. ⏳ UI Actors (`tests/plugins/actors_ui.py`)

### **Phase 6: Page Objects** ⏳
13. ⏳ Base Page (`lib/pages/base_page.py`)
14. ⏳ Page Objects (`lib/pages/*.py`)
15. ⏳ Page Factory (`tests/plugins/pages.py`)

### **Phase 7: Test Organization** ⏳
16. ⏳ Test structure and patterns
17. ⏳ Pytest configuration (`tests/conftest.py`)

---

## 🎯 **Current Focus: Seed Data System**

### **What You've Learned So Far:**
1. ✅ **Seed Templates** (`lib/seed.py`)
   - `SEED_ITEMS` constant (11 predefined items)
   - Template structure for test data

2. ✅ **Global Seed Setup** (`tests/plugins/data.py`)
   - Session-scoped automatic setup
   - Environment variable control (`ENABLE_SEED_SETUP`)
   - User-specific seed data configuration

### **What's Next:**
3. 🔄 **MongoDB Factory Fixtures** (`tests/plugins/mongodb_fixtures.py`)
   - `create_seed_for_user` factory function
   - Direct MongoDB insertion
   - Duplicate prevention logic
   - Bulk insert optimization

4. ⏳ **API Seed Fixtures** (`tests/plugins/seed_fixtures.py`)
   - API-based seed setup
   - Backend logic application
   - Visible items guarantee

5. ⏳ **Seed Factory** (`fixtures/seed_factory.py`)
   - Dynamic seed generation
   - User-specific customization

6. ⏳ **API Test Fixtures** (`tests/plugins/api_fixtures.py`)
   - Ephemeral test data creation
   - Cleanup mechanisms

---

## 🔗 **Key Relationships**

### **Seed Data Flow:**
```
lib/seed.py (Templates)
    ↓
fixtures/seed_factory.py (Dynamic Generation)
    ↓
tests/plugins/data.py (Global Setup)
    ↓
tests/plugins/mongodb_fixtures.py (MongoDB Insertion)
    OR
tests/plugins/seed_fixtures.py (API Insertion)
    ↓
Database (MongoDB)
```

### **Test Execution Flow:**
```
pytest_sessionstart (hooks.py)
    ↓
setup_mongodb_seed (data.py) - Session scope
    ↓
Test Function
    ↓
user_lease.acquire() (core.py)
    ↓
admin_actor / editor_actor (actors_api.py)
    ↓
Test Logic
    ↓
user_lease.release() (core.py)
```

### **Authentication Flow:**
```
UserLease.acquire() → Get User Credentials
    ↓
SmartAuth.authenticate() → Check State File
    ↓
Token Valid? → Yes: Reuse | No: Login
    ↓
APIClient(token) → Ready for API Calls
```

---

## 📝 **Notes**

- **Parallel Testing**: Framework designed for `pytest-xdist` parallel execution
- **State Management**: File-based state for user leases and authentication
- **Fail-Fast**: Short timeouts prevent hanging on deadlocks
- **Isolation**: Each test gets unique user to prevent conflicts
- **Reusability**: Smart caching reduces redundant operations (auth, UI sessions)

---

## 🚀 **Next Steps**

Continue with **Topic 3: MongoDB Factory Fixtures** (`tests/plugins/mongodb_fixtures.py`)

This will cover:
- How `create_seed_for_user` works
- Direct MongoDB insertion logic
- Duplicate prevention mechanism
- Bulk insert optimization
- Error handling strategies
