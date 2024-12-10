import os
from enum import Enum
import asyncio
import streamlit as st
from typing import Dict, Type, Optional

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.messages import UserPrompt, ModelTextResponse

# Change imports to use absolute paths
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.config import settings
from src.agents.base_agent import BaseAgent
from src.agents.web_search_agent import WebSearchAgent
from src.utils.ollama_utils import get_ollama_models, create_ollama_client

class AgentType(Enum):
    WEB_SEARCH = "Web Search"

class AgentManager:
    def __init__(self):
        self.agents: Dict[AgentType, Type[BaseAgent]] = {
            AgentType.WEB_SEARCH: WebSearchAgent,
        }
        self.current_agent: Optional[BaseAgent] = None
        
    def initialize_agent(self, agent_type: AgentType, model: OpenAIModel) -> BaseAgent:
        """Initialize a specific agent with the given model."""
        agent_class = self.agents[agent_type]
        return agent_class(model)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_agent_type" not in st.session_state:
        st.session_state.current_agent_type = AgentType.WEB_SEARCH

def render_sidebar():
    """Render the sidebar with configuration options."""
    st.sidebar.header("Configuration")
    
    # Brave API Key input
    brave_api_key = st.sidebar.text_input(
        "Brave API Key", 
        type="password", 
        value=settings.BRAVE_API_KEY
    )
    
    # Model selection
    ollama_models = get_ollama_models()
    if not ollama_models:
        st.sidebar.warning("No Ollama models found. Please pull a model using 'ollama pull <model-name>'")
        selected_model = None
    else:
        selected_model = st.sidebar.selectbox(
            "Select Ollama Model", 
            options=ollama_models
        )
    
    # Agent selection
    selected_agent = st.sidebar.selectbox(
        "Select Agent",
        options=list(AgentType),
        format_func=lambda x: x.value
    )
    
    return brave_api_key, selected_model, selected_agent

def display_chat_history():
    """Display the chat history."""
    for message in st.session_state.messages:
        role = message.role
        with st.chat_message("human" if role == "user" else "ai"):
            st.markdown(message.content)

async def process_message(agent: BaseAgent, message: str):
    """Process a message using the selected agent."""
    try:
        return await agent.process_query(message)
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
        return f"Error: {str(e)}"

def main():
    st.title("🤖 Multi-Agent AI Assistant")
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get configurations
    brave_api_key, selected_model, selected_agent = render_sidebar()
    
    # Check if we can proceed
    if not selected_model:
        return
    
    # Initialize agent manager
    agent_manager = AgentManager()
    
    # Create Ollama client and model
    ollama_client = create_ollama_client(selected_model)
    model = OpenAIModel(selected_model, openai_client=ollama_client)
    
    # Initialize the selected agent
    current_agent = agent_manager.initialize_agent(selected_agent, model)
    
    # Display existing chat history
    display_chat_history()
    
    # Handle user input
    if prompt := st.chat_input(f"What would you like to ask the {selected_agent.value} agent?"):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append(UserPrompt(content=prompt))
        
        # Process message with selected agent
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            with st.spinner(f'Processing with {selected_agent.value} agent using {selected_model}...'):
                response = asyncio.run(process_message(current_agent, prompt))
                
            message_placeholder.markdown(response)
            st.session_state.messages.append(ModelTextResponse(content=response))

if __name__ == "__main__":
    main()