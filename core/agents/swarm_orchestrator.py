# core/agents/swarm_orchestrator.py
"""
Swarm Orchestrator - Coordinates all agents in the research swarm

Manages the flow of information between agents and provides
a unified interface for the research assistant functionality.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.agents.base_agent import AgentContext, AgentResult, AgentStatus
from core.agents.research_agent import get_research_agent
from core.agents.verification_agent import get_verification_agent
from core.agents.synthesis_agent import get_synthesis_agent


class SwarmOrchestrator:
    """
    Orchestrates the AI swarm for autonomous research assistance.
    
    The swarm consists of:
    1. ResearchAgent - Finds and discovers relevant sources
    2. VerificationAgent - Validates accuracy and citations
    3. SynthesisAgent - Combines evidence into coherent answers
    
    Features:
    - Transparent processing pipeline
    - Progress tracking
    - Error recovery
    - Performance metrics
    """
    
    def __init__(self):
        self.researcher = get_research_agent()
        self.verifier = get_verification_agent()
        self.synthesizer = get_synthesis_agent()
        self._processing_history: List[Dict] = []
        self._active = False
    
    async def process_query(self, query: str, user_goal: str = "", 
                          conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process a research query through the full swarm pipeline.
        
        This is the main entry point for the intelligent research assistant.
        Each step provides visible progress to the user.
        """
        self._active = True
        context = AgentContext(
            query=query,
            user_goal=user_goal,
            conversation_history=conversation_history or []
        )
        
        pipeline_steps = []
        start_time = datetime.now()
        
        # Step 1: Research Phase
        step_result = await self._research_phase(context)
        pipeline_steps.append(("research", step_result))
        
        # Step 2: Verification Phase (only if we have content to verify)
        if context.generated_answer or context.extracted_evidence:
            step_result = await self._verification_phase(context)
            pipeline_steps.append(("verification", step_result))
        
        # Step 3: Synthesis Phase
        step_result = await self._synthesis_phase(context)
        pipeline_steps.append(("synthesis", step_result))
        
        # Build final response
        final_result = self._build_final_response(context, pipeline_steps, start_time)
        
        self._active = False
        return final_result
    
    async def _research_phase(self, context: AgentContext) -> Dict[str, Any]:
        """Phase 1: Research and discover relevant sources"""
        
        print(f"\n🔬 [Research Phase] Starting research for: {context.query[:80]}...")
        
        result = await self.researcher.process(context)
        
        if result.status == AgentStatus.COMPLETED:
            # Update context with discovered sources
            context.discovered_sources = result.output.get("top_sources", [])
            context.metadata["research_analysis"] = result.output.get("analysis", {})
            
            print(f"   ✅ Found {len(context.discovered_sources)} potential sources")
            
            return {
                "status": "success",
                "message": f"Research complete - {len(context.discovered_sources)} sources discovered",
                "sources_discovered": len(context.discovered_sources)
            }
        else:
            print(f"   ⚠️ Research phase had issues")
            return {
                "status": "partial",
                "message": "Research completed with some issues",
                "error": result.error
            }
    
    async def _verification_phase(self, context: AgentContext) -> Dict[str, Any]:
        """Phase 2: Verify accuracy of any existing content"""
        
        print(f"\n✅ [Verification Phase] Checking accuracy...")
        
        result = await self.verifier.process(context)
        
        if result.status == AgentStatus.COMPLETED:
            verification_report = result.output.get("verification_report", {})
            overall = verification_report.get("overall_verification", {})
            
            print(f"   Confidence Score: {overall.get('confidence_score', 0):.0%}")
            print(f"   Status: {overall.get('confidence_level', 'UNKNOWN')}")
            
            return {
                "status": "success",
                "confidence_score": overall.get("confidence_score", 0),
                "confidence_level": overall.get("confidence_level", "UNKNOWN"),
                "uncertainties": context.uncertainties,
                "verification_report": verification_report
            }
        else:
            return {
                "status": "skipped",
                "message": "Verification not applicable"
            }
    
    async def _synthesis_phase(self, context: AgentContext) -> Dict[str, Any]:
        """Phase 3: Synthesize final answer"""
        
        print(f"\n📝 [Synthesis Phase] Generating comprehensive answer...")
        
        result = await self.synthesizer.process(context)
        
        if result.status == AgentStatus.COMPLETED:
            synthesis = result.output.get("synthesized_answer", {})
            completeness = result.output.get("completeness_assessment", {})
            
            print(f"   ✅ Answer synthesized from {synthesis.get('source_count', 0)} sources")
            print(f"   📊 Completeness: {completeness.get('level', 'unknown')}")
            
            return {
                "status": "success",
                "answer": synthesis.get("main_answer", ""),
                "structured_sections": synthesis.get("structured_sections", []),
                "follow_ups": context.suggested_follow_ups,
                "completeness": completeness
            }
        else:
            return {
                "status": "partial",
                "message": "Synthesis completed with issues",
                "error": result.error
            }
    
    def _build_final_response(self, context: AgentContext, 
                              pipeline_steps: List, 
                              start_time: datetime) -> Dict[str, Any]:
        """Build the final response with all metadata"""
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Extract key results from pipeline
        research_result = next((r for s, r in pipeline_steps if s == "research"), {})
        verification_result = next((r for s, r in pipeline_steps if s == "verification"), {})
        synthesis_result = next((r for s, r in pipeline_steps if s == "synthesis"), {})
        
        # Build response with processing transparency
        response = {
            "query": context.query,
            "user_goal": context.user_goal,
            "answer": synthesis_result.get("answer", context.generated_answer),
            "hits": context.extracted_evidence,
            "suggested_links": context.discovered_sources[:5],
            "processing": {
                "research_complete": research_result.get("status") == "success",
                "verification_complete": verification_result.get("status") in ["success", "skipped"],
                "synthesis_complete": synthesis_result.get("status") == "success",
                "confidence_score": verification_result.get("confidence_score", 0),
                "confidence_level": verification_result.get("confidence_level", "LOW"),
                "processing_time_ms": round(processing_time, 2),
                "sources_used": len(context.extracted_evidence),
                "uncertainties": context.uncertainties
            },
            "follow_ups": context.suggested_follow_ups,
            "completeness": synthesis_result.get("completeness", {})
        }
        
        # Log pipeline execution
        pipeline_log = {
            "timestamp": datetime.now().isoformat(),
            "query": context.query[:100],
            "steps": {
                "research": research_result,
                "verification": verification_result,
                "synthesis": synthesis_result
            },
            "processing_time_ms": round(processing_time, 2),
            "confidence": verification_result.get("confidence_score", 0)
        }
        self._processing_history.append(pipeline_log)
        
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "active": self._active,
            "researcher": self.researcher.get_metrics(),
            "verifier": self.verifier.get_metrics(),
            "synthesizer": self.synthesizer.get_metrics(),
            "total_pipelines_run": len(self._processing_history)
        }
    
    def reset(self):
        """Reset all agents"""
        self.researcher.reset()
        self.verifier.reset()
        self.synthesizer.reset()
        self._processing_history = []


# Global instance
_orchestrator: Optional[SwarmOrchestrator] = None

def get_swarm_orchestrator() -> SwarmOrchestrator:
    """Get or create the global swarm orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SwarmOrchestrator()
    return _orchestrator


async def process_research_query(query: str, user_goal: str = "", 
                                 conversation_history: List[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function to process a research query through the swarm.
    """
    orchestrator = get_swarm_orchestrator()
    return await orchestrator.process_query(query, user_goal, conversation_history)