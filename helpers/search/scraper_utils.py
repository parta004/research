import re
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def extract_clean_text_from_markdown(markdown: str) -> str:
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


def extract_structured_data_from_page(page_data: Dict) -> Dict:
    """Extract structured data from page."""
    
    structured = {}
    metadata = page_data.get("metadata", {})
    
    # Extract common structured elements
    structured["title"] = metadata.get("title", "")
    structured["description"] = metadata.get("description", "")
    structured["keywords"] = metadata.get("keywords", "")
    structured["author"] = metadata.get("author", "")
    structured["language"] = metadata.get("language", "")
    
    # Extract Open Graph data
    structured["og_data"] = {
        "title": metadata.get("ogTitle", ""),
        "description": metadata.get("ogDescription", ""),
        "image": metadata.get("ogImage", ""),
        "url": metadata.get("ogUrl", ""),
        "type": metadata.get("ogType", ""),
        "site_name": metadata.get("ogSiteName", "")
    }
    
    # Extract dates if available
    if "publishedTime" in metadata:
        structured["published_date"] = metadata["publishedTime"]
    if "modifiedTime" in metadata:
        structured["modified_date"] = metadata["modifiedTime"]
    
    # Extract additional metadata
    structured["canonical_url"] = metadata.get("canonicalUrl", "")
    structured["robots"] = metadata.get("robots", "")
    structured["viewport"] = metadata.get("viewport", "")
    
    return structured


def generate_content_summary(content: Dict) -> str:
    """Generate a summary of the scraped content."""
    
    text = content.get("text", "")
    if not text:
        return "No content available"
    
    word_count = len(text.split())
    char_count = len(text)
    
    # Extract first meaningful paragraph as preview
    preview = _extract_content_preview(text)
    
    # Calculate reading time (average 200 words per minute)
    reading_time = max(1, word_count // 200)
    
    return (f"Content summary: {word_count} words, {char_count} characters, "
            f"~{reading_time} min read. Preview: {preview}")


def _extract_content_preview(text: str, max_length: int = 200) -> str:
    """Extract a meaningful preview from text content."""
    
    lines = text.split('\n')
    preview = ""
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 50:  # Find substantial content
            preview = line[:max_length]
            if len(line) > max_length:
                # Try to break at word boundary
                last_space = preview.rfind(' ')
                if last_space > max_length * 0.7:  # If we can break reasonably close
                    preview = preview[:last_space]
                preview += "..."
            break
    
    return preview or "No preview available"


def generate_website_summary(pages: List[Dict]) -> str:
    """Generate a summary of the crawled website."""
    
    if not pages:
        return "No pages crawled"
    
    total_pages = len(pages)
    total_words = sum(page.get("word_count", 0) for page in pages)
    
    # Get unique titles
    titles = [page.get("title", "") for page in pages if page.get("title")]
    unique_titles = list(set(titles))
    
    # Calculate average page length
    avg_words = total_words // total_pages if total_pages > 0 else 0
    
    # Identify main topics (simple approach based on titles)
    main_topics = _extract_main_topics(unique_titles)
    
    summary_parts = [
        f"Website crawl summary: {total_pages} pages",
        f"{total_words} total words ({avg_words} avg per page)"
    ]
    
    if main_topics:
        summary_parts.append(f"Main topics: {', '.join(main_topics[:3])}")
    
    if unique_titles:
        title_preview = ', '.join(unique_titles[:5])
        if len(unique_titles) > 5:
            title_preview += "..."
        summary_parts.append(f"Page titles: {title_preview}")
    
    return ". ".join(summary_parts)


def _extract_main_topics(titles: List[str]) -> List[str]:
    """Extract main topics from page titles."""
    
    if not titles:
        return []
    
    # Simple word frequency analysis
    word_freq = {}
    
    for title in titles:
        # Extract meaningful words (skip common words)
        words = re.findall(r'\b[A-Za-z]{3,}\b', title.lower())
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return most frequent words as topics
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:5] if freq > 1]


def create_scraper_error_result(url: str, error_message: str) -> Dict:
    """Create an error result structure for scraping failures."""
    
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


def validate_scraped_content(content: Dict) -> bool:
    """Validate that scraped content is meaningful."""
    
    if not content:
        return False
    
    text = content.get("text", "")
    markdown = content.get("markdown", "")
    
    # Check if we have substantial content
    min_content_length = 100
    
    if len(text) < min_content_length and len(markdown) < min_content_length:
        return False
    
    # Check for error indicators in content
    error_indicators = [
        "access denied", "forbidden", "not found", "error 404",
        "page not available", "temporarily unavailable"
    ]
    
    text_lower = text.lower()
    if any(indicator in text_lower for indicator in error_indicators):
        return False
    
    return True


def extract_metadata_summary(metadata: Dict) -> str:
    """Create a readable summary of page metadata."""
    
    if not metadata:
        return "No metadata available"
    
    summary_parts = []
    
    if metadata.get("title"):
        summary_parts.append(f"Title: {metadata['title']}")
    
    if metadata.get("description"):
        desc = metadata["description"][:100] + "..." if len(metadata["description"]) > 100 else metadata["description"]
        summary_parts.append(f"Description: {desc}")
    
    if metadata.get("author"):
        summary_parts.append(f"Author: {metadata['author']}")
    
    if metadata.get("publishedTime"):
        summary_parts.append(f"Published: {metadata['publishedTime']}")
    
    if metadata.get("language"):
        summary_parts.append(f"Language: {metadata['language']}")
    
    return "; ".join(summary_parts) if summary_parts else "Basic metadata available"