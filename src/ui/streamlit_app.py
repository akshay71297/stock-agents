import asyncio
from typing import List

import streamlit as st
from pydantic_ai.messages import UserPrompt, ModelTextResponse

from src.utils.ollama_utils import get_ollama_models, create_ollama_client
from src.agents.web_search_agent import WebSearchAgent
from src.config import settings
from pydantic_ai.models.openai import OpenAIModel

def initialize_chat_history():
    """Initialize or retrieve chat history from session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat_history():
    """Display existing chat messages."""
    for message in st.session_state.messages:
        role = message.role
        with st.chat_message("human" if role == "user" else "ai"):
            st.markdown(message.content)

def run_streamlit_app():
    """Main Streamlit application entry point."""
    st.title("🔍 AI Web Search Agent")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Brave API Key input
    brave_api_key = st.sidebar.text_input(
        "Brave API Key", 
        type="password", 
        value=settings.BRAVE_API_KEY
    )
    
    # Fetch and display Ollama models
    ollama_models = get_ollama_models()
    
    # Model selection dropdown
    selected_model = st.sidebar.selectbox(
        "Select Ollama Model", 
        options=ollama_models if ollama_models else ['No models found']
    )
    
    # Check if models are available
    if not ollama_models:
        st.sidebar.warning("No Ollama models found. Please pull a model.")
        return

    # Initialize chat history
    initialize_chat_history()
    
    # Display existing chat history
    display_chat_history()

    # User input
    if prompt := st.chat_input("What would you like to research today?"):
        # Display user message
        st.chat_message("user").markdown(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append(UserPrompt(content=prompt))

        # Prepare Ollama client and model
        ollama_client = create_ollama_client(selected_model)
        model = OpenAIModel(selected_model, openai_client=ollama_client)

        # Initialize web search agent
        web_search_agent = WebSearchAgent(model)

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Run the prompt
                with st.spinner(f'Searching and generating response using {selected_model}...'):
                    response = asyncio.run(web_search_agent.process_query(prompt))
                
                # Display the response
                message_placeholder.markdown(response)
                
                # Add model response to chat history
                st.session_state.messages.append(ModelTextResponse(content=response))
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

8. `src/main.py`:
<antArtifact identifier="main-script" type="application/vnd.ant.code" language="python" title="Main Application Entry Point">
import streamlit as st
from src.ui.streamlit_app import run_streamlit_app

def main():
    run_streamlit_app()

if __name__ == '__main__':
    main()