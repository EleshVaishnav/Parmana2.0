from .registry import registry
from duckduckgo_search import DDGS

@registry.register(
    name="web_search",
    description="Searches the web using DuckDuckGo to obtain up-to-date information.",
    parameters={
        "query": {
            "type": "string",
            "description": "The search query to look up on the web."
        },
        "max_results": {
            "type": "string",
            "description": "Maximum number of results to return (default '5')."
        }
    }
)
def web_search(query: str, max_results: str = "5") -> str:
    """Perform a web search using DuckDuckGo."""
    try:
        max_results = int(max_results)
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            
            if not results:
                return "No search results found."
            
            formatted_results = []
            for i, res in enumerate(results):
                formatted_results.append(f"{i+1}. Title: {res.get('title')}\nSnippet: {res.get('body')}\nLink: {res.get('href')}\n")
            
            return "\n".join(formatted_results)
    except Exception as e:
        return f"Web Search Error: {str(e)}"
