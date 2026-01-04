
import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB_NAME")]

TARGETS = ["admin1@test.com", "editor1@test.com", "viewer1@test.com"]

print("--- WIPING DATA FOR TARGET USERS ---")
for email in TARGETS:
    user = db.users.find_one({"email": email})
    if user:
        uid = str(user['_id'])
        # Delete items
        res = db.items.delete_many({"created_by": uid})
        print(f"Deleted {res.deleted_count} items for {email}")
    else:
        print(f"User {email} not found")

print("Validating cleanup...")
count = db.items.count_documents({})
print(f"Total items remaining in DB: {count}")
print("Done.")
