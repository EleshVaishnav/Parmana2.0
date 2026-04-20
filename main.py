import os
import yaml
import threading
from dotenv import load_dotenv

from Core.agent import DeepClawAgent
from Memory.vector_memory import initialize_vector_memory

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def start_telegram(agent, config):
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not tg_token or tg_token == "your-telegram-bot-token":
        print("❌ ERROR: TELEGRAM_BOT_TOKEN is missing or invalid in .env — Telegram skipped.")
        return
    print("✅ Starting Telegram channel...")
    from Channels.telegram_bot import TelegramChannel
    tg = TelegramChannel(token=tg_token, agent=agent)
    tg.start()

def start_whatsapp(agent, config):
    print("✅ Starting WhatsApp channel...")
    from Channels.whatsapp import WhatsAppChannel
    wa = WhatsAppChannel(agent=agent)
    wa.start()

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
    vdb_path = config.get("memory", {}).get("vector_db_path", "./chroma_db")
    os.makedirs(vdb_path, exist_ok=True)
    initialize_vector_memory(vdb_path)
    
    # 4. Initialize Core Agent Instance
    agent = DeepClawAgent(config)
    
    # 5. Launch Active Channel(s)
    active_channel = config.get("channels", {}).get("active", "cli")
    channels_cfg = config.get("channels", {})

    threads = []

    if active_channel == "both":
        # Run both Telegram and WhatsApp simultaneously
        if channels_cfg.get("telegram", {}).get("enabled", False):
            t = threading.Thread(target=start_telegram, args=(agent, config), daemon=True, name="TelegramThread")
            threads.append(t)
        if channels_cfg.get("whatsapp", {}).get("enabled", False):
            t = threading.Thread(target=start_whatsapp, args=(agent, config), daemon=True, name="WhatsAppThread")
            threads.append(t)

        if not threads:
            print("⚠️  No channels are enabled in config.yaml. Set enabled: true under telegram/whatsapp.")
            return

        for t in threads:
            t.start()

        print(f"🚀 Deep Claw running on {len(threads)} channel(s). Press Ctrl+C to stop.")
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Deep Claw...")

    elif active_channel == "telegram":
        start_telegram(agent, config)

    elif active_channel == "whatsapp":
        start_whatsapp(agent, config)

    else:
        # Fallback to CLI for direct testing
        print("Starting Deep Claw CLI Mode. Type 'exit' to quit.")
        
        # Set the proactive notification hook for CLI
        def cli_notify(user, msg):
            print(f"\n\n🔔 PROACTIVE NOTIFICATION for {user}: {msg}\nYou: ", end="", flush=True)
            
        agent.notification_hook = cli_notify

        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.strip().lower() == "exit":
                    break
                
                print("Deep Claw: Thinking...")
                reply = agent.chat(user_input, sender_id="cli_user")
                print(f"Deep Claw: {reply}")
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
