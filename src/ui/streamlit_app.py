import streamlit as st
import asyncio
import hashlib
from typing import List, Optional, Callable, Any

# Configure page
st.set_page_config(
    page_title="AI Agents Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def is_markdown_content(content: str) -> bool:
    """Check if content contains markdown elements"""
    markdown_indicators = [
        "```",        # Code blocks
        "###",        # Headers
        "- ",         # List items
        "1. ",        # Numbered lists
        "|---",       # Tables
        "![",         # Images
        "[",          # Links
        "> ",         # Blockquotes
    ]
    return any(indicator in content for indicator in markdown_indicators)

class EnhancedUI:
    def __init__(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def render(self, agent: Any, process_message: Callable, model_name: str):
        """Render the chat interface"""
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("What would you like to know?"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Show user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process and show assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                status_container = st.empty()
                
                # Show initial status
                status_container.status(f"Processing with {model_name}", state="running", expanded=False)
                
                try:
                    # Get response
                    response = asyncio.run(process_message(agent, prompt))
                    status_container.status("Done!", state="complete", expanded=False)
                    
                    # Add response to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    # Clear status after a short delay
                    status_container.empty()
                    
                    # Display response directly
                    message_placeholder.markdown(response)
                
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    status_container.status("Error occurred", state="error")
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })