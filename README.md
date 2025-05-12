# Omni Agent Telegram Bot

A Telegram bot that provides information and assistance related to blockchain technology and cryptocurrency using OpenAI's GPT models.

## Features

- 🤖 AI-Powered Responses: Intelligent responses using OpenAI's GPT-4 model
- 🔗 Blockchain Expertise: Specialized in blockchain technology and cryptocurrency
- 🛠️ Comprehensive Tools: Access to various blockchain and crypto tools
- 📊 Market Information: Real-time crypto market data and price tracking
- 💰 Token Management: Create and manage your own tokens
- 👤 Account Management: Full account control and management
- 🎨 NFT Creation: Create and manage your NFTs
- 📰 News Updates: Stay updated with latest blockchain news
- 🔍 Web Search: Real-time information search capabilities

## Available Tools

The bot comes equipped with the following tools:

- **Web Search**: Search the web for real-time information
- **Token Price**: Get current prices of cryptocurrencies
- **Token Management**: Create and manage tokens
- **Account Management**:
  - Create new accounts
  - Get account information
  - Get detailed account data
  - Switch between accounts
- **NFT Creation**: Create and manage NFTs
- **News Updates**: Get the latest blockchain and crypto news

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
- `tools/` - Contains various tools for blockchain and crypto operations

## Requirements

- Python 3.8+
- python-telegram-bot
- python-dotenv
- openai
- langchain
- langchain-openai 