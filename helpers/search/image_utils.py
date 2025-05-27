import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def optimize_image_query(query: str) -> str:
    """Optimize query for better image search results."""
    
    # Remove common words that don't help with image search
    stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    
    # Split query and remove stop words
    words = query.lower().split()
    filtered_words = [word for word in words if word not in stop_words]
    
    # Add specific image-related terms based on context
    context_terms = _get_context_terms(query)
    filtered_words.extend(context_terms)
    
    return ' '.join(filtered_words)


def _get_context_terms(query: str) -> List[str]:
    """Get context-specific terms to improve image search."""
    
    query_lower = query.lower()
    terms = []
    
    if any(word in query_lower for word in ['movie', 'film', 'cinema']):
        terms.extend(['poster', 'movie'])
    elif any(word in query_lower for word in ['game', 'gaming', 'video game']):
        terms.extend(['cover', 'game'])
    elif any(word in query_lower for word in ['album', 'music', 'song', 'band']):
        terms.extend(['album', 'cover'])
    elif any(word in query_lower for word in ['sport', 'athlete', 'player']):
        terms.extend(['photo'])
    elif any(word in query_lower for word in ['book', 'novel']):
        terms.extend(['cover', 'book'])
    elif any(word in query_lower for word in ['product', 'item']):
        terms.extend(['image', 'photo'])
    
    return terms


def extract_multiple_image_urls_from_text(text: str) -> List[str]:
    """Extract multiple image URLs from search result text."""
    
    # Enhanced image URL patterns with more specificity
    image_patterns = [
        # Direct image URLs
        r'https?://[^\s<>"\']+\.(?:jpg|jpeg|png|gif|webp|bmp)(?:\?[^\s<>"\']*)?',
        
        # Common image hosting patterns
        r'https?://[^\s<>"\']*(?:image|img|poster|cover|photo|picture)[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
        
        # Specific site patterns
        r'https?://m\.media-amazon\.com/images/[^\s<>"\']+',
        r'https?://[^\s<>"\']*imdb[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
        r'https?://upload\.wikimedia\.org/[^\s<>"\']+\.(?:jpg|jpeg|png|gif|webp)',
        r'https?://[^\s<>"\']*igdb[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
        r'https?://[^\s<>"\']*steamcdn[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
        r'https?://[^\s<>"\']*discogs[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
        
        # Generic CDN patterns
        r'https?://[^\s<>"\']*cdn[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
        r'https?://[^\s<>"\']*static[^\s<>"\']*\.(?:jpg|jpeg|png|gif|webp)',
    ]
    
    found_urls = []
    
    for pattern in image_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean_url = re.sub(r'[.,;:!?\'">\]})]+$', '', match)
            if clean_url not in found_urls and is_valid_image_url(clean_url):
                found_urls.append(clean_url)
    
    return found_urls


def is_valid_image_url(url: str) -> bool:
    """Enhanced validation for image URLs."""
    
    if not url or len(url) < 10:
        return False
    
    if not url.startswith(('http://', 'https://')):
        return False
    
    return validate_image_indicators(url) and not _has_bad_indicators(url)


def validate_image_indicators(url: str) -> bool:
    """Check if URL has positive image indicators."""
    
    image_indicators = [
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
        '/images/', '/img/', '/poster/', '/cover/', '/photo/', '/picture/',
        'media-amazon.com', 'wikimedia.org', 'imdb.', 'igdb.', 'steamcdn'
    ]
    
    url_lower = url.lower()
    return any(indicator in url_lower for indicator in image_indicators)


def _has_bad_indicators(url: str) -> bool:
    """Check if URL has indicators that suggest it's not a good image source."""
    
    bad_indicators = [
        'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
        'youtube.com', 'tiktok.com', '.css', '.js', '.html', '.pdf',
        'amazon.com/dp/', 'amazon.com/gp/', 'reddit.com'
    ]
    
    url_lower = url.lower()
    return any(bad in url_lower for bad in bad_indicators)


def get_google_image_size_param(size: str) -> str:
    """Convert size preference to Google search parameter."""
    
    size_map = {
        "thumbnail": "i",  # Icon
        "small": "s",      # Small
        "medium": "m",     # Medium
        "large": "l",      # Large
        "xlarge": "x",     # Extra Large
        "xxlarge": "xx"    # Extra Extra Large
    }
    
    return size_map.get(size.lower(), "m")


def score_image_relevance(url: str, query: str) -> float:
    """Score how relevant an image URL is to the query (0.0 to 1.0)."""
    
    if not url or not query:
        return 0.0
    
    url_lower = url.lower()
    query_lower = query.lower()
    query_words = query_lower.split()
    
    score = 0.0
    
    # Check if query words appear in URL
    for word in query_words:
        if len(word) > 2 and word in url_lower:
            score += 0.2
    
    # Bonus for high-quality image sources
    quality_sources = [
        'wikimedia.org', 'imdb.com', 'media-amazon.com',
        'igdb.com', 'discogs.com', 'steamcdn.com'
    ]
    
    if any(source in url_lower for source in quality_sources):
        score += 0.3
    
    # Bonus for proper image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if any(ext in url_lower for ext in image_extensions):
        score += 0.1
    
    # Penalty for low-quality indicators
    low_quality = ['thumb', 'thumbnail', 'small', 'tiny']
    if any(indicator in url_lower for indicator in low_quality):
        score -= 0.2
    
    return max(0.0, min(1.0, score))


def filter_best_images(image_urls: List[str], query: str, max_results: int = 5) -> List[str]:
    """Filter and rank image URLs by relevance to query."""
    
    if not image_urls:
        return []
    
    # Score each image
    scored_images = []
    for url in image_urls:
        score = score_image_relevance(url, query)
        scored_images.append((url, score))
    
    # Sort by score (descending) and return top results
    scored_images.sort(key=lambda x: x[1], reverse=True)
    
    return [url for url, score in scored_images[:max_results]]