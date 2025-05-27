"""
Main search tools module that imports and exposes functionality from specialized modules.
"""

# Import from specialized modules
from .search_images import (
    search_for_image_url,
    test_image_search,
    set_search_delay as set_image_search_delay,
    get_search_delay as get_image_search_delay
)

from .search_text import (
    enhanced_text_search,
    multi_provider_search,
    get_search_tool,
    test_enhanced_search,
    set_search_delay as set_text_search_delay,
    get_search_delay as get_text_search_delay
)

from .search_scraper import (
    FirecrawlScraper,
    scrape_url,
    crawl_website,
    test_firecrawl_scraper,
    set_scrape_delay,
    get_scrape_delay
)

import logging

logger = logging.getLogger(__name__)

# Unified delay management
def set_search_delay(delay_seconds: float):
    """Set delay for all search operations."""
    set_image_search_delay(delay_seconds)
    set_text_search_delay(delay_seconds)
    logger.info(f"Unified search delay set to {delay_seconds} seconds")

def set_scrape_delay_unified(delay_seconds: float):
    """Set delay for scraping operations."""
    set_scrape_delay(delay_seconds)
    logger.info(f"Scrape delay set to {delay_seconds} seconds")

# Export commonly used functions
__all__ = [
    # Image search
    "search_for_image_url",
    "test_image_search",
    
    # Text search
    "enhanced_text_search", 
    "multi_provider_search",
    "get_search_tool",
    "test_enhanced_search",
    
    # Web scraping
    "FirecrawlScraper",
    "scrape_url",
    "crawl_website", 
    "test_firecrawl_scraper",
    
    # Delay management
    "set_search_delay",
    "set_scrape_delay_unified"
]

def run_all_tests():
    """Run tests for all search modules."""
    print("="*80)
    print("RUNNING ALL SEARCH TESTS")
    print("="*80)
    
    try:
        print("\n1. Testing Image Search...")
        test_image_search()
    except Exception as e:
        print(f"Image search test failed: {e}")
    
    try:
        print("\n2. Testing Enhanced Text Search...")
        test_enhanced_search()
    except Exception as e:
        print(f"Text search test failed: {e}")
    
    try:
        print("\n3. Testing Firecrawl Scraper...")
        test_firecrawl_scraper()
    except Exception as e:
        print(f"Scraper test failed: {e}")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()