import requests

class APIClient:
    def __init__(self, base_url, token=None):
        # Normalize base_url: remove trailing slashes
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _build_url(self, endpoint):
        """
        Build URL by properly joining base_url and endpoint.
        Handles cases where base_url has trailing slash or endpoint has leading slash.
        """
        # Normalize endpoint: remove leading slashes
        endpoint = endpoint.lstrip('/')
        # Join with single slash
        return f"{self.base_url}/{endpoint}"

    def post(self, endpoint, data=None, json=None):
        url = self._build_url(endpoint)
        response = self.session.post(url, data=data, json=json)
        return response

    def get(self, endpoint, params=None):
        url = self._build_url(endpoint)
        response = self.session.get(url, params=params)
        return response

    def put(self, endpoint, data=None, json=None):
        url = self._build_url(endpoint)
        response = self.session.put(url, data=data, json=json)
        return response
    
    def patch(self, endpoint, data=None, json=None):
        url = self._build_url(endpoint)
        response = self.session.patch(url, data=data, json=json)
        return response
    
    def delete(self, endpoint):
        url = self._build_url(endpoint)
        response = self.session.delete(url)
        return response
