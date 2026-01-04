"""
Seed Data Cleanup Utility (MongoDB Direct)

This script deletes all seed items directly from MongoDB.
Use this to reset the baseline seed data and start fresh.

Prerequisites:
    pip install pymongo python-dotenv

Usage:
    python scripts/cleanup_seed_data.py
    
    # Dry run (preview what would be deleted):
    python scripts/cleanup_seed_data.py --dry-run
    
    # Delete all items (not just seed):
    python scripts/cleanup_seed_data.py --all
"""

import sys
import os
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env')

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure
except ImportError:
    print("❌ Error: pymongo not installed")
    print("Install it with: pip install pymongo")
    sys.exit(1)


def get_mongo_connection():
    """Get MongoDB connection from environment variables."""
    mongo_uri = os.getenv('MONGODB_URI')
    
    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in .env file")
        print("Please add MONGODB_URI to your .env file")
        sys.exit(1)
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {str(e)}")
        sys.exit(1)


def cleanup_seed_data(dry_run: bool = False, delete_all: bool = False):
    """
    Delete seed items directly from MongoDB.
    
    Args:
        dry_run: If True, only preview what would be deleted
        delete_all: If True, delete ALL items (not just seed data)
    """
    print("\n" + "="*60)
    print("🧹 SEED DATA CLEANUP UTILITY (MongoDB Direct)")
    print("="*60)
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No data will be deleted")
    
    if delete_all:
        print("⚠️  WARNING: DELETE ALL MODE - Will delete ALL items!")
    
    # Connect to MongoDB
    print("\n🔌 Connecting to MongoDB...")
    client = get_mongo_connection()
    
    # Get database and collection
    db_name = os.getenv('MONGODB_DB_NAME', 'flowhub')  # Default to 'flowhub'
    db = client[db_name]
    items_collection = db['items']
    
    print(f"✅ Connected to database: {db_name}")
    print(f"📦 Collection: items")
    
    try:
        # Build query
        if delete_all:
            query = {}  # Match all documents
            print("\n🔍 Searching for ALL items...")
        else:
            # Match items with "Seed Item" in name
            query = {"name": {"$regex": "Seed Item", "$options": "i"}}
            print("\n🔍 Searching for seed items (name contains 'Seed Item')...")
        
        # Find matching items
        items = list(items_collection.find(query))
        
        if not items:
            print("✅ No items found (already clean)")
            client.close()
            return
        
        print(f"\n📦 Found {len(items)} items:")
        for item in items[:10]:  # Show first 10
            print(f"   - {item.get('name', 'N/A')} (ID: {item['_id']}, Category: {item.get('category', 'N/A')})")
        
        if len(items) > 10:
            print(f"   ... and {len(items) - 10} more items")
        
        if dry_run:
            print(f"\n⚠️  Would delete {len(items)} items (dry run)")
            client.close()
            return
        
        # Confirm deletion
        if delete_all:
            print(f"\n⚠️  WARNING: About to delete ALL {len(items)} items!")
            confirm = input("Type 'DELETE ALL' to confirm: ")
            if confirm != "DELETE ALL":
                print("❌ Deletion cancelled")
                client.close()
                return
        
        # Delete items
        print(f"\n🗑️  Deleting {len(items)} items...")
        result = items_collection.delete_many(query)
        
        print(f"\n✅ Successfully deleted {result.deleted_count} items")
        
    except OperationFailure as e:
        print(f"❌ MongoDB operation failed: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()
        print("\n🔌 MongoDB connection closed")
    
    print("\n" + "="*60)
    print("✅ CLEANUP COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup seed data from MongoDB")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be deleted without deleting")
    parser.add_argument("--all", action="store_true", help="Delete ALL items (not just seed data)")
    
    args = parser.parse_args()
    
    cleanup_seed_data(dry_run=args.dry_run, delete_all=args.all)
