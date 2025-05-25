from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
import logging
from typing import List, Dict, Optional
from .prompts import get_prompt_template

load_dotenv()

logger = logging.getLogger(__name__)

# API Keys
openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")


def create_backlog(
    category: str,
    model: str = "openai",
    num_items: int = 3,
    time_period: str = "all_time",
    use_search: bool = False,
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
        api_key: Optional API key override
    
    Returns:
        List of dictionaries containing backlog items
    """
    
    try:
        # Initialize LLM based on model parameter
        llm = _get_llm_model(model, api_key)
        
        # Setup tools
        tools = []
        if use_search:
            search = DuckDuckGoSearchRun()
            tools.append(search)
        
        # Get category-specific prompt template
        prompt_template = get_prompt_template(category, num_items, time_period, use_search)
        
        if use_search and tools:
            # Initialize agent with search capability
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
            
            time_text = "of all time" if time_period == "all_time" else f"from the {time_period}"
            search_prompt = f"""
            Search for the top {num_items} best {category} {time_text} and create a backlog.
            {prompt_template}
            """
            
            response = agent.run(search_prompt)
        else:
            # Direct LLM call without search
            response = llm.invoke(prompt_template)
            if hasattr(response, 'content'):
                response = response.content
        
        # Parse response and extract JSON
        backlog_items = _parse_response(response, num_items)
        
        logger.info(f"Successfully created backlog for {category} ({time_period}) with {len(backlog_items)} items")
        return backlog_items
        
    except Exception as e:
        logger.error(f"Error creating backlog for {category}: {str(e)}")
        return []


def _get_llm_model(model: str, api_key: Optional[str]):
    """Initialize and return the specified LLM model."""
    
    if model == "openai":
        return ChatOpenAI(
            api_key=api_key or openai_api_key,
            model="gpt-4o-mini",
            temperature=0.3
        )
    elif model == "groq":
        return ChatGroq(
            api_key=api_key or groq_api_key,
            model="llama-3.1-70b-versatile",
            temperature=0.3
        )
    elif model == "google":
        return ChatGoogleGenerativeAI(
            api_key=api_key or google_api_key,
            model="gemini-1.5-flash",
            temperature=0.3
        )
    else:
        logger.error(f"Unknown model: {model}")
        raise ValueError(f"Unsupported model: {model}")


def _parse_response(response: str, num_items: int) -> List[Dict]:
    """Parse the LLM response and extract valid JSON."""
    
    try:
        # Clean the response
        response = response.strip()
        
        # Find JSON array in response
        start_idx = response.find('[')
        end_idx = response.rfind(']')
        
        if start_idx == -1 or end_idx == -1:
            logger.error("No JSON array found in response")
            return []
        
        json_str = response[start_idx:end_idx + 1]
        
        # Parse JSON
        result = json.loads(json_str)
        
        if isinstance(result, list):
            # Validate and limit items
            valid_items = []
            for item in result[:num_items]:
                if _validate_item(item):
                    valid_items.append(item)
            
            return valid_items
        else:
            logger.error("Response is not a JSON array")
            return []
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
        return []


def _validate_item(item: Dict) -> bool:
    """Validate that an item has all required fields."""
    
    required_fields = ['title', 'creator', 'year', 'description', 'genre_tags', 'priority', 'estimated_time']
    
    if not isinstance(item, dict):
        return False
    
    for field in required_fields:
        if field not in item:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Additional validation
    if not isinstance(item['genre_tags'], list):
        return False
    
    if not isinstance(item['priority'], int):
        return False
    
    return True


# Convenience functions with time period support
def create_movie_backlog(num_items: int = 3, time_period: str = "all_time", use_search: bool = False) -> List[Dict]:
    """Create a movie backlog - convenience function."""
    return create_backlog("movies", "openai", num_items, time_period, use_search)


def create_sports_backlog(num_items: int = 3, time_period: str = "all_time", use_search: bool = False) -> List[Dict]:
    """Create a sports backlog - convenience function."""
    return create_backlog("sports", "openai", num_items, time_period, use_search)


def create_music_backlog(num_items: int = 3, time_period: str = "all_time", use_search: bool = False) -> List[Dict]:
    """Create a music backlog - convenience function."""
    return create_backlog("music", "openai", num_items, time_period, use_search)


def create_game_backlog(num_items: int = 3, time_period: str = "all_time", use_search: bool = False) -> List[Dict]:
    """Create a game backlog - convenience function."""
    return create_backlog("games", "openai", num_items, time_period, use_search)


if __name__ == "__main__":
    # Test the service
    print("Testing backlog service...")
    
    # Test different categories and time periods
    movies_all_time = create_backlog("movies", "openai", 3, "all_time", False)
    print(f"Movies (all time): {json.dumps(movies_all_time, indent=2)}")
    
    games_2010s = create_backlog("games", "groq", 3, "2010s", False)
    print(f"Games (2010s): {json.dumps(games_2010s, indent=2)}")
    
    music_1990s = create_backlog("music", "google", 3, "1990s", False)
    print(f"Music (1990s): {json.dumps(music_1990s, indent=2)}")
