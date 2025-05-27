import logging
from typing import Dict, Any
from schemas.fc_schemas import AgentAnalysis

logger = logging.getLogger(__name__)


def create_safe_agent_analysis(response_data: Dict[str, Any], agent_name: str) -> AgentAnalysis:
    """
    Safely create an AgentAnalysis object from response data.
    
    Args:
        response_data: Dictionary containing response data
        agent_name: Name of the agent
    
    Returns:
        AgentAnalysis object
    """
    try:
        # Ensure we have a proper dictionary
        if not isinstance(response_data, dict):
            logger.error(f"Response data is not a dict: {type(response_data)}")
            return create_error_analysis(agent_name, "Invalid response format")
        
        # Create a copy to avoid reference issues
        data = dict(response_data)
        
        # Validate required fields and provide defaults
        analysis = AgentAnalysis(
            agent_name=data.get('agent_name', agent_name),
            perspective=data.get('perspective', f"{agent_name} analysis"),
            analysis=data.get('analysis', "Analysis not provided"),
            confidence_score=float(data.get('confidence_score', 0.0)),
            key_findings=data.get('key_findings', []),
            supporting_evidence=data.get('supporting_evidence', []),
            verdict=data.get('verdict', 'UNVERIFIABLE'),
            reasoning=data.get('reasoning', "Reasoning not provided")
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error creating AgentAnalysis: {e}")
        return create_error_analysis(agent_name, str(e))


def create_error_analysis(agent_name: str, error_message: str) -> AgentAnalysis:
    """Create an error analysis when the agent fails"""
    return AgentAnalysis(
        agent_name=agent_name,
        perspective=f"Error in {agent_name} analysis",
        analysis=f"Analysis failed due to error: {error_message}",
        confidence_score=0.0,
        key_findings=[f"Agent {agent_name} encountered an error"],
        supporting_evidence=[],
        verdict="UNVERIFIABLE",
        reasoning=f"Error occurred during analysis: {error_message}"
    )