from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict

from httpx import AsyncClient
import logfire

from src.agents.base_agent import BaseAgent
from src.tools.web_search import WebSearchTool
from src.config import settings

class WebSearchAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model)
        
        @self.agent.tool
        async def search_web(ctx, web_query: str) -> str:
            """Web search tool integrated with the agent"""
            return await WebSearchTool.search(
                ctx.deps.client, 
                web_query, 
                ctx.deps.brave_api_key
            )
    
    def get_system_prompt(self) -> str:
        return (
            f"You are an expert at researching the web to answer user questions. "
            f"The current date is: {datetime.now().strftime('%Y-%m-%d')}"
        )
    
    @dataclass
    class Deps:
        client: AsyncClient
        brave_api_key: str | None
    
    async def process_query(self, query: str, context: Dict[str, Any] = None):
        """
        Process a web search query with optional context.
        
        Args:
            query (str): The search query
            context (Dict, optional): Additional context for search
        
        Returns:
            Search results or processed information
        """
        async with AsyncClient() as client:
            deps = self.Deps(
                client=client, 
                brave_api_key=settings.BRAVE_API_KEY
            )
            
            with logfire.span('Web Search Agent', query=query):
                result = await self.agent.run(query, deps=deps)
                return result.data