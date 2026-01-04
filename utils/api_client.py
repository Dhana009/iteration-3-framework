import requests

class APIClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
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
