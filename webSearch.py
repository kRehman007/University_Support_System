# webSearch.py
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# University domain - will be configured by user
UNIVERSITY_DOMAIN = os.getenv("UNIVERSITY_DOMAIN", "example.edu.pk")

# Initialize Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None


def search_university_website(query: str, max_results: int = 3) -> list[dict]:
    """
    Search ONLY within the university website.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        List of dicts with keys: title, url, content
    """
    if not tavily_client:
        print("Warning: TAVILY_API_KEY not set, skipping web search")
        return []
    
    try:
        response = tavily_client.search(
            query=query,
            include_domains=[UNIVERSITY_DOMAIN],
            max_results=max_results,
            search_depth="basic",  # Use "advanced" for deeper search (uses more credits)
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Web search error: {e}")
        return []


def format_web_results(results: list[dict]) -> str:
    """
    Format web search results into a context string for the LLM.
    
    Args:
        results: List of search results from Tavily
        
    Returns:
        Formatted string with titles, URLs, and content
    """
    if not results:
        return ""
    
    formatted = []
    for r in results:
        title = r.get("title", "No title")
        url = r.get("url", "")
        content = r.get("content", "")
        formatted.append(f"**{title}**\nSource: {url}\n{content}")
    
    return "\n\n---\n\n".join(formatted)
