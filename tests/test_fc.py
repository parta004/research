import sys
import os
from pathlib import Path
import logging
current_dir = Path(__file__).parent
research_service_dir = current_dir.parent
sys.path.insert(0, str(research_service_dir))
import time
# Now import from services
from services.fc import fact_check_statement, create_fact_checker
from schemas.fc_schemas import FactCheckConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    print(f"Context: {result.context}")
    print(f"Overall Verdict: {result.overall_verdict}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Number of Agent Analyses: {len(result.agent_analyses)}")
    print(f"Number of Sources: {len(result.sources)}")
    
    print("\n" + "="*80)
    print("WEB RESEARCH SUMMARY:")
    print("="*80)
    print(result.web_research_summary)
    
    print("\n" + "="*80)
    print("DETAILED AGENT ANALYSES:")
    print("="*80)
    
    for i, analysis in enumerate(result.agent_analyses, 1):
        print(f"\n{'-'*60}")
        print(f"AGENT {i}: {analysis.agent_name.upper()}")
        print(f"{'-'*60}")
        
        print(f"🎯 VERDICT: {analysis.verdict}")
        print(f"📊 CONFIDENCE: {analysis.confidence_score:.2f}")
        print(f"👁️  PERSPECTIVE: {analysis.perspective}")
        
        print(f"\n📝 ANALYSIS:")
        print(f"{analysis.analysis}")
        
        print(f"\n🔍 KEY FINDINGS:")
        for j, finding in enumerate(analysis.key_findings, 1):
            print(f"  {j}. {finding}")
        
        print(f"\n🧠 REASONING:")
        print(f"{analysis.reasoning}")
        
        if analysis.supporting_evidence:
            print(f"\n📚 SUPPORTING EVIDENCE:")
            for j, evidence in enumerate(analysis.supporting_evidence, 1):
                source = evidence.get('source', 'Unknown source')
                excerpt = evidence.get('excerpt', 'No excerpt provided')
                # Truncate long excerpts for readability
                if len(excerpt) > 200:
                    excerpt = excerpt[:200] + "..."
                print(f"  {j}. Source: {source}")
                print(f"     Excerpt: {excerpt}")
        else:
            print(f"\n📚 SUPPORTING EVIDENCE: None provided")
    
    print("\n" + "="*80)
    print("RESEARCH SOURCES:")
    print("="*80)
    
    if result.sources:
        for i, source in enumerate(result.sources, 1):
            source_type = source.get('type', 'Unknown')
            excerpt = source.get('excerpt', 'No excerpt available')
            print(f"{i}. [{source_type.upper()}] {excerpt}")
    else:
        print("No sources available")
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print(f"Final Assessment: {result.overall_verdict} (Confidence: {result.confidence:.1%})")
    
    # Calculate agent agreement
    verdicts = [analysis.verdict for analysis in result.agent_analyses]
    verdict_counts = {}
    for verdict in verdicts:
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
    
    print(f"Agent Consensus:")
    for verdict, count in verdict_counts.items():
        percentage = (count / len(verdicts)) * 100
        print(f"  {verdict}: {count}/{len(verdicts)} agents ({percentage:.1f}%)")
    
    avg_confidence = sum(a.confidence_score for a in result.agent_analyses) / len(result.agent_analyses)
    print(f"Average Agent Confidence: {avg_confidence:.1%}")
    
    return result

# Statement: The unemployment rate has never been lower in our country's history
# Speaker: Political Candidate X
# Overall Verdict: MISLEADING
# Confidence: 0.82
# Agent Analyses: 4
#   conspirator: MISLEADING (confidence: 0.85)
#   nerd: MISLEADING (confidence: 0.85)
#   joe: MISLEADING (confidence: 0.80)
#   factchecker: MISLEADING (confidence: 0.80)


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
    models = ["groq"] 
    # models = ["openai", "groq", "google"]
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
    
    providers = ["duckduckgo", "google", "brave"] 
    
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
    # test_search_providers()
    
    # Agent performance
    # test_agent_performance()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
    
    return {
        "basic_result": basic_result,
        "model_results": model_results
    }


if __name__ == "__main__":
    run_comprehensive_test()