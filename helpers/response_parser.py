import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def parse_llm_response(response: str, num_items: int) -> List[Dict]:
    """
    Parse the LLM response and extract valid JSON.
    
    Args:
        response: Raw LLM response string
        num_items: Maximum number of items to return
    
    Returns:
        List of validated dictionary items
    """
    
    try:
        response_str = str(response).strip()
        
        # Find JSON array in response
        start_idx = response_str.find('[')
        end_idx = response_str.rfind(']')
        
        if start_idx == -1 or end_idx == -1:
            logger.error("No JSON array found in response")
            return []
        
        json_str = response_str[start_idx:end_idx + 1]
        result = json.loads(json_str)
        
        if isinstance(result, list):
            valid_items = []
            for item in result[:num_items]:
                if validate_item(item):
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


def validate_item(item: Dict) -> bool:
    """
    Validate that an item has required fields.
    
    Args:
        item: Dictionary item to validate
    
    Returns:
        True if item is valid, False otherwise
    """
    
    if not isinstance(item, dict):
        return False
    
    # Basic required fields that should be present in most responses
    required_fields = ['title', 'creator']
    
    for field in required_fields:
        if field not in item:
            return False
    
    return True


def extract_json_from_text(text: str) -> List[Dict]:
    """
    Extract JSON arrays from text that might contain additional content.
    
    Args:
        text: Text that may contain JSON
    
    Returns:
        List of extracted JSON objects
    """
    
    # Multiple patterns to find JSON arrays
    patterns = [
        r'\[[\s\S]*?\]',  # Basic array pattern
        r'```json\s*(\[[\s\S]*?\])\s*```',  # Markdown code blocks
        r'```\s*(\[[\s\S]*?\])\s*```',  # Generic code blocks
    ]
    
    for pattern in patterns:
        import re
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            try:
                if isinstance(match, tuple):
                    match = match[0]  # Extract from regex group
                result = json.loads(match)
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                continue
    
    return []