from .registry import registry
import requests

@registry.register(
    name="call_rest_api",
    description="Makes a generic HTTP REST API call (GET, POST, etc.)",
    parameters={
        "method": {"type": "string", "description": "GET, POST, PUT, DELETE"},
        "url": {"type": "string", "description": "The target URL."},
        "headers_json": {"type": "string", "description": "JSON string of headers. Default is empty dict."},
        "payload_json": {"type": "string", "description": "JSON string of payload for POST/PUT. Default is empty."}
    }
)
def call_rest_api(method: str, url: str, headers_json: str = "{}", payload_json: str = "{}") -> str:
    import json
    try:
        headers = json.loads(headers_json)
        payload = json.loads(payload_json)
        if method.upper() == "GET":
            req = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            req = requests.post(url, headers=headers, json=payload)
        else:
            req = requests.request(method, url, headers=headers, json=payload)
        return f"Status: {req.status_code}\nResponse: {req.text[:2000]}"
    except Exception as e:
        return f"API Error: {str(e)}"
