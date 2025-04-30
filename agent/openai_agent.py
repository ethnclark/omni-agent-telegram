import os
import logging
import html
import asyncio
import json
import time
import re
from openai import OpenAI
from dotenv import load_dotenv
from agent.markdown_formatter import MarkdownFormatter
from tools.web_search import WebSearchTool
from tools.get_price_token import TokenPriceTool
from tools.create_token import CreateTokenTool
from tools.create_account import CreateAccountTool
from tools.get_account import GetAccountTool, GetAccountDetailTool

# Set up logging
logger = logging.getLogger(__name__)

class OpenAIAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Using gpt-4o-mini as specified
        self.request_timeout = 15  # Reduced timeout in seconds for faster response
        
        # Initialize tools
        self.web_search_tool = WebSearchTool()
        self.token_price_tool = TokenPriceTool()
        self.create_token_tool = CreateTokenTool()
        self.create_account_tool = CreateAccountTool()
        self.get_account_tool = GetAccountTool()
        self.get_account_detail_tool = GetAccountDetailTool()
        
        # Initialize conversation history
        self.conversation_history = []
    
    async def get_response(self, user_message, user_id=None):
        """
        Get a response from OpenAI's GPT model
        
        Args:
            user_message (str): The message from the user
            user_id (number, optional): The Telegram user id of the user
            
        Returns:
            tuple: (response_text, is_html_formatted)
                - response_text: The response from the AI
                - is_html_formatted: Boolean indicating if the response is HTML formatted
        """
        start_time = time.time()
        try:
            logger.info(f"Starting request at {start_time}")
            
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Limit conversation history to last 10 messages to avoid token limit issues
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # Reset history if user requests it
            if "reset" in user_message.lower() or "clear" in user_message.lower() or "hủy" in user_message.lower():
                self.conversation_history = [{"role": "user", "content": user_message}]
                logger.info("Conversation history reset")
            
            system_prompt = """You are Omni Agent, a specialized AI assistant focused on blockchain technology and cryptocurrency.

Your expertise includes:
- Blockchain fundamentals and technologies
- Cryptocurrencies and tokens
- DeFi (Decentralized Finance)
- NFTs and Web3
- Crypto markets and trends
- Latest blockchain news and developments

IMPORTANT RESPONSE RULES:
- ALWAYS respond in the same language the user used in their query
- If the user asks in English, respond in English
- If the user asks in Vietnamese, respond in Vietnamese
- If the user's query contains "yes" or "no", include "yes" or "no" in your response
- Match the user's tone and style of communication
- Keep your responses concise, informative, and friendly
- Use line breaks to make your responses more readable
- If you're not sure about something, be honest about it

IMPORTANT FORMATTING RULES:
- NEVER include disclaimers about financial advice in your responses
- NEVER include information about exchanges (like "Exchange: Binance")
- NEVER add notes like "You can find more information at..." at the end of responses
- DO NOT add any disclaimers or notes at the end of your responses

NETWORK SELECTION PROMPT FORMAT:
When asking users to select a network, use this exact format:
"Which network would you like to check? Please select one:

- Mainnet
- Testnet
- Devnet"

For Vietnamese:
"Bạn muốn kiểm tra trên mạng nào? Vui lòng chọn một mạng:

- Mainnet
- Testnet
- Devnet"


Important balance formatting rules:
1. Always use "-" for bullet points, never use "•"
2. Maintain proper indentation with 2 spaces
3. Keep decimal places consistent
4. Only show tokens that exist in the user's balance
5. Keep the structure consistent with proper markdown
6. Use "###" for section headers
7. Add a blank line after each section header
8. Display tokens in order of highest balance to lowest
9. Include zero balances only if specifically relevant to the user's query

You should use Markdown formatting to make your answers clear and well-structured:
- Use # Header and ## Subheader for section titles
- Use **bold** for important terms and concepts
- Use _italic_ for definitions and emphasis
- Use `code` for technical terms, commands, or symbols
- Use numbered lists (1., 2., etc.) for sequential steps
- Use bullet points (-) for lists of items
- Use [text](URL) for links to trusted sources

Make your responses well-structured with clear headings, bullet points, and formatting to improve readability.

You have access to these tools:
1. Web search tool - for general information
2. Token price tool - for getting current cryptocurrency prices
3. Create token tool - for creating new tokens on the Sui blockchain
4. Create account tool - for creating new wallet accounts on the Sui blockchain
5. Get account tool - for getting Sui wallet account information
6. Get account detail tool - for getting detailed information about a Sui wallet account

SPECIAL INSTRUCTIONS FOR TOKEN CREATION:

When a user wants to create a token, guide them through a conversational flow to collect all required information. Use your memory of the conversation to avoid asking for information they've already provided.

For token creation, you need to collect the following information and ask users to provide meaningful details for each field:

- **Token name (required)**: Ask users to provide a clear and meaningful token name. Inquire about the purpose of the token and what the name represents.

- **Token symbol (required)**: Request a concise abbreviation, typically 3-5 uppercase characters. This symbol will be used on exchanges and wallets.

- **Initial supply (required)**: Ask about the initial number of tokens to be created. Encourage users to carefully consider tokenomics and token distribution.

- **Wallet address (required)**: A Sui wallet address to receive the tokens. If the user doesn't have one, offer to create a new wallet.

- **Description (optional)**: Encourage users to provide a detailed description of the token, its utility, value, and the reason for creating it.

- **Image URL (optional)**: URL for a token logo image, preferably in PNG/JPG format with a transparent background.

Once you have all required information, use the create_token tool. If they need a wallet, use the create_account tool.

IMPORTANT: When you create a wallet, HIGHLIGHT the private key and warn the user to save it securely.

You should always adapt your conversation to the language the user is using (English or Vietnamese) and maintain a helpful, conversational tone throughout this process.

For questions about blockchain fundamentals, concepts, or general knowledge that isn't time-sensitive, you can answer directly.

IMPORTANT: Be concise and respond quickly.

CRITICAL SYSTEM INSTRUCTION:
- You ALWAYS have access to the user's Telegram user_id from the backend. NEVER ask the user for their user_id. When you need to fetch Sui account information or perform any user-specific action, ALWAYS use the available user_id automatically. Do not prompt or request the user to provide their user_id under any circumstances.
"""
            
            # Prepare full message history with system prompt
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            messages.extend(self.conversation_history)
            
            # Define the tools
            tools = [
                self.web_search_tool.get_function_schema(),
                self.token_price_tool.get_function_schema(),
                self.create_token_tool.get_function_schema(),
                self.create_account_tool.get_function_schema(),
                self.get_account_tool.get_function_schema(),
                self.get_account_detail_tool.get_function_schema()
            ]
            
            # Create a task with timeout for the OpenAI request
            async def make_openai_request():
                # Run the API call in a separate thread to avoid blocking
                return await asyncio.to_thread(
                    lambda: self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=tools,
                        temperature=0.7,
                        timeout=self.request_timeout,
                        max_tokens=800  # Reduced token count for faster responses
                    )
                )

            # Execute with timeout
            response = await asyncio.wait_for(
                make_openai_request(),
                timeout=self.request_timeout
            )
            
            assistant_message = response.choices[0].message
            
            # Save assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content if not assistant_message.tool_calls else None,
                "tool_calls": assistant_message.tool_calls
            })
            
            # Check if the model wants to use tools
            if assistant_message.tool_calls:
                logger.info("Model is using tools")
                
                # Extract the function call details
                tool_call = assistant_message.tool_calls[0]
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "search_web":
                    # Execute the web search
                    query = function_args.get("query")
                    count = function_args.get("count", 3)  # Reduced count for faster response
                    
                    logger.info(f"Executing web search for query: {query}")
                    search_result = self.web_search_tool.execute(query, count)
                    
                    # Add tool response to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(search_result) 
                    })
                    
                    # Call the model again with the search results
                    second_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages + [
                            {"role": "assistant", "content": None, "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {"name": function_name, "arguments": tool_call.function.arguments}
                                }
                            ]},
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(search_result)
                            }
                        ],
                        temperature=0.7,
                        timeout=self.request_timeout,
                        max_tokens=800  # Reduced token count for faster responses
                    )
                    
                    ai_response = second_response.choices[0].message.content
                    
                    # Save the final response to history
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": ai_response
                    })
                
                elif function_name == "get_token_price":
                    # Execute the token price tool
                    token = function_args.get("token")
                    
                    logger.info(f"Fetching price for token: {token}")
                    price_result = self.token_price_tool.execute(token)
                    
                    # Add tool response to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(price_result) 
                    })
                    
                    # Call the model again with the price results
                    second_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages + [
                            {"role": "assistant", "content": None, "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {"name": function_name, "arguments": tool_call.function.arguments}
                                }
                            ]},
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(price_result)
                            }
                        ],
                        temperature=0.7,
                        timeout=self.request_timeout,
                        max_tokens=800  # Reduced token count for faster responses
                    )
                    
                    ai_response = second_response.choices[0].message.content
                    
                    # Save the final response to history
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": ai_response
                    })
                
                elif function_name == "create_token":
                    # Extract token parameters from function call
                    name = function_args.get("name")
                    symbol = function_args.get("symbol")
                    description = function_args.get("description", "")
                    image_url = function_args.get("image_url", "")
                    init_supply = function_args.get("init_supply")
                    wallet_address = function_args.get("wallet_address", "")
                    network = function_args.get("network")
                    
                    # Execute token creation if all required parameters are present
                    if name and symbol and init_supply is not None and wallet_address and network:
                        logger.info(f"Creating token: {name} ({symbol}) with initial supply: {init_supply} for wallet: {wallet_address} on network: {network}")
                        token_result = self.create_token_tool.execute(
                            name=name,
                            symbol=symbol,
                            description=description,
                            image_url=image_url,
                            init_supply=init_supply,
                            wallet_address=wallet_address,
                            network=network
                        )
                    else:
                        # If required parameters are missing, let the model know
                        missing = []
                        if not name: missing.append("name")
                        if not symbol: missing.append("symbol")
                        if init_supply is None: missing.append("init_supply")
                        if not wallet_address: missing.append("wallet_address")
                        if not network: missing.append("network")
                        
                        token_result = {
                            "success": False,
                            "error": f"Missing required parameters: {', '.join(missing)}"
                        }
                    
                    # Add tool response to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(token_result) 
                    })
                    
                    # Call the model again with the token creation results
                    second_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages + [
                            {"role": "assistant", "content": None, "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {"name": function_name, "arguments": tool_call.function.arguments}
                                }
                            ]},
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(token_result)
                            }
                        ],
                        temperature=0.7,
                        timeout=self.request_timeout,
                        max_tokens=800
                    )
                    
                    ai_response = second_response.choices[0].message.content
                    
                    # Save the final response to history
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": ai_response
                    })
                
                elif function_name == "create_account":
                    # Extract account parameters from function call
                    scheme = function_args.get("scheme", "secp256k1")
                    network = function_args.get("network")
                    
                    # Validate network parameter
                    if not network:
                        account_result = {
                            "status": "error",
                            "error": "Network parameter is required. Please specify 'mainnet', 'testnet', or 'devnet'."
                        }
                    else:
                        # Pass user_id if available
                        logger.info(f"Creating Sui wallet account with scheme: {scheme}, network: {network}, user_id: {user_id}")
                        account_result = self.create_account_tool.execute(
                            scheme=scheme,
                            network=network,
                            user_id=user_id
                        )
                    
                    # Add tool response to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(account_result) 
                    })
                    
                    # Call the model again with the account creation results
                    second_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages + [
                            {"role": "assistant", "content": None, "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {"name": function_name, "arguments": tool_call.function.arguments}
                                }
                            ]},
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(account_result)
                            }
                        ],
                        temperature=0.7,
                        timeout=self.request_timeout,
                        max_tokens=800
                    )
                    
                    ai_response = second_response.choices[0].message.content
                    
                    # Save the final response to history
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": ai_response
                    })
                elif function_name == "get_account_by_user":
                    # Kiểm tra xem network đã được cung cấp chưa
                    network = function_args.get("network")
                    if not network:
                        # Nếu chưa có network, trả về yêu cầu người dùng chọn network
                        account_result = {
                            "status": "error",
                            "error": "Vui lòng chọn mạng lưới để kiểm tra (mainnet/testnet/devnet)."
                        }
                    else:
                        # Nếu đã có network, tiếp tục lấy thông tin tài khoản
                        privatekey = function_args.get("privatekey")
                        logger.info(f"Getting Sui account for user_id: {user_id}, network: {network}, privatekey: {'provided' if privatekey else 'not provided'}")
                        account_result = self.get_account_tool.execute(
                            user_id=user_id, 
                            privatekey=privatekey,
                            network=network
                        )

                    # Luôn trả về toàn bộ kết quả cho model
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(account_result)
                    })
                    # Call the model again with the full account get results
                    second_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages + [
                            {"role": "assistant", "content": None, "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {"name": function_name, "arguments": tool_call.function.arguments}
                                }
                            ]},
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(account_result)
                            }
                        ],
                        temperature=0.7,
                        timeout=self.request_timeout,
                        max_tokens=800
                    )
                    ai_response = second_response.choices[0].message.content
                    # Save the final response to history
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": ai_response
                    })
                elif function_name == "get_account_detail":
                    address = function_args.get("address")
                    network = function_args.get("network")
                    
                    if not network:
                        # Nếu chưa có network, yêu cầu người dùng chọn network
                        detail_result = {
                            "status": "error", 
                            "error": "Please select a network to check the balance:\n\n- Mainnet\n- Testnet\n- Devnet\n\nPlease choose one of the networks above!"
                        }
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(detail_result)
                        })
                        second_response = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages + [
                                {"role": "assistant", "content": None, "tool_calls": [
                                    {
                                        "id": tool_call.id,
                                        "type": "function",
                                        "function": {"name": function_name, "arguments": tool_call.function.arguments}
                                    }
                                ]},
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps(detail_result)
                                }
                            ],
                            temperature=0.7,
                            timeout=self.request_timeout,
                            max_tokens=800
                        )
                        ai_response = second_response.choices[0].message.content
                        self.conversation_history.append({
                            "role": "assistant", 
                            "content": ai_response
                        })
                        return ai_response, False

                    if not address:
                        # Nếu thiếu address, chỉ trả về lỗi yêu cầu cung cấp address
                        detail_result = {"status": "error", "error": "Please provide a Sui wallet address to get account details."}
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(detail_result)
                        })
                        second_response = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages + [
                                {"role": "assistant", "content": None, "tool_calls": [
                                    {
                                        "id": tool_call.id,
                                        "type": "function",
                                        "function": {"name": function_name, "arguments": tool_call.function.arguments}
                                    }
                                ]},
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps(detail_result)
                                }
                            ],
                            temperature=0.7,
                            timeout=self.request_timeout,
                            max_tokens=800
                        )
                        ai_response = second_response.choices[0].message.content
                        self.conversation_history.append({
                            "role": "assistant", 
                            "content": ai_response
                        })
                        return ai_response, False
                    
                    logger.info(f"Getting Sui account detail for address: {address}, network: {network}")
                    detail_result = self.get_account_detail_tool.execute(
                        address=address,
                        network=network
                    )
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(detail_result)
                    })
                    second_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages + [
                            {"role": "assistant", "content": None, "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {"name": function_name, "arguments": tool_call.function.arguments}
                                }
                            ]},
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(detail_result).replace("coin objects", "coin").replace("Coin Objects", "Coin")
                                .replace("  - Số lượng đối tượng: 2999630763\n", "")
                                .replace("• ", "- ")
                                .replace("  - ", "  • ")
                            }
                        ],
                        temperature=0.7,
                        timeout=self.request_timeout,
                        max_tokens=800
                    )
                    ai_response = second_response.choices[0].message.content
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": ai_response
                    })
                else:
                    # This shouldn't happen, but just in case
                    ai_response = assistant_message.content or "I couldn't process your request correctly."
            else:
                # Model answered directly
                ai_response = assistant_message.content
            
            end_time = time.time()
            logger.info(f"Received response from OpenAI in {end_time - start_time:.2f} seconds")
            
            # Convert markdown to HTML for better display in Telegram
            html_response, is_html = MarkdownFormatter.markdown_to_html(ai_response)
            
            return html_response, is_html
            
        except asyncio.TimeoutError:
            end_time = time.time()
            logger.error(f"OpenAI request timed out after {end_time - start_time:.2f} seconds")
            return "Sorry, the request took too long to process. Please try again or ask a simpler question.", False
            
        except Exception as e:
            end_time = time.time()
            logger.error(f"Error getting response from OpenAI in {end_time - start_time:.2f} seconds: {e}")
            return "Sorry, I encountered an error processing your request.\nPlease try again later or ask a different question.", False 