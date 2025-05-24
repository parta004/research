from typing import List, Dict, Any, Optional
import json
from abc import ABC, abstractmethod
from langchain.agents.agent import AgentExecutor
from models.models import Statement, StatementType  
from langchain.tools import Tool

from agents.factcheck.ag_conspirator import ConspiratorAgent
from agents.factcheck.ag_fact_db import FactCheckDatabaseAgent
from agents.factcheck.ag_joe import SimpleJoeAgent
from agents.factcheck.ag_nerd import NerdAgent


class EvaluationAgent(ABC):
    """Base class for evaluation agents"""

    def __init__(self, llm, tools: List[Tool] = None):
        self.llm = llm
        self.tools = tools or []
        self.agent = self._create_agent()

    @abstractmethod
    def _create_agent(self):
        """Create the agent with specific prompt and tools"""
        pass

    @abstractmethod
    def evaluate(self, statement: Statement, context: str = "") -> Dict[str, Any]:
        """Evaluate a statement and return perspective"""
        pass


    def evaluate(self, statement: Statement, context: str = "") -> Dict[str, Any]:
        executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=True)

        input_text = f"""
        Statement: "{statement.text}"
        Speaker: {statement.speaker.name}
        
        Explain what this really means in simple terms.
        How would this affect regular people?
        Break it down like you're explaining to a friend.
        """

        result = executor.invoke({"input": input_text})

        return {
            "agent": "SimpleJoe",
            "perspective": "Common Sense Explanation",
            "analysis": result["output"],
            "confidence": 0.8,
            "target_audience": "General public"
        }




class MultiPerspectiveEvaluator:
    """Orchestrates multiple agents for comprehensive evaluation"""

    def __init__(self, llm):
        self.agents = {
            "fact_checker": FactCheckDatabaseAgent(llm),
            "conspirator": ConspiratorAgent(llm),
            "simple_joe": SimpleJoeAgent(llm),
            "nerd": NerdAgent(llm)
        }
        self.synthesis_llm = llm

    def evaluate_statement(self, statement: Statement, context: str = "",
                           agents_to_use: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get multiple perspectives on a statement"""

        if agents_to_use is None:
            agents_to_use = list(self.agents.keys())

        perspectives = {}

        # Gather perspectives from each agent
        for agent_name in agents_to_use:
            if agent_name in self.agents:
                try:
                    perspective = self.agents[agent_name].evaluate(
                        statement, context)
                    perspectives[agent_name] = perspective
                except Exception as e:
                    perspectives[agent_name] = {
                        "agent": agent_name,
                        "error": str(e),
                        "analysis": "Error during analysis"
                    }

        # Synthesize findings
        synthesis = self._synthesize_perspectives(statement, perspectives)

        return {
            "statement": statement.text,
            "perspectives": perspectives,
            "synthesis": synthesis,
            "consensus_level": self._calculate_consensus(perspectives)
        }

    def _synthesize_perspectives(self, statement: Statement,
                                 perspectives: Dict[str, Dict]) -> Dict[str, Any]:
        """Synthesize multiple perspectives into a coherent summary"""

        synthesis_prompt = f"""
        Statement: "{statement.text}"
        
        Multiple agents have analyzed this statement:
        
        {json.dumps(perspectives, indent=2)}
        
        Synthesize these perspectives:
        1. What do they agree on?
        2. Where do they diverge?
        3. What's the most likely truth?
        4. What context is crucial?
        5. Overall assessment?
        
        Provide a balanced synthesis.
        """

        response = self.synthesis_llm.invoke(synthesis_prompt)

        # Determine overall verdict based on synthesis
        verdict = self._determine_verdict(response.content)

        return {
            "summary": response.content,
            "verdict": verdict,
            "confidence": self._calculate_synthesis_confidence(perspectives),
            "key_disagreements": self._extract_disagreements(perspectives),
            "action_items": self._generate_action_items(statement, perspectives)
        }

    def _determine_verdict(self, synthesis: str) -> StatementType:
        """Determine overall verdict from synthesis"""
        synthesis_lower = synthesis.lower()

        if "mostly true" in synthesis_lower or "largely accurate" in synthesis_lower:
            return StatementType.TRUTH
        elif "selective" in synthesis_lower or "cherry-pick" in synthesis_lower:
            return StatementType.SELECTIVE_TRUTH
        elif "false" in synthesis_lower or "incorrect" in synthesis_lower:
            return StatementType.LIE
        else:
            return StatementType.UNVERIFIABLE

    def _calculate_consensus(self, perspectives: Dict[str, Dict]) -> float:
        """Calculate consensus level among agents"""
        if len(perspectives) < 2:
            return 1.0

        # Simple consensus based on sentiment alignment
        sentiments = []
        for p in perspectives.values():
            if "error" not in p:
                analysis = p.get("analysis", "").lower()
                if "true" in analysis or "accurate" in analysis:
                    sentiments.append(1)
                elif "false" in analysis or "incorrect" in analysis:
                    sentiments.append(-1)
                else:
                    sentiments.append(0)

        if not sentiments:
            return 0.5

        # Calculate variance as inverse of consensus
        mean_sentiment = sum(sentiments) / len(sentiments)
        variance = sum((s - mean_sentiment) **
                       2 for s in sentiments) / len(sentiments)

        # Convert to 0-1 scale (0 = no consensus, 1 = full consensus)
        # Normalize by max possible variance
        consensus = 1 - min(variance / 4, 1)

        return round(consensus, 2)

    def _calculate_synthesis_confidence(self, perspectives: Dict[str, Dict]) -> float:
        """Calculate confidence in synthesis based on agent agreements"""
        confidences = [p.get("confidence", 0.5)
                       for p in perspectives.values() if "error" not in p]

        if not confidences:
            return 0.5

        # Weight by consensus
        avg_confidence = sum(confidences) / len(confidences)
        consensus = self._calculate_consensus(perspectives)

        # High consensus increases confidence, low consensus decreases it
        weighted_confidence = avg_confidence * (0.5 + 0.5 * consensus)

        return round(weighted_confidence, 2)

    def _extract_disagreements(self, perspectives: Dict[str, Dict]) -> List[str]:
        """Extract key points of disagreement between agents"""
        disagreements = []

        # Compare fact checker vs conspirator
        if "fact_checker" in perspectives and "conspirator" in perspectives:
            if "accurate" in perspectives["fact_checker"].get("analysis", "").lower() and \
               "manipulat" in perspectives["conspirator"].get("analysis", "").lower():
                disagreements.append(
                    "Fact-checker finds claim accurate, but Conspirator sees manipulation")

        # Compare nerd vs simple joe
        if "nerd" in perspectives and "simple_joe" in perspectives:
            if "statistical" in perspectives["nerd"].get("analysis", "").lower() and \
               "doesn't make sense" in perspectives["simple_joe"].get("analysis", "").lower():
                disagreements.append(
                    "Data supports claim but common sense interpretation differs")

        return disagreements

    def _generate_action_items(self, statement: Statement, perspectives: Dict[str, Dict]) -> List[str]:
        """Generate action items for further verification"""
        actions = []

        for agent_name, perspective in perspectives.items():
            if "error" not in perspective:
                analysis = perspective.get("analysis", "")

                if "verify" in analysis.lower():
                    actions.append(
                        f"Verify claims as suggested by {agent_name}")

                if "context" in analysis.lower() and "missing" in analysis.lower():
                    actions.append(
                        "Obtain missing context for complete evaluation")

                if "source" in analysis.lower() and "primary" in analysis.lower():
                    actions.append("Access primary sources for verification")

        return list(set(actions))[:3]  # Return top 3 unique actions


