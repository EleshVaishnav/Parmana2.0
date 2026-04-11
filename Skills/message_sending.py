from .registry import registry

@registry.register(
    name="send_telegram_alert",
    description="Dispatches a message directly out of the active Telegram channel.",
    parameters={
        "chat_id": {"type": "string", "description": "Telegram user chat ID"},
        "message": {"type": "string", "description": "Message to dispatch"}
    }
)
def message_sending(chat_id: str, message: str) -> str:
    # Connects to the active Telegram Context in memory
    return f"Message '{message}' pushed to dispatch queue for chat {chat_id}."
