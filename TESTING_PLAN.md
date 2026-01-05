# Testing Plan: Data Management System Verification

## Overview

This plan outlines the systematic testing approach to verify all data management operations:
1. Global MongoDB seeding (before tests)
2. On-demand data insertion (during tests)
3. Update operations
4. Delete operations (soft and hard)
5. UI integration
6. Flow 2 and Flow 3 integration

## Prerequisites

### Environment Setup

1. **MongoDB Connection**
   - Verify `MONGODB_URI` and `MONGODB_DB_NAME` are set in `.env`
   - Test connection: MongoDB should be accessible

2. **Environment Variables**
   ```bash
   ENABLE_SEED_SETUP=true  # For global seeding
   INTERNAL_AUTOMATION_KEY=flowhub-secret-automation-key-2025  # For hard delete operations
   ```

3. **Backend API**
   - Backend server should be running
   - API endpoints should be accessible
   - Internal endpoints should accept `x-internal-key` header

4. **Test Users**
   - admin1@test.com, admin2@test.com
   - editor1@test.com, editor2@test.com
   - viewer1@test.com
   - All users should exist in MongoDB

## Testing Phases

### Phase 1: Verification Tests (Foundation)

**Purpose**: Verify core data management operations work correctly

**Test File**: `tests/verification/test_data_management_complete.py`

**Execution Order**:

1. **Test Global Seeding**
   ```bash
   # Test 1.1: Verify global seeding works when enabled
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestGlobalSeeding::test_global_seeding_enabled -v -s
   
   # Test 1.2: Verify global seeding can be disabled
   ENABLE_SEED_SETUP=false pytest tests/verification/test_data_management_complete.py::TestGlobalSeeding::test_global_seeding_disabled -v -s
   ```

2. **Test On-Demand Insertion**
   ```bash
   # Test 2.1: Insert new items
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestOnDemandInsertion::test_insert_new_items -v -s
   
   # Test 2.2: Duplicate prevention
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestOnDemandInsertion::test_insert_duplicate_prevention -v -s
   
   # Test 2.3: Mixed new/duplicate
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestOnDemandInsertion::test_insert_mixed_new_duplicate -v -s
   ```

3. **Test Update Operations**
   ```bash
   # Test 3.1: Update success
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestUpdateOperations::test_update_item_success -v -s
   
   # Test 3.2: Version conflict
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestUpdateOperations::test_update_version_conflict -v -s
   ```

4. **Test Delete Operations**
   ```bash
   # Test 4.1: Soft delete
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestDeleteOperations::test_soft_delete -v -s
   
   # Test 4.2: Hard delete single
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestDeleteOperations::test_hard_delete_single -v -s
   
   # Test 4.3: Hard delete user items
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestDeleteOperations::test_hard_delete_user_items -v -s
   
   # Test 4.4: Hard delete user data
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestDeleteOperations::test_hard_delete_user_data -v -s
   ```

5. **Test End-to-End Workflow**
   ```bash
   # Test 5.1: Complete lifecycle
   ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py::TestEndToEndWorkflow::test_complete_lifecycle -v -s
   ```

**Expected Results**:
- All 12 tests should pass
- No errors or warnings
- Clean test execution

**Success Criteria**:
- ✅ All verification tests pass
- ✅ No duplicate data created
- ✅ All operations work as expected
- ✅ Cleanup works correctly

---

### Phase 2: Flow 2 Integration Tests

**Purpose**: Verify Flow 2 (Create Item) works with new data management fixtures

**Test File**: `tests/ui/test_create_item.py`

**Execution**:
```bash
# Run all Flow 2 tests
ENABLE_SEED_SETUP=true pytest tests/ui/test_create_item.py -v -s

# Run specific test
ENABLE_SEED_SETUP=true pytest tests/ui/test_create_item.py::test_create_digital_item -v -s
```

**What to Verify**:
1. Global seed data exists before test runs
2. Test-specific data is inserted using `insert_data_if_not_exists`
3. Update operations work if used
4. Cleanup happens correctly
5. UI shows all data correctly

**Success Criteria**:
- ✅ Flow 2 tests pass
- ✅ Seed data visible in UI
- ✅ Test data created correctly
- ✅ No data leaks between tests

---

### Phase 3: Flow 3 Integration Tests

**Purpose**: Verify Flow 3 (Search & Discovery) works with new data management fixtures

**Test File**: `tests/ui/test_search_discovery.py`

**Execution**:
```bash
# Run all Flow 3 tests
ENABLE_SEED_SETUP=true pytest tests/ui/test_search_discovery.py -v -s

# Run specific tests
ENABLE_SEED_SETUP=true pytest tests/ui/test_search_discovery.py::test_editor_pagination -v -s
ENABLE_SEED_SETUP=true pytest tests/ui/test_search_discovery.py::test_admin_full_discovery_flow -v -s
```

**What to Verify**:
1. Global seed data visible in search results
2. Test-specific data appears in search
3. Pagination works with seed data + test data
4. Search/filter works correctly
5. Cleanup happens after tests

**Success Criteria**:
- ✅ Flow 3 tests pass
- ✅ Seed data appears in search
- ✅ Test data appears in search
- ✅ Pagination works correctly
- ✅ No data leaks

---

### Phase 4: UI Integration Tests

**Purpose**: Verify all data management operations are reflected correctly in UI

**Test File**: `tests/integration/test_data_management_ui_integration.py`

**Execution**:
```bash
# Run all UI integration tests
ENABLE_SEED_SETUP=true pytest tests/integration/test_data_management_ui_integration.py -v -s

# Run individual tests
ENABLE_SEED_SETUP=true pytest tests/integration/test_data_management_ui_integration.py::TestDataManagementUIIntegration::test_global_seed_data_visible_in_ui -v -s
ENABLE_SEED_SETUP=true pytest tests/integration/test_data_management_ui_integration.py::TestDataManagementUIIntegration::test_on_demand_insertion_visible_in_ui -v -s
ENABLE_SEED_SETUP=true pytest tests/integration/test_data_management_ui_integration.py::TestDataManagementUIIntegration::test_update_item_reflects_in_ui -v -s
ENABLE_SEED_SETUP=true pytest tests/integration/test_data_management_ui_integration.py::TestDataManagementUIIntegration::test_soft_delete_hides_from_ui -v -s
ENABLE_SEED_SETUP=true pytest tests/integration/test_data_management_ui_integration.py::TestDataManagementUIIntegration::test_hard_delete_removes_from_ui -v -s
```

**What to Verify**:
1. Seed data appears in UI
2. Inserted data appears in UI
3. Updated data reflects in UI
4. Soft deleted items are hidden
5. Hard deleted items are removed

**Success Criteria**:
- ✅ All UI integration tests pass
- ✅ UI reflects all operations correctly
- ✅ No UI glitches or errors

---

### Phase 5: Complete Test Suite Run

**Purpose**: Run all tests together to verify complete integration

**Execution**:
```bash
# Run all new tests
ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py tests/ui/test_create_item.py tests/ui/test_search_discovery.py tests/integration/test_data_management_ui_integration.py -v

# Run with coverage (if available)
ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py tests/ui/test_create_item.py tests/ui/test_search_discovery.py tests/integration/test_data_management_ui_integration.py --cov=tests/plugins --cov-report=html -v
```

**Success Criteria**:
- ✅ All tests pass
- ✅ No test conflicts
- ✅ Clean execution
- ✅ Proper cleanup between tests

---

## Test Execution Checklist

### Before Starting

- [ ] MongoDB is running and accessible
- [ ] Backend API is running
- [ ] Environment variables are set correctly
- [ ] Test users exist in database
- [ ] `.env` file is configured

### During Testing

- [ ] Phase 1: Verification tests pass (12 tests)
- [ ] Phase 2: Flow 2 integration tests pass
- [ ] Phase 3: Flow 3 integration tests pass
- [ ] Phase 4: UI integration tests pass (5 tests)
- [ ] Phase 5: Complete test suite passes

### After Testing

- [ ] All tests pass
- [ ] No data leaks between tests
- [ ] Cleanup works correctly
- [ ] UI reflects all operations
- [ ] Performance is acceptable
- [ ] No errors in logs

---

## Troubleshooting Guide

### Issue: Global seeding not working

**Check**:
1. `ENABLE_SEED_SETUP=true` is set
2. MongoDB connection is working
3. Test users exist in database
4. Check MongoDB for items with 'seed' tag

**Fix**:
- Verify environment variable
- Check MongoDB connection
- Verify user existence

### Issue: Duplicate items created

**Check**:
1. `insert_data_if_not_exists` is being used correctly
2. Duplicate check logic is working
3. Item names are unique

**Fix**:
- Verify fixture usage
- Check duplicate detection logic
- Use unique names for test items

### Issue: Hard delete not working

**Check**:
1. `INTERNAL_AUTOMATION_KEY` is set correctly
2. Internal API endpoint is accessible
3. User ID is correct format

**Fix**:
- Verify internal key in environment
- Check API endpoint accessibility
- Verify user ID format (ObjectId)

### Issue: UI not reflecting changes

**Check**:
1. Page refresh is happening
2. API calls are successful
3. UI selectors are correct

**Fix**:
- Add explicit waits
- Verify API responses
- Check UI selectors

---

## Quick Start Commands

### Run All Tests (Recommended Order)

```bash
# 1. Verification tests first
ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py -v

# 2. Flow 2 integration
ENABLE_SEED_SETUP=true pytest tests/ui/test_create_item.py -v

# 3. Flow 3 integration
ENABLE_SEED_SETUP=true pytest tests/ui/test_search_discovery.py -v

# 4. UI integration
ENABLE_SEED_SETUP=true pytest tests/integration/test_data_management_ui_integration.py -v

# 5. Complete suite
ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py tests/ui/test_create_item.py tests/ui/test_search_discovery.py tests/integration/test_data_management_ui_integration.py -v
```

### Run Specific Test Group

```bash
# Only verification tests
ENABLE_SEED_SETUP=true pytest tests/verification/test_data_management_complete.py -v

# Only UI tests
ENABLE_SEED_SETUP=true pytest tests/ui/ -v

# Only integration tests
ENABLE_SEED_SETUP=true pytest tests/integration/test_data_management_ui_integration.py -v
```

---

## Expected Test Results

### Verification Tests (12 tests)
- ✅ TestGlobalSeeding::test_global_seeding_enabled
- ✅ TestGlobalSeeding::test_global_seeding_disabled
- ✅ TestOnDemandInsertion::test_insert_new_items
- ✅ TestOnDemandInsertion::test_insert_duplicate_prevention
- ✅ TestOnDemandInsertion::test_insert_mixed_new_duplicate
- ✅ TestUpdateOperations::test_update_item_success
- ✅ TestUpdateOperations::test_update_version_conflict
- ✅ TestDeleteOperations::test_soft_delete
- ✅ TestDeleteOperations::test_hard_delete_single
- ✅ TestDeleteOperations::test_hard_delete_user_items
- ✅ TestDeleteOperations::test_hard_delete_user_data
- ✅ TestEndToEndWorkflow::test_complete_lifecycle

### UI Integration Tests (5 tests)
- ✅ TestDataManagementUIIntegration::test_global_seed_data_visible_in_ui
- ✅ TestDataManagementUIIntegration::test_on_demand_insertion_visible_in_ui
- ✅ TestDataManagementUIIntegration::test_update_item_reflects_in_ui
- ✅ TestDataManagementUIIntegration::test_soft_delete_hides_from_ui
- ✅ TestDataManagementUIIntegration::test_hard_delete_removes_from_ui

### Flow 2 Tests
- ✅ test_create_digital_item
- ✅ test_create_physical_item
- ✅ test_create_service_item

### Flow 3 Tests
- ✅ test_editor_pagination
- ✅ test_admin_full_discovery_flow
- ✅ Other Flow 3 tests

---

## Success Metrics

- **Test Pass Rate**: 100% of new tests should pass
- **Execution Time**: Tests should complete within reasonable time
- **Data Integrity**: No duplicate data, proper cleanup
- **UI Consistency**: All operations reflected correctly in UI
- **Error Rate**: Zero errors in test execution

---

## Next Steps After Testing

1. **If All Tests Pass**:
   - Document any findings
   - Update documentation if needed
   - Proceed with integration into main test suite

2. **If Tests Fail**:
   - Document failure details
   - Check logs for errors
   - Fix issues and re-run tests
   - Update test cases if needed

3. **Performance Optimization**:
   - Measure test execution time
   - Optimize slow tests if needed
   - Consider parallel execution

---

## Notes

- Always run with `ENABLE_SEED_SETUP=true` for full verification
- Use `-v -s` flags for verbose output and print statements
- Check MongoDB directly if API verification fails
- Verify UI manually if automated UI tests fail
- Keep test data cleanup in mind
