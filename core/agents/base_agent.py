# core/agents/base_agent.py
"""
Base Agent Class - Foundation for all AI agents in the swarm
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(Enum):
    RESEARCHER = "researcher"
    VERIFIER = "verifier"
    SYNTHESIZER = "synthesizer"
    PLANNER = "planner"
    MONITOR = "monitor"


@dataclass
class AgentContext:
    """Context passed between agents in the swarm"""
    task_id: str = ""
    query: str = ""
    user_goal: str = ""
    conversation_history: List[Dict] = field(default_factory=list)
    discovered_sources: List[Dict] = field(default_factory=list)
    extracted_evidence: List[Dict] = field(default_factory=list)
    generated_answer: str = ""
    confidence_score: float = 0.0
    uncertainties: List[str] = field(default_factory=list)
    suggested_follow_ups: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from an agent"""
    agent_name: str
    status: AgentStatus
    context: AgentContext
    output: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    error: Optional[str] = None


class BaseAgent:
    """
    Base class for all agents in the swarm.
    
    Features:
    - Standardized status tracking
    - Processing metrics
    - Error handling
    - Inter-agent communication
    - Logging and debugging
    """
    
    def __init__(self, name: str, role: AgentRole, model_preference: str = None):
        self.name = name
        self.role = role
        self.model_preference = model_preference
        self.status = AgentStatus.IDLE
        self.context = AgentContext()
        self.processing_history: List[Dict] = []
        self._created_at = datetime.now().isoformat()
        self._total_processing_time_ms = 0.0
        self._tasks_completed = 0
        self._tasks_failed = 0
    
    async def process(self, context: AgentContext) -> AgentResult:
        """
        Main processing method - override in subclasses.
        
        Args:
            context: Current context with query, history, etc.
            
        Returns:
            AgentResult with status, updated context, and output
        """
        start_time = time.time()
        self.status = AgentStatus.THINKING
        self.context = context
        
        try:
            self._log_start()
            result = await self._execute(context)
            processing_time = (time.time() - start_time) * 1000
            
            self._total_processing_time_ms += processing_time
            self._tasks_completed += 1
            self.status = AgentStatus.COMPLETED
            
            self._log_completion(result, processing_time)
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._tasks_failed += 1
            self.status = AgentStatus.FAILED
            
            error_msg = f"{self.name} failed: {str(e)}"
            print(f"[{self.name}] ✗ {error_msg}")
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                context=context,
                output={"error": error_msg},
                processing_time_ms=processing_time,
                error=str(e)
            )
    
    async def _execute(self, context: AgentContext) -> AgentResult:
        """Override this method with actual agent logic"""
        raise NotImplementedError
    
    def _log_start(self):
        """Log agent start"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "start",
            "query": self.context.query[:100] + "..." if len(self.context.query) > 100 else self.context.query,
        }
        self.processing_history.append(entry)
        print(f"[{self.name}] → Processing: {self.context.query[:60]}...")
    
    def _log_completion(self, result: AgentResult, processing_time: float):
        """Log agent completion"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "complete",
            "status": result.status.value,
            "processing_time_ms": round(processing_time, 2),
            "output_summary": str(result.output)[:200]
        }
        self.processing_history.append(entry)
        status_emoji = {"completed": "✅", "failed": "❌"}.get(result.status.value, "❓")
        print(f"[{self.name}] {status_emoji} Done in {processing_time:.1f}ms")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            "name": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "total_processing_time_ms": round(self._total_processing_time_ms, 2),
            "avg_processing_time_ms": round(
                self._total_processing_time_ms / max(self._tasks_completed, 1), 2
            ),
            "success_rate": round(
                self._tasks_completed / max(self._tasks_completed + self._tasks_failed, 1) * 100, 1
            ),
            "created_at": self._created_at,
        }
    
    def reset(self):
        """Reset agent state"""
        self.status = AgentStatus.IDLE
        self.context = AgentContext()
        self.processing_history = []
        self._total_processing_time_ms = 0.0
        self._tasks_completed = 0
        self._tasks_failed = 0
    
    def to_dict(self) -> Dict:
        """Serialize agent state"""
        return {
            "name": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "metrics": self.get_metrics(),
            "recent_history": self.processing_history[-10:] if self.processing_history else []
        }