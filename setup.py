import os
import sys
import subprocess

# --- Auto-Install Setup Dependencies ---
def check_dependencies():
    missing = False
    try:
        import rich
        import yaml
        import requests
    except ImportError:
        missing = True

    if missing:
        print("\nInstalling setup wizard dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "pyyaml", "requests"], stdout=subprocess.DEVNULL)
        os.execv(sys.executable, ['python', __file__] + sys.argv[1:])

check_dependencies()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint
import yaml
import requests

console = Console()

# --- ASCII ART ---
ASCII_LOGO = r"""
 [cyan]
  ____   _    ____  __  __    _    _   _    _      ____     ___  
 |  _ \ / \  |  _ \|  \/  |  / \  | \ | |  / \    |___ \   / _ \ 
 | |_) / _ \ | |_) | |\/| | / _ \ |  \| | / _ \     __) | | | | |
 |  __/ ___ \|  _ <| |  | |/ ___ \| |\  |/ ___ \   / __/ _| |_| |
 |_| /_/   \_\_| \_\_|  |_/_/   \_\_| \_/_/   \_\ |_____(_)\___/ 
 
 Agentic Framework Setup Wizard
 [/cyan]
"""

# --- PROVIDERS ---
PROVIDERS = [
    {"name": "OpenAI", "env_var": "OPENAI_API_KEY"},
    {"name": "Anthropic", "env_var": "ANTHROPIC_API_KEY"},
    {"name": "Google Gemini", "env_var": "GEMINI_API_KEY"},
    {"name": "Groq", "env_var": "GROQ_API_KEY"},
    {"name": "Mistral", "env_var": "MISTRAL_API_KEY"},
    {"name": "Amazon Bedrock", "env_var": "AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY"},
    {"name": "OpenRouter", "env_var": "OPENROUTER_API_KEY"},
    {"name": "DeepSeek", "env_var": "DEEPSEEK_API_KEY"},
    {"name": "xAI (Grok)", "env_var": "XAI_API_KEY"},
    {"name": "Fireworks", "env_var": "FIREWORKS_API_KEY"},
    {"name": "Alibaba DashScope (Qwen)", "env_var": "DASHSCOPE_API_KEY"},
    {"name": "BytePlus", "env_var": "BYTEPLUS_API_KEY"},
    {"name": "Moonshot (Kimi)", "env_var": "MOONSHOT_API_KEY"},
    {"name": "StepFun", "env_var": "STEPFUN_API_KEY"},
    {"name": "Chutes", "env_var": "CHUTES_API_KEY"},
    {"name": "Venice AI", "env_var": "VENICE_API_KEY"},
    {"name": "Z.AI", "env_var": "ZAI_API_KEY"},
    {"name": "OpenCode", "env_var": "OPENCODE_API_KEY"},
    {"name": "Vercel AI Gateway", "env_var": "VERCEL_AI_GATEWAY_TOKEN"},
    {"name": "Cloudflare AI Gateway", "env_var": "CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_GATEWAY_ID"},
    {"name": "MiniMax", "env_var": "MINIMAX_API_KEY"},
    {"name": "Zhipu (GLM)", "env_var": "ZHIPUAI_API_KEY"},
    {"name": "Qianfan (Baidu)", "env_var": "QIANFAN_ACCESS_KEY"},
    {"name": "Ollama", "env_var": "NONE"},
    {"name": "fal", "env_var": "FAL_KEY"},
    {"name": "Runway", "env_var": "RUNWAY_API_KEY"},
    {"name": "ComfyUI", "env_var": "NONE"},
]

# --- SKILLS ---
SKILL_CATEGORIES = {
    "Task planning / reasoning": ["task_planning"],
    "Tool calling / function execution": ["tool_calling"],
    "Error handling & retry logic": ["error_handling"],
    "File read/write": ["file_system"],
    "Terminal / command execution": ["system_control"],
    "Environment and config handling": ["env_config"],
    "Web search": ["web_search"],
    "Content fetching / scraping": ["content_fetching"],
    "Data parsing (JSON, APIs)": ["data_parsing"],
    "Workflow chaining": ["workflow_chaining"],
    "Scheduling": ["scheduling"],
    "Event triggers": ["event_triggers"],
    "API calling (REST/webhooks)": ["api_calling"],
    "Database access": ["database_access"],
    "External services (email / Telegram / Slack)": ["external_services"],
    "Message sending": ["message_sending"],
    "Notifications": ["notifications"],
    "Code execution": ["code_execution"],
    "Debugging": ["debugging"],
    "Version control interaction": ["version_control"],
    "API key management": ["api_key_management"],
    "Permission control": ["permission_control"]
}

def main():
    console.print(ASCII_LOGO)
    
    # 1. Install Project Dependencies
    console.print("[yellow]Installing project dependencies from requirements.txt...[/yellow]")
    if os.path.exists("requirements.txt"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        console.print("[green]Dependencies installed successfully.[/green]\n")
    else:
        console.print("[red]requirements.txt not found. Skipping...[/red]\n")

    # 2. Provider Selection
    console.print(Panel("[bold cyan]Step 1: Select LLM Provider[/bold cyan]"))
    for idx, provider in enumerate(PROVIDERS):
        console.print(f"[green]{idx + 1}[/green]. {provider['name']}")
    
    provider_idx = -1
    while not (0 <= provider_idx < len(PROVIDERS)):
        try:
            user_input = Prompt.ask("\nSelect your provider by number")
            provider_idx = int(user_input) - 1
        except ValueError:
            pass

    selected_provider = PROVIDERS[provider_idx]
    env_vars_needed = selected_provider["env_var"]
    
    env_updates = {}
    if env_vars_needed != "NONE":
        keys = env_vars_needed.split(" + ")
        for key in keys:
            val = Prompt.ask(f"Enter your API Key for [yellow]{selected_provider['name']}[/yellow] ([cyan]{key}[/cyan])")
            if not val.strip():
                console.print(f"[red]No API key found for {key}. Proceeding with empty key...[/red]")
                env_updates[key] = ""
            else:
                env_updates[key] = val.strip()

    # Determine default provider string for Litellm config
    provider_code = selected_provider["name"].lower().split()[0]
    
    # 3. Skills Selection
    console.print(Panel("[bold cyan]Step 2: Select Skills[/bold cyan]"))
    skill_names = list(SKILL_CATEGORIES.keys())
    for idx, s in enumerate(skill_names):
        console.print(f"[green]{idx + 1}[/green]. {s}")
    
    selected_skill_indices_str = Prompt.ask("\nEnter the numbers of the skills you want to enable, separated by commas (e.g. 4,5,7)")
    selected_skills = []
    if selected_skill_indices_str.strip():
        for i_str in selected_skill_indices_str.split(","):
            try:
                i = int(i_str.strip()) - 1
                if 0 <= i < len(skill_names):
                    category_name = skill_names[i]
                    selected_skills.extend(SKILL_CATEGORIES[category_name])
            except ValueError:
                pass
                
    console.print(f"\n[cyan]Downloading selected skills from GitHub...[/cyan]")
    os.makedirs("Skills", exist_ok=True)
    for skill_file in selected_skills:
        url = f"https://raw.githubusercontent.com/EleshVaishnav/Parmana2.0/main/Skills/{skill_file}.py"
        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(f"Skills/{skill_file}.py", "w", encoding="utf-8") as f:
                    f.write(r.text)
                console.print(f"[green]✔ Installed {skill_file}.py[/green]")
            else:
                console.print(f"[yellow]⚠ Skill '{skill_file}' does not exist on the remote repository yet. Skipped.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error downloading {skill_file}: {e}[/red]")

    # 4. Channel Configuration
    console.print(Panel("[bold cyan]Step 3: Interface Channel Setup[/bold cyan]"))
    console.print("Currently supported: [yellow]Telegram[/yellow]")
    
    use_telegram = Confirm.ask("Do you want to enable the Telegram bot channel?")
    telegram_token = ""
    telegram_allow = ""
    if use_telegram:
        telegram_token = Prompt.ask("Enter your Telegram Bot Token")
        if not telegram_token.strip():
             console.print(f"[red]No API key found for TELEGRAM_BOT_TOKEN.[/red]")
        env_updates["TELEGRAM_BOT_TOKEN"] = telegram_token.strip()
        
        telegram_allow = Prompt.ask("Allow requests from a specific username? (Leave blank to allow all)")
        if telegram_allow.startswith("@"):
            telegram_allow = telegram_allow[1:]

    # 5. Writing Configs
    console.print("\n[cyan]Saving configurations...[/cyan]")
    
    # Write .env
    env_content = ""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()
            
    # Modify env_content with env_updates
    env_lines = env_content.splitlines()
    for k, v in env_updates.items():
        if v == "": continue
        
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith(f"{k}="):
                env_lines[i] = f'{k}="{v}"'
                found = True
                break
        if not found:
            env_lines.append(f'{k}="{v}"')
            
    with open(".env", "w") as f:
        f.write("\n".join(env_lines))
        
    # Write config.yaml
    config_dict = {
        "llm": {
            "default_provider": provider_code,
            "model_name": ""
        },
        "memory": {
            "short_term_max_messages": 20,
            "vector_db_path": "./chroma_db",
            "chunk_size": 500
        },
        "channels": {
            "active": "telegram" if use_telegram else "cli",
            "telegram": {
                "enabled": use_telegram,
                "allowed_username": telegram_allow.strip() if telegram_allow.strip() else "*"
            },
            "whatsapp": {"enabled": False}
        },
        "tools": { skill: True for skill in selected_skills }
    }
    
    with open("config.yaml", "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False)
        
    console.print("[bold green]\n✓ Setup Complete! You can now run `python main.py`[/bold green]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Setup cancelled.[/red]")
        sys.exit(1)
