import os

class PromptManager:
    def __init__(self, system_prompt_path: str = "system_prompt.txt"):
        self.system_prompt_path = system_prompt_path
        self._base_prompt = self._load_base_prompt()

    def _load_base_prompt(self) -> str:
        if os.path.exists(self.system_prompt_path):
            with open(self.system_prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "You are an AI assistant."

    def construct_system_message(self, context_snippets: list = None) -> dict:
        """Constructs the system message dynamically injected with long-term memory."""
        prompt = self._base_prompt
        
        if context_snippets and len(context_snippets) > 0:
            prompt += "\n\n--- RELEVANT MEMORY RETRIEVED ---\n"
            for i, snip in enumerate(context_snippets):
                prompt += f"{i+1}. {snip}\n"
            prompt += "--- END RELEVANT MEMORY ---\n"
            prompt += "Use the above memory snippets if they are relevant to answer the user's current request."
            
        return {"role": "system", "content": prompt}
