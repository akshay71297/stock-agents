"""
Package containing all agent implementations.
"""

from src.agents.base_agent import BaseAgent
from src.agents.web_search_agent import WebSearchAgent

__all__ = [
    'BaseAgent',
    'WebSearchAgent',
    # Add new agents here as they are created
    # 'StockMarketAgent',
    # 'SimFinAgent',
]