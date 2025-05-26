import time
import json
import logging
from typing import Dict, List
from services.llm import create_backlog

logger = logging.getLogger(__name__)


def test_llm_performance(
    category: str = "movies",
    num_items: int = 2,
    time_period: str = "all_time",
    search_provider: str = "duckduckgo",
    models: List[str] = None
) -> Dict:
    """
    Test multiple LLMs and measure their performance.
    
    Args:
        category: Category to test
        num_items: Number of items to generate
        time_period: Time period filter
        search_provider: Search provider for images
        models: List of models to test (default: all available)
    
    Returns:
        Dictionary containing test results
    """
    
    if models is None:
        models = ["openai", "groq", "google"]
    
    print("=== LLM PERFORMANCE TEST ===")
    print(f"Testing: Top {num_items} {category.title()} {time_period.replace('_', ' ').title()}")
    print(f"Search Provider: {search_provider}")
    print("-" * 60)
    
    results = {}
    
    for model in models:
        print(f"\nTesting {model.upper()}...")
        
        start_time = time.time()
        try:
            result = create_backlog(
                category=category,
                model=model,
                num_items=num_items,
                time_period=time_period,
                use_search=False,
                search_provider=search_provider,
                validate_urls=True,
                search_delay=1.0
            )
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            results[model] = {
                "response_time": response_time,
                "result": result,
                "success": True,
                "items_count": len(result)
            }
            
            print(f"✅ {model.upper()} completed in {response_time}s")
            
        except Exception as e:
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            results[model] = {
                "response_time": response_time,
                "result": [],
                "success": False,
                "error": str(e),
                "items_count": 0
            }
            
            print(f"❌ {model.upper()} failed in {response_time}s: {e}")
    
    _print_detailed_results(results)
    _print_performance_summary(results)
    
    return results


def _print_detailed_results(results: Dict):
    """Print detailed test results."""
    print("\n" + "=" * 60)
    print("DETAILED RESULTS")
    print("=" * 60)
    
    for model, data in results.items():
        print(f"\n{model.upper()} RESULTS:")
        print(f"Response Time: {data['response_time']}s")
        print(f"Success: {data['success']}")
        
        if data['success']:
            print(f"Items Returned: {data['items_count']}")
            
            # Show URL validation status
            if data['result']:
                url_stats = {}
                for item in data['result']:
                    status = item.get('url_status', 'unknown')
                    url_stats[status] = url_stats.get(status, 0) + 1
                print(f"URL Status: {url_stats}")
            
            print("Response:")
            print(json.dumps(data['result'], indent=2))
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
        
        print("-" * 30)


def _print_performance_summary(results: Dict):
    """Print performance summary."""
    print("\nPERFORMANCE SUMMARY:")
    successful_models = [model for model, data in results.items() if data['success']]
    
    if successful_models:
        fastest = min(successful_models, key=lambda m: results[m]['response_time'])
        print(f"Fastest: {fastest.upper()} ({results[fastest]['response_time']}s)")
        
        avg_time = sum(results[m]['response_time'] for m in successful_models) / len(successful_models)
        print(f"Average time: {round(avg_time, 2)}s")
        
        # Items analysis
        total_items = sum(results[m]['items_count'] for m in successful_models)
        avg_items = total_items / len(successful_models) if successful_models else 0
        print(f"Average items per model: {round(avg_items, 1)}")
    else:
        print("No successful runs to analyze")


def test_category_comparison(categories: List[str] = None, model: str = "openai") -> Dict:
    """
    Test performance across different categories.
    
    Args:
        categories: List of categories to test
        model: Model to use for testing
    
    Returns:
        Dictionary containing category comparison results
    """
    
    if categories is None:
        categories = ["movies", "music", "games", "sports"]
    
    print(f"=== CATEGORY COMPARISON TEST ({model.upper()}) ===")
    print("-" * 50)
    
    results = {}
    
    for category in categories:
        print(f"\nTesting {category}...")
        start_time = time.time()
        
        try:
            result = create_backlog(category, model, 2, "all_time", False, "duckduckgo", True, 1.0)
            end_time = time.time()
            
            results[category] = {
                "response_time": round(end_time - start_time, 2),
                "items_count": len(result),
                "success": True
            }
            
        except Exception as e:
            results[category] = {
                "response_time": round(time.time() - start_time, 2),
                "items_count": 0,
                "success": False,
                "error": str(e)
            }
    
    # Print results
    print("\nCATEGORY PERFORMANCE:")
    for category, data in results.items():
        status = "✅" if data['success'] else "❌"
        print(f"{status} {category.title()}: {data['response_time']}s ({data['items_count']} items)")
    
    return results


if __name__ == "__main__":
    # Run default performance test
    test_llm_performance()
    
    # Uncomment to run category comparison
    # test_category_comparison()