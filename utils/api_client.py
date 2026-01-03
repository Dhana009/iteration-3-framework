import os
import requests

# Manual Env Loader to avoid extra dependencies
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config

ENV = load_env()
BASE_URL = ENV.get('BACKEND_BASE_URL', 'http://localhost:3000/api/v1')

class APIClient:
    def __init__(self, token=None):
        self.base_url = BASE_URL
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def post(self, endpoint, data=None, json=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, data=data, json=json)
        return response

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        return response

    def put(self, endpoint, data=None, json=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, data=data, json=json)
        return response
    
    def patch(self, endpoint, data=None, json=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.patch(url, data=data, json=json)
        return response
    
    def delete(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url)
        return response
        
    def login(self, email, password):
        """
        Specific login helper.
        Returns (token, user_data) or Raises Error.
        """
        resp = self.post("/auth/login", json={"email": email, "password": password})
        if resp.status_code == 200:
            data = resp.json()
            return data.get("token"), data.get("user")
        else:
            raise ValueError(f"Login failed for {email}: {resp.status_code} {resp.text}")

    def validate_token(self):
        """
        Hits /auth/me to check token validity.
        Returns True if valid (200), False otherwise.
        """
        resp = self.get("/auth/me")
        return resp.status_code == 200
