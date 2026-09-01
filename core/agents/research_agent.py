# core/agents/research_agent.py
"""
Research Agent - Autonomous paper discovery and analysis

Finds relevant papers from CERN Document Server and local database,
suggests imports, and provides context for research queries.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentContext, AgentResult, AgentStatus, AgentRole
from core.cern_search import CernDbSearch


class ResearchAgent(BaseAgent):
    """
    Agent that autonomously discovers and analyzes research papers.
    
    Capabilities:
    - Search CERN Document Server
    - Analyze local document collection
    - Suggest relevant papers for import
    - Identify research gaps
    """
    
    def __init__(self):
        super().__init__(
            name="ResearchAgent",
            role=AgentRole.RESEARCHER,
            model_preference="nousresearch/hermes-3-llama-3.1-405b"
        )
        self.cds_searcher = CernDbSearch()
        self._search_cache: Dict[str, List[Dict]] = {}
    
    async def _execute(self, context: AgentContext) -> AgentResult:
        """Execute research task based on context"""
        
        # Determine what kind of research is needed
        if not context.query:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                context=context,
                output={"message": "No query provided"}
            )
        
        # Step 1: Analyze user's query for intent
        analysis = await self._analyze_query_intent(context.query)
        
        # Step 2: Search local documents first
        local_results = await self._search_local_documents(context)
        
        # Step 3: Search CERN database if needed
        cern_results = []
        if analysis.get("needs_external_search", False):
            cern_results = await self._search_cern_database(context.query)
        
        # Step 4: Analyze and rank results
        ranked_sources = self._rank_sources(local_results, cern_results, context)
        
        # Step 5: Generate recommendations
        recommendations = await self._generate_recommendations(ranked_sources, context)
        
        # Update context with findings
        context.discovered_sources = ranked_sources[:10]
        context.metadata["research_analysis"] = analysis
        context.metadata["recommendations_count"] = len(recommendations)
        
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            context=context,
            output={
                "analysis": analysis,
                "local_results": local_results[:5],
                "cern_results": cern_results[:5],
                "recommendations": recommendations,
                "top_sources": ranked_sources[:5]
            }
        )
    
    async def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine search intent"""
        
        # Keyword patterns for different research needs
        intent_patterns = {
            "needs_external_search": [
                "find papers", "search for", "look up", "discover",
                "what research", "latest", "recent", "new results",
                "recommend", "suggest", "related work", "literature"
            ],
            "needs_local_search": [
                "import", "already have", "indexed", "my documents",
                "in my collection", "uploaded", "stored"
            ],
            "needs_synthesis": [
                "summarize", "compare", "analyze", "review",
                "overview", "status", "update", "progress"
            ],
            "needs_methodology": [
                "how to", "method", "approach", "technique",
                "experimental", "setup", "procedure", "protocol"
            ]
        }
        
        query_lower = query.lower()
        analysis = {
            "needs_external_search": False,
            "needs_local_search": False,
            "needs_synthesis": False,
            "needs_methodology": False,
            "detected_intents": [],
            "query_complexity": "simple"
        }
        
        for intent, keywords in intent_patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    analysis[intent] = True
                    analysis["detected_intents"].append(intent.replace("_", " "))
                    break
        
        # Assess complexity
        word_count = len(query.split())
        has_multiple_clauses = query.count(",") + query.count(" and ") + query.count(" or ") > 2
        if word_count > 15 or has_multiple_clauses:
            analysis["query_complexity"] = "complex"
        elif word_count > 8:
            analysis["query_complexity"] = "moderate"
        
        return analysis
    
    async def _search_local_documents(self, context: AgentContext) -> List[Dict]:
        """Search locally indexed documents"""
        from core.vector_store_lance import LanceVectorStore
        
        results = []
        try:
            # Use the existing RAG pipeline's search
            from core.rag_pipeline import RAGPipeline
            # This would be called from the main application context
            results = [{
                "source": "local",
                "message": "Local search would be performed here",
                "status": "available"
            }]
        except Exception:
            results = [{"source": "local", "message": "Local search not available", "status": "unavailable"}]
        
        return results
    
    async def _search_cern_database(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search CERN Document Server"""
        try:
            results = self.cds_searcher.search(query, top_k=top_k)
            return [
                {
                    "doc_id": r.get("doc_id", ""),
                    "title": r.get("title", ""),
                    "authors": r.get("authors", ""),
                    "abstract": r.get("abstract", "")[:200] + "...",
                    "url": r.get("url", ""),
                    "source": "cds_api"
                }
                for r in results
            ]
        except Exception as e:
            print(f"[ResearchAgent] CDS search failed: {e}")
            return []
    
    def _rank_sources(self, local: List, cern: List, context: AgentContext) -> List[Dict]:
        """Combine and rank sources by relevance"""
        all_sources = local + cern
        
        # Simple ranking: prefer sources with more complete metadata
        ranked = sorted(all_sources, key=lambda x: len(str(x)), reverse=True)
        return ranked
    
    async def _generate_recommendations(self, sources: List[Dict], context: AgentContext) -> List[Dict]:
        """Generate actionable recommendations based on research"""
        recommendations = []
        
        if not sources:
            return [{
                "type": "suggestion",
                "action": "import",
                "message": "Consider importing relevant papers from CERN Document Server",
                "priority": "high"
            }]
        
        # Generate recommendations based on source types
        local_sources = [s for s in sources if s.get("source") == "local"]
        cern_sources = [s for s in sources if s.get("source") in ["cds_api", "cds"]]
        
        if cern_sources:
            recommendations.append({
                "type": "import_suggestion",
                "action": "import_from_cds",
                "papers": cern_sources[:3],
                "message": f"Found {len(cern_sources)} relevant papers on CERN DS",
                "priority": "high"
            })
        
        if local_sources:
            recommendations.append({
                "type": "local_reference",
                "action": "query_local",
                "documents": local_sources[:3],
                "message": f"{len(local_sources)} local documents may be relevant",
                "priority": "medium"
            })
        
        # Always suggest follow-up actions
        recommendations.append({
            "type": "methodology",
            "action": "suggest_methodology",
            "message": "Consider reviewing the experimental methodology in related papers",
            "priority": "medium"
        })
        
        return recommendations


# Global instance
_research_agent: Optional[ResearchAgent] = None

def get_research_agent() -> ResearchAgent:
    """Get or create the global research agent instance"""
    global _research_agent
    if _research_agent is None:
        _research_agent = ResearchAgent()
    return _research_agent