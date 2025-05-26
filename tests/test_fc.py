import json
import time
from typing import Dict, List

from fact_checker import fact_check_statement, create_fact_checker
from fc_schemas import FactCheckConfig


def test_basic_fact_check():
    """Test basic fact-checking functionality"""
    
    print("=== BASIC FACT-CHECK TEST ===")
    
    # Test statement
    result = fact_check_statement(
        statement="The unemployment rate has never been lower in our country's history",
        speaker="Political Candidate X",
        background={
            "where": "Campaign rally in Ohio",
            "when": "November 2024"
        }
    )
    
    print(f"Statement: {result.statement}")
    print(f"Speaker: {result.speaker}")
    print(f"Overall Verdict: {result.overall_verdict}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Agent Analyses: {len(result.agent_analyses)}")
    
    # Print each agent's verdict
    for analysis in result.agent_analyses:
        print(f"  {analysis.agent_name}: {analysis.verdict} (confidence: {analysis.confidence_score:.2f})")
    
    return result


def test_multiple_models():
    """Test fact-checking with different LLM models"""
    
    print("\n=== MULTI-MODEL FACT-CHECK TEST ===")
    
    test_statement = {
        "statement": "Climate change is a hoax created by scientists to get funding",
        "speaker": "Climate Skeptic",
        "background": {
            "where": "Social media post",
            "when": "December 2024"
        }
    }
    
    models = ["openai", "groq", "google"]
    results = {}
    
    for model in models:
        print(f"\nTesting with {model.upper()}...")
        start_time = time.time()
        
        try:
            fact_checker = create_fact_checker(model_name=model)
            result = fact_checker.fact_check_statement(**test_statement)
            
            end_time = time.time()
            
            results[model] = {
                "verdict": result.overall_verdict,
                "confidence": result.confidence,
                "time": round(end_time - start_time, 2),
                "success": True,
                "agent_count": len(result.agent_analyses)
            }
            
            print(f"✅ {model.upper()}: {result.overall_verdict} (confidence: {result.confidence:.2f}, time: {results[model]['time']}s)")
            
        except Exception as e:
            end_time = time.time()
            results[model] = {
                "error": str(e),
                "time": round(end_time - start_time, 2),
                "success": False
            }
            print(f"❌ {model.upper()}: Failed - {e}")
    
    return results


def test_search_providers():
    """Test fact-checking with different search providers"""
    
    print("\n=== SEARCH PROVIDER TEST ===")
    
    test_statement = {
        "statement": "The latest inflation rate is 3.2%",
        "speaker": "Economic Analyst",
        "background": {
            "where": "Economic conference",
            "when": "January 2025"
        }
    }
    
    providers = ["duckduckgo", "google"]  # Add "brave" if you have API key
    
    for provider in providers:
        print(f"\nTesting with {provider.upper()} search...")
        start_time = time.time()
        
        try:
            config = FactCheckConfig(search_provider=provider)
            result = fact_check_statement(**test_statement, config=config)
            
            end_time = time.time()
            
            print(f"✅ {provider.upper()}: {result.overall_verdict} (confidence: {result.confidence:.2f})")
            print(f"   Sources found: {len(result.sources)}")
            print(f"   Time: {round(end_time - start_time, 2)}s")
            
        except Exception as e:
            print(f"❌ {provider.upper()}: Failed - {e}")


def test_agent_performance():
    """Test individual agent performance and consistency"""
    
    print("\n=== AGENT PERFORMANCE TEST ===")
    
    test_statements = [
        {
            "statement": "Vaccines cause autism",
            "speaker": "Anti-vaccine activist",
            "background": {"where": "Online forum", "when": "2024"}
        },
        {
            "statement": "The 2020 election was stolen",
            "speaker": "Political figure",
            "background": {"where": "Rally", "when": "2024"}
        },
        {
            "statement": "Solar energy is now cheaper than fossil fuels",
            "speaker": "Energy expert",
            "background": {"where": "Conference", "when": "2024"}
        }
    ]
    
    agent_performance = {}
    
    for i, test in enumerate(test_statements, 1):
        print(f"\nTest {i}: {test['statement'][:50]}...")
        
        result = fact_check_statement(**test)
        
        for analysis in result.agent_analyses:
            agent_name = analysis.agent_name
            if agent_name not in agent_performance:
                agent_performance[agent_name] = []
            
            agent_performance[agent_name].append({
                "verdict": analysis.verdict,
                "confidence": analysis.confidence_score,
                "test": i
            })
    
    # Print agent summary
    print("\nAGENT PERFORMANCE SUMMARY:")
    for agent_name, performances in agent_performance.items():
        avg_confidence = sum(p["confidence"] for p in performances) / len(performances)
        verdicts = [p["verdict"] for p in performances]
        print(f"{agent_name.upper()}:")
        print(f"  Average confidence: {avg_confidence:.2f}")
        print(f"  Verdicts: {verdicts}")


def run_comprehensive_test():
    """Run all tests"""
    
    print("=" * 60)
    print("COMPREHENSIVE FACT-CHECKER TEST SUITE")
    print("=" * 60)
    
    # Basic test
    basic_result = test_basic_fact_check()
    
    # Model comparison
    model_results = test_multiple_models()
    
    # Search provider test
    test_search_providers()
    
    # Agent performance
    test_agent_performance()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
    
    return {
        "basic_result": basic_result,
        "model_results": model_results
    }


if __name__ == "__main__":
    run_comprehensive_test()