<div align="center">

# ⚙️ Deep Claw 2.0
**The Ultimate Modular Agentic Framework**

A highly flexible, extensible, and powerful conversational agent framework built to flawlessly fuse Multi-Provider LLMs, Persistent Memory, Terminal Access, and multi-channel interfaces into one autonomous powerhouse.

---

</div>

## ✨ Key Features
- 🧠 **Dynamic Multi-Provider Setup**: Out-of-the-box routing support for **27** different LLM providers (from OpenAI & Groq to Alibaba and Ollama) letting you hot-swap brains effortlessly.
- 🗃️ **Dual Memory Architecture**:
  - **Short-Term Session Memory**: Keeps context laser-focused in your computer's RAM during active loops.
  - **Long-Term Vector Memory**: A locally persistent `ChromaDB` (SQLite) module that permanently stores user preferences and framework knowledge between reboots.
- 🔧 **Expansive Modular Skill Engine**: An extensible `@registry.register` system that gives your LLM access to execute explicit Python functions.
- 👁️ **Multi-modal Vision Handlers**: Native image handling for multimodal cognitive processing.
- 📡 **Multi-Channel Deployments**: Natively built for Telegram integration with a secure whitelisting system, with placeholders for WhatsApp and a dedicated CLI testing mode.
- 🛡️ **Intelligent Background Logging**: Uses a resilient, rotating file handler system dumping outputs directly into `logs/deep claw.log` for debugging unmonitored production cycles.

## 🚀 Installation & Setup

We have stripped away complex setup environments and replaced them with a stunning **Interactive Setup Wizard**. It features beautiful ASCII art, automated dependency installation, seamless LLM Provider configuration, and automatic GitHub skill fetching!

### 🪟 Windows (Powershell)
Run this one-liner straight in your PowerShell:
```powershell
iwr -useb https://raw.githubusercontent.com/EleshVaishnav/DeepClaw2.0/main/install.ps1 | iex
```
*(Alternatively, you can manually clone the repo and drag-and-drop `install.ps1` into your terminal).*

### 🍎 Linux / macOS
```bash
curl -sSL https://raw.githubusercontent.com/EleshVaishnav/DeepClaw2.0/main/install.sh | bash
```
*(Alternatively, clone the repo and run `bash install.sh`).*

---

## 🏃 Running the Bot
Because the setup wizard securely contains the framework in a python virtual environment (`.venv`), you must activate it before launching `main.py`!

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```
**Linux / Mac:**
```bash
source .venv/bin/activate
python main.py
```

## 🧹 Uninstallation & Cleanup
If your python environment ever breaks or you simply want to reset the cache, run:
- **Windows**: `.\uninstall.ps1`
- **Linux/Mac**: `bash uninstall.sh`

> **Note:** The uninstaller is designed to be safe! It will wipe `.venv/` and cache files, but it will **never delete** your actual API keys (`.env`) or the bot's permanent memory (`chroma_db/`).

---

## 🛠️ The Skills Architecture
The heart of Deep Claw 2.0 is its `@registry` system, allowing the agent to break out of the text window and affect the real world.

### 📦 Pre-Installed Core Skills
These ship naturally with the framework:
- `calculator.py`: Safely solves complex math using Python's `ast` tree instead of relying on unreliable LLM hallucinated arithmetic.
- `web_search.py`: Live-access internet fetching to retrieve real-world and current event data.
- `file_system.py`: Safely create, modify, and read files directly from the host system.
- `system_control.py`: Gives the agent the absolute authority to run raw CLI commands (like `pip install`, `mkdir`, etc.) on the host machine.

### ☁️ Optional/Downloadable Skills
During the interactive `setup.py` phase, you can strictly select additional advanced skills for the bot. The wizard will automatically `GET` them from the remote GitHub repository and install them! Supported endpoints include:
*   **Web & Data**: Content Fetching, Data Parsing.
*   **Automation**: Workflow Chaining, Scheduling, Event Triggers.
*   **Integrations & Dev Tools**: Database Access, Code Execution, Debugging, API Key Management.
*   *...and many more.*

---

## 📁 Project Structure

```
DeepClaw2.0/
├── Channels/               # Handlers for sending/receiving messages (Telegram, WhatsApp)
├── Core/                   # The Brain: LLM orchestrator, prompts, and loggers
├── LLM_Gateway/            # LiteLLM routing architecture for 27+ providers
├── Memory/                 # Dual memory system (Session & ChromaDB Vector storage)
├── Skills/                 # Extensible Python tools that the LLM can execute
├── Vision/                 # Handling logic for image context injection
├── setup.py                # The Interactive Setup UI Wizard
├── main.py                 # Core initialization script
├── config.yaml             # Non-secret configurations (Models, Channel toggles)
├── .env.example            # Secure local placeholder template for API Keys
└── install.ps1 / .sh       # Automated Bootstrapping Initializers
```
