import yaml
from pathlib import Path

class ClientConfig:
    def __init__(self, data: dict):
        self.name = data.get("name")
        self.client_id = data.get("client_id")
        self.client_secret = data.get("client_secret")
        self.tenant = data.get("tenant")
        self.base_url = data.get("base_url")
        self.app_to_access = data.get("app_to_access")

class RagConfig:
    def __init__(self, data: dict):
        self.documents_path = data.get("documents_path")
        self.supported_file_types = data.get("supported_file_types", [".txt", ".pdf"])
        self.recurse_folders = data.get("recurse_folders", False)

class Config:
    def __init__(self, config_path: str = "backend/config/config.yaml"):
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        self.client = ClientConfig(data.get("client", {}))
        self.rag = RagConfig(data.get("rag", {}))
        self.api_token = "" # Placeholder for API token management

config = Config()
