# 🧹 Seed Data Cleanup Configuration Guide

## Quick Start

### Option 1: Manual Cleanup (Recommended)

Run the cleanup script whenever you want to reset seed data:

```bash
# Preview what will be deleted
python scripts/cleanup_seed_data.py --dry-run

# Delete seed data
python scripts/cleanup_seed_data.py

# Delete ALL items (nuclear option)
python scripts/cleanup_seed_data.py --all
```

---

### Option 2: Auto-Cleanup Before Tests

Enable automatic cleanup before every test session:

**1. Edit your `.env` file:**
```bash
CLEANUP_SEED_ON_START=true  # Enable auto-cleanup
```

**2. Run tests normally:**
```bash
pytest tests/ui/
```

The seed data will be automatically cleaned before tests start!

**To disable auto-cleanup:**
```bash
CLEANUP_SEED_ON_START=false  # Or remove the line
```

---

## Configuration Options

### `.env` Settings

```bash
# Seed Data Cleanup
CLEANUP_SEED_ON_START=false  # true = auto-cleanup, false = manual only

# MongoDB Connection (Required)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=test  # Your database name
```

---

## When to Use Each Option

| Scenario | Recommended Approach |
|----------|---------------------|
| **Daily development** | Manual cleanup (`python scripts/cleanup_seed_data.py`) |
| **CI/CD pipeline** | Auto-cleanup (`CLEANUP_SEED_ON_START=true`) |
| **Fresh start** | Manual cleanup |
| **Debugging tests** | Manual cleanup (more control) |

---

## Examples

### Example 1: Clean and Run Tests
```bash
# Step 1: Clean seed data
python scripts/cleanup_seed_data.py

# Step 2: Run tests (will recreate seed data)
pytest tests/ui/test_search_discovery.py -v
```

### Example 2: Auto-Clean Every Run
```bash
# In .env:
CLEANUP_SEED_ON_START=true

# Just run tests:
pytest tests/ui/ -n 5 -v
# Seed data will be cleaned automatically before tests start
```

### Example 3: Nuclear Reset (Delete Everything)
```bash
python scripts/cleanup_seed_data.py --all
# Type "DELETE ALL" to confirm
```

---

## Troubleshooting

**Q: Auto-cleanup not working?**
- Check `.env` has `CLEANUP_SEED_ON_START=true`
- Verify `MONGODB_URI` is set correctly
- Check `conftest.py` exists in project root

**Q: Want to disable auto-cleanup?**
```bash
# In .env:
CLEANUP_SEED_ON_START=false
```

**Q: Cleanup too slow?**
- Use manual cleanup only when needed
- Disable auto-cleanup for faster test runs

---

## Summary

**Easiest way to clean seed data:**
```bash
python scripts/cleanup_seed_data.py
```

**Enable auto-cleanup:**
```bash
# Add to .env:
CLEANUP_SEED_ON_START=true
```

Done! 🎉
