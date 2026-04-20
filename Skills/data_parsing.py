from .registry import registry

@registry.register(
    name="parse_json_data",
    description="Parses a raw JSON string into formatted and queried data.",
    parameters={
        "json_string": {"type": "string", "description": "Raw JSON string"},
        "key_to_extract": {"type": "string", "description": "Optional specific key to extract from the root level."}
    }
)
def parse_json_data(json_string: str, key_to_extract: str = None) -> str:
    import json
    try:
        data = json.loads(json_string)
        if key_to_extract and isinstance(data, dict):
            return str(data.get(key_to_extract, "Key not found."))
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"JSON Parse Error: {str(e)}"
