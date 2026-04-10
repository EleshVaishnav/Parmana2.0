import json
from LLM_Gateway.provider_router import ProviderRouter
from Memory.session_memory import SessionMemory
from Memory.vector_memory import vector_memory # initialized globally
from Core.prompt_manager import PromptManager
from Skills.registry import registry
from Vision.vision_handler import VisionHandler

class ParmanaAgent:
    def __init__(self, config: dict):
        self.config = config
        
        # Init Router
        llm_cfg = config.get("llm", {})
        self.router = ProviderRouter(
            default_provider=llm_cfg.get("default_provider", "openai"),
            default_model=llm_cfg.get("model_name", "gpt-4o")
        )
        
        # Init Memory
        mem_cfg = config.get("memory", {})
        self.session_memory = SessionMemory(max_messages=mem_cfg.get("short_term_max_messages", 20))
        self.prompt_manager = PromptManager()
        
    def _execute_tool_calls(self, tool_calls) -> list:
        results = []
        for call in tool_calls:
            # Depending on Litellm version, call structure might vary slightly.
            # Usually struct: call.function.name, call.function.arguments (json str)
            func_name = call.function.name
            args_str = call.function.arguments
            
            try:
                args = json.loads(args_str)
                print(f"[ACTION] Executing {func_name} with args {args}")
                result_str = registry.execute(func_name, **args)
            except Exception as e:
                result_str = f"Error interpreting or executing tool: {str(e)}"
                
            results.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": func_name,
                "content": result_str
            })
            
            # Save important tool outputs to vector memory implicitly?
            # E.g., if we web search, maybe remember the summary. (Omitted for brevity, but possible).
            
        return results

    def chat(self, user_input: str, image_path: str = None) -> str:
        """
        Main cognitive loop:
        1. Query Vector Memory
        2. Construct system prompt
        3. Iterate through LLM thinking -> Tool Calling -> LLM Response until final text answer
        """
        # 1. Retrieve associated long-term memory
        context = []
        if vector_memory:
            context = vector_memory.search_memory(user_input, n_results=3)

        # 2. Add System Prompt to messages temporarily
        system_msg = self.prompt_manager.construct_system_message(context)
        
        # 3. Handle User Input (Vision vs Text)
        message_content = user_input
        if image_path:
            message_content = VisionHandler.construct_vision_message(user_input, image_path)
            
        self.session_memory.add_message("user", message_content)
        
        # 4. Cognitive Loop
        tools = registry.get_schemas()
        max_loops = 5
        loops = 0
        
        while loops < max_loops:
            messages = [system_msg] + self.session_memory.get_history()
            
            # Call LLM
            response = self.router.chat_completion(
                messages=messages,
                tools=tools if tools else None
            )
            
            msg_obj = response.choices[0].message
            
            # If standard response
            if not msg_obj.tool_calls:
                # Save assistant response to session memory
                self.session_memory.add_message("assistant", msg_obj.content)
                
                # Save user query + assistant answer to vector memory
                if vector_memory:
                    combined = f"User: {user_input}\nParmana: {msg_obj.content}"
                    vector_memory.add_memory(combined)
                    
                return msg_obj.content
                
            # If tool calls
            # Save the assistant's intention to call tools
            tool_call_dicts = [m.model_dump() for m in msg_obj.tool_calls] if hasattr(msg_obj.tool_calls[0], "model_dump") else msg_obj.tool_calls
            self.session_memory.add_message("assistant", content=msg_obj.content, tool_calls=tool_call_dicts)
            
            # Execute tools
            tool_responses = self._execute_tool_calls(msg_obj.tool_calls)
            for tr in tool_responses:
                self.session_memory.add_message(
                    role="tool", 
                    content=tr["content"], 
                    name=tr["name"], 
                    tool_call_id=tr["tool_call_id"]
                )
                
            loops += 1
            
        return "Error: Brain loop max iterations reached without final answer."
