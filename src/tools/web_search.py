from typing import Optional
from httpx import AsyncClient

class WebSearchTool:
    @staticmethod
    async def search(
        client: AsyncClient, 
        query: str, 
        brave_api_key: Optional[str] = None
    ) -> str:
        """
        Perform a web search using Brave Search API.
        
        Args:
            client (AsyncClient): HTTP client for making requests
            query (str): Search query
            brave_api_key (Optional[str]): Brave Search API key
        
        Returns:
            str: Formatted search results
        """
        if not brave_api_key:
            return "No Brave API key provided. Cannot perform web search."

        headers = {
            'X-Subscription-Token': brave_api_key,
            'Accept': 'application/json',
        }
        
        try:
            r = await client.get(
                'https://api.search.brave.com/res/v1/web/search',
                params={
                    'q': query,
                    'count': 5,
                    'text_decorations': True,
                    'search_lang': 'en'
                },
                headers=headers
            )
            r.raise_for_status()
            data = r.json()

            results = []
            web_results = data.get('web', {}).get('results', [])
            for item in web_results[:3]:
                title = item.get('title', '')
                description = item.get('description', '')
                url = item.get('url', '')
                if title and description:
                    results.append(f"Title: {title}\nSummary: {description}\nSource: {url}\n")

            return "\n".join(results) if results else "No results found for the query."
        
        except Exception as e:
            return f"Web search error: {str(e)}"