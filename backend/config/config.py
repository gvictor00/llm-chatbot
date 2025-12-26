import yaml
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_default_config() -> Dict[str, Any]:
    """Return default configuration."""
    return {
        "client": {
            "name": "flow",
            "client_id": "",
            "client_secret": "",
            "tenant": "cit",
            "base_url": "https://flow.ciandt.com"
        },
        "rag": {
            "documents_path": "files",
            "supported_file_types": [".txt", ".pdf"],
            "recurse_folders": False
        }
    }

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and return configuration."""
    return config

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, looks for config.yaml in config directory.

    Returns:
        Dictionary containing configuration
    """
    if config_path is None:
        config_dir = Path(__file__).parent
        config_path = config_dir / "config.yaml"

    try:
        if not os.path.exists(config_path):
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return get_default_config()

        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        config = validate_config(config)
        logger.info(f"Configuration loaded from {config_path}")
        return config

    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        logger.info("Using default configuration")
        return get_default_config()

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
    def __init__(self, config_path: str = None):
        data = load_config(config_path)
        self.client = ClientConfig(data.get("client", {}))
        self.rag = RagConfig(data.get("rag", {}))
        self.api_token = ""  # Placeholder for API token management

config = Config()
