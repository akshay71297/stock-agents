import os
from enum import Enum
import asyncio
import streamlit as st
from typing import Dict, Type, Optional

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.messages import UserPrompt, ModelTextResponse

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.agents.base_agent import BaseAgent
from src.agents.web_search_agent import WebSearchAgent
from src.utils.ollama_utils import get_ollama_models, create_ollama_client
from src.ui.streamlit_app import EnhancedUI

class AgentType(Enum):
    WEB_SEARCH = "Web Search"

class AgentManager:
    def __init__(self):
        self.agents: Dict[AgentType, Type[BaseAgent]] = {
            AgentType.WEB_SEARCH: WebSearchAgent,
        }
        self.current_agent: Optional[BaseAgent] = None
        
    def initialize_agent(self, agent_type: AgentType, model: OpenAIModel) -> BaseAgent:
        agent_class = self.agents[agent_type]
        return agent_class(model)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_agent_type" not in st.session_state:
        st.session_state.current_agent_type = AgentType.WEB_SEARCH

def render_sidebar():
    st.sidebar.header("Configuration")
    
    brave_api_key = st.sidebar.text_input(
        "Brave API Key", 
        type="password", 
        value=settings.BRAVE_API_KEY
    )
    
    ollama_models = get_ollama_models()
    if not ollama_models:
        st.sidebar.warning("No Ollama models found. Please pull a model using 'ollama pull <model-name>'")
        selected_model = None
    else:
        selected_model = st.sidebar.selectbox(
            "Select Ollama Model", 
            options=ollama_models
        )
    
    selected_agent = st.sidebar.selectbox(
        "Select Agent",
        options=list(AgentType),
        format_func=lambda x: x.value
    )
    
    return brave_api_key, selected_model, selected_agent

async def process_message(agent: BaseAgent, message: str):
    try:
        return await agent.process_query(message)
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
        return f"Error: {str(e)}"

def main():
    # Initialize UI
    ui = EnhancedUI()
    
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
    
    # Pass agent to UI for processing
    ui.render(current_agent, process_message, selected_model)

if __name__ == "__main__":
    main()