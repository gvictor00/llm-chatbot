class FlowAPIEndpoints:
    AUTH_TOKEN = "/auth-engine-api/v1/api-key/token"
    AUTH_HEALTH = "/auth-engine-api/v1/health"
    LLM_HEALTH = "/ai-orchestration-api/v1/health"

# Example of usage:
# url = f"{config.flow_api_base_url}{FlowAPIEndpoints.LLM_HEALTH}"
