# MongoDB Configuration for Test Framework

## Add to your .env file:

```bash
# MongoDB Connection
MONGODB_URI=mongodb+srv://djtesting:testingdemo@cluster0.6vhvvpf.mongodb.net
MONGODB_DB_NAME=test
MONGODB_ITEMS_COLLECTION=items

# Feature Flags
ENABLE_SEED_SETUP=true  # Set to false to disable automatic seed data setup

# Internal Automation Key (for cleanup endpoint)
INTERNAL_AUTOMATION_KEY=flowhub-secret-automation-key-2025
```

## Usage:

### Enable Seed Setup
```bash
ENABLE_SEED_SETUP=true pytest tests/
```

### Disable Seed Setup
```bash
ENABLE_SEED_SETUP=false pytest tests/
```
