from typing import Dict, List,Any, Optional
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool,tool
from datetime import datetime
import requests
import os

@tool("searxng_search", return_direct=False)
def searxng_search(query: str, api_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Search the web or a SearXNG instance specifically for legal texts and documents 
    related to the Egyptian Civil Law (Sanhuri Law / كتاب السنهوري).

    This tool is designed to assist research in Egyptian civil law by providing 
    relevant articles, principles, and explanations from official documents, 
    legal commentaries, and online resources.

    Args:
        query (str): The search query in Arabic or English, e.g., 
                     "المادة 147 القانون المدني السنهوري القوة الملزمة".
        api_url (Optional[str]): The base URL of the SearXNG instance. 
                                 If None, defaults to the `SEARXNG_URL` environment variable 
                                 or a public instance (`https://search.snopyta.org`).

    Returns:
        Dict[str, Any]: A dictionary containing a nested 'output' key for compatibility with 
                        the chatbot agent. The inner 'output' key contains:
                        - 'results': a list of dictionaries with 'title', 'url', and 'snippet' of each document
                        - or an 'error' message if no results are found or a network issue occurs.
    """
    api_url = "https://google.com"

    try:
        response = requests.get(
            f"{api_url}/search",
            params={"q": query, "format": "json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results_raw: List[Dict[str, Any]] = data.get("results", [])

        if not results_raw:
            return {"output": {"output": "No results found."}}

        formatted_results: List[Dict[str, str]] = []
        for result in results_raw[:5]:
            formatted_results.append({
                "title": result.get("title", "No Title"),
                "url": result.get("url", "No URL"),
                "snippet": result.get("content", "No Snippet")
            })

        return {"output": {"output": formatted_results}}

    except requests.exceptions.RequestException as e:
        return {"output": {"output": f"Error during search: {str(e)}"}}

search_tool=searxng_search
