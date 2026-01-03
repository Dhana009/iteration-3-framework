# Architecture Strategy: Reliability & Isolation Blueprint

This document outlines the core architectural patterns chosen to solve the "Parallel Execution vs. Shared Environment" conflict.

---

## 1. User Pool Strategy: "Capacity Guarantee"

**Problem:** Parallel workers competing for limited user accounts leads to race conditions, complex locking queues, and flaky timeouts.

**The Solution:**
We eliminate valid "Waiting" entirely. The infrastructure MUST match the test load.

*   **Model:** "The Reservation Whiteboard"
*   **Mechanism:**
    1.  **Lock & Check:** Worker locks the pool file.
    2.  **Acquire:** Finds the first `FREE` user of the requested Role.
    3.  **Fail Fast:** If NO users are free -> **CRASH IMMEDIATELY** (Infrastructure Error).
    4.  **Release:** On test completion (Teardown), the user is marked `FREE` again.

**Risk Mitigation (Crash Handling):**
*   **Problem:** If a worker crashes while holding a user, that user remains `BUSY` forever.
*   **Fix: "The Morning Roll Call"**
    *   On `pytest_sessionstart` (Master Process), we forcibly reset **ALL** users to `FREE`.
    *   This ensures every test session starts with a 100% clean pool, recovering from any previous crashes.

**Why:** Zero latency. Zero deadlocks. If a test fails, it's a configuration issue (add more users), not a code issue.

---

## 2. Authentication Strategy: "Traffic Control"

**Problem:** UI Login is slow (5-10s). Reusing tokens blindly leads to failure when they expire or invalid states occur.

**The Solution:**
We implement a "Smart Gate" that validates credentials *before* the test code runs.

*   **Model:** "The Smart Gate"
*   **Flow:**
    1.  **Load Badge:** Worker checks for specific user's `auth.json`.
    2.  **Gate Check (Validate):**
        *   Worker sends a fast API request (`HEAD /api/me`) using the Badge.
        *   **200 OK?** -> **Green Light.** Proceed to test. (Time: 10ms).
        *   **401/403?** -> **Red Light.** Go to Step 3.
    3.  **Fast Track (Heal):**
        *   Discard old Badge.
        *   Perform **API Login** (`POST /api/login`).
        *   Save new Badge.
    4.  **Proceed:** Inject valid state into Browser Context.

**Why:** Tests *never* fail due to "Logged Out". We skip the slow UI login 99% of the time, but recover instantly if the token dies.

---

## 3. Data Strategy: "Hybrid Isolation"

**Problem:** We have Shared Users (Persistent) but need Isolated Tests. Usage of `.reset()` or `DELETE *` is dangerous/forbidden.

**The Solution:**
We distinguish between "Infrastructure Data" (Seed) and "Test Data" (Work).

### A. Seed Data ("The Desk")
*   **Definition:** The baseline profile/settings required for the user to exist/work.
*   **Strategy:** **Trust But Verify (Self-Healing)**
    *   **Logic:** Before *every* test, check: "Does the standard seed data exist?"
    *   **Yes:** Do nothing. (Fast).
    *   **No:** Re-create it via API. (Healing).
    *   **Concurrency Safety (Double-Checked Locking):**
        *   If missing, acquire `seed_repair.lock`.
        *   **Check Again:** Maybe someone else fixed it while we waited?
        *   **Fix:** Only if still missing.
*   **Result:** The environment is persistent but resilient. We never "wipe" the user.

### B. Test Data ("The Sticky Note")
*   **Definition:** Data created *during* a specific test (e.g., "Invoice #1").
*   **Strategy:** **Namespaced Isolation**
    *   **Logic:** Every test generates a `Unique ID` (UUID).
    *   **Create:** Name items `Item X - {UUID}`.
    *   **Read:** Filter items by `Name Contains {UUID}`.
    *   **Ignore:** Any item sitting in the account that does *not* match the UUID is ignored (treated as background noise).
*   **Result:** Tests run in parallel on the same account without seeing each other's data. No cleanup "Panic" if a test crashes—the junk stays but is ignored.

---

## Summary of Guarantees

1.  **Availability:** If the infra is correct, a user is *always* ready instantly.
2.  **Auth:** A test *always* starts with a valid, working login.
3.  **Isolation:** A test *never* fails because of another test's leftover data.

---

## 4. System Implementation Standards (Agent Persona)

To ensure this architecture is built correctly, the following engineering standards are enforced:

*   **Mindset:** "Defensive Systems Engineering". Reliability > Speed.
*   **Atomic Decomposition:** We build one layer at a time. We verify it. We move on.
*   **No Magic:** Every "Self-Healing" action (Login, Seed Create) must be explicit, logged, and thread-safe.
*   **Resource Safety:** Uses `try/finally` blocks for ALL locks, files, and API connections.

---

## 5. Phased Implementation Plan

We will build this system in 4 strict, verifiable steps:

**Step 1: The Foundation (Config & Locking)**
*   Artifacts: `config/user_pool.json`, `utils/file_lock.py`
*   *Verification:* Multi-process script proving the lock prevents race conditions.

**Step 2: The User Acquisition (Capacity)**
*   Artifacts: `fixtures/users.py`
*   *Verification:* Script proving 5 workers fail gracefully when competing for 4 users.

**Step 3: The Authentication (Traffic Control)**
*   Artifacts: `utils/api_client.py`, `fixtures/auth.py`
*   *Verification:* Script proving "Stale Token" triggers login, "Fresh Token" skips login.

**Step 4: The Data Healer (Trust But Verify)**
*   Artifacts: `fixtures/data.py`
*   *Verification:* Script proving manually deleted seed data is automatically re-created (Healed).
