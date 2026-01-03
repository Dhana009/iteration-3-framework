"""
Debug Script: Seed Healer
Reason: Isolate the 422 Error.
"""
import os
import json
from fixtures.auth import SmartAuth
from utils.api_client import APIClient

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config', 'user_pool.json')

SEED_ITEM = {
    "name": "Debug Item Digital",
    "description": "This is a debug item description.",
    "item_type": "DIGITAL", 
    "price": 10.00,
    "category": "Software",
    "download_url": "https://example.com/debug",
    "file_size": 100
}

# Variant ideas: 
# "itemType": "DIGITAL"
# "type": "DIGITAL"
# "item_type": "digital"

def get_admin_creds():
    with open(CONFIG_PATH, 'r') as f:
        pool = json.load(f)
        return pool['ADMIN'][0]['email'], pool['ADMIN'][0]['password']

def run_debug():
    email, password = get_admin_creds()
    print(f"Login as {email}...")
    
    auth = SmartAuth(email, password)
    token, user = auth.authenticate()
    client = APIClient(token=token)
    
    # Try POST
    print("Attempting POST /items...")
    resp = client.post("/items", json=SEED_ITEM)
    
    print(f"Status: {resp.status_code}")
    try:
        print("Response Body:")
        print(json.dumps(resp.json(), indent=2))
    except:
        print(resp.text)
        
    # Validations from docs:
    # name: 3-100 chars, alphanumeric + spaces/hyphens/underscores
    # description: 10-500 chars
    # item_type: DIGITAL
    # price: 0.01 - 999999.99
    # category: 1-50 chars
    # download_url: valid URL
    # file_size: >= 1

if __name__ == "__main__":
    run_debug()
