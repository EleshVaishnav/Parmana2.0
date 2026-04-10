from typing import List, Dict

class SessionMemory:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[Dict[str, str]] = []

    def get_history(self) -> List[Dict[str, str]]:
        return self.messages

    def add_message(self, role: str, content: str, tool_calls: list = None, name: str = None, tool_call_id: str = None):
        """Appends a new message to the sliding window conversation history."""
        msg = {"role": role}

        # Omit 'content' if it's None and there are tool_calls
        if content is not None or role == "tool":
            msg["content"] = str(content) if content is not None else ""
            
        if name:
            msg["name"] = name
            
        if tool_calls:
            msg["tool_calls"] = tool_calls
            
        if tool_call_id:
            msg["tool_call_id"] = tool_call_id

        self.messages.append(msg)
        
        # Enforce sliding window on regular messages (need to be careful not to orphaned tool calls)
        if len(self.messages) > self.max_messages:
            self._trim_history()
            
    def _trim_history(self):
        """Trim history carefully to not split tool_call and tool response."""
        # Simple trim for now, removing oldest message that isn't a system prompt
        trim_from = 0
        if self.messages and self.messages[0].get("role") == "system":
            trim_from = 1
            
        while len(self.messages) > self.max_messages + trim_from:
            # Check if the message we are removing is an assistant tool_call
            msg_to_remove = self.messages[trim_from]
            if msg_to_remove.get("role") == "assistant" and "tool_calls" in msg_to_remove:
                # Need to also remove the corresponding tool responses
                self.messages.pop(trim_from)
                while trim_from < len(self.messages) and self.messages[trim_from].get("role") == "tool":
                    self.messages.pop(trim_from)
            elif msg_to_remove.get("role") == "tool":
                # Should ideally not happen if trimmed sequentially, but safe fallback
                self.messages.pop(trim_from)
            else:
                self.messages.pop(trim_from)

    def clear(self):
        self.messages.clear()
