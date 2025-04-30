import os
import logging
import re
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agent.openai_agent import OpenAIAgent

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
        
        # Register handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register command and message handlers"""
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Message handler for text messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        self.app.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued"""
        user = update.effective_user
        welcome_message = f"""
Hi {user.first_name}!

I'm Omni Agent, your blockchain and cryptocurrency assistant.

Can I help you with anything?
"""
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued"""
        help_text = """
Available commands:
/start - Start the bot
/help - Show this help message

I am Omni Agent, your blockchain and cryptocurrency assistant. You can ask me about:

• Blockchain technology and concepts
• Cryptocurrencies and tokens
• DeFi (Decentralized Finance)
• NFTs and Web3
• Crypto markets and news
• Latest blockchain developments

Just send me a message with your blockchain-related question!
"""
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
    
    def run(self):
        """Run the bot until the user presses Ctrl-C"""
        logger.info("Starting bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
    
    def run_async(self):
        """Run the bot asynchronously"""
        logger.info("Starting bot asynchronously...")
        return self.app.initialize() 