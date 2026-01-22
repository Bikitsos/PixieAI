"""
Web Search Module

Provides internet search capabilities using DuckDuckGo.
"""

from ddgs import DDGS
from typing import Optional

from src.config import MAX_SEARCH_RESULTS


def search_web(query: str, max_results: int = MAX_SEARCH_RESULTS) -> list[dict]:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default from config).
    
    Returns:
        List of search result dictionaries with 'title', 'href', and 'body' keys.
    """
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception:
        return []


def format_search_results(results: list[dict]) -> str:
    """
    Format search results into a structured string for LLM context.
    
    Args:
        results: List of search result dictionaries.
    
    Returns:
        Formatted string with titles and snippets.
    """
    if not results:
        return "No search results found."
    
    formatted_parts = []
    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        snippet = result.get("body", "No description")
        url = result.get("href", "")
        
        formatted_parts.append(
            f"[{i}] Title: {title}\n"
            f"    Snippet: {snippet}\n"
            f"    URL: {url}"
        )
    
    return "\n\n".join(formatted_parts)


def search_and_format(query: str, max_results: int = MAX_SEARCH_RESULTS) -> Optional[str]:
    """
    Convenience function to search and format results in one call.
    
    Args:
        query: The search query string.
        max_results: Maximum number of results to return.
    
    Returns:
        Formatted search results string, or None if search failed.
    """
    results = search_web(query, max_results)
    if results:
        return format_search_results(results)
    return None
