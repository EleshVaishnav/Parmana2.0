import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from Core.agent import ParmanaAgent

class TelegramChannel:
    def __init__(self, token: str, agent: ParmanaAgent):
        self.token = token
        self.agent = agent

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
            
        allowed_user = self.agent.config.get("channels", {}).get("telegram", {}).get("allowed_username", "*")
        username = update.message.from_user.username
        
        if allowed_user != "*" and username != allowed_user:
            from Core.logger import logger
            logger.warning(f"[Security] Blocked unauthorized Telegram message from @{username}")
            return

            
        user_msg = update.message.text
        chat_id = update.message.chat_id
        
        # Send typing action
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        try:
            # We run the agent inference in a thread so we don't block the async event loop
            # if the agent's LLM calls are synchronous.
            loop = asyncio.get_running_loop()
            reply = await loop.run_in_executor(None, self.agent.chat, user_msg)
            
            await context.bot.send_message(chat_id=chat_id, text=reply)
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"System Error: {str(e)}")

    def start(self):
        print("[Telegram] Starting bot...")
        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self._handle_message))
        
        # Start polling
        app.run_polling()
