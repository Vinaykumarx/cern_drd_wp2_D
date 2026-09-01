#!/usr/bin/env python3
from core.bootstrap import require_bootstrap; require_bootstrap()
"""
🤖 PROJECT STATUS AGENT
CERN Multimodal RAG - Production-Ready Status & Task Management

This agent:
1. Analyzes project status and health
2. Identifies critical issues and fixes required
3. Manages tasks with kanban board workflow
4. Recommends task allocation to engineers
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


class TaskStatus(Enum):
    """Kanban board task statuses"""
    BACKLOG = "📋 Backlog"
    TODO = "🔲 Todo"
    IN_PROGRESS = "⏳ In Progress"
    IN_REVIEW = "👀 In Review"
    DONE = "✅ Done"
    BLOCKED = "🚫 Blocked"


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = "🔴 Critical"
    HIGH = "🟠 High"
    MEDIUM = "🟡 Medium"
    LOW = "🟢 Low"


class TaskCategory(Enum):
    """Task categories for organization"""
    BUG_FIX = "Bug Fix"
    FEATURE = "Feature"
    REFACTOR = "Refactor"
    INFRASTRUCTURE = "Infrastructure"
    DOCUMENTATION = "Documentation"
    OPTIMIZATION = "Optimization"


class EngineerLevel(Enum):
    """Engineer expertise levels"""
    JUNIOR = "Junior (0-2 years)"
    MID = "Mid (2-5 years)"
    SENIOR = "Senior (5-10 years)"
    STAFF = "Staff (10+ years)"


@dataclass
class TaskAssignment:
    """Task assignment record"""
    engineer_name: str
    level: EngineerLevel
    skills: List[str]
    current_load: int = 0  # Number of tasks already assigned
    estimated_capacity: int = 5  # Tasks they can handle


@dataclass
class Task:
    """Individual task in the kanban board"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    category: TaskCategory
    assigned_to: Optional[str] = None
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None
    estimated_hours: float = 0.0
    tags: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['category'] = self.category.value
        if self.assigned_to:
            data['assigned_to'] = self.assigned_to
        return data

    @staticmethod
    def from_dict(data: Dict) -> 'Task':
        data_copy = data.copy()
        status_map = {v.value: k for k, v in TaskStatus.__members__.items()}
        priority_map = {v.value: k for k, v in Priority.__members__.items()}
        category_map = {v.value: k for k, v in TaskCategory.__members__.items()}

        data_copy['status'] = TaskStatus[status_map[data['status']]]
        data_copy['priority'] = Priority[priority_map[data['priority']]]
        data_copy['category'] = TaskCategory[category_map[data['category']]]
        return Task(**data_copy)


class ProjectHealthAnalyzer:
    """Analyzes project health status"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.health_score = 100.0
        self.issues = []
        self.verified_components = []
        self.warnings = []

    def analyze(self) -> Dict[str, Any]:
        """Run full health analysis"""
        self._check_directory_structure()
        self._check_configuration()
        self._check_dependencies()
        self._check_code_quality()
        self._check_architecture()

        return {
            'health_score': self.health_score,
            'timestamp': datetime.now().isoformat(),
            'verified_components': self.verified_components,
            'critical_issues': self.issues,
            'warnings': self.warnings,
            'status': self._get_status(),
        }

    def _check_directory_structure(self):
        """Verify required directories exist"""
        required_dirs = [
            'app', 'backend', 'core', 'frontend', 'extraction',
            'lancedb', 'data', 'outputs'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                self.verified_components.append(f"✅ {dir_name}/ exists")
            else:
                self.health_score -= 5
                self.issues.append(f"Missing directory: {dir_name}/")

    def _check_configuration(self):
        """Check if config files exist"""
        config_files = [
            'requirements.txt',
            'frontend/package.json',
            'docker/docker-compose.yml',
        ]
        
        for config in config_files:
            config_path = self.project_root / config
            if config_path.exists():
                self.verified_components.append(f"✅ {config} found")
            else:
                self.health_score -= 3
                self.issues.append(f"Missing config: {config}")

    def _check_dependencies(self):
        """Check Python and Node dependencies"""
        # Check requirements.txt
        req_path = self.project_root / 'requirements.txt'
        if req_path.exists():
            with open(req_path, 'r') as f:
                reqs = f.readlines()
                if len(reqs) > 0:
                    self.verified_components.append(f"✅ Python dependencies ({len(reqs)} packages)")
                else:
                    self.health_score -= 5
                    self.issues.append("requirements.txt is empty")

        # Check package.json
        pkg_path = self.project_root / 'frontend' / 'package.json'
        if pkg_path.exists():
            self.verified_components.append("✅ Frontend package.json found")
        else:
            self.health_score -= 3
            self.warnings.append("Frontend package.json missing - frontend may not be buildable")

    def _check_code_quality(self):
        """Check code structure and patterns"""
        core_modules = [
            'config.py', 'rag_pipeline.py', 'vector_store_lance.py',
            'chunker.py', 'embedder.py', 'llm_client.py'
        ]
        
        for module in core_modules:
            module_path = self.project_root / 'core' / module
            if module_path.exists():
                self.verified_components.append(f"✅ core/{module}")
            else:
                self.health_score -= 2
                self.issues.append(f"Missing core module: {module}")

    def _check_architecture(self):
        """Validate architecture components"""
        backend_exists = (self.project_root / 'backend' / 'main.py').exists()
        frontend_exists = (self.project_root / 'frontend' / 'src').exists()
        
        if backend_exists:
            self.verified_components.append("✅ FastAPI Backend (main.py)")
        else:
            self.health_score -= 10
            self.issues.append("Backend entry point missing (backend/main.py)")

        if frontend_exists:
            self.verified_components.append("✅ Next.js Frontend (src/)")
        else:
            self.health_score -= 10
            self.issues.append("Frontend source missing (frontend/src/)")

    def _get_status(self) -> str:
        """Determine overall project status"""
        if self.health_score >= 90:
            return "🟢 Production Ready"
        elif self.health_score >= 70:
            return "🟡 Needs Minor Fixes"
        elif self.health_score >= 50:
            return "🟠 Major Issues Detected"
        else:
            return "🔴 Critical Issues - Not Production Ready"


class KanbanBoard:
    """Manages task kanban board"""

    def __init__(self, storage_path: str = "tasks.json"):
        self.storage_path = Path(storage_path)
        self.tasks: Dict[str, Task] = self._load_tasks()
        self._task_counter = len(self.tasks)

    def _load_tasks(self) -> Dict[str, Task]:
        """Load tasks from JSON storage"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return {task_id: Task.from_dict(task_data) 
                       for task_id, task_data in data.items()}
        return {}

    def save_tasks(self):
        """Save tasks to JSON storage"""
        data = {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add_task(self, title: str, description: str, category: TaskCategory,
                 priority: Priority, estimated_hours: float = 0.0) -> Task:
        """Add new task to backlog"""
        self._task_counter += 1
        task_id = f"TASK-{self._task_counter:04d}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.BACKLOG,
            priority=priority,
            category=category,
            estimated_hours=estimated_hours,
        )
        
        self.tasks[task_id] = task
        self.save_tasks()
        return task

    def update_task_status(self, task_id: str, new_status: TaskStatus):
        """Update task status"""
        if task_id in self.tasks:
            self.tasks[task_id].status = new_status
            self.save_tasks()

    def assign_task(self, task_id: str, engineer_name: str):
        """Assign task to engineer"""
        if task_id in self.tasks:
            self.tasks[task_id].assigned_to = engineer_name
            self.tasks[task_id].status = TaskStatus.TODO
            self.save_tasks()

    def get_kanban_view(self) -> str:
        """Get kanban board visualization"""
        board = "\n" + "="*100 + "\n"
        board += "📊 KANBAN BOARD - PROJECT TASK STATUS\n"
        board += "="*100 + "\n\n"

        for status in TaskStatus:
            tasks_in_status = [t for t in self.tasks.values() if t.status == status]
            
            board += f"\n{status.value}\n"
            board += "-" * 100 + "\n"
            
            if not tasks_in_status:
                board += "  (no tasks)\n"
            else:
                for task in sorted(tasks_in_status, key=lambda t: t.priority.name):
                    assignee = f" → {task.assigned_to}" if task.assigned_to else ""
                    board += f"  {task.id} | {task.priority.value} | {task.title}\n"
                    board += f"    📝 {task.description[:70]}...\n" if len(task.description) > 70 else f"    📝 {task.description}\n"
                    if task.estimated_hours:
                        board += f"    ⏱️ Estimated: {task.estimated_hours}h{assignee}\n"
                    else:
                        board += f"    {assignee}\n"

        return board

    def get_stats(self) -> Dict[str, Any]:
        """Get board statistics"""
        status_counts = {}
        for status in TaskStatus:
            count = len([t for t in self.tasks.values() if t.status == status])
            status_counts[status.value] = count

        priority_counts = {}
        for priority in Priority:
            count = len([t for t in self.tasks.values() if t.priority == priority])
            priority_counts[priority.value] = count

        total_hours = sum(t.estimated_hours for t in self.tasks.values())

        return {
            'total_tasks': len(self.tasks),
            'by_status': status_counts,
            'by_priority': priority_counts,
            'total_estimated_hours': total_hours,
        }


class TeamResourceAllocator:
    """Allocates engineers to tasks"""

    def __init__(self):
        self.engineers = self._initialize_team()

    def _initialize_team(self) -> List[TaskAssignment]:
        """Initialize recommended team structure"""
        return [
            TaskAssignment(
                engineer_name="Senior Architect",
                level=EngineerLevel.STAFF,
                skills=["System Design", "Architecture", "RAG Pipelines", "LLMs", "FastAPI"],
                estimated_capacity=3,
            ),
            TaskAssignment(
                engineer_name="Backend Engineer (Senior)",
                level=EngineerLevel.SENIOR,
                skills=["FastAPI", "Python", "LanceDB", "Async/Await", "API Design"],
                estimated_capacity=5,
            ),
            TaskAssignment(
                engineer_name="Frontend Engineer (Senior)",
                level=EngineerLevel.SENIOR,
                skills=["Next.js", "TypeScript", "Tailwind CSS", "React", "WebGL"],
                estimated_capacity=5,
            ),
            TaskAssignment(
                engineer_name="ML/AI Specialist",
                level=EngineerLevel.SENIOR,
                skills=["Transformers", "BLIP", "Embeddings", "Ollama", "Qwen2-VL"],
                estimated_capacity=4,
            ),
            TaskAssignment(
                engineer_name="DevOps/Infrastructure",
                level=EngineerLevel.SENIOR,
                skills=["Docker", "Kubernetes", "CI/CD", "AWS", "Monitoring"],
                estimated_capacity=4,
            ),
            TaskAssignment(
                engineer_name="Mid-level Backend Engineer",
                level=EngineerLevel.MID,
                skills=["Python", "FastAPI", "Testing", "LanceDB"],
                estimated_capacity=6,
            ),
            TaskAssignment(
                engineer_name="QA/Test Engineer",
                level=EngineerLevel.MID,
                skills=["Testing", "Debugging", "Performance Testing", "Automation"],
                estimated_capacity=7,
            ),
        ]

    def recommend_assignments(self, tasks: List[Task]) -> Dict[str, Any]:
        """Recommend task assignments based on skills"""
        recommendations = []
        
        for task in tasks:
            if task.assigned_to:
                continue  # Skip already assigned

            # Match based on category and priority
            best_match = self._find_best_engineer(task)
            if best_match:
                recommendations.append({
                    'task_id': task.id,
                    'task_title': task.title,
                    'recommended_engineer': best_match.engineer_name,
                    'level': best_match.level.value,
                    'skills_match': self._get_matching_skills(task, best_match),
                    'current_load': best_match.current_load,
                    'capacity': best_match.estimated_capacity,
                })

        return {
            'timestamp': datetime.now().isoformat(),
            'recommendations': recommendations,
            'team': [{'name': e.engineer_name, 'level': e.level.value} for e in self.engineers],
        }

    def _find_best_engineer(self, task: Task) -> Optional[TaskAssignment]:
        """Find best engineer for a task"""
        # Sort engineers by their fit and available capacity
        candidates = [(e, self._calculate_fit_score(task, e)) for e in self.engineers]
        candidates = [(e, score) for e, score in candidates if e.current_load < e.estimated_capacity]
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates[0][0] if candidates else None

    def _calculate_fit_score(self, task: Task, engineer: TaskAssignment) -> float:
        """Calculate how well engineer fits the task"""
        score = 0.0
        
        # Category-based skills matching
        category_skills = {
            "Feature": ["FastAPI", "Python", "Async/Await", "System Design", "Architecture"],
            "Bug Fix": ["Debugging", "Testing", "Python"],
            "Infrastructure": ["Docker", "Kubernetes", "CI/CD"],
            "Optimization": ["Performance Testing", "Python", "FastAPI"],
            "Refactor": ["System Design", "Python"],
            "Documentation": ["Writing"],
        }
        
        required = category_skills.get(task.category.value, [])
        for skill in required:
            if skill in engineer.skills:
                score += 20
        
        # Priority-based level matching
        if task.priority == Priority.CRITICAL and engineer.level in [EngineerLevel.STAFF, EngineerLevel.SENIOR]:
            score += 30
        elif task.priority == Priority.HIGH and engineer.level in [EngineerLevel.SENIOR, EngineerLevel.MID]:
            score += 20
        
        # Availability bonus
        available_slots = engineer.estimated_capacity - engineer.current_load
        score += available_slots * 5
        
        return score

    def _get_matching_skills(self, task: Task, engineer: TaskAssignment) -> List[str]:
        """Get skills that match between task and engineer"""
        category_skills = {
            "Feature": ["FastAPI", "Python", "Async/Await", "System Design"],
            "Bug Fix": ["Debugging", "Testing"],
            "Infrastructure": ["Docker", "Kubernetes"],
            "Optimization": ["Performance Testing"],
        }
        
        required = category_skills.get(task.category.value, [])
        return [s for s in required if s in engineer.skills]


class ProjectStatusAgent:
    """Main agent orchestrating project analysis and management"""

    def __init__(self, project_root: str = "/home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration"):
        self.project_root = project_root
        self.analyzer = ProjectHealthAnalyzer(project_root)
        self.kanban = KanbanBoard(Path(project_root) / "project_tasks.json")
        self.allocator = TeamResourceAllocator()
        self.report = {}

    def run_full_assessment(self) -> Dict[str, Any]:
        """Run complete project assessment"""
        print("\n🔍 Running Project Status Assessment...")
        
        # Step 1: Health analysis
        print("  → Analyzing project health...")
        health = self.analyzer.analyze()
        
        # Step 2: Initialize default tasks if empty
        print("  → Checking task board...")
        if not self.kanban.tasks:
            self._populate_default_tasks()
        
        # Step 3: Get recommendations
        print("  → Generating resource recommendations...")
        backlog_tasks = [t for t in self.kanban.tasks.values() if t.status == TaskStatus.BACKLOG]
        allocations = self.allocator.recommend_assignments(backlog_tasks)
        
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'project_health': health,
            'kanban_stats': self.kanban.get_stats(),
            'resource_recommendations': allocations,
        }
        
        return self.report

    def _populate_default_tasks(self):
        """Create default tasks based on architecture review"""
        default_tasks = [
            # CRITICAL - Production blockers
            {
                'title': 'Fix LanceDB Synchronization Issues',
                'description': 'Backend dashboard_status counts vectors incorrectly; fix vector sync between extraction and LanceDB',
                'category': TaskCategory.BUG_FIX,
                'priority': Priority.CRITICAL,
                'hours': 8,
            },
            {
                'title': 'Async/Await Mismatch in FastAPI Backend',
                'description': 'SemanticChunker and vector searches run synchronously, blocking event loop under load',
                'category': TaskCategory.REFACTOR,
                'priority': Priority.CRITICAL,
                'hours': 12,
            },
            {
                'title': 'Fix Knowledge Graph Memory Leak',
                'description': 'get_knowledge_graph loads all 200 vectors causing browser freeze; implement pagination',
                'category': TaskCategory.BUG_FIX,
                'priority': Priority.CRITICAL,
                'hours': 6,
            },
            # HIGH - Feature completeness
            {
                'title': 'Replace pymupdf4llm with Docling',
                'description': 'Improve PDF parsing reliability for scientific papers with tables and multi-column layouts',
                'category': TaskCategory.REFACTOR,
                'priority': Priority.HIGH,
                'hours': 16,
            },
            {
                'title': 'Implement ColPali for Visual Retrieval',
                'description': 'Replace BLIP captioning with ColPali for direct PDF visual embedding (5 -> unlimited images)',
                'category': TaskCategory.FEATURE,
                'priority': Priority.HIGH,
                'hours': 20,
            },
            {
                'title': 'Deprecate Streamlit, Unify on Next.js',
                'description': 'Move PDF upload and all UX to Next.js frontend, remove Streamlit to reduce tech debt',
                'category': TaskCategory.REFACTOR,
                'priority': Priority.HIGH,
                'hours': 24,
            },
            # MEDIUM - Optimization & Infrastructure
            {
                'title': 'Implement Hybrid Chunking with Nomic',
                'description': 'Combine deterministic splitting with nomic-embed-text for smart topic/keyword generation',
                'category': TaskCategory.OPTIMIZATION,
                'priority': Priority.MEDIUM,
                'hours': 14,
            },
            {
                'title': 'Graph Pagination & Query Optimization',
                'description': 'Refactor get_knowledge_graph to query only relevant nodes per user query/doc_id',
                'category': TaskCategory.OPTIMIZATION,
                'priority': Priority.MEDIUM,
                'hours': 10,
            },
            {
                'title': 'Docker Container Optimization',
                'description': 'Multi-stage build, size optimization, security scanning in CI/CD',
                'category': TaskCategory.INFRASTRUCTURE,
                'priority': Priority.MEDIUM,
                'hours': 8,
            },
            # MEDIUM - Quality & Testing
            {
                'title': 'Comprehensive E2E Testing Suite',
                'description': 'Add tests for: extraction → chunking → embedding → retrieval → synthesis pipeline',
                'category': TaskCategory.FEATURE,
                'priority': Priority.MEDIUM,
                'hours': 18,
            },
            {
                'title': 'Performance Benchmarking Setup',
                'description': 'Track latency, throughput, vector quality across pipeline stages',
                'category': TaskCategory.INFRASTRUCTURE,
                'priority': Priority.MEDIUM,
                'hours': 10,
            },
            # LOW - Documentation & Future
            {
                'title': 'Update Architecture Documentation',
                'description': 'Document all design decisions, API contracts, and deployment procedures',
                'category': TaskCategory.DOCUMENTATION,
                'priority': Priority.LOW,
                'hours': 12,
            },
            {
                'title': 'Physics-Aware Prompt Engineering',
                'description': 'Refine semantic splitter prompts for CERN terminology and scientific concepts',
                'category': TaskCategory.FEATURE,
                'priority': Priority.LOW,
                'hours': 8,
            },
        ]
        
        for task_data in default_tasks:
            self.kanban.add_task(
                title=task_data['title'],
                description=task_data['description'],
                category=task_data['category'],
                priority=task_data['priority'],
                estimated_hours=task_data['hours'],
            )

    def generate_summary_report(self) -> str:
        """Generate human-readable summary report"""
        if not self.report:
            self.run_full_assessment()

        report = "\n" + "="*100 + "\n"
        report += "🎯 PROJECT STATUS AGENT - EXECUTIVE SUMMARY\n"
        report += "="*100 + "\n"

        # Health Status
        health = self.report['project_health']
        report += f"\n📊 PROJECT HEALTH: {health['status']}\n"
        report += f"   Health Score: {health['health_score']:.1f}/100\n\n"

        report += "✅ VERIFIED COMPONENTS:\n"
        for component in health['verified_components'][:10]:
            report += f"   {component}\n"
        if len(health['verified_components']) > 10:
            report += f"   ... and {len(health['verified_components'])-10} more\n"

        if health['critical_issues']:
            report += "\n🚨 CRITICAL ISSUES:\n"
            for issue in health['critical_issues']:
                report += f"   • {issue}\n"

        if health['warnings']:
            report += "\n⚠️  WARNINGS:\n"
            for warning in health['warnings']:
                report += f"   • {warning}\n"

        # Task Stats
        stats = self.report['kanban_stats']
        report += "\n📈 TASK STATISTICS:\n"
        report += f"   Total Tasks: {stats['total_tasks']}\n"
        report += f"   Total Estimated Hours: {stats['total_estimated_hours']:.0f}h\n\n"
        report += "   By Status:\n"
        for status, count in stats['by_status'].items():
            report += f"      {status}: {count}\n"

        # Resource Recommendations
        recs = self.report['resource_recommendations']
        report += f"\n👥 TEAM STRUCTURE: {len(recs.get('team', []))} Engineers\n"
        for engineer in recs.get('team', [])[:5]:
            report += f"   • {engineer['name']} ({engineer['level']})\n"

        report += "\n" + "="*100 + "\n"

        return report

    def generate_detailed_report(self) -> str:
        """Generate detailed technical report"""
        if not self.report:
            self.run_full_assessment()

        report = self.generate_summary_report()
        report += "\n\n" + self.kanban.get_kanban_view()

        # Recommendations
        recs = self.report['resource_recommendations']
        report += "\n\n" + "="*100 + "\n"
        report += "🎯 TASK ALLOCATION RECOMMENDATIONS\n"
        report += "="*100 + "\n"

        for rec in recs.get('recommendations', [])[:15]:
            report += f"\n{rec['task_id']}: {rec['task_title']}\n"
            report += f"  → Recommended: {rec['recommended_engineer']} ({rec['level']})\n"
            if rec['skills_match']:
                report += f"  → Matched Skills: {', '.join(rec['skills_match'])}\n"
            report += f"  → Current Load: {rec['current_load']}/{rec['capacity']} tasks\n"

        if len(recs.get('recommendations', [])) > 15:
            report += f"\n  ... and {len(recs['recommendations'])-15} more recommendations\n"

        report += "\n" + "="*100 + "\n"
        report += "🚀 NEXT STEPS:\n"
        report += "="*100 + "\n"
        report += """
1. 🔴 CRITICAL (Week 1-2):
   - Assign Senior Architect to async/await refactoring (12h)
   - Assign Backend Senior to LanceDB sync fix (8h)
   - Assign QA Engineer to identify all knowledge graph edge cases (6h)

2. 🟠 HIGH PRIORITY (Week 3-4):
   - Begin Docling integration (requires ML Specialist + Backend)
   - Start ColPali POC (requires ML Specialist, 20h)
   - Plan Next.js consolidation (requires Frontend Senior, 24h)

3. 🟡 MEDIUM (Week 5+):
   - Implement hybrid chunking strategy
   - Add comprehensive testing suite
   - Performance benchmarking

📋 RESOURCE ALLOCATION TIPS:
   - Pair Junior/Mid engineers with Seniors for faster onboarding
   - Run ParallelSprints: async refactoring + Docling integration + testing
   - Schedule bi-weekly sync with Staff Architect for design reviews
   - Use CI/CD for automated testing on all critical modules

⏱️ ESTIMATED TIMELINE:
   - Production Ready: 6-8 weeks with full team
   - Minimum Critical Path: 3-4 weeks with 5 engineers
"""
        return report


def main():
    """Main entry point"""
    import sys

    agent = ProjectStatusAgent()

    print("\n" + "="*100)
    print("🤖 PROJECT STATUS AGENT - INITIALIZING")
    print("="*100)

    # Run assessment
    agent.run_full_assessment()

    # Display reports
    if len(sys.argv) > 1 and sys.argv[1] == '--detailed':
        print(agent.generate_detailed_report())
    else:
        print(agent.generate_summary_report())
        print("\n💡 TIP: Run with --detailed flag for full kanban board and allocation recommendations")
        print("   python project_agent.py --detailed\n")


if __name__ == '__main__':
    main()
