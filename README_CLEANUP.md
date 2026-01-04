# Seed Data Cleanup Guide

## Prerequisites

Install MongoDB driver:
```bash
pip install pymongo
```

## Add MongoDB URI to .env

Add your MongoDB connection string to `.env`:
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=flowhub  # Optional, defaults to 'flowhub'
```

## Usage

### 1. Dry Run (Preview)
See what would be deleted without actually deleting:
```bash
python scripts/cleanup_seed_data.py --dry-run
```

### 2. Delete Seed Data
Delete all items with "Seed Item" in the name:
```bash
python scripts/cleanup_seed_data.py
```

### 3. Delete ALL Items (Nuclear Option)
Delete everything in the items collection:
```bash
python scripts/cleanup_seed_data.py --all
```
⚠️ **WARNING:** This will delete ALL items, not just seed data!

## What Gets Deleted?

**Default mode:** Only items with "Seed Item" in the name (case-insensitive)
- Seed Item Alpha - 8fed
- Seed Item Beta - 8fed
- etc.

**`--all` mode:** ALL items in the database

## After Cleanup

After running cleanup, the next test run will automatically recreate seed data via `check_and_heal_seed()` fixture.

## Troubleshooting

**Error: pymongo not installed**
```bash
pip install pymongo
```

**Error: MONGODB_URI not found**
Add `MONGODB_URI` to your `.env` file

**Connection timeout**
Check your MongoDB connection string and network access
