import time
import re
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Global rate limiting
_last_search_time = 0
_search_delay = 1.0


def apply_rate_limit():
    """Apply rate limiting delay between search requests."""
    global _last_search_time
    
    current_time = time.time()
    time_since_last_search = current_time - _last_search_time
    
    if time_since_last_search < _search_delay:
        sleep_time = _search_delay - time_since_last_search
        logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    _last_search_time = time.time()


def set_unified_search_delay(delay_seconds: float):
    """Set the delay between search requests."""
    global _search_delay
    _search_delay = delay_seconds
    logger.info(f"Unified search delay set to {delay_seconds} seconds")


def get_unified_search_delay() -> float:
    """Get the current search delay setting."""
    return _search_delay


def validate_url(url: str) -> bool:
    """Validate if a string is a proper URL."""
    try:
        if not url or len(url) < 10:
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
        
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
        
    except Exception:
        return False


def clean_search_query(query: str) -> str:
    """Clean and optimize a search query."""
    if not query:
        return ""
    
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Remove special characters that might interfere with search
    query = re.sub(r'[<>"\']', '', query)
    
    # Limit length
    if len(query) > 200:
        query = query[:200].rsplit(' ', 1)[0]  # Cut at word boundary
    
    return query


def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None


def is_trusted_domain(url: str) -> bool:
    """Check if URL is from a trusted domain for fact-checking."""
    trusted_domains = {
        # News organizations
        'reuters.com', 'ap.org', 'bbc.com', 'npr.org', 'pbs.org',
        
        # Government sources
        'gov', '.gov.', 'bls.gov', 'census.gov', 'cdc.gov', 'fda.gov',
        
        # Academic and research
        'edu', '.edu.', 'nih.gov', 'ncbi.nlm.nih.gov',
        
        # Fact-checking sites
        'snopes.com', 'factcheck.org', 'politifact.com',
        
        # Reference sites
        'wikipedia.org', 'britannica.com',
        
        # Financial data
        'sec.gov', 'federalreserve.gov', 'treasury.gov'
    }
    
    domain = extract_domain_from_url(url)
    if not domain:
        return False
    
    return any(trusted in domain for trusted in trusted_domains)


def calculate_source_credibility_score(url: str, title: str = "", snippet: str = "") -> float:
    """Calculate a credibility score for a source (0.0 to 1.0)."""
    score = 0.5  # Base score
    
    domain = extract_domain_from_url(url)
    if not domain:
        return 0.0
    
    # Trusted domain bonus
    if is_trusted_domain(url):
        score += 0.3
    
    # Government source bonus
    if '.gov' in domain:
        score += 0.2
    
    # Academic source bonus  
    if '.edu' in domain:
        score += 0.15
    
    # News organization bonus
    news_indicators = ['news', 'times', 'post', 'herald', 'tribune', 'journal']
    if any(indicator in domain for indicator in news_indicators):
        score += 0.1
    
    # Content quality indicators
    if title:
        # Longer, more descriptive titles tend to be better
        if len(title) > 20:
            score += 0.05
        
        # Avoid clickbait indicators
        clickbait_words = ['shocking', 'amazing', 'unbelievable', 'you won\'t believe']
        if any(word in title.lower() for word in clickbait_words):
            score -= 0.1
    
    # Ensure score stays within bounds
    return max(0.0, min(1.0, score))