import logging
import os
import sys
import subprocess
from bot.telegram_bot import TelegramBot

def is_bot_running():
    """Check if another instance of the bot is already running"""
    try:
        output = subprocess.check_output(['pgrep', '-f', 'python.*main.py'])
        pids = output.decode().strip().split('\n')
        # If there's more than one process (including the current one)
        if len(pids) > 1 or (len(pids) == 1 and int(pids[0]) != os.getpid()):
            return True
        return False
    except subprocess.CalledProcessError:
        # No processes found
        return False

def main():
    # Check for existing instances
    if is_bot_running():
        print("Bot is already running. Exiting to prevent conflicts.")
        sys.exit(1)

    # Set up logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Initialize and start the Telegram bot
    try:
        bot = TelegramBot()
        print("Bot initialized successfully! Starting...")
        bot.run()
    except Exception as e:
        logging.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    main()
