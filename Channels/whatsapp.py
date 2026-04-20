import asyncio
import json
import os
import shutil
import subprocess
import threading
import concurrent.futures
from typing import Optional

from Core.agent import DeepClawAgent

class WhatsAppChannel:
    def __init__(self, agent: DeepClawAgent, bridge_url: str = "ws://localhost:3001"):
        self.agent = agent
        self.bridge_url = bridge_url
        self._ws = None
        self._connected = False
        self._running = False
        self._bridge_process: Optional[subprocess.Popen] = None
        # Use a single thread to guarantee Playwright stability
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def _ensure_bridge_running(self):
        """Builds and starts the Node.js bridge if not already running."""
        bridge_dir = os.path.join(os.path.dirname(__file__), "whatsapp_bridge")
        
        # Check npm
        npm_path = shutil.which("npm")
        if not npm_path:
            # Use shell=True fallback if npm is not directly in path but works in shell
            npm_path = "npm.cmd" if os.name == "nt" else "npm"

        print("[WhatsApp] Setting up bridge dependencies (this may take a minute)...")
        # Ensure dependencies are installed
        try:
            subprocess.run([npm_path, "install"], cwd=bridge_dir, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"[WhatsApp Error] Failed to npm install: {e.stderr.decode('utf-8', errors='ignore')}")
            return False
        
        print("[WhatsApp] Starting Node.js Baileys Bridge...")
        # Start the script in the background
        node_path = shutil.which("node") or "node.exe"
        try:
            # We don't wait for this; it stays running in the background.
            self._bridge_process = subprocess.Popen(
                [node_path, "index.js"],
                cwd=bridge_dir,
                stdout=subprocess.PIPE, # We can redirect or leave it to inherit but we want to see the QR code
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                bufsize=1 # Line buffered
            )
            
            # Start a thread to read output so we see the QR code
            def stream_output(pipe, prefix=""):
                for line in iter(pipe.readline, ''):
                    print(f"{prefix}{line.strip()}")
            
            threading.Thread(target=stream_output, args=(self._bridge_process.stdout, "[Node Bridge] "), daemon=True).start()
            threading.Thread(target=stream_output, args=(self._bridge_process.stderr, "[Node Bridge Error] "), daemon=True).start()
            
            return True
        except Exception as e:
            print(f"[WhatsApp] Failed to start node process: {e}")
            return False

    async def _handle_message(self, data: dict):
        """Process messages received from the bridge."""
        sender = data.get("sender")
        content = data.get("content")
        
        if not sender or not content:
            return
            
        allow_from = self.agent.config.get("channels", {}).get("whatsapp", {}).get("allow_from", [])
        if allow_from and "*" not in allow_from:
            # Check if any allowed identifier is a substring of the sender JID
            if not any(str(allowed) in sender for allowed in allow_from):
                print(f"[WhatsApp Security] Blocked unauthorized message from {sender}")
                return
            
        print(f"[WhatsApp] processing message from {sender}: {content}")
        
        try:
            # We run agent chat in executor because it might be synchronous and block the asyncio loop
            loop = asyncio.get_running_loop()
            reply = await loop.run_in_executor(self.executor, lambda: self.agent.chat(content, sender_id=sender))
            
            if reply:
                payload = {
                    "type": "send",
                    "to": sender,
                    "text": reply
                }
                await self._ws.send(json.dumps(payload))
        except Exception as e:
            print(f"[WhatsApp Process] Error generating reply: {e}")

    def _proactive_send(self, target_id: str, message: str):
        """Called by background daemon threads to inject messages."""
        if self._ws and self._connected and hasattr(self, "_loop"):
            payload = {
                "type": "send",
                "to": target_id,
                "text": message
            }
            try:
                asyncio.run_coroutine_threadsafe(self._ws.send(json.dumps(payload)), self._loop)
            except Exception as e:
                print(f"[WhatsApp] Error dispatching proactive message: {e}")

    async def _async_start(self):
        try:
            import websockets
        except ImportError:
            print("[WhatsApp] The 'websockets' library is required. Install via 'pip install websockets'")
            return
            
        self._loop = asyncio.get_running_loop()
        self.agent.notification_hook = self._proactive_send
        
        self._running = True
        print(f"[WhatsApp] Connecting to bridge at {self.bridge_url} ...")
        
        while self._running:
            try:
                async with websockets.connect(self.bridge_url) as ws:
                    self._ws = ws
                    self._connected = True
                    print("[WhatsApp] Connected to Bridge Server via WebSockets")
                    
                    # Notify auth
                    await ws.send(json.dumps({"type": "auth", "token": ""}))
                    
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            if data.get("type") == "message":
                                asyncio.create_task(self._handle_message(data))
                        except Exception as e:
                            print(f"[WhatsApp] Error parsing ws message: {e}")
                            
            except (asyncio.CancelledError, KeyboardInterrupt):
                break
            except Exception as e:
                self._connected = False
                self._ws = None
                print(f"[WhatsApp] Connection dropped! Reconnecting in 3s... ({e})")
                await asyncio.sleep(3)

    def start(self):
        """Entry point for main.py."""
        success = self._ensure_bridge_running()
        if not success:
            return
            
        # Run local websocket listener loop
        try:
            asyncio.run(self._async_start())
        except KeyboardInterrupt:
            print("[WhatsApp] Stopping...")
        finally:
            self._running = False
            if self._bridge_process:
                self._bridge_process.terminate()
                self._bridge_process.wait()
