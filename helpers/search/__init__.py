"""
Search helpers module for common utilities and helper functions.
"""

from .search_utils import (
    apply_rate_limit,
    set_unified_search_delay,
    get_unified_search_delay,
    validate_url,
    clean_search_query,
    extract_domain_from_url
)

from .text_parsing import (
    extract_structured_results_from_text,
    create_search_summary,
    create_simple_result,
    extract_urls_from_text,
    clean_text_content
)

from .image_utils import (
    optimize_image_query,
    extract_multiple_image_urls_from_text,
    is_valid_image_url,
    get_google_image_size_param,
    validate_image_indicators
)

from .scraper_utils import (
    extract_clean_text_from_markdown,
    extract_structured_data_from_page,
    generate_content_summary,
    generate_website_summary,
    create_scraper_error_result
)

__all__ = [
    # General utilities
    "apply_rate_limit",
    "set_unified_search_delay", 
    "get_unified_search_delay",
    "validate_url",
    "clean_search_query",
    "extract_domain_from_url",
    
    # Text parsing
    "extract_structured_results_from_text",
    "create_search_summary",
    "create_simple_result", 
    "extract_urls_from_text",
    "clean_text_content",
    
    # Image utilities
    "optimize_image_query",
    "extract_multiple_image_urls_from_text",
    "is_valid_image_url",
    "get_google_image_size_param",
    "validate_image_indicators",
    
    # Scraper utilities
    "extract_clean_text_from_markdown",
    "extract_structured_data_from_page",
    "generate_content_summary",
    "generate_website_summary",
    "create_scraper_error_result"
]