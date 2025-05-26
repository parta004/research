def get_prompt_template(category: str, num_items: int, time_period: str = "all_time", use_search: bool = False) -> str:
    """
    Get the appropriate prompt template based on category and time period.
    
    Args:
        category: The category (movies, sports, music, games)
        num_items: Number of items to include
        time_period: "all_time" or specific decade like "2010s", "1990s", etc.
        use_search: Whether search will be used
    
    Returns:
        Formatted prompt template string
    """
    
    search_instruction = ""
    if use_search:
        search_instruction = "Use the search tool to find current and accurate information about the top items. "
    
    # Get category-specific template
    if category.lower() in ["movies", "films", "cinema"]:
        return _get_movies_prompt(num_items, time_period, search_instruction)
    elif category.lower() in ["sports", "athletes", "sporting"]:
        return _get_sports_prompt(num_items, time_period, search_instruction)
    elif category.lower() in ["music", "albums", "songs", "artists"]:
        return _get_music_prompt(num_items, time_period, search_instruction)
    elif category.lower() in ["games", "video games", "gaming"]:
        return _get_games_prompt(num_items, time_period, search_instruction)
    else:
        return _get_generic_prompt(category, num_items, time_period, search_instruction)


def _get_time_period_text(time_period: str) -> str:
    """Convert time period parameter to descriptive text."""
    if time_period == "all_time":
        return "of all time"
    elif time_period.endswith("s") and len(time_period) == 5:  # e.g., "2010s", "1990s"
        return f"from the {time_period}"
    else:
        return f"from {time_period}"


def _get_movies_prompt(num_items: int, time_period: str, search_instruction: str) -> str:
    """Generate prompt template for movies."""
    
    time_text = _get_time_period_text(time_period)
    
    return f"""
    {search_instruction}Create a backlog of the top {num_items} best movies {time_text}.
    
    TASK: Generate a curated list of {num_items} essential films that represent the highest quality and most influential cinema {time_text}.
    
    OUTPUT REQUIREMENTS:
    - Respond ONLY with a valid JSON array
    - Do NOT include any explanations, notes, or text outside the JSON structure
    - Each movie should be a separate object in the array
    - If you cannot generate items, return exactly '[]' without any additional text
    
    SCHEMA: Each movie object must include EXACTLY these fields:
    - 'title': The official title of the film
    - 'creator': Director name
    - 'year': Release year
    - 'group': 1 specific genre tag (e.g., "Drama", "Action", "Comedy") 
    - 'order': Integer from 1-{num_items} (1 = highest priority)
    - 'rating': IMDB or critical consensus rating
    - 'awards': Notable awards won (if any)
    - 'reference': Link to a relevant source or database entry (e.g., IMDB, Rotten Tomatoes)
    - 'image_url': URL to a relevant movie poster or still
    
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "The Godfather",
        "creator": "Francis Ford Coppola",
        "year": 1972,
        "group": "Drama",
        "order": 1,
        "rating": "9.2/10",
        "awards": "3 Academy Awards including Best Picture"
        "reference": "https://www.imdb.com/title/tt0068646/"
        "image_url": "https://example.com/godfather-poster.jpg"
      }}
    ]
    
    IMPORTANT: Use IMDB rating or critical consensus to determine quality {time_text}. Ensure your response contains ONLY the JSON array.
    """


def _get_sports_prompt(num_items: int, time_period: str, search_instruction: str) -> str:
    """Generate prompt template for sports."""
    
    time_text = _get_time_period_text(time_period)
    
    return f"""
    {search_instruction}Create a backlog of the top {num_items} greatest sports moments/achievements {time_text}.
    
    TASK: Generate a curated list of {num_items} essential sports events, performances, or achievements that represent the pinnacle of athletic excellence {time_text}.
    
    OUTPUT REQUIREMENTS:
    - Respond ONLY with a valid JSON array
    - Do NOT include any explanations, notes, or text outside the JSON structure
    - Each sports item should be a separate object in the array
    - If you cannot generate items, return exactly '[]' without any additional text
    
    SCHEMA: Each sports object must include EXACTLY these fields:
    - 'title': Name of the athlete
    - 'group': Major group/genre or team involved (if applicable)
    - 'priority': Integer from 1-{num_items} (1 = highest priority)
    - 'accolades': Array of maximum of 5 main accolades or awards (e.g., "MVP", "World Champion")
    - 'image_url': URL to a relevant image of the athlete or moment
    
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "Michael Jordan's Last Shot - 1998 NBA Finals",
        "creator": "Michael Jordan",
        "group": "Chicago Bulls",
        "priority": 1,
        "accolades": ["6x NBA Champion", "5x MVP", "10x All-Star"],
        "image_url": "https://example.com/jordan-last-shot.jpg"
      }}
    ]
    
    """


def _get_music_prompt(num_items: int, time_period: str, search_instruction: str) -> str:
    """Generate prompt template for music."""
    
    time_text = _get_time_period_text(time_period)
    
    return f"""
    {search_instruction}Create a backlog of the top {num_items} greatest albums {time_text}.
    
    TASK: Generate a curated list of {num_items} essential albums that represent the highest quality and most influential music {time_text}.
    
    OUTPUT REQUIREMENTS:
    - Respond ONLY with a valid JSON array
    - Do NOT include any explanations, notes, or text outside the JSON structure
    - Each album should be a separate object in the array
    - If you cannot generate items, return exactly '[]' without any additional text
    
    SCHEMA: Each album object must include EXACTLY these fields:
    - 'title': The official album title
    - 'creator': Artist or band name
    - 'year': Release year
    - 'group': One specifc genre tag (e.g., ["Rock", "Hip-Hop", "Jazz"])
    - 'order': Integer from 1-{num_items} (1 = highest priority)
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "The Dark Side of the Moon",
        "creator": "Pink Floyd",
        "year": 1973,
        "group": "Progressive Rock",
        "order": 1,
      }}
    ]
    
    IMPORTANT: Focus on critically acclaimed and culturally influential albums {time_text}. Ensure your response contains ONLY the JSON array.
    """


def _get_games_prompt(num_items: int, time_period: str, search_instruction: str) -> str:
    """Generate prompt template for video games."""
    
    time_text = _get_time_period_text(time_period)
    
    return f"""
    {search_instruction}Create a backlog of the top {num_items} greatest video games {time_text}.
    
    TASK: Generate a curated list of {num_items} essential video games that represent the highest quality and most influential gaming experiences {time_text}.
    
    OUTPUT REQUIREMENTS:
    - Respond ONLY with a valid JSON array
    - Do NOT include any explanations, notes, or text outside the JSON structure
    - Each game should be a separate object in the array
    - If you cannot generate items, return exactly '[]' without any additional text
    
    SCHEMA: Each game object must include EXACTLY these fields:
    - 'title': The official game title
    - 'creator': Developer/Studio name
    - 'year': Release year
    - 'group': One specific genre tag (e.g., ["Action-Adventure", "RPG", "Platformer"])
    - 'priority': Integer from 1-{num_items} (1 = highest priority) based on ranking from IGN
    - 'rating': IGN rating or critical consensus rating (e.g., "10/10", "4.5")
    - 'accolades': Array of accolades or awards (e.g., "Game of the Year", "Best Design")
    - 'image_url': URL to a relevant game cover or screenshot
        
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "The Legend of Zelda: Ocarina of Time",
        "creator": "Nintendo EAD",
        "year": 1998,
        "group": aRPG,
        "priority": 1,
        "accolades": ["GOTY"],
        "rating": "10/10",
        "image_url": "https://example.com/zelda-ocarina.jpg"
      }}
    ]
    
    IMPORTANT: Focus on games that pushed boundaries and influenced the medium {time_text}. Ensure your response contains ONLY the JSON array.
    """


def _get_generic_prompt(category: str, num_items: int, time_period: str, search_instruction: str) -> str:
    """Generate generic prompt template for unknown categories."""
    
    time_text = _get_time_period_text(time_period)
    
    return f"""
    {search_instruction}Create a backlog of the top {num_items} best {category} {time_text}.
    
    TASK: Generate a curated list of {num_items} essential {category} that represent the highest quality and most influential works in this field {time_text}.
    
    OUTPUT REQUIREMENTS:
    - Respond ONLY with a valid JSON array
    - Do NOT include any explanations, notes, or text outside the JSON structure
    - Each item should be a separate object in the array
    - If you cannot generate items, return exactly '[]' without any additional text
    
    SCHEMA: Each item object must include EXACTLY these fields:
    - 'title': The official title of the work
    - 'creator': Creator/Author/Developer/Artist name
    - 'description': Brief description of why this is considered top-tier (50-100 characters)
    - 'genre_tags': Array of 2-3 specific sub-category tags
    - 'priority': Integer from 1-{num_items} (1 = highest priority)
    
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "Example Title",
        "creator": "Example Creator",
        "description": "Brief description of significance",
        "genre_tags": ["Tag1", "Tag2", "Tag3"],
        "priority": 1,
      }}
    ]
    
    IMPORTANT: Focus on widely acclaimed and influential {category} {time_text}. Ensure your response contains ONLY the JSON array.
    """