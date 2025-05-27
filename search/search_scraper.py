from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv
import os
import logging
import time
import json
import re
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse, urljoin
import requests

load_dotenv()

logger = logging.getLogger(__name__)

# Firecrawl API Key
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Rate limiting
_last_scrape_time = 0
_scrape_delay = 2.0  # 2 seconds between scrapes (more conservative for scraping)


def _apply_rate_limit():
    """Apply rate limiting delay between scrape requests."""
    global _last_scrape_time
    
    current_time = time.time()
    time_since_last_scrape = current_time - _last_scrape_time
    
    if time_since_last_scrape < _scrape_delay:
        sleep_time = _scrape_delay - time_since_last_scrape
        logger.debug(f"Scrape rate limiting: sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    _last_scrape_time = time.time()


def set_scrape_delay(delay_seconds: float):
    """Set the delay between scrape requests."""
    global _scrape_delay
    _scrape_delay = delay_seconds
    logger.info(f"Scrape delay set to {delay_seconds} seconds")


def get_scrape_delay() -> float:
    """Get the current scrape delay setting."""
    return _scrape_delay


class FirecrawlScraper:
    """Enhanced web scraper using Firecrawl API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or FIRECRAWL_API_KEY
        if not self.api_key:
            raise ValueError("Firecrawl API key not found. Set FIRECRAWL_API_KEY environment variable.")
        
        self.app = FirecrawlApp(api_key=self.api_key)
        logger.info("Firecrawl scraper initialized")
    
    def scrape_url(
        self, 
        url: str, 
        formats: List[str] = None,
        include_tags: List[str] = None,
        exclude_tags: List[str] = None,
        wait_for: int = 0,
        extract_structured: bool = True
    ) -> Dict[str, Union[str, Dict, List]]:
        """
        Scrape a single URL with enhanced options.
        
        Args:
            url: URL to scrape
            formats: Output formats (default: ['markdown', 'html'])
            include_tags: HTML tags to include
            exclude_tags: HTML tags to exclude  
            wait_for: Time to wait for page load (milliseconds)
            extract_structured: Whether to extract structured data
        
        Returns:
            Dictionary with scraped content and metadata
        """
        
        _apply_rate_limit()
        
        try:
            # Default formats
            if formats is None:
                formats = ['markdown', 'html']
            
            # Configure scrape options
            scrape_options = ScrapeOptions(
                formats=formats,
                includeTags=include_tags,
                excludeTags=exclude_tags,
                waitFor=wait_for
            )
            
            logger.info(f"Scraping URL: {url}")
            
            # Perform the scrape
            result = self.app.scrape_url(url, scrape_options=scrape_options)
            
            if result.get("success"):
                scraped_data = result.get("data", {})
                
                # Enhanced result processing
                processed_result = {
                    "success": True,
                    "url": url,
                    "scraped_at": time.time(),
                    "content": {
                        "markdown": scraped_data.get("markdown", ""),
                        "html": scraped_data.get("html", ""),
                        "text": self._extract_clean_text(scraped_data.get("markdown", "")),
                    },
                    "metadata": scraped_data.get("metadata", {}),
                    "structured_data": {},
                    "summary": ""
                }
                
                # Extract structured data if requested
                if extract_structured:
                    processed_result["structured_data"] = self._extract_structured_data(scraped_data)
                
                # Generate summary
                processed_result["summary"] = self._generate_content_summary(processed_result["content"])
                
                logger.info(f"Successfully scraped {url}")
                return processed_result
            
            else:
                logger.error(f"Scraping failed for {url}: {result}")
                return self._create_error_result(url, "Firecrawl scraping failed")
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return self._create_error_result(url, str(e))
    
    def crawl_website(
        self,
        base_url: str,
        limit: int = 10,
        formats: List[str] = None,
        exclude_patterns: List[str] = None,
        include_patterns: List[str] = None,
        max_depth: int = 2
    ) -> Dict[str, Union[str, List, Dict]]:
        """
        Crawl an entire website with enhanced options.
        
        Args:
            base_url: Base URL to start crawling
            limit: Maximum number of pages to crawl
            formats: Output formats for each page
            exclude_patterns: URL patterns to exclude
            include_patterns: URL patterns to include
            max_depth: Maximum crawl depth
        
        Returns:
            Dictionary with crawled pages and aggregated data
        """
        
        _apply_rate_limit()
        
        try:
            # Default formats
            if formats is None:
                formats = ['markdown']
            
            # Configure crawl options
            scrape_options = ScrapeOptions(formats=formats)
            
            logger.info(f"Crawling website: {base_url} (limit: {limit})")
            
            # Perform the crawl
            crawl_result = self.app.crawl_url(
                base_url,
                limit=limit,
                scrape_options=scrape_options
            )
            
            if crawl_result.get("success"):
                pages_data = crawl_result.get("data", [])
                
                # Process all crawled pages
                processed_pages = []
                all_content = []
                
                for page_data in pages_data:
                    page_result = {
                        "url": page_data.get("metadata", {}).get("sourceURL", ""),
                        "title": page_data.get("metadata", {}).get("title", ""),
                        "description": page_data.get("metadata", {}).get("description", ""),
                        "content": {
                            "markdown": page_data.get("markdown", ""),
                            "html": page_data.get("html", ""),
                            "text": self._extract_clean_text(page_data.get("markdown", "")),
                        },
                        "metadata": page_data.get("metadata", {}),
                        "word_count": len(page_data.get("markdown", "").split()),
                        "structured_data": self._extract_structured_data(page_data)
                    }
                    
                    processed_pages.append(page_result)
                    all_content.append(page_result["content"]["text"])
                
                # Create aggregated result
                aggregated_result = {
                    "success": True,
                    "base_url": base_url,
                    "crawled_at": time.time(),
                    "total_pages": len(processed_pages),
                    "pages": processed_pages,
                    "aggregated_content": {
                        "combined_text": "\n\n".join(all_content),
                        "total_words": sum(page["word_count"] for page in processed_pages),
                        "all_titles": [page["title"] for page in processed_pages if page["title"]],
                        "all_descriptions": [page["description"] for page in processed_pages if page["description"]]
                    },
                    "summary": self._generate_website_summary(processed_pages)
                }
                
                logger.info(f"Successfully crawled {len(processed_pages)} pages from {base_url}")
                return aggregated_result
            
            else:
                logger.error(f"Crawling failed for {base_url}: {crawl_result}")
                return self._create_error_result(base_url, "Firecrawl crawling failed")
                
        except Exception as e:
            logger.error(f"Error crawling {base_url}: {e}")
            return self._create_error_result(base_url, str(e))
    
    def scrape_multiple_urls(
        self,
        urls: List[str],
        formats: List[str] = None,
        max_concurrent: int = 3
    ) -> Dict[str, Dict]:
        """
        Scrape multiple URLs with rate limiting.
        
        Args:
            urls: List of URLs to scrape
            formats: Output formats
            max_concurrent: Maximum concurrent requests (not used with rate limiting)
        
        Returns:
            Dictionary mapping URLs to their scrape results
        """
        
        results = {}
        
        for url in urls:
            try:
                result = self.scrape_url(url, formats=formats)
                results[url] = result
                
                # Rate limiting between requests
                if len(results) < len(urls):  # Not the last request
                    time.sleep(_scrape_delay)
                    
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                results[url] = self._create_error_result(url, str(e))
        
        return results
    
    def _extract_clean_text(self, markdown: str) -> str:
        """Extract clean text from markdown content."""
        
        if not markdown:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'```[\s\S]*?```', '', markdown)  # Remove code blocks
        text = re.sub(r'`[^`]*`', '', text)  # Remove inline code
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Remove images
        text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)  # Convert links to text
        text = re.sub(r'[#*_~`]', '', text)  # Remove markdown symbols
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean up whitespace
        
        return text.strip()
    
    def _extract_structured_data(self, page_data: Dict) -> Dict:
        """Extract structured data from page."""
        
        structured = {}
        metadata = page_data.get("metadata", {})
        
        # Extract common structured elements
        structured["title"] = metadata.get("title", "")
        structured["description"] = metadata.get("description", "")
        structured["keywords"] = metadata.get("keywords", "")
        structured["author"] = metadata.get("author", "")
        structured["language"] = metadata.get("language", "")
        structured["og_data"] = {
            "title": metadata.get("ogTitle", ""),
            "description": metadata.get("ogDescription", ""),
            "image": metadata.get("ogImage", ""),
            "url": metadata.get("ogUrl", "")
        }
        
        # Extract dates if available
        if "publishedTime" in metadata:
            structured["published_date"] = metadata["publishedTime"]
        if "modifiedTime" in metadata:
            structured["modified_date"] = metadata["modifiedTime"]
        
        return structured
    
    def _generate_content_summary(self, content: Dict) -> str:
        """Generate a summary of the scraped content."""
        
        text = content.get("text", "")
        if not text:
            return "No content available"
        
        word_count = len(text.split())
        char_count = len(text)
        
        # Extract first paragraph as preview
        lines = text.split('\n')
        preview = ""
        for line in lines:
            if line.strip() and len(line.strip()) > 50:
                preview = line.strip()[:200] + "..."
                break
        
        return f"Content summary: {word_count} words, {char_count} characters. Preview: {preview}"
    
    def _generate_website_summary(self, pages: List[Dict]) -> str:
        """Generate a summary of the crawled website."""
        
        total_pages = len(pages)
        total_words = sum(page["word_count"] for page in pages)
        
        # Get unique titles
        titles = [page["title"] for page in pages if page["title"]]
        unique_titles = list(set(titles))
        
        return f"Website crawl summary: {total_pages} pages, {total_words} total words. Page titles: {', '.join(unique_titles[:5])}{'...' if len(unique_titles) > 5 else ''}"
    
    def _create_error_result(self, url: str, error_message: str) -> Dict:
        """Create an error result structure."""
        
        return {
            "success": False,
            "url": url,
            "scraped_at": time.time(),
            "error": error_message,
            "content": {
                "markdown": "",
                "html": "",
                "text": "",
            },
            "metadata": {},
            "structured_data": {},
            "summary": f"Scraping failed: {error_message}"
        }


# Convenience functions
def scrape_url(url: str, **kwargs) -> Dict:
    """Convenience function to scrape a single URL."""
    
    if not FIRECRAWL_API_KEY:
        logger.error("Firecrawl API key not configured")
        return {"success": False, "error": "API key not configured", "url": url}
    
    scraper = FirecrawlScraper()
    return scraper.scrape_url(url, **kwargs)


def crawl_website(base_url: str, **kwargs) -> Dict:
    """Convenience function to crawl a website."""
    
    if not FIRECRAWL_API_KEY:
        logger.error("Firecrawl API key not configured")
        return {"success": False, "error": "API key not configured", "base_url": base_url}
    
    scraper = FirecrawlScraper()
    return scraper.crawl_website(base_url, **kwargs)


def test_firecrawl_scraper():
    """Test Firecrawl scraper functionality."""
    
    if not FIRECRAWL_API_KEY:
        print("Firecrawl API key not configured. Set FIRECRAWL_API_KEY environment variable.")
        return
    
    print("=== FIRECRAWL SCRAPER TEST ===")
    
    test_urls = [
        "https://en.wikipedia.org/wiki/Unemployment_in_the_United_States",
        "https://www.bls.gov/news.release/empsit.nr0.htm"
    ]
    
    scraper = FirecrawlScraper()
    
    # Test single URL scraping
    for url in test_urls:
        print(f"\nTesting single URL scrape: {url}")
        print("-" * 60)
        
        result = scraper.scrape_url(url, formats=['markdown'])
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"Title: {result['structured_data'].get('title', 'No title')}")
            print(f"Content length: {len(result['content']['text'])} characters")
            print(f"Summary: {result['summary']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    # Test website crawling
    print(f"\n\nTesting website crawl: https://firecrawl.dev")
    print("-" * 60)
    
    crawl_result = scraper.crawl_website(
        "https://firecrawl.dev",
        limit=3,
        formats=['markdown']
    )
    
    if crawl_result["success"]:
        print(f"✅ Crawl Success!")
        print(f"Pages crawled: {crawl_result['total_pages']}")
        print(f"Total words: {crawl_result['aggregated_content']['total_words']}")
        print(f"Summary: {crawl_result['summary']}")
    else:
        print(f"❌ Crawl Failed: {crawl_result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_firecrawl_scraper()