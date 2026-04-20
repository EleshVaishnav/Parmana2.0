from .registry import registry
import yaml

@registry.register(
    name="update_permission",
    description="Updates the Telegram allowed_username config property.",
    parameters={
        "username": {"type": "string", "description": "The new username to whitelist, or '*' for all."}
    }
)
def update_permission(username: str) -> str:
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        config["channels"]["telegram"]["allowed_username"] = username
        with open("config.yaml", "w") as f:
            yaml.dump(config, f)
        return f"Whitelisted username updated to: {username}"
    except Exception as e:
        return f"Permission Error: {str(e)}"
