import os
import re
import json
import uuid
import litellm

class ProviderRouter:
    def __init__(self, default_provider: str = "openai", default_model: str = "gpt-4o"):
        """
        Initializes the router instance. Litellm automatically handles API keys if they
        are set in the environment (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY).
        """
        self.default_provider = default_provider.lower()
        self.default_model = default_model

    def _normalize_model_name(self, provider: str, model: str) -> str:
        if provider == "anthropic" and not model.startswith("claude"):
            return f"anthropic/{model}"
        elif provider == "gemini" and not model.startswith("gemini"):
            return f"gemini/{model}"
        elif provider == "groq" and not model.startswith("groq/"):
            return f"groq/{model}"
        return model

    def _parse_malformed_tool_call(self, error_str: str):
        """
        Llama 3 on Groq generates tool calls with many broken tag formats.
        All observed broken patterns:
          <function=name{"args"}>          - missing separator
          <function=name {"args"}>         - space
          <function=name,{"args"}>         - comma
          <function=name({"args"})>        - parentheses  ← NEW
          <function=name>{"args"}</function> - correct but still fails

        Strategy:
          1. Extract the JSON error body from the raw error string
          2. Pull `failed_generation` from it (handling escaped inner quotes)
          3. Apply a flexible regex covering all separator patterns
        """
        failed_gen = None

        # Step 1: Find the JSON block after "GroqException - " in the error string
        json_start = error_str.find('{')
        if json_start != -1:
            try:
                error_json = json.loads(error_str[json_start:])
                failed_gen = error_json.get("error", {}).get("failed_generation", "")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 2: If JSON parse failed, try simple unicode-decode of the whole string
        if not failed_gen:
            # Normalize \u003c -> < and \u003e -> > manually
            normalized = error_str.replace('\\u003c', '<').replace('\\u003e', '>').replace('\\u0022', '"')
            failed_gen = normalized

        # Step 3: Match the function tag — name then ANY separator then JSON object
        # Covers: >{, {, ,{, ({...}), >{...}<, space{, etc.
        match = re.search(
            r'<function=([a-zA-Z_][a-zA-Z0-9_]*)[\s,>(>]*(\{.+?\})\)?(?:\s*</function>)?',
            failed_gen,
            re.DOTALL
        )
        if not match:
            return None

        tool_name = match.group(1).strip()
        args_str = match.group(2).strip()

        try:
            args = json.loads(args_str)
            return tool_name, args
        except json.JSONDecodeError:
            return None

    def _make_synthetic_tool_call_response(self, tool_name: str, args: dict):
        """
        Builds a synthetic litellm-compatible response object that mimics a proper
        tool_calls response, so the agent loop can execute the tool normally.
        """
        call_id = f"call_{uuid.uuid4().hex[:8]}"
        
        # Use SimpleNamespace to mimic the litellm response object structure
        from types import SimpleNamespace

        tool_call = SimpleNamespace(
            id=call_id,
            type="function",
            function=SimpleNamespace(
                name=tool_name,
                arguments=json.dumps(args)
            )
        )

        # Add model_dump() to mimic pydantic model behaviour expected by agent.py
        def model_dump():
            return {
                "id": call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(args)
                }
            }
        tool_call.model_dump = model_dump

        message = SimpleNamespace(
            content=None,
            tool_calls=[tool_call],
            role="assistant"
        )

        choice = SimpleNamespace(message=message)
        response = SimpleNamespace(choices=[choice])
        return response

    def chat_completion(self, messages: list, tools: list = None, provider: str = None, model: str = None, **kwargs):
        """
        Wraps the litellm completion call for robust routing and error handling.
        Includes a fallback XML parser for Llama 3 / Groq malformed tool call errors.
        """
        p = provider or self.default_provider
        m = model or self.default_model

        normalized_model = self._normalize_model_name(p, m)

        completion_kwargs = {
            "model": normalized_model,
            "messages": messages,
            **kwargs
        }

        if tools and len(tools) > 0:
            completion_kwargs["tools"] = tools

        try:
            response = litellm.completion(**completion_kwargs)
            return response
        except Exception as e:
            error_str = str(e)

            # --- Fallback: Try to recover from Llama 3 malformed tool call ---
            if "tool_use_failed" in error_str or "failed_generation" in error_str:
                parsed = self._parse_malformed_tool_call(error_str)
                if parsed:
                    tool_name, args = parsed
                    return self._make_synthetic_tool_call_response(tool_name, args)

            # Not recoverable — raise as before
            raise RuntimeError(f"LLM Gateway Error [{p}]: {error_str}")
