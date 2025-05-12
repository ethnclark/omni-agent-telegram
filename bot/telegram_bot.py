import os
import logging
import re
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from agent.openai_agent import OpenAIAgent
from tools.get_news import get_news

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Create the application instance
        self.app = Application.builder().token(self.token).build()
        
        # Initialize OpenAI agent
        self.agent = OpenAIAgent()
        
        # Set up bot commands
        self._setup_commands()
        
        # Register handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register command and message handlers"""
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Message handler for text messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handler for inline buttons
        self.app.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Error handler
        self.app.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued"""
        user = update.effective_user
        welcome_message = f"""
👋 Hello {user.first_name}!

I'm Omni Agent – your AI crypto assistant.

🔹 Quick Actions:
• 💼 Check wallet balance
• 🚀 Create/Send tokens
• 📰 Get SUI news
• 🔍 Search crypto info

Try these commands:
- "get news sui"
- "check my wallet"
- "create token"
- "send tokens"

Need help? Type /help for more info! 🤖
"""
        keyboard = [
            [InlineKeyboardButton("📰 News", callback_data="news")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued"""
        help_text = (
            "🤖 Omni Agent - Your AI Crypto Assistant\n\n"
            "🔹 Core Features:\n"
            "- 💼 Wallet Management\n"
            "  • Create new Sui wallets\n"
            "  • Check wallet balances\n"
            "  • View detailed account info\n\n"
            "- 🪙 Token Operations\n"
            "  • Create custom tokens\n"
            "  • Check token prices\n"
            "  • Send tokens on Sui network\n\n"
            "- 📰 News & Research\n"
            "  • Latest SUI blockchain news\n"
            "  • Web search for crypto info\n\n"
            "🔸 Available Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n\n"
            "💡 Just ask me anything about crypto or blockchain!"
        )
        await update.message.reply_text(help_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages using OpenAI"""
        message_text = update.message.text
        user = update.effective_user
        user_id = user.id if user.id else None
        logger.info(f"Received message from {user.first_name} ({user_id}): {message_text}")
        
        # Show typing indicator immediately
        await update.effective_chat.send_chat_action(action="typing")
        
        # Immediately send a processing message
        processing_message = await update.message.reply_text("⏳ Processing...")
        
        # Process the OpenAI response in a separate task to avoid blocking
        async def process_response():
            try:
                # Get response from OpenAI with HTML formatting
                response, is_html = await self.agent.get_response(message_text, user_id=user_id)
                
                # Delete the processing message
                try:
                    await processing_message.delete()
                except Exception as e:
                    logger.warning(f"Failed to delete processing message: {e}")
                
                # Send the actual response with HTML formatting if available
                if is_html:
                    await update.message.reply_text(
                        response,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                else:
                    # Fallback to plain text if HTML formatting fails
                    await update.message.reply_text(response)
                
            except Exception as e:
                # Delete the processing message in case of error
                try:
                    await processing_message.delete()
                except Exception:
                    pass
                    
                logger.error(f"Failed to process or send message: {e}")
                await update.message.reply_text("Sorry, I encountered an error processing your request. Please try again.")
        
        # Start processing without waiting
        asyncio.create_task(process_response())
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
    
    async def _setup_commands(self):
        """Set up the bot commands that will be shown in the Telegram client."""
        commands = [
            BotCommand("start", "Start the bot and see what I can do"),
            BotCommand("help", "Show help information and available commands")
        ]
        await self.app.bot.set_my_commands(commands)
    
    def run(self):
        """Run the bot until the user presses Ctrl-C"""
        logger.info("Starting bot...")
        # Set up commands before starting polling
        asyncio.get_event_loop().run_until_complete(self._setup_commands())
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
    
    def run_async(self):
        """Run the bot asynchronously"""
        logger.info("Starting bot asynchronously...")
        # Set up commands before initializing
        asyncio.get_event_loop().run_until_complete(self._setup_commands())
        return self.app.initialize()

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboard buttons"""
        query = update.callback_query
        await query.answer()  # Answer the callback query to remove loading state
        
        if query.data == "news":
            # Show processing message
            processing_msg = await query.message.reply_text("⏳ Fetching latest SUI news...")
            
            try:
                # Get news using get_news function
                news_result = get_news()
                if isinstance(news_result, str):
                    news_result = eval(news_result)  # Convert string to dict
                
                if news_result.get("data"):
                    # Format news for OpenAI processing
                    news_text = "Here are the latest SUI news articles:\n\n"
                    for idx, article in enumerate(news_result["data"][:5], 1):  # Limit to 5 items
                        news_text += f"📰 {article['title']}\n"
                        news_text += f"🔗 {article['url']}\n\n"
                    
                    # Try to get summary from OpenAI with retry logic
                    max_retries = 3
                    retry_delay = 5  # seconds
                    
                    for attempt in range(max_retries):
                        try:
                            # Get response from OpenAI
                            response, is_html = await self.agent.get_response(
                                f"Please summarize these SUI news articles in a concise way:\n\n{news_text}"
                            )
                            
                            # Delete processing message
                            await processing_msg.delete()
                            
                            # Send the response
                            await query.message.reply_text(
                                response,
                                parse_mode="HTML" if is_html else None,
                                disable_web_page_preview=True
                            )
                            break
                            
                        except Exception as e:
                            if attempt == max_retries - 1:
                                logger.error(f"Failed to get news summary after {max_retries} attempts: {e}")
                                await processing_msg.delete()
                                await query.message.reply_text(
                                    "Sorry, I couldn't summarize the news at this time. Here are the raw articles:\n\n" + news_text
                                )
                            else:
                                await asyncio.sleep(retry_delay)
                else:
                    await processing_msg.delete()
                    await query.message.reply_text("Sorry, I couldn't fetch the latest news at this time.")
                    
            except Exception as e:
                logger.error(f"Error handling news callback: {e}")
                await processing_msg.delete()
                await query.message.reply_text("Sorry, I encountered an error while fetching the news.") 