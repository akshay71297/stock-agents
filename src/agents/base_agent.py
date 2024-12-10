from abc import ABC, abstractmethod
from typing import Any, List, Dict
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel

class BaseAgent(ABC):
    def __init__(self, model: OpenAIModel):
        """
        Initialize a base agent with a specific model.
        
        Args:
            model (OpenAIModel): The language model to use for the agent
        """
        self.agent = Agent(
            model,
            system_prompt=self.get_system_prompt(),
            retries=2
        )
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Define the system prompt for the specific agent.
        
        Returns:
            str: System prompt describing the agent's role and capabilities
        """
        pass
    
    @abstractmethod
    async def process_query(self, query: str, context: Dict[str, Any] = None):
        """
        Process a query using the agent's specific capabilities.
        
        Args:
            query (str): The input query to process
            context (Dict, optional): Additional context for processing
        
        Returns:
            The processed result
        """
        pass