import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
    OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY', 'ollama')

    # Brave Search API
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY', '')

    # Logging Configuration
    LOGFIRE_ENABLED = os.getenv('LOGFIRE_ENABLED', 'if-token-present')

    # Default Model
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'llama3')

settings = Settings()