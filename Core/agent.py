import json
from LLM_Gateway.provider_router import ProviderRouter
from Memory.session_memory import SessionMemory
import Memory.vector_memory as vm
from Core.prompt_manager import PromptManager
from Skills.registry import registry
from Vision.vision_handler import VisionHandler
from Core.logger import logger

class DeepClawAgent:
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
        self.notification_hook = None
        self.current_sender_id = None  # Tracks the real sender for the current chat turn
        
        try:
            import Skills.scheduling as sched
            sched.global_notification_hook = lambda user, msg: self.notification_hook(user, msg) if self.notification_hook else None
            sched._current_agent_ref = self  # Allow scheduler to read real sender_id
        except Exception:
            pass
        
    def _execute_tool_calls(self, tool_calls) -> list:
        results = []
        for call in tool_calls:
            # Depending on Litellm version, call structure might vary slightly.
            # Usually struct: call.function.name, call.function.arguments (json str)
            func_name = call.function.name
            args_str = call.function.arguments
            
            try:
                args = json.loads(args_str)
                logger.info(f"[ACTION] Executing {func_name} with args {args}")
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

    def chat(self, user_input: str, image_path: str = None, sender_id: str = None) -> str:
        """
        Main cognitive loop:
        1. Query Vector Memory
        2. Construct system prompt
        3. Iterate through LLM thinking -> Tool Calling -> LLM Response until final text answer
        """
        # Track the real sender for this turn (used by scheduling system)
        self.current_sender_id = sender_id
        
        # 1. Retrieve associated long-term memory
        context = []
        if vm.vector_memory:
            context = vm.vector_memory.search_memory(user_input, n_results=3)

        # 2. Add System Prompt to messages temporarily
        system_msg = self.prompt_manager.construct_system_message(context)
        if sender_id:
            system_msg["content"] += f"\n\n[CONTEXT]\nThe current user interacting with you has the ID: {sender_id}. When using schedule_action, you MUST use EXACTLY this ID as target_user_id: {sender_id}"
        
        # 3. Handle User Input (Vision vs Text)
        message_content = f"<user_input>\n{user_input}\n</user_input>"
        if image_path:
            message_content = VisionHandler.construct_vision_message(f"<user_input>\n{user_input}\n</user_input>", image_path)
            
        self.session_memory.add_message("user", message_content)
        
        # 4. Cognitive Loop
        tools = registry.get_schemas()
        max_loops = 10  # Increased for browser tasks that need many steps
        loops = 0
        
        while loops < max_loops:
            messages = [system_msg] + self.session_memory.get_history()
            
            # On the last loop, remove tools to FORCE a text answer from the LLM
            is_last_loop = (loops >= max_loops - 2)
            active_tools = None if is_last_loop else (tools if tools else None)
            
            # Call LLM
            response = self.router.chat_completion(
                messages=messages,
                tools=active_tools
            )
            
            msg_obj = response.choices[0].message
            
            # If standard text response → return it
            if not msg_obj.tool_calls:
                content = msg_obj.content or "Done."
                # Save assistant response to session memory
                self.session_memory.add_message("assistant", content)
                
                # Save user query + assistant answer to vector memory
                if vm.vector_memory:
                    combined = f"User: {user_input}\nDeepClaw: {content}"
                    vm.vector_memory.add_memory(combined)
                    
                return content
                
            # If tool calls → execute them
            tool_call_dicts = [m.model_dump() for m in msg_obj.tool_calls] if hasattr(msg_obj.tool_calls[0], "model_dump") else msg_obj.tool_calls
            self.session_memory.add_message("assistant", content=msg_obj.content, tool_calls=tool_call_dicts)
            
            tool_responses = self._execute_tool_calls(msg_obj.tool_calls)
            for tr in tool_responses:
                self.session_memory.add_message(
                    role="tool", 
                    content=tr["content"], 
                    name=tr["name"], 
                    tool_call_id=tr["tool_call_id"]
                )
                
            loops += 1
        
        # Absolute fallback — ask LLM to summarize what happened
        try:
            messages = [system_msg] + self.session_memory.get_history() + [{
                "role": "user",
                "content": "Summarize what you did so far in one or two sentences for the user."
            }]
            fallback = self.router.chat_completion(messages=messages, tools=None)
            return fallback.choices[0].message.content or "I completed the task but could not prepare a summary."
        except Exception:
            return "I ran into an issue while processing your request. Please try again."

