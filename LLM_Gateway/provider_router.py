import os
import litellm

# Explicitly setup supported providers format mapping based on configuration
class ProviderRouter:
    def __init__(self, default_provider: str = "openai", default_model: str = "gpt-4o"):
        """
        Initializes the router instance. Litellm automatically handles API keys if they
        are set in the environment (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY).
        """
        self.default_provider = default_provider.lower()
        self.default_model = default_model

    def _normalize_model_name(self, provider: str, model: str) -> str:
        # litellm expects formats like '{provider}/{model}' for non-openai sometimes,
        # but for native ones like claude-3-opus-20240229 it handles it if we prefix.
        if provider == "anthropic" and not model.startswith("claude"):
            return f"anthropic/{model}"
        elif provider == "gemini" and not model.startswith("gemini"):
            return f"gemini/{model}"
        elif provider == "groq" and not model.startswith("groq/"):
            return f"groq/{model}"
        return model

    def chat_completion(self, messages: list, tools: list = None, provider: str = None, model: str = None, **kwargs):
        """
        Wraps the litellm completion call for robust routing and error handling.
        """
        p = provider or self.default_provider
        m = model or self.default_model
        
        normalized_model = self._normalize_model_name(p, m)
        
        # Mapping parameter diffs
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
            # We could add fallbacks here (e.g., if openai fails, try anthropic)
            raise RuntimeError(f"LLM Gateway Error [{p}]: {str(e)}")
