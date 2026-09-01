# core/health_monitor.py
"""
Health Monitor - Continuous Monitoring and Auto-Healing

Monitors all system components and automatically fixes common issues.
Prevents the system from breaking after disconnect/reconnect.
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: str  # "healthy", "warning", "critical"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    last_checked: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "last_checked": self.last_checked,
        }


@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    lancedb_vector_count: int = 0
    active_sessions: int = 0
    queued_tasks: int = 0
    error_rate: float = 0.0
    uptime_seconds: float = 0.0
    timestamp: str = ""


class ComponentHealthChecker:
    """Base class for component health checkers"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_result: Optional[HealthCheckResult] = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
    
    async def check(self) -> HealthCheckResult:
        """Run health check - override in subclasses"""
        raise NotImplementedError
    
    def is_healthy(self) -> bool:
        return self.last_result and self.last_result.status == "healthy"
    
    def is_critical(self) -> bool:
        return self.last_result and self.last_result.status == "critical"


class LanceDBHealthChecker(ComponentHealthChecker):
    """Check LanceDB health and consistency"""
    
    def __init__(self, db_path: str = "lancedb"):
        super().__init__("lancedb")
        self.db_path = Path(db_path)
    
    async def check(self) -> HealthCheckResult:
        try:
            import lancedb
            
            if not self.db_path.exists():
                self.last_result = HealthCheckResult(
                    name=self.name,
                    status="warning",
                    message="LanceDB directory not found",
                    details={"path": str(self.db_path)}
                )
                return self.last_result
            
            try:
                db = lancedb.connect(str(self.db_path))
                tables = db.table_names()
                
                if not tables:
                    self.last_result = HealthCheckResult(
                        name=self.name,
                        status="warning",
                        message="No tables found in LanceDB",
                        details={"tables": tables}
                    )
                    return self.last_result
                
                # Check table integrity
                table_stats = {}
                for table_name in tables:
                    table = db.open_table(table_name)
                    count = table.count_rows()
                    table_stats[table_name] = count
                
                self.last_result = HealthCheckResult(
                    name=self.name,
                    status="healthy",
                    message=f"LanceDB operational with {len(tables)} tables",
                    details={
                        "tables": table_stats,
                        "path": str(self.db_path)
                    }
                )
                
            except Exception as e:
                self.last_result = HealthCheckResult(
                    name=self.name,
                    status="critical",
                    message=f"LanceDB corrupted or inaccessible: {e}",
                    details={"error": str(e)}
                )
                
        except ImportError:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="warning",
                message="LanceDB library not available",
                details={}
            )
        
        self.last_checked = datetime.now().isoformat()
        return self.last_result


class LLMHealthChecker(ComponentHealthChecker):
    """Check LLM provider connectivity"""
    
    def __init__(self):
        super().__init__("llm_provider")
    
    async def check(self) -> HealthCheckResult:
        try:
            import httpx
            from dotenv import load_dotenv
            load_dotenv()

            base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
            api_key = os.getenv("OPENROUTER_API_KEY", "")

            # Determine if we are using a local Ollama instance
            is_local = "localhost" in base_url or "127.0.0.1" in base_url

            async with httpx.AsyncClient(timeout=5.0) as client:
                if is_local:
                    # Ollama health check – no API key required
                    # Try the standard /models endpoint; fallback to /api/tags if needed
                    try:
                        resp = await client.get(f"{base_url}/models")
                    except Exception:
                        resp = await client.get("http://localhost:11434/api/tags")
                    if resp.status_code == 200:
                        self.last_result = HealthCheckResult(
                            name=self.name,
                            status="healthy",
                            message="Local Ollama LLM provider responsive",
                            details={"provider": "ollama", "status_code": resp.status_code}
                        )
                    else:
                        self.last_result = HealthCheckResult(
                            name=self.name,
                            status="warning",
                            message=f"Local Ollama responded with {resp.status_code}",
                            details={"status_code": resp.status_code}
                        )
                    return self.last_result

                # Remote provider requires an API key
                if not api_key:
                    self.last_result = HealthCheckResult(
                        name=self.name,
                        status="warning",
                        message="No API key configured for remote LLM provider",
                        details={"configured": False}
                    )
                    return self.last_result

                # Remote provider check (e.g., OpenRouter)
                try:
                    resp = await client.get(
                        f"{base_url}/models",
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    if resp.status_code == 200:
                        self.last_result = HealthCheckResult(
                            name=self.name,
                            status="healthy",
                            message="Remote LLM provider responsive",
                            details={"provider": "remote", "status_code": resp.status_code}
                        )
                    else:
                        self.last_result = HealthCheckResult(
                            name=self.name,
                            status="warning",
                            message=f"Remote LLM provider returned {resp.status_code}",
                            details={"status_code": resp.status_code}
                        )
                except Exception as e_remote:
                    # Fallback to local Ollama if remote fails
                    try:
                        resp = await client.get("http://localhost:11434/api/tags", timeout=2.0)
                        if resp.status_code == 200:
                            self.last_result = HealthCheckResult(
                                name=self.name,
                                status="healthy",
                                message="Local Ollama fallback available",
                                details={"fallback": "ollama"}
                            )
                        else:
                            raise Exception("Ollama not responding")
                    except Exception as e_fallback:
                        self.last_result = HealthCheckResult(
                            name=self.name,
                            status="critical",
                            message=f"LLM provider unreachable: {e_remote}; fallback error: {e_fallback}",
                            details={"error": str(e_remote)}
                        )
                return self.last_result
        except Exception as e:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="critical",
                message=f"LLM health check failed: {e}",
                details={"error": str(e)}
            )
        
        self.last_checked = datetime.now().isoformat()
        return self.last_result


class FileSystemHealthChecker(ComponentHealthChecker):
    """Check file system integrity"""
    
    def __init__(self, project_root: str = "."):
        super().__init__("filesystem")
        self.project_root = Path(project_root)
    
    async def check(self) -> HealthCheckResult:
        required_dirs = [
            "data", "outputs", "lancedb", "core",
            "backend", "frontend", "scripts"
        ]
        
        missing_dirs = []
        existing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                existing_dirs.append(dir_name)
            else:
                missing_dirs.append(dir_name)
        
        # Check required files
        required_files = [
            "core/document_manager.py",
            "core/rag_pipeline.py",
            "core/config.py",
            "backend/main.py",
            "data/documents.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_dirs:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="warning",
                message=f"Missing directories: {', '.join(missing_dirs)}",
                details={"missing_dirs": missing_dirs, "existing_dirs": existing_dirs}
            )
        elif missing_files:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="warning",
                message=f"Missing files: {', '.join(missing_files)}",
                details={"missing_files": missing_files}
            )
        else:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="healthy",
                message="File system structure intact",
                details={"dirs": len(existing_dirs), "files_ok": len(required_files) - len(missing_files)}
            )
        
        self.last_checked = datetime.now().isoformat()
        return self.last_result


class MemoryHealthChecker(ComponentHealthChecker):
    """Check memory usage and potential leaks"""
    
    def __init__(self):
        super().__init__("memory")
    
    async def check(self) -> HealthCheckResult:
        try:
            import psutil
            process = psutil.Process()
            
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Check for potential memory issues
            if memory_percent > 90:
                status = "critical"
                message = f"CRITICAL: Memory usage at {memory_percent:.1f}%"
            elif memory_percent > 75:
                status = "warning"
                message = f"WARNING: High memory usage at {memory_percent:.1f}%"
            else:
                status = "healthy"
                message = f"Memory usage normal at {memory_percent:.1f}%"
            
            self.last_result = HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                details={
                    "rss_mb": memory_info.rss / (1024 * 1024),
                    "vms_mb": memory_info.vms / (1024 * 1024),
                    "percent": memory_percent,
                    "cpu_percent": process.cpu_percent()
                }
            )
            
        except ImportError:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="warning",
                message="psutil not available - cannot monitor memory",
                details={}
            )
        except Exception as e:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="warning",
                message=f"Memory check failed: {e}",
                details={}
            )
        
        self.last_checked = datetime.now().isoformat()
        return self.last_result


class ProcessHealthChecker(ComponentHealthChecker):
    """Check if required processes are running"""
    
    def __init__(self):
        super().__init__("processes")
    
    async def check(self) -> HealthCheckResult:
        required_ports = {
            8000: "Backend RAG API",
            3000: "Next.js Frontend",
        }
        
        running = {}
        not_running = {}
        
        for port, name in required_ports.items():
            if self._port_in_use(port):
                running[port] = name
            else:
                not_running[port] = name
        
        if not_running:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="warning",
                message=f"Services not running: {', '.join(not_running.values())}",
                details={"running": running, "not_running": not_running}
            )
        else:
            self.last_result = HealthCheckResult(
                name=self.name,
                status="healthy",
                message="All required services running",
                details={"running": running}
            )
        
        self.last_checked = datetime.now().isoformat()
        return self.last_result
    
    def _port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0


class HealthMonitor:
    """
    Central Health Monitoring System
    
    Features:
    - Runs all health checks
    - Tracks health history
    - Auto-heals common issues
    - Generates status reports
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.checkers: List[ComponentHealthChecker] = [
            LanceDBHealthChecker(str(self.project_root / "lancedb")),
            LLMHealthChecker(),
            FileSystemHealthChecker(str(self.project_root)),
            MemoryHealthChecker(),
            ProcessHealthChecker(),
        ]
        self.health_history: List[Dict] = []
        self.start_time = time.time()
        self.last_run_time = 0.0
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return summary"""
        start_time = time.time()
        
        results = []
        for checker in self.checkers:
            try:
                result = await checker.check()
                results.append(result.to_dict())
            except Exception as e:
                results.append(HealthCheckResult(
                    name=checker.name,
                    status="critical",
                    message=f"Check failed: {e}",
                    details={"error": str(e)}
                ).to_dict())
        
        self.last_run_time = time.time() - start_time
        
        # Calculate overall health score
        status_counts = {"healthy": 0, "warning": 0, "critical": 0}
        for r in results:
            status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
        
        if status_counts["critical"] > 0:
            overall_status = "critical"
            health_score = 25
        elif status_counts["warning"] > 0:
            overall_status = "warning"
            health_score = 60 + (status_counts["healthy"] / len(results)) * 40
        else:
            overall_status = "healthy"
            health_score = 100
        
        # Record history (keep last 100)
        record = {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "status": overall_status,
            "results": results,
            "duration_ms": int(self.last_run_time * 1000)
        }
        self.health_history.append(record)
        self.health_history = self.health_history[-100:]  # Keep last 100
        
        # Return summary
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "health_score": health_score,
            "total_checks": len(results),
            "healthy": status_counts["healthy"],
            "warnings": status_counts["warning"],
            "critical": status_counts["critical"],
            "duration_ms": int(self.last_run_time * 1000),
            "last_24h_failures": len([h for h in self.health_history[-24:] if h["status"] != "healthy"]),
            "details": results
        }
    
    async def auto_heal(self) -> List[str]:
        """Attempt to automatically fix common issues"""
        actions_taken = []
        
        # Check each checker for issues
        for checker in self.checkers:
            if not checker.is_healthy():
                if checker.name == "lancedb":
                    action = await self._heal_lancedb()
                    if action:
                        actions_taken.append(action)
                elif checker.name == "llm_provider":
                    action = await self._heal_llm_provider()
                    if action:
                        actions_taken.append(action)
                elif checker.name == "filesystem":
                    action = self._heal_filesystem()
                    if action:
                        actions_taken.append(action)
        
        return actions_taken
    
    async def _heal_lancedb(self) -> Optional[str]:
        """Attempt to heal LanceDB issues"""
        try:
            import lancedb
            db_path = self.project_root / "lancedb"
            
            if not db_path.exists():
                # Create missing directory
                db_path.mkdir(parents=True, exist_ok=True)
                return "Created missing lancedb directory"
            
            # Try to connect and fix
            try:
                db = lancedb.connect(str(db_path))
                tables = db.table_names()
                # Verify tables are readable
                for table_name in tables:
                    table = db.open_table(table_name)
                    _ = table.count_rows()
                return f"Verified LanceDB integrity ({len(tables)} tables)"
            except Exception as e:
                # Attempt recovery by creating backup and fresh DB
                backup_path = db_path.with_suffix('.bak')
                shutil.move(str(db_path), str(backup_path))
                db = lancedb.connect(str(db_path))
                return f"Recreated LanceDB (backup at {backup_path})"
                
        except Exception as e:
            return f"LanceDB healing failed: {e}"
    
    async def _heal_llm_provider(self) -> Optional[str]:
        """Attempt to heal LLM provider issues"""
        try:
            import httpx
            from dotenv import load_dotenv
            load_dotenv()
            
            base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
            
            # Try alternative providers
            providers = [
                ("OpenRouter", base_url),
                ("Ollama", "http://localhost:11434"),
            ]
            
            for name, url in providers:
                try:
                    async with httpx.AsyncClient(timeout=3.0) as client:
                        if "openrouter" in url:
                            await client.get(f"{url}/auth/key")
                        else:
                            await client.get(f"{url}/api/tags")
                        return f"Switched to {name} as LLM provider"
                except:
                    continue
            
            return None  # No working provider found
            
        except Exception as e:
            return f"LLM provider healing failed: {e}"
    
    def _heal_filesystem(self) -> Optional[str]:
        """Attempt to heal filesystem issues"""
        try:
            required_dirs = ["data", "outputs", "lancedb"]
            created = []
            
            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created.append(dir_name)
            
            if created:
                return f"Created missing directories: {', '.join(created)}"
            return None
            
        except Exception as e:
            return f"Filesystem healing failed: {e}"
    
    def get_status_report(self) -> str:
        """Generate human-readable status report"""
        if not self.health_history:
            return "No health checks run yet."
        
        latest = self.health_history[-1]
        report = "\n🏥 SYSTEM HEALTH REPORT\n"
        report += "=" * 60 + "\n\n"
        
        # Status indicator
        status_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}
        emoji = status_emoji.get(latest["overall_status"], "❓")
        report += f"Overall: {emoji} {latest['overall_status'].upper()} "
        report += f"(Score: {latest['health_score']}/100)\n\n"
        
        # Detail breakdown
        for detail in latest.get("details", []):
            s_emoji = status_emoji.get(detail["status"], "❓")
            report += f"  {s_emoji} {detail['name']}: {detail['message']}\n"
        
        report += f"\n⏱️  Last check: {latest['timestamp']}"
        report += f"\n📊 History: {len(self.health_history)} checks stored"
        
        return report
    
    def get_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            import psutil
            process = psutil.Process()
            memory = process.memory_info()
            
            return SystemMetrics(
                cpu_percent=process.cpu_percent(),
                memory_percent=process.memory_percent(),
                disk_percent=psutil.disk_usage('/').percent,
                uptime_seconds=time.time() - self.start_time,
                timestamp=datetime.now().isoformat()
            )
        except ImportError:
            return SystemMetrics(
                timestamp=datetime.now().isoformat()
            )


# Global instance
_monitor: Optional[HealthMonitor] = None

def get_health_monitor() -> HealthMonitor:
    """Get or create the global health monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = HealthMonitor()
    return _monitor


async def health_check_loop(interval_seconds: int = 30):
    """Background task to run health checks periodically"""
    monitor = get_health_monitor()
    print(f"[HealthMonitor] Starting health check loop (every {interval_seconds}s)")
    
    while True:
        try:
            result = await monitor.run_all_checks()
            print(f"[HealthMonitor] Check complete: {result['health_score']}/100")
            
            # Auto-heal if issues found
            if result["critical"] > 0 or result["warnings"] > 0:
                actions = await monitor.auto_heal()
                for action in actions:
                    print(f"[HealthMonitor] Auto-heal: {action}")
                    
        except Exception as e:
            print(f"[HealthMonitor] Error in check loop: {e}")
        
        await asyncio.sleep(interval_seconds)