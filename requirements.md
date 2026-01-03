# Web Automation Framework — Architecture Overview

## Core Architecture Solutions (Summary)

This section summarizes the resolved strategies for the 3 core structural problems.

### Problem 1: Parallel User Management (The Availability Struggle)
*   **Conflict:** Parallel workers fighting for limited user accounts led to race conditions and complex locking.
*   **Solution: Capacity-Guaranteed Pool.**
    *   **Logic:** We enforce `Pool Size >= Max Workers`.
    *   **Mechanism:** Simple FileLock to "Check Out" a user.
    *   **Result:** Zero waiting. If no user is free, the test fails immediately (Infrastructure Error). NO complex queues.

### Problem 2: Authentication Strategy (The Login Struggle)
*   **Conflict:** UI Login is slow (5-10s). Reusing tokens blindly leads to failures when tokens expire.
*   **Solution: Traffic Control Login (Lazy & Verified).**
    *   **Logic:** `Load State -> Ping API (Validate) -> Reuse`.
    *   **Mechanism:** If the "Ping" (e.g., `HEAD /api/me`) fails, we discard the state and perform a fast API-based login.
    *   **Result:** 99% of tests start in 10ms. Self-healing if execution takes too long.

### Problem 3: Seed Data Strategy (The Isolation Struggle)
*   **Conflict:** Admins need Shared Data; Editors need Private Data. Resetting data per test is too slow/destructive.
*   **Solution: Trust But Verify (Shared Baseline).**
    *   **Logic:** `Check Baseline Existence -> Heal if Missing -> Proceed`.
    *   **Mechanism:** We do NOT wipe data. We verify the "Baseline" (User Profile, Default settings) exists.
    *   **Result:** Environment is persistent but self-fixing. Test-specific creation (e.g., "Create Invoice") is handled strictly *inside* the test case, independent of the Seed Strategy.

---

## 1. Objective

The goal of this framework is to support **reliable web automation** that works identically in:
- sequential execution (debugging, local runs)
- parallel execution (CI, scale)

Execution mode must **not affect correctness, behavior, or test design**.

---

## 2. Execution Model

- Tests may run sequentially or in parallel.
- Sequential execution is treated as parallel execution with concurrency = 1.
- Tests must not depend on:
  - execution order
  - shared mutable state
  - side effects of other tests
- Parallelism is an execution concern, not a test concern.

---

## 3. Role-Based Access Model

The application enforces three roles:

### Admin
- Can create, read, update, and delete data.
- Data created by any Admin:
  - is visible to all Admins
  - is visible to all Viewers

### Editor
- Can create, read, update, and delete data.
- Data created by an Editor:
  - is visible to that Editor
  - is visible to all Admins
  - is visible to all Viewers
  - is NOT visible to other Editors

### Viewer
- Cannot create, update, or delete data.
- Can only read data.
- Can see:
  - Admin-created data
  - Editor-created data

### Visibility Summary

| Created By | Admin | Same Editor | Other Editor | Viewer |
|----------|-------|-------------|--------------|--------|
| Admin    | Yes   | No          | No           | Yes    |
| Editor   | Yes   | Yes         | No           | Yes    |

---

## 4. User Pool Strategy (Infrastructure Capacity)

- **Capacity Guarantee**: The infrastructure MUST provision enough users to cover the maximum concurrency (Parallel Workers).
  - Rule: `Total Users >= Max Parallel Workers`.
- **No Waiting / Queueing**:
  - If a test requests a role and no user is available, it is treated as an **Infrastructure Configuration Failure**.
  - The test will **fail immediately** with a clear error (e.g., "NoFreeUsersError: Increase user pool size").
- **Exclusive Lease**: Users are still locked exclusively for a single test, but we assume availability.

The framework does NOT:
- Implement wait loops or timeouts for users.
- handle resource starving (this is an infra config issue).

---

## 5. Authentication Strategy (Lazy Login)

- Users are **not logged in upfront**.
- Authentication happens **only when a test requires a user**.
- Authentication state (token / storage state) is:
  - cached per user
  - reused across tests
- If cached authentication becomes invalid:
  - the framework re-authenticates once
  - updates the cache
  - fails fast if it still fails

Authentication state may live longer than a test,  
but users are leased **per test**.

---

## 6. CRUD Flow Support

The framework supports end-to-end CRUD flows:
- Create
- Read / View
- Update
- Delete

All CRUD operations:
- run using the leased user’s identity
- respect role permissions
- behave identically in sequential and parallel runs

---

## 7. Seed Data Strategy (Trust but Verify)

Seed data represents **baseline system state**. We do not assume it persists; we verify it.

### Admin Seed Data (Global Shared)

- **Verification:** Before **EVERY** Admin test, the framework checks if global seed data exists.
  - *Mechanism:* Fast API check (e.g., `HEAD /api/global-config`).
- **Self-Healing:** If the check fails (404/Missing):
  - The framework obtains a lock (to prevent race conditions).
  - Re-creates the missing global data.
  - Proceeds with the test.
- **Usage:** Reused by all Admins/Viewers, but constantly validated.

### Editor Seed Data (Shared Baseline - "The Desk")

- **Usage:** Editors are treated as a reusable pool. We do not wipe them per test.
- **Verification:** Before **EVERY** Editor test, the framework checks if the *specific* editor acquired has the baseline seed data (e.g., Profile, Default Settings).
- **Self-Healing:** If the baseline data is missing, the framework creates it. This ensures the "Desk" is ready.

### Test Data Isolation ("The Sticky Note")

- **Problem:** Since we don't wipe editors, old test data persists.
- **Solution (Namespacing):**
  - Tests creating new data (e.g., Invoices, Reports) MUST append a unique ID (UUID) to the item name.
  - Tests MUST filter/search using that unique ID.
  - Tests MUST ignore any data that does not match their unique ID.
- **Result:** Tests run in parallel on the same user without interference. Old garbage is simply ignored.

---

## 8. Seed Reset Strategy

- Seed reset is **explicit and controlled**.
- When enabled:
  - seed data is deleted directly from the database
  - seed data is recreated via application APIs
- Reset is environment maintenance, not test logic.

---

## 9. Test Responsibilities

Tests:
- declare required role
- execute business flows
- assert UI behavior

Tests do NOT:
- manage users
- handle authentication
- create or reset seed data
- depend on execution order

All orchestration is owned by the framework.

---

## 10. Key Guarantees

- Identical behavior in sequential and parallel execution
- Minimal logins through authentication reuse
- Deterministic data state through lazy seed enforcement
- Role and permission behavior matches production
