# DELETE /api/v1/internal/users/:userId/items

## Purpose
Delete only items for a specific user (preserves bulk jobs, activity logs, OTPs, and user record)

## Endpoint
```
DELETE /api/v1/internal/users/:userId/items
```

## Authentication
Requires `x-internal-key` header:
```
x-internal-key: flowhub-secret-automation-key-2025
```

## Path Parameters
- `userId` (String, required) - User ID in ObjectId format (24-character hex string)

## Response (200 Success)
```json
{
  "status": "success",
  "deleted": {
    "items": 25,
    "files": 8
  },
  "preserved": {
    "user": true,
    "bulk_jobs": true,
    "activity_logs": true,
    "otps": true
  }
}
```

## What Gets Deleted (Hard Delete)
- ✅ Items: All items where `created_by = userId`
- ✅ Files: Physical files associated with deleted items

## What Gets Preserved
- ✅ User record
- ✅ BulkJobs
- ✅ ActivityLogs
- ✅ OTPs
- ✅ Other users' data

## Use Cases
1. **Test cleanup** - Remove test items without affecting logs
2. **Seed data reset** - Clear items but keep activity history
3. **Partial cleanup** - Delete items but preserve bulk job records

## Comparison with Full Cleanup

| Feature | `/users/:userId/items` | `/users/:userId/data` |
|---------|------------------------|----------------------|
| Items | ✅ Deleted | ✅ Deleted |
| Files | ✅ Deleted | ✅ Deleted |
| BulkJobs | ✅ Preserved | ✅ Deleted |
| ActivityLogs | ✅ Preserved | ✅ Deleted (optional) |
| OTPs | ✅ Preserved | ✅ Deleted (optional) |
| User | ✅ Preserved | ✅ Preserved |

## Example Usage

### Python (Test Framework)
```python
def test_cleanup_items_only(delete_user_items, env_config):
    """Delete only items, preserve logs"""
    success = delete_user_items(
        "editor1@test.com",
        env_config.API_BASE_URL,
        os.getenv('INTERNAL_AUTOMATION_KEY')
    )
    assert success
```

### cURL
```bash
curl -X DELETE \
  http://localhost:3000/api/v1/internal/users/507f1f77bcf86cd799439011/items \
  -H 'x-internal-key: flowhub-secret-automation-key-2025'
```

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "error_code": 400,
  "error_type": "Bad Request - Invalid ID format",
  "message": "Invalid user ID format. Expected 24-character hexadecimal string."
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Unauthorized: Invalid or missing Internal Safety Key"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "error_code": 404,
  "error_type": "Not Found",
  "message": "User not found"
}
```

## Implementation Details
- Uses MongoDB transactions (graceful fallback for test environments)
- Atomic operation (all-or-nothing deletion)
- Fast bulk delete operations
- Deletes files from filesystem (only counts files that actually existed)

## Test Results
- 11/11 tests passing for items-only endpoint
- 19/19 tests passing for full data cleanup endpoint
- Total: 30/30 tests passing ✅
