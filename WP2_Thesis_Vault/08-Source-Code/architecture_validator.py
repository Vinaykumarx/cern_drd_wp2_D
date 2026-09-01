"""
Architecture Validator — Runtime enforcement of canonical system architecture.

Scans all Python files and runtime state for:
  - Forbidden imports (e.g. direct lancedb import)
  - Direct lancedb.connect() calls outside LanceVectorStore
  - rag.store.table.* access patterns
  - Deprecated file execution (standalone extraction scripts)
  - Scripts running without bootstrap

Returns structured violation reports.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_IMPORTS = [
    "lancedb",
]

FORBIDDEN_CALL_PATTERNS = [
    "lancedb.connect(",
    "rag.store.table.",
    ".store.table.search",
    ".store.table.to_pandas",
    ".store.table.delete",
    ".store.table.add",
]

ALLOWED_LANCEDB_MODULES = [
    "core.vector_store_lance",
    "core.health_monitor",
]

EXEMPT_PATTERN_FILES = [
    "core/system_validator.py",
    "core/canonical_gate.py",
    "core/architecture_validator.py",
]

EXEMPT_PATTERN_DIRS = [
    "scripts/",
]

CANONICAL_ENTRY_POINTS = {
    "ingestion": "extraction.extract_with_docid",
    "retrieval": "core.rag_pipeline.RAGPipeline",
    "vector_store": "core.vector_store_lance.LanceVectorStore",
    "api": "backend.main",
}

DEPRECATED_EXTRACTION_SCRIPTS = [
    "extraction/extract_text.py",
    "extraction/extract_images.py",
    "extraction/extract_tables.py",
    "extraction/extract_graphs.py",
    "extraction/caption_images.py",
    "extraction/build_metadata.py",
    "extraction/pipeline.py",
    "extraction/extract_groq_vision.py",
    "extraction/hybrid_extractor.py",
]

SCRIPTS_REQUIRING_BOOTSTRAP = [
    "project_cli.py",
    "master_control.py",
    "project_dashboard.py",
    "reingest_all.py",
    "manual_ingest.py",
    "ingest_specific_doc.py",
    "project_agent.py",
    "project_manager.py",
    "run_implementation_plan.py",
    "validate_startup.py",
    "health_check.py",
]


class ArchitectureValidator:
    def __init__(self, root_path: Path = PROJECT_ROOT):
        self.root_path = root_path
        self.violations: List[Dict[str, Any]] = []

    def scan_forbidden_imports(self, filepath: Path) -> List[Dict[str, Any]]:
        violations = []
        rel_path = str(filepath.relative_to(self.root_path))
        for exempt_dir in EXEMPT_PATTERN_DIRS:
            if rel_path.startswith(exempt_dir):
                return violations
        try:
            with open(filepath, "r") as f:
                tree = ast.parse(f.read(), filename=str(filepath))

            file_module = self._module_from_path(filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in FORBIDDEN_IMPORTS:
                            if not self._is_allowed_module(file_module):
                                violations.append(self._violation(
                                    filepath, node.lineno,
                                    f"import {alias.name}",
                                    "CRITICAL",
                                    f"Direct '{alias.name}' import bypasses LanceVectorStore"
                                ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module in FORBIDDEN_IMPORTS:
                        if not self._is_allowed_module(file_module):
                            violations.append(self._violation(
                                filepath, node.lineno,
                                f"from {node.module} import ...",
                                "CRITICAL",
                                f"Direct '{node.module}' import bypasses LanceVectorStore"
                            ))
        except (SyntaxError, UnicodeDecodeError, OSError):
            pass
        return violations

    def scan_forbidden_calls(self, filepath: Path) -> List[Dict[str, Any]]:
        violations = []
        rel_path = str(filepath.relative_to(self.root_path))
        if rel_path in EXEMPT_PATTERN_FILES:
            return violations
        for exempt_dir in EXEMPT_PATTERN_DIRS:
            if rel_path.startswith(exempt_dir):
                return violations
        try:
            with open(filepath, "r") as f:
                content = f.read()

            file_module = self._module_from_path(filepath)
            for line_num, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                for pattern in FORBIDDEN_CALL_PATTERNS:
                    if pattern in line:
                        if not self._is_allowed_module(file_module):
                            violations.append(self._violation(
                                filepath, line_num,
                                pattern,
                                "CRITICAL",
                                f"Forbidden call pattern '{pattern}' bypasses canonical store"
                            ))
        except (UnicodeDecodeError, OSError):
            pass
        return violations

    def scan_deprecated_files(self) -> List[Dict[str, Any]]:
        violations = []
        for script_rel in DEPRECATED_EXTRACTION_SCRIPTS:
            script_path = self.root_path / script_rel
            if script_path.exists():
                violations.append(self._violation(
                    script_path, 0,
                    "deprecated extraction script",
                    "HIGH",
                    f"Running '{script_rel}' — use extraction/extract_with_docid.py instead"
                ))
        return violations

    def scan_scripts_without_bootstrap(self) -> List[Dict[str, Any]]:
        violations = []
        for script_rel in SCRIPTS_REQUIRING_BOOTSTRAP:
            script_path = self.root_path / script_rel
            if not script_path.exists():
                continue
            try:
                content = script_path.read_text()
                if "from core.bootstrap import" not in content and "import core.bootstrap" not in content:
                    violations.append(self._violation(
                        script_path, 0,
                        "missing bootstrap import",
                        "HIGH",
                        f"'{script_rel}' must import bootstrop at top of file: from core.bootstrap import require_bootstrap"
                    ))
            except (OSError, UnicodeDecodeError):
                pass
        return violations

    def scan_all(self) -> List[Dict[str, Any]]:
        self.violations = []
        python_files = list(self.root_path.rglob("*.py"))
        python_files = [
            p for p in python_files
            if ".venv" not in str(p)
            and "venv/" not in str(p)
            and "node_modules" not in str(p)
            and "__pycache__" not in str(p)
        ]

        for filepath in python_files:
            self.violations.extend(self.scan_forbidden_imports(filepath))
            self.violations.extend(self.scan_forbidden_calls(filepath))

        self.violations.extend(self.scan_deprecated_files())
        self.violations.extend(self.scan_scripts_without_bootstrap())

        return self.violations

    def report(self) -> Dict[str, Any]:
        total = len(self.violations)
        by_severity: Dict[str, int] = {}
        for v in self.violations:
            sev = v.get("severity", "UNKNOWN")
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "total_violations": total,
            "by_severity": by_severity,
            "violations": self.violations,
            "status": "FAIL" if total > 0 else "PASS",
            "canonical_entry_points": CANONICAL_ENTRY_POINTS,
        }

    def assert_clean(self):
        report = self.report()
        if report["status"] == "FAIL":
            print("\n".join(
                f"  [{v['severity']}] {v['file']}:{v['line']} — {v['message']}"
                for v in report["violations"]
            ))
            raise SystemExit(
                f"ARCHITECTURE VIOLATION: {report['total_violations']} violations found. "
                "Fix violations before running the system."
            )

    def _module_from_path(self, filepath: Path) -> str:
        rel = filepath.relative_to(self.root_path)
        parts = list(rel.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].replace(".py", "")
        return ".".join(parts)

    def _is_allowed_module(self, module_name: str) -> bool:
        for allowed in ALLOWED_LANCEDB_MODULES:
            if module_name == allowed or module_name.startswith(allowed + "."):
                return True
        return False

    def _violation(self, filepath: Path, line: int, pattern: str, severity: str, message: str) -> Dict[str, Any]:
        return {
            "file": str(filepath.relative_to(self.root_path)),
            "line": line,
            "pattern": pattern,
            "severity": severity,
            "message": message,
        }


def run_architecture_validation(exit_on_fail: bool = False) -> Dict[str, Any]:
    validator = ArchitectureValidator()
    validator.scan_all()
    report = validator.report()
    if report["total_violations"] > 0:
        print(f"[ArchitectureValidator] FAIL: {report['total_violations']} violations detected")
        for v in report["violations"][:15]:
            print(f"  [{v['severity']}] {v['file']}:{v['line']} — {v['message']}")
        if exit_on_fail:
            validator.assert_clean()
    else:
        print("[ArchitectureValidator] PASS — All canonical architecture rules enforced")
    return report
