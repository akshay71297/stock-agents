import subprocess
from typing import List
import streamlit as st

def get_ollama_models() -> List[str]:
    """
    Fetch list of available Ollama models.
    
    Returns:
        List of model names or empty list if no models found.
    """
    try:
        # Use subprocess to run Ollama list command
        result = subprocess.run(
            ['ollama', 'list'], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Parse the output and extract model names
        models = []
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                # Split the line and take the first column (model name)
                model_name = line.split()[0]
                models.append(model_name)
        
        return models
    except Exception as e:
        st.error(f"Error fetching Ollama models: {e}")
        return []

def create_ollama_client(model_name: str):
    """
    Create an Ollama client for the selected model.
    
    Args:
        model_name (str): Name of the Ollama model
    
    Returns:
        AsyncOpenAI client configured for Ollama
    """
    from openai import AsyncOpenAI
    from src.config import settings

    return AsyncOpenAI(
        base_url=settings.OLLAMA_BASE_URL,
        api_key=settings.OLLAMA_API_KEY
    )