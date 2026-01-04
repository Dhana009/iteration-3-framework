"""
Quick test of MongoDB fixtures implementation

Run this to verify:
1. MongoDB connection works
2. Fixtures are loaded
3. Feature flag works
"""

import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv()

def test_env_variables():
    """Test that environment variables are set"""
    print("\n" + "="*60)
    print("Testing Environment Variables")
    print("="*60)
    
    mongo_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME')
    enable_seed = os.getenv('ENABLE_SEED_SETUP', 'false')
    
    print(f"✓ MONGODB_URI: {mongo_uri[:50]}..." if mongo_uri else "✗ MONGODB_URI: Not set")
    print(f"✓ MONGODB_DB_NAME: {db_name}" if db_name else "✗ MONGODB_DB_NAME: Not set")
    print(f"✓ ENABLE_SEED_SETUP: {enable_seed}")
    
    assert mongo_uri, "MONGODB_URI not set in .env"
    assert db_name, "MONGODB_DB_NAME not set in .env"
    print("\n✅ Environment variables OK")

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n" + "="*60)
    print("Testing MongoDB Connection")
    print("="*60)
    
    from pymongo import MongoClient
    
    mongo_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME')
    
    print(f"Connecting to: {db_name}...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    # Test connection
    db.command('ping')
    print("✓ MongoDB connection successful")
    
    # Check collections
    collections = db.list_collection_names()
    print(f"✓ Found {len(collections)} collections: {', '.join(collections)}")
    
    # Check users
    user_count = db.users.count_documents({})
    print(f"✓ Found {user_count} users in database")
    
    client.close()
    print("\n✅ MongoDB connection OK")

def test_fixtures_import():
    """Test that fixtures can be imported"""
    print("\n" + "="*60)
    print("Testing Fixture Imports")
    print("="*60)
    
    try:
        from tests.plugins import mongodb_fixtures
        print("✓ mongodb_fixtures imported")
        
        from tests.plugins import api_fixtures
        print("✓ api_fixtures imported")
        
        print("\n✅ Fixture imports OK")
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        raise

def test_seed_items():
    """Test that seed items are defined"""
    print("\n" + "="*60)
    print("Testing Seed Items")
    print("="*60)
    
    from lib.seed import SEED_ITEMS
    
    print(f"✓ Found {len(SEED_ITEMS)} seed items")
    
    # Show first item
    if SEED_ITEMS:
        first = SEED_ITEMS[0]
        print(f"✓ Sample item: {first.get('name')}")
        print(f"  - Category: {first.get('category')}")
        print(f"  - Type: {first.get('item_type')}")
        print(f"  - Price: ${first.get('price')}")
    
    assert len(SEED_ITEMS) == 11, f"Expected 11 seed items, found {len(SEED_ITEMS)}"
    print("\n✅ Seed items OK")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MongoDB Fixtures - Quick Test")
    print("="*60)
    
    try:
        test_env_variables()
        test_mongodb_connection()
        test_fixtures_import()
        test_seed_items()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nReady to run pytest tests:")
        print("  pytest tests/verification/")
        
    except Exception as e:
        print(f"\n" + "="*60)
        print("✗ TEST FAILED")
        print("="*60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
