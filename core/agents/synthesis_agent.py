# core/agents/synthesis_agent.py
"""
Synthesis Agent - Combines evidence into coherent answers

Takes verified information from multiple sources and synthesizes
a comprehensive, well-cited answer for the user.
"""

import asyncio
from typing import Dict, List, Any, Optional

from core.agents.base_agent import BaseAgent, AgentContext, AgentResult, AgentStatus, AgentRole


class SynthesisAgent(BaseAgent):
    """
    Agent that synthesizes evidence from multiple sources into coherent answers.
    
    Capabilities:
    - Combines information from multiple sources
    - Generates well-structured answers
    - Includes proper citations
    - Identifies knowledge gaps
    - Suggests follow-up questions
    """
    
    def __init__(self):
        super().__init__(
            name="SynthesisAgent",
            role=AgentRole.SYNTHESIZER,
            model_preference="llama-3.3-70b-versatile"
        )
    
    async def _execute(self, context: AgentContext) -> AgentResult:
        """Execute synthesis task"""
        
        if not context.extracted_evidence and not context.discovered_sources:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                context=context,
                output={"message": "No evidence to synthesize"}
            )
        
        # Step 1: Organize evidence by type and relevance
        organized_evidence = self._organize_evidence(context.extracted_evidence)
        
        # Step 2: Generate structured answer
        synthesized_answer = await self._generate_answer(context, organized_evidence)
        
        # Step 3: Generate follow-up suggestions
        follow_ups = self._generate_follow_ups(context, organized_evidence)
        
        # Step 4: Assess completeness
        completeness = self._assess_completeness(organized_evidence, context)
        
        # Update context
        context.generated_answer = synthesized_answer["main_answer"]
        context.suggested_follow_ups = follow_ups
        
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            context=context,
            output={
                "synthesized_answer": synthesized_answer,
                "follow_up_suggestions": follow_ups,
                "completeness_assessment": completeness,
                "evidence_summary": self._summarize_evidence(organized_evidence)
            }
        )
    
    def _organize_evidence(self, evidence: List[Dict]) -> Dict[str, List]:
        """Organize evidence by type (text, figure, table)"""
        
        organized = {
            "text": [],
            "figure": [],
            "table": [],
            "external": []
        }
        
        for item in evidence:
            if isinstance(item, dict):
                section_type = item.get("section_type", "text")
                if section_type in organized:
                    organized[section_type].append(item)
                else:
                    organized["text"].append(item)
        
        return organized
    
    async def _generate_answer(self, context: AgentContext, evidence: Dict) -> Dict[str, str]:
        """Generate a structured answer from evidence"""
        
        # Build answer structure
        answer_parts = []
        
        # Introduction
        answer_parts.append(self._generate_introduction(context.query))
        
        # Main body from text evidence
        if evidence["text"]:
            answer_parts.append(self._generate_text_section(evidence["text"], context))
        
        # Figures and tables
        if evidence["figure"]:
            answer_parts.append(self._generate_figure_section(evidence["figure"]))
        
        if evidence["table"]:
            answer_parts.append(self._generate_table_section(evidence["table"]))
        
        # External sources
        if evidence["external"]:
            answer_parts.append(self._generate_external_section(evidence["external"]))
        
        # Conclusion
        answer_parts.append(self._generate_conclusion(context.query, evidence))
        
        main_answer = "\n\n".join(answer_parts)
        
        return {
            "main_answer": main_answer,
            "structured_sections": answer_parts,
            "has_figures": len(evidence["figure"]) > 0,
            "has_tables": len(evidence["table"]) > 0,
            "source_count": sum(len(v) for v in evidence.values())
        }
    
    def _generate_introduction(self, query: str) -> str:
        """Generate an introduction section"""
        return f"Based on your question about *{query}*, here is a comprehensive analysis drawing from multiple sources."
    
    def _generate_text_section(self, text_evidence: List[Dict], context: AgentContext) -> str:
        """Generate the main text section from evidence"""
        
        if not text_evidence:
            return ""
        
        # Extract key findings from text evidence
        key_findings = []
        for item in text_evidence[:5]:  # Limit to top 5
            text = item.get("text", "")
            title = item.get("title", "")
            page = item.get("page", "N/A")
            doc_id = item.get("doc_id", "Unknown")
            
            if text:
                # Summarize the text (first 200 chars)
                summary = text[:200] + "..." if len(text) > 200 else text
                key_findings.append(f"**From {doc_id} (Page {page})**: {summary}")
        
        if not key_findings:
            return ""
        
        section = "## Key Findings\n\n"
        section += "\n\n".join(key_findings)
        return section
    
    def _generate_figure_section(self, figure_evidence: List[Dict]) -> str:
        """Generate section for figures/graphs"""
        
        if not figure_evidence:
            return ""
        
        section = "## Visual Evidence\n\n"
        for fig in figure_evidence[:3]:  # Limit to 3 figures
            caption = fig.get("caption", "Figure")
            page = fig.get("page", "N/A")
            doc_id = fig.get("doc_id", "Unknown")
            section += f"- **{caption}** (Page {page} of {doc_id})\n"
        
        return section
    
    def _generate_table_section(self, table_evidence: List[Dict]) -> str:
        """Generate section for tables"""
        
        if not table_evidence:
            return ""
        
        section = "## Tabular Data\n\n"
        for table in table_evidence[:3]:  # Limit to 3 tables
            page = table.get("page", "N/A")
            doc_id = table.get("doc_id", "Unknown")
            preview = table.get("metadata", {}).get("preview_rows", [])
            
            if preview:
                section += f"**Table from {doc_id} (Page {page}):**\n\n"
                for row in preview[:5]:
                    section += "| " + " | ".join(str(cell) for cell in row) + " |\n"
                section += "\n"
        
        return section
    
    def _generate_external_section(self, external_evidence: List[Dict]) -> str:
        """Generate section for external sources"""
        
        if not external_evidence:
            return ""
        
        section = "## External References\n\n"
        for ref in external_evidence[:3]:
            title = ref.get("title", "Reference")
            authors = ref.get("authors", "Unknown")
            doc_id = ref.get("doc_id", "")
            section += f"- **{title}** by {authors} [{doc_id}]\n"
        
        return section
    
    def _generate_conclusion(self, query: str, evidence: Dict) -> str:
        """Generate conclusion section"""
        
        total_sources = sum(len(v) for v in evidence.values())
        
        conclusion = "## Summary\n\n"
        conclusion += f"This analysis synthesized information from **{total_sources} sources** "
        conclusion += f"to address your question about *{query}*.\n\n"
        
        if evidence["external"]:
            conclusion += "The findings are supported by both local documents and external CERN Database references. "
        
        conclusion += "\n**Note**: For the most accurate results, ensure all relevant documents are fully indexed."
        
        return conclusion
    
    def _generate_follow_ups(self, context: AgentContext, evidence: Dict) -> List[str]:
        """Generate follow-up questions or actions"""
        
        follow_ups = []
        
        # Check if there are unindexed documents that might be relevant
        total_sources = sum(len(v) for v in evidence.values())
        
        if total_sources < 3:
            follow_ups.append("Consider importing more documents related to your research topic")
        
        if any(evidence.values()):
            follow_ups.append("Would you like me to search for more specific aspects of your question?")
        
        if context.query and len(context.query.split()) > 5:
            follow_ups.append("You could narrow down your query for more focused results")
        
        if not follow_ups:
            follow_ups.append("Your research seems comprehensive. Would you like to explore related topics?")
        
        return follow_ups
    
    def _assess_completeness(self, evidence: Dict, context: AgentContext) -> Dict[str, Any]:
        """Assess how complete the answer is"""
        
        total_sources = sum(len(v) for v in evidence.values())
        
        if total_sources == 0:
            completeness = "very_low"
            message = "No evidence found. Consider importing relevant documents."
        elif total_sources <= 2:
            completeness = "low"
            message = "Limited evidence found. More documents may improve the answer."
        elif total_sources <= 5:
            completeness = "moderate"
            message = "Moderate evidence coverage."
        else:
            completeness = "high"
            message = "Comprehensive evidence from multiple sources."
        
        return {
            "level": completeness,
            "message": message,
            "source_count": total_sources,
            "coverage_percentage": min(total_sources * 20, 100)
        }
    
    def _summarize_evidence(self, evidence: Dict) -> str:
        """Create a brief summary of available evidence"""
        
        parts = []
        for evidence_type, items in evidence.items():
            if items:
                parts.append(f"{len(items)} {evidence_type} source(s)")
        
        return ", ".join(parts) if parts else "No evidence available"


# Global instance
_synthesis_agent: Optional[SynthesisAgent] = None

def get_synthesis_agent() -> SynthesisAgent:
    """Get or create the global synthesis agent instance"""
    global _synthesis_agent
    if _synthesis_agent is None:
        _synthesis_agent = SynthesisAgent()
    return _synthesis_agent