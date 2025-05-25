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
    - 'description': Brief description of why this is considered a top film (50-100 characters)
    - 'genre_tags': Array of 2-3 specific movie genre tags (e.g., ["Drama", "Crime", "Epic"])
    - 'priority': Integer from 1-{num_items} (1 = highest priority)
    - 'estimated_time': Runtime in hours and minutes (e.g., "2h 55m")
    - 'rating': IMDB or critical consensus rating
    - 'awards': Notable awards won (if any)
    
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "The Godfather",
        "creator": "Francis Ford Coppola",
        "year": 1972,
        "description": "Epic crime saga defining the gangster genre",
        "genre_tags": ["Crime Drama", "Epic", "Family Saga"],
        "priority": 1,
        "estimated_time": "2h 55m",
        "rating": "9.2/10",
        "awards": "3 Academy Awards including Best Picture"
      }}
    ]
    
    IMPORTANT: Focus on critically acclaimed and culturally significant films {time_text}. Ensure your response contains ONLY the JSON array.
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
    - 'title': Name of the event, game, or achievement
    - 'creator': Athlete(s) or team name
    - 'year': Year the event occurred
    - 'description': Brief description of why this is considered legendary (50-100 characters)
    - 'genre_tags': Array of 2-3 sport/category tags (e.g., ["Basketball", "Championship", "Comeback"])
    - 'priority': Integer from 1-{num_items} (1 = highest priority)
    - 'estimated_time': Viewing/reading time (e.g., "2 hours", "30 minutes")
    - 'sport': The specific sport involved
    - 'significance': What made this moment historically important
    
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "Michael Jordan's Last Shot - 1998 NBA Finals",
        "creator": "Michael Jordan",
        "year": 1998,
        "description": "Championship-winning shot cementing GOAT status",
        "genre_tags": ["Basketball", "Championship", "Clutch Performance"],
        "priority": 1,
        "estimated_time": "2 hours",
        "sport": "Basketball",
        "significance": "Sealed Jordan's 6th championship and retirement on top"
      }}
    ]
    
    IMPORTANT: Focus on legendary performances and moments that defined sports history {time_text}. Ensure your response contains ONLY the JSON array.
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
    - 'description': Brief description of why this is considered a classic (50-100 characters)
    - 'genre_tags': Array of 2-3 specific music genre tags (e.g., ["Rock", "Progressive", "Concept Album"])
    - 'priority': Integer from 1-{num_items} (1 = highest priority)
    - 'estimated_time': Album duration (e.g., "42 minutes", "1h 15m")
    - 'label': Record label
    - 'influence': Brief note on cultural/musical impact
    
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "The Dark Side of the Moon",
        "creator": "Pink Floyd",
        "year": 1973,
        "description": "Conceptual masterpiece exploring human experience",
        "genre_tags": ["Progressive Rock", "Concept Album", "Psychedelic"],
        "priority": 1,
        "estimated_time": "43 minutes",
        "label": "Harvest Records",
        "influence": "Redefined album production and conceptual storytelling"
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
    - 'description': Brief description of why this is considered a classic (50-100 characters)
    - 'genre_tags': Array of 2-3 specific game genre tags (e.g., ["RPG", "Open World", "Story-Driven"])
    - 'priority': Integer from 1-{num_items} (1 = highest priority)
    - 'estimated_time': Approximate completion time (e.g., "40 hours", "15-20 hours")
    - 'platform': Original or primary platform
    - 'innovation': What gameplay or technical innovation it introduced
    
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "The Legend of Zelda: Ocarina of Time",
        "creator": "Nintendo EAD",
        "year": 1998,
        "description": "3D adventure that revolutionized game design",
        "genre_tags": ["Action-Adventure", "3D Platformer", "Fantasy"],
        "priority": 1,
        "estimated_time": "25-30 hours",
        "platform": "Nintendo 64",
        "innovation": "Z-targeting system and seamless 3D world exploration"
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
    - 'year': Release/publication year
    - 'description': Brief description of why this is considered top-tier (50-100 characters)
    - 'genre_tags': Array of 2-3 specific sub-category tags
    - 'priority': Integer from 1-{num_items} (1 = highest priority)
    - 'estimated_time': Estimated time to complete/consume (e.g., "2 hours", "300 pages")
    
    EXAMPLE RESPONSE FORMAT:
    [
      {{
        "title": "Example Title",
        "creator": "Example Creator",
        "year": 2000,
        "description": "Brief description of significance",
        "genre_tags": ["Tag1", "Tag2", "Tag3"],
        "priority": 1,
        "estimated_time": "2 hours"
      }}
    ]
    
    IMPORTANT: Focus on widely acclaimed and influential {category} {time_text}. Ensure your response contains ONLY the JSON array.
    """