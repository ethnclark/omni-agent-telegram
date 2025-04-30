# Omni Agent Telegram Bot

A Telegram bot that provides information and assistance related to blockchain technology and cryptocurrency using OpenAI's GPT models.

## Features

- Responds to user messages with AI-powered responses
- Specialized in blockchain technology and cryptocurrency
- Uses OpenAI's gpt-4o-mini model
- Provides information on:
  - Blockchain fundamentals and technologies
  - Cryptocurrencies and tokens
  - DeFi (Decentralized Finance)
  - NFTs and Web3
  - Crypto markets and trends
  - Latest blockchain news and developments

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up your environment variables in a `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```
4. Run the bot:
   ```
   python main.py
   ```

## Development Mode

For development, you can use the auto-restart functionality that watches for file changes:

```
python run_dev.py
```

Or use the convenient bash script, which also handles the virtual environment setup:

```
./dev.sh
```

This will:
- Start the bot
- Monitor all Python files in the project directories
- Automatically restart the bot when any source file changes
- Provide logging information about restarts

## Commands

- `/start` - Start the bot
- `/help` - Show help message with information about what the bot can do

## Project Structure

- `main.py` - Entry point for the application
- `bot/` - Contains the Telegram bot implementation
- `agent/` - Contains the OpenAI agent implementation

## Requirements

- Python 3.8+
- python-telegram-bot
- python-dotenv
- openai 