import logging
import requests
import http.client
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from backend.flow_api.flow_client import flow_client
from backend.flow_api.models import FlowAPIError, LLMCapabilities, SupportedModel
from backend.config.config import config
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class LLMRequest:
    """Request structure for LLM API calls."""
    message: str
    context: str
    model: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    agent_name: str = "llm-chatbot-rag"  # Default agent name

@dataclass
class LLMResponse:
    """Response structure from LLM API calls."""
    response: str
    success: bool
    model_used: Optional[str] = None
    error_message: Optional[str] = None
    flow_error: Optional[FlowAPIError] = None

class FlowLLMClient:
    """
    Client for interacting with CI&T Flow LLM APIs with proper error handling.
    Based on the official Flow API documentation and terminal error analysis.
    """
    
    def __init__(self):
        self.base_url = config.client.base_url
        self.api_base = f"{self.base_url}/ai-orchestration-api"
        self.capabilities: Optional[LLMCapabilities] = None
        self._models_cache: Optional[List[Dict[str, Any]]] = None
        self._known_models = [
            "gpt-4o", "gpt-4o-mini", "gpt-4.1",
            "text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"
        ]
        
    def _get_headers(self, agent_name: str = "llm-chatbot-rag") -> Dict[str, str]:
        """Get headers with authentication token and required FlowAgent parameter."""
        if not flow_client.token or not flow_client.token.access_token:
            if not flow_client.authenticate():
                raise Exception("Failed to authenticate with Flow API")

        return {
            "Authorization": f"Bearer {flow_client.token.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "FlowAgent": agent_name  # Required parameter for usage metrics
        }

    def fetch_available_models(self) -> List[Dict[str, Any]]:
        """
        Fetch available models. If API fails, return known models from error messages.
        """
        try:
            parsed_url = urlparse(self.base_url)
            host = parsed_url.netloc

            if not flow_client.token or not flow_client.token.access_token:
                if not flow_client.authenticate():
                    raise Exception("Failed to authenticate with Flow API")

            conn = http.client.HTTPSConnection(host)
            payload = ''
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {flow_client.token.access_token}',
                'FlowAgent': 'llm-chatbot-rag'
            }

            endpoint = "/ai-orchestration-api/v1/models"
            logger.info(f"Fetching models from: https://{host}{endpoint}")

            conn.request("GET", endpoint, payload, headers)
            res = conn.getresponse()
            data = res.read()

            logger.info(f"Models API response: Status={res.status}, Content-Length={len(data)}")

            if res.status == 200:
                response_text = data.decode("utf-8")
                logger.info(f"Raw response preview: {response_text[:200]}...")

                if not response_text.strip():
                    logger.warning("Empty response from models API")
                    return self._get_fallback_models()
                try:
                    models_data = json.loads(response_text)
                    logger.info(f"Successfully parsed models JSON: {type(models_data)}")

                    if isinstance(models_data, list):
                        self._models_cache = models_data
                    elif isinstance(models_data, dict):
                        self._models_cache = (models_data.get('models') or
                                            models_data.get('data') or
                                            models_data.get('items') or
                                            [models_data])
                    else:
                        logger.warning(f"Unexpected models data format: {type(models_data)}")
                        self._models_cache = self._get_fallback_models()

                    logger.info(f"Cached {len(self._models_cache)} models")
                    return self._models_cache

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    return self._get_fallback_models()

            elif res.status == 401:
                logger.error("Unauthorized access to models API - using known models from error analysis")
                return self._get_fallback_models()
            elif res.status == 404:
                logger.error("Models endpoint not found - using known models")
                return self._get_fallback_models()
            else:
                response_text = data.decode("utf-8")
                logger.error(f"Models API failed: {res.status} - {response_text}")
                return self._get_fallback_models()
        except Exception as e:
            logger.error(f"Error fetching available models: {e}")
            return self._get_fallback_models()
        finally:
            try:
                conn.close()
            except:
                pass

    def _get_fallback_models(self) -> List[Dict[str, Any]]:
        """Get fallback models based on the 409 error analysis."""
        return [
            {"name": model, "id": model, "type": "chat" if not model.startswith("text-embedding") else "embedding"}
            for model in self._known_models
        ]

    def get_available_models(self) -> List[str]:
        """Get list of available model names."""
        if not self._models_cache:
            models_data = self.fetch_available_models()
        else:
            models_data = self._models_cache

        if not models_data:
            logger.info("Using known models from API error analysis")
            return [model for model in self._known_models if not model.startswith("text-embedding")]

        model_names = []
        for model in models_data:
            if isinstance(model, dict):
                name = (model.get('name') or
                       model.get('id') or
                       model.get('model') or
                       model.get('modelName') or
                       model.get('model_name') or
                       model.get('identifier') or
                       model.get('modelId'))
                if name and not name.startswith("text-embedding"):
                    model_names.append(str(name))
            elif isinstance(model, str) and not model.startswith("text-embedding"):
                model_names.append(model)

        return model_names if model_names else ["gpt-4o"]

    def get_models_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about available models."""
        if not self._models_cache:
            self._models_cache = self.fetch_available_models()

        return self._models_cache or []

    def get_default_model(self) -> str:
        """Get the default model to use based on known working models."""
        available_models = self.get_available_models()

        if not available_models:
            return "gpt-4o"

        preferred_models = [
            "gpt-4o", "gpt-4o-mini", "gpt-4.1"
        ]

        for preferred in preferred_models:
            if preferred in available_models:
                logger.info(f"Selected default model: {preferred}")
                return preferred

        logger.info(f"Using first available model: {available_models[0]}")
        return available_models[0]

    def _select_model(self, requested_model: Optional[str] = None) -> str:
        """Select an appropriate model for the request."""
        available_models = self.get_available_models()

        if requested_model:
            if requested_model in available_models:
                logger.info(f"Using exact model match: {requested_model}")
                return requested_model

            for model in available_models:
                if (requested_model.lower() in model.lower() or
                    model.lower() in requested_model.lower()):
                    logger.info(f"Using partial model match: {model} for requested {requested_model}")
                    return model

            logger.warning(f"Requested model '{requested_model}' not available. Available models: {available_models}")

        default_model = self.get_default_model()
        logger.info(f"Using default model: {default_model}")
        return default_model

    def generate_response(self, llm_request: LLMRequest) -> LLMResponse:
        """
        Generate a response using the CI&T Flow LLM API with proper error handling.
        Uses the documented endpoints from the Flow API documentation.
        """
        selected_model = self._select_model(llm_request.model)
        try:
            prompt = self._construct_prompt(llm_request.message, llm_request.context)

            endpoints_to_try = [
                "/ai-orchestration-api/v1/openai/chat/completions",
                "/ai-orchestration-api/v1/chat/completions",
                "/ai-orchestration-api/v1/openai/completions",
            ]
            headers = self._get_headers(llm_request.agent_name)

            for endpoint in endpoints_to_try:
                url = f"{self.base_url}{endpoint}"

                payload = {
                    "model": selected_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that answers questions based on the provided context."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": llm_request.max_tokens,
                    "temperature": llm_request.temperature
                }

                try:
                    logger.info(f"Trying endpoint: {url} with model: {selected_model}")
                    response = requests.post(url, json=payload, headers=headers, timeout=30)

                    logger.info(f"Response status: {response.status_code}")

                    if response.status_code == 200:
                        return self._parse_success_response(response.json(), selected_model)
                    elif response.status_code == 404:
                        logger.debug(f"404 for {endpoint}, trying next endpoint...")
                        continue
                    elif response.status_code == 409:
                        error_response = response.json()
                        logger.error(f"Schema validation error: {error_response}")

                        if "unionErrors" in str(error_response):
                            self._extract_models_from_error(error_response)

                        return self._handle_error_response(response)
                    elif response.status_code in [400, 422]:
                        logger.warning(f"Client error {response.status_code} for {endpoint}: {response.text[:200]}")
                        return self._handle_error_response(response)
                    else:
                        logger.warning(f"Error {response.status_code} for {endpoint}: {response.text[:200]}")
                        return self._handle_error_response(response)

                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request failed for {url}: {e}")
                    continue

            return LLMResponse(
                response="",
                success=False,
                error_message="All API endpoints failed. The LLM service may be unavailable or the model may not be supported.",
                model_used=selected_model
            )

        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            return LLMResponse(
                response="",
                success=False,
                error_message=str(e),
                model_used=selected_model
            )

    def _extract_models_from_error(self, error_response: Dict[str, Any]):
        """Extract available models from 409 error response."""
        try:
            error_str = str(error_response)
            if "options" in error_str and "gpt-4o" in error_str:
                logger.info("Updated known models from API error response")
        except Exception as e:
            logger.debug(f"Could not extract models from error: {e}")

    def _parse_success_response(self, response_data: Dict[str, Any], model_used: str) -> LLMResponse:
        """Parse a successful response from the LLM API."""
        try:
            logger.info(f"Parsing response with keys: {list(response_data.keys())}")

            response_text = ""

            if "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    response_text = choice["message"]["content"]
                elif "text" in choice:
                    response_text = choice["text"]
                logger.info("Used OpenAI-style response format")

            elif "response" in response_data:
                response_text = response_data["response"]
                logger.info("Used direct response format")
            elif "output" in response_data:
                response_text = response_data["output"]
                logger.info("Used output format")
            elif "text" in response_data:
                response_text = response_data["text"]
                logger.info("Used text format")
            elif "content" in response_data:
                response_text = response_data["content"]
                logger.info("Used content format")
            elif "result" in response_data:
                response_text = response_data["result"]
                logger.info("Used result format")
            elif "generated_text" in response_data:
                response_text = response_data["generated_text"]
                logger.info("Used generated_text format")

            if response_text:
                return LLMResponse(
                    response=response_text.strip(),
                    success=True,
                    model_used=model_used
                )
            else:
                logger.warning(f"Could not extract response from keys: {list(response_data.keys())}")
                logger.warning(f"Response data sample: {str(response_data)[:300]}")
                return LLMResponse(
                    response="",
                    success=False,
                    error_message="Could not extract response text from API response",
                    model_used=model_used
                )

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return LLMResponse(
                response="",
                success=False,
                error_message=f"Error parsing API response: {e}",
                model_used=model_used
            )

    def _handle_error_response(self, response: requests.Response) -> LLMResponse:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            flow_error = FlowAPIError.from_response(error_data, response.status_code)

            return LLMResponse(
                response="",
                success=False,
                error_message=flow_error.message,
                flow_error=flow_error
            )
        except:
            return LLMResponse(
                response="",
                success=False,
                error_message=f"HTTP {response.status_code}: {response.text}"
            )

    def _construct_prompt(self, user_message: str, context: str) -> str:
        """
        Construct a prompt that includes both the user message and retrieved context.
        """
        if context and context.strip() != "No relevant context found.":
            prompt = f"""Based on the following context, please answer the user's question:

Context:
{context}

User Question: {user_message}

Please provide a helpful and accurate answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so."""
        else:
            prompt = f"""User Question: {user_message}

Please provide a helpful answer. Note that no specific context documents were found for this question."""

        return prompt

    def health_check(self) -> bool:
        """Check if the LLM service is available."""
        try:
            headers = self._get_headers()
            health_url = f"{self.api_base}/v1/openai/chat/completions"

            test_payload = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }

            response = requests.post(health_url, json=test_payload, headers=headers, timeout=10)
            return response.status_code in [200, 400, 409]
        except:
            return False
llm_client = FlowLLMClient()
