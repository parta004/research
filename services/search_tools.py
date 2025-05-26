from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities import BraveSearchWrapper
from langchain.tools import Tool
from dotenv import load_dotenv
import os
import re
import logging
import time
import requests
import json
from typing import Optional, List, Dict

load_dotenv()

logger = logging.getLogger(__name__)

# API Keys for search providers
GOOGLE_SERPER_API_KEY = os.getenv("SERPER_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

# Rate limiting tracking
_last_search_time = 0
_search_delay = 1.0  # 1 second delay between searches


def _apply_rate_limit():
    """Apply rate limiting delay between searches."""
    global _last_search_time
    
    current_time = time.time()
    time_since_last_search = current_time - _last_search_time
    
    if time_since_last_search < _search_delay:
        sleep_time = _search_delay - time_since_last_search
        logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    _last_search_time = time.time()


def search_for_image_url(query: str, provider: str = "duckduckgo", image_size: str = "medium") -> Optional[str]:
    """
    Search for an image URL using the specified search provider with proper image search.
    
    Args:
        query: Search query (e.g., "The Godfather movie poster")
        provider: Search provider ("duckduckgo", "google", "brave")
        image_size: Image size preference ("small", "medium", "large", "thumbnail")
    
    Returns:
        Image URL string or None if not found
    """
    
    # Apply rate limiting before making any search request
    _apply_rate_limit()
    
    try:
        # Clean and optimize query for image search
        optimized_query = _optimize_image_query(query)
        
        if provider == "google" and GOOGLE_SERPER_API_KEY:
            return _search_google_images(optimized_query, image_size)
        elif provider == "brave" and BRAVE_API_KEY:
            return _search_brave_images(optimized_query, image_size)
        elif provider == "duckduckgo":
            return _search_duckduckgo_images_improved(optimized_query)
        else:
            logger.warning(f"Provider {provider} not available or missing API key, falling back to DuckDuckGo")
            return _search_duckduckgo_images_improved(optimized_query)
            
    except Exception as e:
        logger.error(f"Error searching for image with {provider}: {e}")
        return None


def _optimize_image_query(query: str) -> str:
    """Optimize query for better image search results."""
    
    # Remove common words that don't help with image search
    stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    
    # Split query and remove stop words
    words = query.lower().split()
    filtered_words = [word for word in words if word not in stop_words]
    
    # Add specific image-related terms
    if 'movie' in query.lower() or 'film' in query.lower():
        filtered_words.extend(['poster', 'movie'])
    elif 'game' in query.lower():
        filtered_words.extend(['cover', 'game'])
    elif 'album' in query.lower() or 'music' in query.lower():
        filtered_words.extend(['album', 'cover'])
    elif 'sport' in query.lower() or 'athlete' in query.lower():
        filtered_words.extend(['photo'])
    
    return ' '.join(filtered_words)


def _search_google_images(query: str, image_size: str = "medium") -> Optional[str]:
    """Search for images using Google Serper API with proper image search."""
    
    try:
        # Configure for image search
        search = GoogleSerperAPIWrapper(
            serper_api_key=GOOGLE_SERPER_API_KEY,
            type="images",
            tbs=f"isz:{_get_google_size_param(image_size)}",  # Image size parameter
            num=10  # Get more results to choose from
        )
        
        logger.info(f"Searching Google Images for: '{query}' (size: {image_size})")
        results = search.run(query)
        
        # Parse the results properly
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except json.JSONDecodeError:
                logger.error("Failed to parse Google Serper results as JSON")
                return None
        
        if isinstance(results, dict) and "images" in results:
            images = results["images"]
            logger.info(f"Found {len(images)} images from Google")
            
            # Try to find the best image
            for image in images:
                if isinstance(image, dict):
                    # Try different possible URL fields
                    image_url = (image.get("imageUrl") or 
                               image.get("link") or 
                               image.get("url") or
                               image.get("original"))
                    
                    if image_url and _is_valid_image_url(image_url):
                        logger.info(f"Selected Google image: {image_url}")
                        return image_url
        
        logger.warning("No valid images found in Google results")
        return None
        
    except Exception as e:
        logger.error(f"Google Images search error: {e}")
        return None


def _get_google_size_param(size: str) -> str:
    """Convert size preference to Google search parameter."""
    size_map = {
        "thumbnail": "i",  # Icon
        "small": "s",      # Small
        "medium": "m",     # Medium
        "large": "l"       # Large
    }
    return size_map.get(size.lower(), "m")


def _search_brave_images(query: str, image_size: str = "medium") -> Optional[str]:
    """Search for images using Brave Search API with image-specific search."""
    
    try:
        search = BraveSearchWrapper(
            api_key=BRAVE_API_KEY,
            search_kwargs={
                "search_type": "images",
                "count": 10,
                "safesearch": "moderate"
            }
        )
        
        logger.info(f"Searching Brave Images for: '{query}'")
        results = search.run(query)
        
        # Extract image URLs from Brave results
        image_urls = _extract_multiple_image_urls_from_text(results)
        
        if image_urls:
            logger.info(f"Found {len(image_urls)} images from Brave")
            # Return the first valid one
            for url in image_urls[:3]:  # Check first 3
                if _is_valid_image_url(url):
                    logger.info(f"Selected Brave image: {url}")
                    return url
        
        return None
        
    except Exception as e:
        logger.error(f"Brave Images search error: {e}")
        return None


def _search_duckduckgo_images_improved(query: str) -> Optional[str]:
    """Improved DuckDuckGo search focusing on image-rich sites."""
    
    try:
        search = DuckDuckGoSearchRun()
        
        # Search image-focused sites first
        image_sites = [
            "site:imdb.com",
            "site:wikipedia.org", 
            "site:ign.com",
            "site:metacritic.com",
            "site:gamespot.com",
            "site:allmusic.com",
            "site:discogs.com",
            "site:themoviedb.org"
        ]
        
        # Try each site
        for site in image_sites:
            try:
                site_query = f"{query} {site}"
                logger.info(f"Searching DuckDuckGo: '{site_query}'")
                results = search.run(site_query)
                
                # Extract image URLs
                image_urls = _extract_multiple_image_urls_from_text(results)
                
                if image_urls:
                    for url in image_urls[:2]:  # Check first 2 from each site
                        if _is_valid_image_url(url):
                            logger.info(f"Selected DuckDuckGo image: {url}")
                            return url
                
                # Small delay between site searches
                time.sleep(0.2)
                
            except Exception as e:
                logger.debug(f"Site search failed for {site}: {e}")
                continue
        
        # Fallback to general search with image terms
        logger.info("Trying general image search")
        general_query = f"{query} poster cover image jpg png"
        results = search.run(general_query)
        image_urls = _extract_multiple_image_urls_from_text(results)
        
        if image_urls:
            for url in image_urls[:3]:
                if _is_valid_image_url(url):
                    logger.info(f"Selected general search image: {url}")
                    return url
        
        return None
        
    except Exception as e:
        logger.error(f"DuckDuckGo Images search error: {e}")
        return None


def _extract_multiple_image_urls_from_text(text: str) -> List[str]:
    """Extract multiple image URLs from search result text."""
    
    # Enhanced image URL patterns with more specificity
    image_patterns = [
        # Direct image URLs
        r'https?://[^\s<>"\']+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s<>"\']*)?',
        
        # Common image hosting patterns
        r'https?://[^\s<>"\']*(?:image|img|poster|cover|photo|picture)[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
        
        # Specific site patterns
        r'https?://m\.media-amazon\.com/images/[^\s<>"\']+',  # Amazon images
        r'https?://[^\s<>"\']*imdb[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',  # IMDB
        r'https?://upload\.wikimedia\.org/[^\s<>"\']+\.(?:jpg|jpeg|png|gif|webp)',  # Wikipedia
        r'https?://[^\s<>"\']*igdb[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',  # IGDB
        r'https?://[^\s<>"\']*steamcdn[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',  # Steam
        r'https?://[^\s<>"\']*discogs[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',  # Discogs
        
        # Generic CDN patterns
        r'https?://[^\s<>"\']*cdn[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
        r'https?://[^\s<>"\']*static[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
    ]
    
    found_urls = []
    
    for pattern in image_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean the URL (remove trailing punctuation/quotes)
            clean_url = re.sub(r'[.,;:!?\'">\]})]+$', '', match)
            if clean_url not in found_urls and _is_valid_image_url(clean_url):
                found_urls.append(clean_url)
    
    return found_urls


def _is_valid_image_url(url: str) -> bool:
    """Enhanced validation for image URLs."""
    
    # Basic validation
    if not url or len(url) < 10:
        return False
    
    # Should start with http/https
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Should end with image extension or contain image-related paths
    image_indicators = [
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
        '/images/', '/img/', '/poster/', '/cover/', '/photo/', '/picture/',
        'media-amazon.com', 'wikimedia.org', 'imdb.', 'igdb.', 'steamcdn'
    ]
    
    url_lower = url.lower()
    has_indicator = any(indicator in url_lower for indicator in image_indicators)
    
    # Avoid obviously bad URLs
    bad_indicators = [
        'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
        'youtube.com', 'tiktok.com', '.css', '.js', '.html', '.pdf',
        'amazon.com/dp/', 'amazon.com/gp/'  # Product pages, not images
    ]
    
    has_bad_indicator = any(bad in url_lower for bad in bad_indicators)
    
    return has_indicator and not has_bad_indicator


def set_search_delay(delay_seconds: float):
    """Set the delay between search requests."""
    global _search_delay
    _search_delay = delay_seconds
    logger.info(f"Search delay set to {delay_seconds} seconds")


def get_search_delay() -> float:
    """Get the current search delay setting."""
    return _search_delay


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


# Test function with improved image search
def test_image_search():
    """Test improved image search functionality with different providers."""
    
    test_queries = [
        "The Godfather movie poster",
        "Michael Jordan basketball photo",
        "Pink Floyd Dark Side of the Moon album cover",
        "The Legend of Zelda Ocarina of Time game cover"
    ]
    
    providers = ["google", "duckduckgo"]
    if BRAVE_API_KEY:
        providers.append("brave")
    
    print("=== IMPROVED IMAGE SEARCH TEST ===")
    print(f"Search delay: {_search_delay} seconds")
    
    start_time = time.time()
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        print("-" * 50)
        
        for provider in providers:
            if provider == "google" and not GOOGLE_SERPER_API_KEY:
                print(f"GOOGLE: Skipping (no API key)")
                continue
                
            search_start = time.time()
            print(f"{provider.upper()}:")
            
            # Test with medium size (good for thumbnails)
            image_url = search_for_image_url(query, provider, "medium")
            search_end = time.time()
            search_time = round(search_end - search_start, 2)
            
            print(f"  Result: {image_url or 'No image found'}")
            print(f"  Time: {search_time}s")
        print()
    
    total_time = round(time.time() - start_time, 2)
    print(f"Total test time: {total_time}s")


if __name__ == "__main__":
    test_image_search()