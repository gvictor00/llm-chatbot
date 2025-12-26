import requests
from src.config.config import config
from src.flow_api.endpoints import FlowAPIEndpoints
from src.flow_api.models import FlowAccessToken, HealthStatus

class FlowAPIClient:
    def __init__(self):
        self.base_url = config.client.base_url
        self.tenant = config.client.tenant
        self.client_id = config.client.client_id
        self.client_secret = config.client.client_secret
        self.app_to_access = config.client.app_to_access
        self.token = None

    def authenticate(self) -> bool:
        url = f"{self.base_url}{FlowAPIEndpoints.AUTH_TOKEN}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "FlowTenant": self.tenant
        }
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "appToAccess": self.app_to_access
        }
        try:
            print("Authenticating with payload:", payload)
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                self.token = FlowAccessToken.from_dict(response.json())
                print("Authentication successful, token obtained.")
                return True
            else:
                print("Authentication failed with status code:", response.status_code, response.text)
            return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def check_token_validity(self) -> bool:
        if self.token is None:
            return False

        url = f"{self.base_url}/auth-engine-api/v1/health"
        headers = {
            "Authorization": f"Bearer {self.token.access_token}"
        }

        try:
            print("Checking token validity with headers:", headers)
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                print("Token is valid.")
                return True
            else:
                print("Token is invalid with status code:", response.status_code, response.text)
            return False
        except Exception as e:
            print(f"Token validity check failed: {e}")
            return False

    def health_check(self) -> bool:
        if not self.authenticate():
            return False

        url = f"{self.base_url}{FlowAPIEndpoints.LLM_HEALTH}"
        headers = {
            "Authorization": f"Bearer {self.token.access_token}",
            "Content-Type": "application/json"
        }
        try:
            print("Performing health check to", url, "with payload:", headers)
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            if response.status_code == 200:
                health = HealthStatus.from_dict(response.json())
                print("Health check successful:", health)
                return True
            else:
                print("Health check failed with status code:", response.status_code, response.text)
                return False
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

flow_client = FlowAPIClient()