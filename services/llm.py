from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
from helpers.model_management import get_llm_model
from helpers.response_parser import parse_llm_response, validate_item
from helpers.url_validator import validate_and_fix_image_urls, fill_missing_image_urls
from prompts import get_prompt_template
from search_tools import set_search_delay
from helpers.agent_management import create_search_agent

load_dotenv()
logger = logging.getLogger(__name__)


def create_backlog(
    category: str,
    model: str = "openai",
    num_items: int = 3,
    time_period: str = "all_time",
    use_search: bool = False,
    search_provider: str = "duckduckgo",
    validate_urls: bool = True,
    search_delay: float = 1.0,
    api_key: Optional[str] = None
) -> List[Dict]:
    """
    Create a backlog for top items in a specific category.
    
    Args:
        category: The category to create backlog for (e.g., "movies", "sports", "music", "games")
        model: LLM model to use ("openai", "groq", "google")
        num_items: Number of items to include in backlog (default: 3)
        time_period: "all_time" or decade like "2010s", "1990s" (default: "all_time")
        use_search: Whether to use browser search for current information
        search_provider: Search provider for image URLs ("duckduckgo", "google", "brave")
        validate_urls: Whether to validate image URLs and replace broken ones (default: True)
        search_delay: Delay between search requests in seconds (default: 1.0)
        api_key: Optional API key override
    
    Returns:
        List of dictionaries containing backlog items
    """
    
    # Set the search delay for rate limiting
    set_search_delay(search_delay)
    
    try:
        # Initialize LLM based on model parameter
        llm = get_llm_model(model, api_key)
        
        # Get category-specific prompt template
        prompt_template = get_prompt_template(category, num_items, time_period, use_search)
        
        # Generate response using appropriate method
        if use_search:
            response = _generate_with_search(llm, prompt_template, category, num_items, time_period)
        else:
            response = _generate_direct(llm, prompt_template)
        
        # Parse response and extract JSON
        backlog_items = parse_llm_response(response, num_items)
        
        # Handle image URLs
        if validate_urls:
            logger.info(f"Validating URLs with {search_delay}s delay between searches")
            backlog_items = validate_and_fix_image_urls(backlog_items, category, search_provider)
        else:
            backlog_items = fill_missing_image_urls(backlog_items, category, search_provider)
        
        logger.info(f"Created backlog for {category} ({time_period}) with {len(backlog_items)} items using {model}")
        return backlog_items
        
    except Exception as e:
        logger.error(f"Error creating backlog for {category}: {str(e)}")
        return []


def _generate_with_search(llm, prompt_template: str, category: str, num_items: int, time_period: str) -> str:
    """Generate response using search agent."""
    agent = create_search_agent(llm)
    
    time_text = "of all time" if time_period == "all_time" else f"from the {time_period}"
    search_prompt = f"""
    Search for the top {num_items} best {category} {time_text} and create a backlog.
    {prompt_template}
    """
    
    return agent.run(search_prompt)


def _generate_direct(llm, prompt_template: str) -> str:
    """Generate response using direct LLM call."""
    response = llm.invoke(prompt_template)
    return response.content if hasattr(response, 'content') else response


# Convenience functions
def create_movie_backlog(num_items: int = 3, time_period: str = "all_time", use_search: bool = False, 
                        validate_urls: bool = True, search_delay: float = 1.0) -> List[Dict]:
    """Create a movie backlog - convenience function."""
    return create_backlog("movies", "openai", num_items, time_period, use_search, 
                         "duckduckgo", validate_urls, search_delay)


def create_sports_backlog(num_items: int = 3, time_period: str = "all_time", use_search: bool = False, 
                         validate_urls: bool = True, search_delay: float = 1.0) -> List[Dict]:
    """Create a sports backlog - convenience function."""
    return create_backlog("sports", "openai", num_items, time_period, use_search, 
                         "duckduckgo", validate_urls, search_delay)


def create_music_backlog(num_items: int = 3, time_period: str = "all_time", use_search: bool = False, 
                        validate_urls: bool = True, search_delay: float = 1.0) -> List[Dict]:
    """Create a music backlog - convenience function."""
    return create_backlog("music", "openai", num_items, time_period, use_search, 
                         "duckduckgo", validate_urls, search_delay)


def create_game_backlog(num_items: int = 3, time_period: str = "all_time", use_search: bool = False, 
                       validate_urls: bool = True, search_delay: float = 1.0) -> List[Dict]:
    """Create a game backlog - convenience function."""
    return create_backlog("games", "openai", num_items, time_period, use_search, 
                         "duckduckgo", validate_urls, search_delay)