import os
import logging
import asyncio
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from agent.markdown_formatter import MarkdownFormatter
from tools import (
    search_web,
    get_token_price,
    create_token,
    create_account,
    get_account,
    get_account_detail,
    get_news,
    switch_account,
    create_nft
)


# Set up logging
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()  
class OpenAIAgent:
    def __init__(self):
        # Initialize OpenAI client with updated parameters
        self.model = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            timeout=15,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize tools
        self.tools = [
            search_web,
            get_token_price,
            create_token,
            create_account,
            get_account,
            get_account_detail,
            get_news,
            switch_account,
            create_nft
        ]
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a helpful assistant that uses tools to answer questions about cryptocurrency, blockchain, and NFTs."),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        self.agent = create_openai_tools_agent(self.model, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    async def get_response(self, user_message, user_id=None):
        """
        Get a response from OpenAI's GPT model using LangChain's tool calling
        
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
            
            # Limit conversation history to last 10 messages
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # Reset history if user requests it
            if "reset" in user_message.lower() or "clear" in user_message.lower() or "hủy" in user_message.lower():
                self.conversation_history = [{"role": "user", "content": user_message}]
                logger.info("Conversation history reset")
            
            # Create the prompt template with user_id context
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=f"You are a helpful assistant that uses tools to answer questions about cryptocurrency, blockchain, and NFTs. The current user's Telegram ID is {user_id}."),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessage(content="{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Recreate the agent with the updated prompt
            agent = create_openai_tools_agent(self.model, self.tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
            # Get response from agent with user_id in the input
            response = await agent_executor.ainvoke({
                "input": user_message,
                "chat_history": self.conversation_history,
                "user_id": user_id  # Pass user_id to the agent
            })
            
            ai_response = response["output"]
            
            # Save the final response to history
            self.conversation_history.append({
                "role": "assistant", 
                "content": ai_response
            })
            
            end_time = time.time()
            logger.info(f"Received response in {end_time - start_time:.2f} seconds")
            
            # Convert markdown to HTML for better display in Telegram
            html_response, is_html = MarkdownFormatter.markdown_to_html(ai_response)
            
            return html_response, is_html
            
        except asyncio.TimeoutError:
            end_time = time.time()
            logger.error(f"Request timed out after {end_time - start_time:.2f} seconds")
            return "Sorry, the request took too long to process. Please try again or ask a simpler question.", False
            
        except Exception as e:
            end_time = time.time()
            logger.error(f"Error processing request in {end_time - start_time:.2f} seconds: {e}")
            return "Sorry, I encountered an error processing your request.\nPlease try again later or ask a different question.", False 