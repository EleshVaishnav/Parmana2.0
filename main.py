import os
import yaml
from dotenv import load_dotenv

from Core.agent import ParmanaAgent
from Memory.vector_memory import initialize_vector_memory

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    # 1. Load Environment Variables (API Keys)
    load_dotenv()
    
    # 2. Load Configuration
    config = load_config()
    
    # 2.5 Dynamically Load Skills
    import importlib
    skills_dir = os.path.join(os.path.dirname(__file__), "Skills")
    if os.path.exists(skills_dir):
        for filename in os.listdir(skills_dir):
            if filename.endswith(".py") and filename not in ["__init__.py", "registry.py"]:
                module_name = filename[:-3]
                importlib.import_module(f"Skills.{module_name}")

    
    # 3. Initialize Long-Term Memory Component
    # This requires local persistent directory based on config
    vdb_path = config.get("memory", {}).get("vector_db_path", "./chroma_db")
    os.makedirs(vdb_path, exist_ok=True)
    initialize_vector_memory(vdb_path)
    
    # 4. Initialize Core Agent Instance
    agent = ParmanaAgent(config)
    
    # 5. Launch Active Channel
    active_channel = config.get("channels", {}).get("active", "cli")
    
    if active_channel == "telegram":
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not tg_token or tg_token == "your-telegram-bot-token":
            print("ERROR: TELEGRAM_BOT_TOKEN is missing or invalid in .env")
            return
            
        from Channels.telegram_bot import TelegramChannel
        tg = TelegramChannel(token=tg_token, agent=agent)
        tg.start()
        
    elif active_channel == "whatsapp":
        print("WhatsApp channel is not fully implemented yet.")
        
    else:
        # Fallback to CLI for direct testing
        print("Starting Parmana CLI Mode. Type 'exit' to quit.")
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.strip().lower() == "exit":
                    break
                
                print("Parmana: Thinking...")
                reply = agent.chat(user_input)
                print(f"Parmana: {reply}")
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
