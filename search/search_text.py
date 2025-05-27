from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities import BraveSearchWrapper
from langchain.tools import Tool
from dotenv import load_dotenv
import os
import logging
import json
from typing import Dict, List, Union

# Import helpers
from helpers.search import (
    apply_rate_limit,
    set_unified_search_delay,
    get_unified_search_delay,
    extract_structured_results_from_text,
    create_search_summary,
    create_simple_result
)

load_dotenv()

logger = logging.getLogger(__name__)

# API Keys
GOOGLE_SERPER_API_KEY = os.getenv("SERPER_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")


def set_search_delay(delay_seconds: float):
    """Set the delay between search requests."""
    set_unified_search_delay(delay_seconds)


def get_search_delay() -> float:
    """Get the current search delay setting."""
    return get_unified_search_delay()


def enhanced_text_search(
    query: str, 
    provider: str = "duckduckgo", 
    max_results: int = 10,
    time_filter: str = None,
    safe_search: str = "moderate",
    region: str = "us-en"
) -> Dict[str, Union[str, List[Dict]]]:
    """
    Enhanced text search with structured results and metadata.
    
    Args:
        query: Search query
        provider: Search provider ("duckduckgo", "google", "brave")
        max_results: Maximum number of results
        time_filter: Time filter ("day", "week", "month", "year")
        safe_search: Safe search setting ("strict", "moderate", "off")
        region: Region for search results
    
    Returns:
        Dictionary with search results and metadata
    """
    
    apply_rate_limit()
    
    try:
        if provider == "google" and GOOGLE_SERPER_API_KEY:
            return _search_google_enhanced(query, max_results, time_filter, safe_search, region)
        elif provider == "brave" and BRAVE_API_KEY:
            return _search_brave_enhanced(query, max_results, time_filter, safe_search, region)
        elif provider == "duckduckgo":
            return _search_duckduckgo_enhanced(query, max_results, safe_search, region)
        else:
            logger.warning(f"Provider {provider} not available, falling back to DuckDuckGo")
            return _search_duckduckgo_enhanced(query, max_results, safe_search, region)
            
    except Exception as e:
        logger.error(f"Enhanced search failed: {e}")
        return {
            "query": query,
            "provider": provider,
            "success": False,
            "error": str(e),
            "results": [],
            "summary": f"Search failed: {str(e)}"
        }


def _search_google_enhanced(
    query: str, 
    max_results: int, 
    time_filter: str, 
    safe_search: str, 
    region: str
) -> Dict:
    """Enhanced Google search with structured results."""
    
    try:
        search_params = {
            "serper_api_key": GOOGLE_SERPER_API_KEY,
            "num": max_results,
            "gl": region.split("-")[0] if "-" in region else "us",
            "hl": region.split("-")[1] if "-" in region else "en"
        }
        
        if time_filter:
            time_map = {"day": "d", "week": "w", "month": "m", "year": "y"}
            if time_filter in time_map:
                search_params["tbs"] = f"qdr:{time_map[time_filter]}"
        
        search = GoogleSerperAPIWrapper(**search_params)
        
        logger.info(f"Google enhanced search: '{query}'")
        results = search.run(query)
        
        # Parse Google results
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except json.JSONDecodeError:
                return create_simple_result(query, "google", results)
        
        if isinstance(results, dict):
            structured_results = []
            
            # Extract organic results
            organic = results.get("organic", [])
            for item in organic[:max_results]:
                structured_results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "date": item.get("date", ""),
                    "source": "google_organic"
                })
            
            # Extract knowledge panel if available
            knowledge_graph = results.get("knowledgeGraph", {})
            if knowledge_graph:
                structured_results.insert(0, {
                    "title": knowledge_graph.get("title", ""),
                    "url": knowledge_graph.get("website", ""),
                    "snippet": knowledge_graph.get("description", ""),
                    "date": "",
                    "source": "google_knowledge"
                })
            
            return {
                "query": query,
                "provider": "google",
                "success": True,
                "total_results": len(structured_results),
                "results": structured_results,
                "summary": create_search_summary(structured_results),
                "metadata": {
                    "search_time": results.get("searchInformation", {}).get("searchTime", ""),
                    "total_results_available": results.get("searchInformation", {}).get("totalResults", "")
                }
            }
        
        return create_simple_result(query, "google", str(results))
        
    except Exception as e:
        logger.error(f"Google enhanced search error: {e}")
        raise


def _search_brave_enhanced(
    query: str, 
    max_results: int, 
    time_filter: str, 
    safe_search: str, 
    region: str
) -> Dict:
    """Enhanced Brave search with structured results."""
    
    try:
        search_kwargs = {
            "count": max_results,
            "safesearch": safe_search,
            "country": region.split("-")[0] if "-" in region else "us"
        }
        
        if time_filter:
            time_map = {"day": "pd", "week": "pw", "month": "pm", "year": "py"}
            if time_filter in time_map:
                search_kwargs["freshness"] = time_map[time_filter]
        
        search = BraveSearchWrapper(
            api_key=BRAVE_API_KEY,
            search_kwargs=search_kwargs
        )
        
        logger.info(f"Brave enhanced search: '{query}'")
        results = search.run(query)
        
        # Parse Brave results using helper
        structured_results = extract_structured_results_from_text(results, "brave")
        
        return {
            "query": query,
            "provider": "brave",
            "success": True,
            "total_results": len(structured_results),
            "results": structured_results,
            "summary": create_search_summary(structured_results),
            "raw_text": results[:500] + "..." if len(results) > 500 else results
        }
        
    except Exception as e:
        logger.error(f"Brave enhanced search error: {e}")
        raise


def _search_duckduckgo_enhanced(
    query: str, 
    max_results: int, 
    safe_search: str, 
    region: str
) -> Dict:
    """Enhanced DuckDuckGo search with structured results."""
    
    try:
        search = DuckDuckGoSearchRun()
        
        logger.info(f"DuckDuckGo enhanced search: '{query}'")
        results = search.run(query)
        
        # Parse DuckDuckGo results using helper
        structured_results = extract_structured_results_from_text(results, "duckduckgo")
        
        return {
            "query": query,
            "provider": "duckduckgo",
            "success": True,
            "total_results": len(structured_results),
            "results": structured_results[:max_results],
            "summary": create_search_summary(structured_results[:max_results]),
            "raw_text": results[:500] + "..." if len(results) > 500 else results
        }
        
    except Exception as e:
        logger.error(f"DuckDuckGo enhanced search error: {e}")
        raise


def multi_provider_search(
    query: str, 
    providers: List[str] = None, 
    max_results_per_provider: int = 5
) -> Dict[str, Dict]:
    """Search across multiple providers and aggregate results."""
    
    if providers is None:
        providers = ["duckduckgo"]
        if GOOGLE_SERPER_API_KEY:
            providers.append("google")
        if BRAVE_API_KEY:
            providers.append("brave")
    
    all_results = {}
    
    for provider in providers:
        try:
            logger.info(f"Searching with {provider}")
            results = enhanced_text_search(
                query=query,
                provider=provider,
                max_results=max_results_per_provider
            )
            all_results[provider] = results
            
        except Exception as e:
            logger.error(f"Multi-provider search failed for {provider}: {e}")
            all_results[provider] = {
                "query": query,
                "provider": provider,
                "success": False,
                "error": str(e),
                "results": []
            }
    
    return all_results


def get_search_tool(provider: str = "duckduckgo") -> Tool:
    """Get a LangChain Tool for the specified search provider."""
    
    if provider == "duckduckgo":
        return DuckDuckGoSearchRun()
    elif provider == "google" and GOOGLE_SERPER_API_KEY:
        search = GoogleSerperAPIWrapper(serper_api_key=GOOGLE_SERPER_API_KEY)
        return Tool(
            name="Google Search",
            description="Search the web using Google Serper API",
            func=search.run
        )
    elif provider == "brave" and BRAVE_API_KEY:
        search = BraveSearchWrapper(api_key=BRAVE_API_KEY)
        return Tool(
            name="Brave Search",
            description="Search the web using Brave Search API",
            func=search.run
        )
    else:
        logger.warning(f"Provider {provider} not available, using DuckDuckGo")
        return DuckDuckGoSearchRun()


def test_enhanced_search():
    """Test enhanced search functionality."""
    
    test_queries = [
        "unemployment rate United States 2024",
        "climate change scientific consensus",
        "inflation rate current statistics"
    ]
    
    providers = ["duckduckgo"]
    if GOOGLE_SERPER_API_KEY:
        providers.append("google")
    if BRAVE_API_KEY:
        providers.append("brave")
    
    print("=== ENHANCED TEXT SEARCH TEST ===")
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        print("-" * 60)
        
        # Test multi-provider search
        results = multi_provider_search(query, providers, 3)
        
        for provider, result in results.items():
            print(f"\n{provider.upper()} Results:")
            print(f"Success: {result.get('success', False)}")
            print(f"Total Results: {result.get('total_results', 0)}")
            print(f"Summary: {result.get('summary', 'No summary')}")
            
            if result.get('results'):
                print("Top Results:")
                for i, res in enumerate(result['results'][:2], 1):
                    print(f"  {i}. {res.get('title', 'No title')}")
                    print(f"     URL: {res.get('url', 'No URL')}")
                    print(f"     Snippet: {res.get('snippet', 'No snippet')[:100]}...")


if __name__ == "__main__":
    test_enhanced_search()