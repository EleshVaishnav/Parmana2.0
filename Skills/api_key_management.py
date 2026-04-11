from .registry import registry
import os
from dotenv import set_key

@registry.register(
    name="manage_api_key",
    description="Updates or sets an API key in the local .env file remotely.",
    parameters={
        "key_name": {"type": "string", "description": "Name of the key"},
        "key_value": {"type": "string", "description": "Value of the key"}
    }
)
def manage_api_key(key_name: str, key_value: str) -> str:
    try:
        if not os.path.exists(".env"):
            open(".env", "w").close()
        # Note: requires pip install python-dotenv
        set_key(".env", key_name, key_value)
        return f"Successfully updated {key_name} in .env file."
    except ImportError:
        return "Error: python-dotenv is not installed."
    except Exception as e:
        return str(e)
