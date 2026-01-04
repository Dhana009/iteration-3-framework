import os
import json
from utils.api_client import APIClient

STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'state')

class SmartAuth:
    def __init__(self, user_email, user_password, base_url):
        self.email = user_email
        self.password = user_password
        self.base_url = base_url
        self.state_file = os.path.join(STATE_DIR, f"{self.email}.json")
        self.token = None
        self.user_data = None

    def authenticate(self):
        """
        The Smart Gate Logic:
        1. Load Badge (File)
        2. Gate Check (Validate API)
        3. Fast Track (Login if needed)
        """
        # Step 1: Try to load existing state
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    self.user_data = data.get('user')
            except:
                pass # Corrupt file, ignore
        
        # Step 2: Gate Check
        is_valid = False
        if self.token:
            client = APIClient(base_url=self.base_url, token=self.token)
            is_valid = client.validate_token()
            print(f"[SmartAuth] Token for {self.email} is {'VALID' if is_valid else 'EXPIRED'}")

        # Step 3: Fast Track (Login) if invalid
        if not is_valid:
            print(f"[SmartAuth] Logging in fresh for {self.email}...")
            client = APIClient(base_url=self.base_url)
            self.token, self.user_data = client.login(self.email, self.password)
            
            # Save Badge
            with open(self.state_file, 'w') as f:
                json.dump({'token': self.token, 'user': self.user_data}, f)
        
        return self.token, self.user_data
