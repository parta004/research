import re
import logging
from typing import Dict, List, Union

logger = logging.getLogger(__name__)


def extract_structured_results_from_text(text: str, provider: str) -> List[Dict]:
    """Extract structured results from text-based search results."""
    
    results = []
    
    # Try to extract structured information
    lines = text.split('\n')
    current_result = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_result:
                results.append(current_result)
                current_result = {}
            continue
        
        # Look for URLs
        url_match = re.search(r'https?://[^\s]+', line)
        if url_match:
            url = url_match.group(0)
            # Clean URL
            url = re.sub(r'[.,;:!?\'">\]})]+$', '', url)
            
            # If this line has a URL, treat the rest as title/snippet
            title_text = line.replace(url, '').strip()
            if title_text:
                current_result = {
                    "title": title_text[:100],
                    "url": url,
                    "snippet": title_text,
                    "date": "",
                    "source": f"{provider}_organic"
                }
                results.append(current_result)
                current_result = {}
        elif line and len(line) > 20:  # Potential snippet or title
            if not current_result:
                current_result = {
                    "title": line[:100],
                    "url": "",
                    "snippet": line,
                    "date": "",
                    "source": f"{provider}_organic"
                }
    
    # Add final result if exists
    if current_result:
        results.append(current_result)
    
    # Filter out results without URLs
    results = [r for r in results if r.get("url")]
    
    return results


def create_search_summary(results: List[Dict]) -> str:
    """Create a summary of search results."""
    
    if not results:
        return "No results found."
    
    total = len(results)
    
    # Extract key information
    titles = [r.get("title", "") for r in results if r.get("title")]
    snippets = [r.get("snippet", "") for r in results if r.get("snippet")]
    
    # Create summary
    summary_parts = [
        f"Found {total} results.",
    ]
    
    if titles:
        summary_parts.append(f"Top results include: {', '.join(titles[:3])}...")
    
    if snippets:
        # Combine snippets for overview
        all_text = " ".join(snippets)
        if len(all_text) > 300:
            all_text = all_text[:300] + "..."
        summary_parts.append(f"Content overview: {all_text}")
    
    return " ".join(summary_parts)


def create_simple_result(query: str, provider: str, raw_result: str) -> Dict:
    """Create a simple result structure when parsing fails."""
    
    return {
        "query": query,
        "provider": provider,
        "success": True,
        "total_results": 1,
        "results": [{
            "title": f"Search results for: {query}",
            "url": "",
            "snippet": raw_result[:500] + "..." if len(raw_result) > 500 else raw_result,
            "date": "",
            "source": f"{provider}_raw"
        }],
        "summary": f"Retrieved search results from {provider}",
        "raw_text": raw_result
    }


def extract_urls_from_text(text: str) -> List[str]:
    """Extract all URLs from text."""
    
    url_pattern = r'https?://[^\s<>"\'`]+'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    # Clean URLs
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation
        clean_url = re.sub(r'[.,;:!?\'">\]})]+$', '', url)
        if clean_url and clean_url not in cleaned_urls:
            cleaned_urls.append(clean_url)
    
    return cleaned_urls


def clean_text_content(text: str) -> str:
    """Clean and normalize text content."""
    
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common artifacts
    text = re.sub(r'\[.*?\]', '', text)  # Remove bracketed content
    text = re.sub(r'\(Advertisement\)', '', text, re.IGNORECASE)
    text = re.sub(r'Click here.*?(?=\.|$)', '', text, re.IGNORECASE)
    
    # Clean up remaining whitespace
    text = text.strip()
    
    return text


def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
    """Extract key phrases from text content."""
    
    if not text:
        return []
    
    # Simple phrase extraction based on common patterns
    phrases = []
    
    # Look for quoted phrases
    quoted_phrases = re.findall(r'"([^"]{10,50})"', text)
    phrases.extend(quoted_phrases)
    
    # Look for capitalized phrases (potential proper nouns)
    cap_phrases = re.findall(r'\b[A-Z][a-zA-Z\s]{5,30}(?=[.!?]|\b)', text)
    phrases.extend(cap_phrases)
    
    # Look for numbered/statistical information
    stat_phrases = re.findall(r'\b\d+(?:\.\d+)?%?\s+[a-zA-Z\s]{5,20}', text)
    phrases.extend(stat_phrases)
    
    # Remove duplicates and limit
    unique_phrases = list(set(phrases))[:max_phrases]
    
    return unique_phrases


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities from text (simple pattern-based approach)."""
    
    entities = {
        "dates": [],
        "numbers": [],
        "organizations": [],
        "locations": [],
        "people": []
    }
    
    if not text:
        return entities
    
    # Extract dates
    date_patterns = [
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities["dates"].extend(matches)
    
    # Extract numbers/statistics
    number_patterns = [
        r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:%|percent|million|billion|trillion)\b',
        r'\$\d+(?:,\d{3})*(?:\.\d{2})?\b'
    ]
    
    for pattern in number_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities["numbers"].extend(matches)
    
    # Extract potential organizations (words ending in Inc, Corp, LLC, etc.)
    org_pattern = r'\b[A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Organization|Association|Institute|Foundation)\b'
    entities["organizations"] = re.findall(org_pattern, text)
    
    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    return entities