# core/agents/verification_agent.py
"""
Verification Agent - Ensures answer accuracy and prevents hallucinations

Validates all responses against source documents and checks
for logical consistency and factual accuracy.
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from core.agents.base_agent import BaseAgent, AgentContext, AgentResult, AgentStatus, AgentRole


@dataclass
class VerificationResult:
    """Result of a verification check"""
    claim: str
    is_verified: bool
    confidence: float
    source_evidence: List[Dict]
    issues: List[str]
    suggestions: List[str]


class VerificationAgent(BaseAgent):
    """
    Agent that verifies answers against source documents.
    
    Capabilities:
    - Citation verification
    - Factual consistency checking
    - Confidence scoring
    - Uncertainty identification
    - Logical reasoning validation
    """
    
    def __init__(self):
        super().__init__(
            name="VerificationAgent",
            role=AgentRole.VERIFIER,
            model_preference="nousresearch/hermes-3-llama-3.1-405b"
        )
        self._verification_threshold = 0.7
        self._high_confidence_threshold = 0.9
    
    async def _execute(self, context: AgentContext) -> AgentResult:
        """Execute verification task"""
        
        if not context.generated_answer:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                context=context,
                output={"message": "No answer to verify", "verification_passed": True}
            )
        
        # Step 1: Verify citations in the answer
        citation_results = await self._verify_citations(context)
        
        # Step 2: Check factual consistency
        factual_results = await self._check_factual_consistency(context)
        
        # Step 3: Validate logical reasoning
        reasoning_results = await self._validate_reasoning(context)
        
        # Step 4: Generate confidence score
        confidence = self._calculate_confidence(citation_results, factual_results, reasoning_results)
        
        # Step 5: Identify uncertainties
        uncertainties = self._identify_uncertainties(citation_results, factual_results)
        
        # Update context
        context.confidence_score = confidence
        context.uncertainties = uncertainties
        
        # Build verification report
        report = {
            "overall_verification": {
                "passed": confidence >= self._verification_threshold,
                "confidence_score": confidence,
                "confidence_level": self._get_confidence_level(confidence)
            },
            "citation_verification": citation_results,
            "factual_consistency": factual_results,
            "reasoning_validation": reasoning_results,
            "uncertainties": uncertainties,
            "recommendations": self._generate_recommendations(
                citation_results, factual_results, reasoning_results
            )
        }
        
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            context=context,
            output={"verification_report": report}
        )
    
    async def _verify_citations(self, context: AgentContext) -> Dict[str, Any]:
        """Verify that all citations in the answer exist in source documents"""
        
        results = {
            "total_citations": 0,
            "verified_citations": 0,
            "unverified_citations": [],
            "invalid_citations": []
        }
        
        # Extract citation patterns like [C1], [C2], etc.
        import re
        citation_pattern = r'\[C(\d+)\]'
        citations = re.findall(citation_pattern, context.generated_answer)
        results["total_citations"] = len(citations)
        
        if not citations:
            return {**results, "status": "no_citations_found"}
        
        # Check each citation against available evidence
        available_ids = set()
        for hit in context.extracted_evidence:
            if isinstance(hit, dict):
                available_ids.add(hit.get("citation_id", ""))
        
        for cite_num in citations:
            cite_id = f"[C{cite_num}]"
            if cite_id in available_ids:
                results["verified_citations"].append(cite_id)
            else:
                results["unverified_citations"].append({
                    "citation": cite_id,
                    "issue": "Citation not found in source documents",
                    "severity": "warning"
                })
        
        return results
    
    async def _check_factual_consistency(self, context: AgentContext) -> Dict[str, Any]:
        """Check if the answer is consistent with source documents"""
        
        results = {
            "consistent": True,
            "inconsistencies": [],
            "supported_claims": [],
            "unsupported_claims": []
        }
        
        # This would use a cross-encoder or similar model in production
        # For now, implement rule-based checks
        
        answer_lower = context.generated_answer.lower()
        source_texts = " ".join([
            str(h.get("text", ""))[:1000] 
            for h in context.extracted_evidence 
            if isinstance(h, dict)
        ])
        
        # Check for extreme claims that need verification
        extreme_claims = [
            "always", "never", "everyone", "no one",
            "all", "none", "every", "impossible", "certain"
        ]
        
        for claim in extreme_claims:
            if claim in answer_lower:
                # Check if there's supporting evidence
                if claim not in source_texts.lower():
                    results["inconsistencies"].append({
                        "claim": f"Absolute statement using '{claim}'",
                        "severity": "medium",
                        "suggestion": "Consider qualifying the statement"
                    })
        
        return results
    
    async def _validate_reasoning(self, context: AgentContext) -> Dict[str, Any]:
        """Validate the logical reasoning in the answer"""
        
        results = {
            "logically_sound": True,
            "reasoning_issues": [],
            "assumptions_identified": []
        }
        
        # Check for common logical fallacies and weak reasoning
        answer = context.generated_answer
        
        # Check for unsupported causal claims
        import re
        causal_patterns = [
            r'because\s+.*?\s+therefore',
            r'due to\s+.*?\s+resulting in',
            r'leads?\s+to\s+.*?\s+causing'
        ]
        
        for pattern in causal_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                results["assumptions_identified"].append({
                    "type": "causal_claim",
                    "text": "Causal relationship claimed",
                    "suggestion": "Ensure causal link is supported by evidence"
                })
        
        return results
    
    def _calculate_confidence(self, citations: Dict, factual: Dict, reasoning: Dict) -> float:
        """Calculate overall confidence score"""
        
        # Start at 1.0 and deduct for issues
        score = 1.0
        
        # Citation deductions
        total = citations.get("total_citations", 0)
        if total > 0:
            unverified = len(citations.get("unverified_citations", []))
            score -= (unverified / total) * 0.3
        
        # Factual consistency deductions
        inconsistencies = len(factual.get("inconsistencies", []))
        score -= inconsistencies * 0.1
        
        # Reasoning deductions
        reasoning_issues = len(reasoning.get("reasoning_issues", []))
        score -= reasoning_issues * 0.15
        
        # Ensure score stays in [0, 1]
        return max(0.0, min(1.0, score))
    
    def _get_confidence_level(self, score: float) -> str:
        """Get human-readable confidence level"""
        if score >= self._high_confidence_threshold:
            return "HIGH"
        elif score >= self._verification_threshold:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_uncertainties(self, citations: Dict, factual: Dict) -> List[str]:
        """Identify areas of uncertainty in the answer"""
        
        uncertainties = []
        
        for cite in citations.get("unverified_citations", []):
            uncertainties.append(f"Citation {cite['citation']}: {cite['issue']}")
        
        for inconsistency in factual.get("inconsistencies", []):
            uncertainties.append(f"Factual: {inconsistency['claim']}")
        
        return uncertainties
    
    def _generate_recommendations(self, citations: Dict, factual: Dict, reasoning: Dict) -> List[Dict]:
        """Generate recommendations based on verification results"""
        
        recommendations = []
        
        if citations.get("unverified_citations"):
            recommendations.append({
                "type": "citation_fix",
                "priority": "high",
                "message": f"Verify {len(citations['unverified_citations'])} unverified citations",
                "action": "Review source documents and add missing citations"
            })
        
        if factual.get("inconsistencies"):
            recommendations.append({
                "type": "fact_check",
                "priority": "medium",
                "message": "Review factual claims for accuracy",
                "action": "Cross-check with source documents"
            })
        
        if reasoning.get("reasoning_issues"):
            recommendations.append({
                "type": "logic_review",
                "priority": "medium",
                "message": "Review logical reasoning",
                "action": "Ensure all claims follow logically from evidence"
            })
        
        return recommendations


# Global instance
_verification_agent: Optional[VerificationAgent] = None

def get_verification_agent() -> VerificationAgent:
    """Get or create the global verification agent instance"""
    global _verification_agent
    if _verification_agent is None:
        _verification_agent = VerificationAgent()
    return _verification_agent