import requests
from bs4 import BeautifulSoup
from .registry import registry

@registry.register(
    name="web_search",
    description="Searches the web using DuckDuckGo to obtain up-to-date information (Pure Python version).",
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
    """Perform a web search using DuckDuckGo via pure Python scraping."""
    try:
        max_results = int(max_results)
        # Using the html version of ddg which is more scraper-friendly
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("div", class_="result")[:max_results]
        
        if not results:
            return "No search results found. (The search engine may be ratelimiting or the query returned no data)."
        
        formatted_results = []
        for i, res in enumerate(results):
            title_tag = res.find("a", class_="result__a")
            snippet_tag = res.find("a", class_="result__snippet")
            
            if title_tag:
                title = title_tag.get_text()
                link = title_tag.get("href")
                snippet = snippet_tag.get_text() if snippet_tag else "No snippet available."
                formatted_results.append(f"{i+1}. Title: {title}\nSnippet: {snippet}\nLink: {link}\n")
        
        if not formatted_results:
             return "No search results found (parsing error)."
             
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Web Search Error (Pure Python): {str(e)}"

