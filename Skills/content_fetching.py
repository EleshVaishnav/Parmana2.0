from .registry import registry
import urllib.request
from bs4 import BeautifulSoup

@registry.register(
    name="fetch_url_content",
    description="Fetches and extracts plain text content from a specified URL website.",
    parameters={
        "url": {"type": "string", "description": "The full URL to fetch (http/https)."}
    }
)
def fetch_url_content(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=15).read()
        try:
            soup = BeautifulSoup(html, features="html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text[:4000]
        except NameError:
            return "Error: BeautifulSoup (bs4) is not installed. Run `pip install beautifulsoup4`"
    except Exception as e:
        return f"Fetch Error: {str(e)}"
