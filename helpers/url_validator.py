import requests
import logging
from typing import List, Dict
from services.search_tools import search_for_image_url

logger = logging.getLogger(__name__)


def validate_url(url: str, timeout: int = 5) -> bool:
    """
    Validate if a URL is accessible and returns a valid response.
    
    Args:
        url: The URL to validate
        timeout: Request timeout in seconds
    
    Returns:
        True if URL is valid and accessible, False otherwise
    """
    
    if not url or url == "No image found" or not url.startswith(('http://', 'https://')):
        return False
    
    try:
        # Use HEAD request first (faster, less bandwidth)
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        # Check if status code is successful
        if response.status_code == 200:
            # Check if it's an image content type
            content_type = response.headers.get('content-type', '').lower()
            if any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'gif', 'webp']):
                return True
        
        # If HEAD fails, try GET with small range (some servers don't support HEAD)
        if response.status_code in [405, 501]:  # Method not allowed
            response = requests.get(url, timeout=timeout, stream=True, 
                                  headers={'Range': 'bytes=0-1023'})  # Just first 1KB
            return response.status_code == 206 or response.status_code == 200
        
        return False
        
    except requests.exceptions.RequestException as e:
        logger.debug(f"URL validation failed for {url}: {e}")
        return False


def validate_and_fix_image_urls(items: List[Dict], category: str, search_provider: str) -> List[Dict]:
    """
    Validate existing image URLs and replace broken ones using improved image search.
    
    Args:
        items: List of items to process
        category: Category for search context
        search_provider: Search provider to use for replacements
    
    Returns:
        List of items with validated and fixed image URLs
    """
    
    logger.info(f"Validating {len(items)} items with improved image search")
    
    for i, item in enumerate(items, 1):
        current_url = item.get('image_url', '')
        title = item.get('title', 'Unknown')
        
        logger.info(f"Processing item {i}/{len(items)}: '{title}'")
        
        # Check if URL exists and needs validation
        if current_url and current_url != "No image found":
            logger.info(f"Validating existing URL: {current_url}")
            
            if validate_url(current_url):
                logger.info(f"✅ URL is valid")
                item['url_status'] = 'valid'
                continue
            else:
                logger.info(f"❌ URL is broken, searching for replacement")
                item = _search_replacement_url(item, category, search_provider)
        else:
            # No URL provided, search for one
            logger.info(f"No URL provided, searching with improved search...")
            item = _search_new_url(item, category, search_provider)
    
    return items


def fill_missing_image_urls(items: List[Dict], category: str, search_provider: str) -> List[Dict]:
    """Fill missing image URLs using improved image search tools."""
    
    for item in items:
        if 'image_url' not in item or not item['image_url'] or item['image_url'] == "":
            # Search for image URL using improved search
            search_query = f"{item.get('title', '')} {item.get('creator', '')}"
            image_url = search_for_image_url(search_query, search_provider, "medium")
            item['image_url'] = image_url or "No image found"
    
    return items


def _search_replacement_url(item: Dict, category: str, search_provider: str) -> Dict:
    """Search for a replacement URL for a broken image."""
    search_query = f"{item.get('title', '')} {item.get('creator', '')}"
    new_url = search_for_image_url(search_query, search_provider, "medium")
    
    if new_url and new_url != "No image found":
        if validate_url(new_url):
            logger.info(f"✅ Found valid replacement: {new_url}")
            item['image_url'] = new_url
            item['url_status'] = 'replaced'
        else:
            logger.info(f"❌ Replacement URL also broken: {new_url}")
            item['image_url'] = "No valid image found"
            item['url_status'] = 'failed'
    else:
        logger.info("❌ No replacement found")
        item['image_url'] = "No valid image found"
        item['url_status'] = 'failed'
    
    return item


def _search_new_url(item: Dict, category: str, search_provider: str) -> Dict:
    """Search for a new URL when none exists."""
    search_query = f"{item.get('title', '')} {item.get('creator', '')}"
    new_url = search_for_image_url(search_query, search_provider, "medium")
    
    if new_url and new_url != "No image found":
        if validate_url(new_url):
            logger.info(f"✅ Found valid URL: {new_url}")
            item['image_url'] = new_url
            item['url_status'] = 'found'
        else:
            logger.info(f"❌ Found URL but it's broken: {new_url}")
            item['image_url'] = "No valid image found"
            item['url_status'] = 'failed'
    else:
        item['image_url'] = "No valid image found"
        item['url_status'] = 'not_found'
    
    return item