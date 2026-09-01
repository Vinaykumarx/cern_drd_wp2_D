"""
System Validator — Scans runtime for canonical architecture violations.

Runs at FastAPI startup to detect:
  - Direct lancedb.connect() calls outside LanceVectorStore
  - rag.store.table.* access patterns outside store wrapper
  - Standalone extraction scripts in execution path
  - Non-canonical imports in active code paths
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_IMPORTS = [
    "lancedb",
]

FORBIDDEN_CALL_PATTERNS = [
    ".connect(",
    "rag.store.table.",
    ".store.table.search",
    ".store.table.to_pandas",
    ".store.table.delete",
]

CANONICAL_ENTRY_POINTS = {
    "ingestion": "extraction.extract_with_docid",
    "retrieval": "core.rag_pipeline.RAGPipeline",
    "vector_store": "core.vector_store_lance.LanceVectorStore",
    "api": "backend.main",
}

STANDALONE_EXTRACTION_SCRIPTS = [
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


class SystemValidator:
    def __init__(self, root_path: Path = PROJECT_ROOT):
        self.root_path = root_path
        self.violations: List[Dict[str, Any]] = []
        self._executor = ThreadPoolExecutor(max_workers=4)

    def scan_forbidden_imports(self, filepath: Path) -> List[Dict[str, Any]]:
        """Scan a single Python file for forbidden import patterns."""
        violations = []
        try:
            with open(filepath, "r") as f:
                tree = ast.parse(f.read(), filename=str(filepath))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in FORBIDDEN_IMPORTS:
                            violations.append({
                                "file": str(filepath.relative_to(self.root_path)),
                                "line": node.lineno,
                                "pattern": f"import {alias.name}",
                                "severity": "CRITICAL",
                                "message": f"Direct '{alias.name}' import bypasses LanceVectorStore",
                            })
                elif isinstance(node, ast.ImportFrom):
                    if node.module in FORBIDDEN_IMPORTS:
                        violations.append({
                            "file": str(filepath.relative_to(self.root_path)),
                            "line": node.lineno,
                            "pattern": f"from {node.module} import ...",
                            "severity": "CRITICAL",
                            "message": f"Direct '{node.module}' import bypasses LanceVectorStore",
                        })
        except (SyntaxError, UnicodeDecodeError):
            pass
        return violations

    def scan_forbidden_calls(self, filepath: Path) -> List[Dict[str, Any]]:
        """Scan a single Python file for forbidden call patterns."""
        violations = []
        try:
            with open(filepath, "r") as f:
                content = f.read()

            for line_num, line in enumerate(content.splitlines(), 1):
                for pattern in FORBIDDEN_CALL_PATTERNS:
                    if pattern in line and not line.strip().startswith("#"):
                        violations.append({
                            "file": str(filepath.relative_to(self.root_path)),
                            "line": line_num,
                            "pattern": pattern,
                            "severity": "CRITICAL",
                            "message": f"Forbidden call pattern '{pattern}' bypasses canonical store",
                        })
        except (UnicodeDecodeError, OSError):
            pass
        return violations

    def scan_standalone_extraction(self) -> List[Dict[str, Any]]:
        """Check if standalone extraction scripts exist and flag them."""
        violations = []
        for script_rel in STANDALONE_EXTRACTION_SCRIPTS:
            script_path = self.root_path / script_rel
            if script_path.exists():
                violations.append({
                    "file": script_rel,
                    "line": 0,
                    "pattern": "standalone extraction script",
                    "severity": "HIGH",
                    "message": f"Standalone extraction script exists — use extract_with_docid.py instead",
                })
        return violations

    def scan_all(self) -> List[Dict[str, Any]]:
        """Run all scans and return aggregated violations."""
        self.violations = []

        python_files = list(self.root_path.rglob("*.py"))
        python_files = [
            p for p in python_files
            if ".venv" not in str(p)
            and "node_modules" not in str(p)
            and "__pycache__" not in str(p)
        ]

        for filepath in python_files:
            self.violations.extend(self.scan_forbidden_imports(filepath))
            self.violations.extend(self.scan_forbidden_calls(filepath))

        self.violations.extend(self.scan_standalone_extraction())

        return self.violations

    def report(self) -> Dict[str, Any]:
        """Generate a validation report."""
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

    def print_report(self):
        """Print a human-readable report."""
        report = self.report()
        print("=" * 60)
        print("SYSTEM VALIDATOR REPORT")
        print("=" * 60)
        print(f"Status: {report['status']}")
        print(f"Total violations: {report['total_violations']}")
        print(f"By severity: {report['by_severity']}")
        print()
        if report["violations"]:
            print("Violations:")
            for v in report["violations"]:
                print(f"  [{v['severity']}] {v['file']}:{v['line']} — {v['message']}")
        print()
        print("Canonical entry points:")
        for role, path in CANONICAL_ENTRY_POINTS.items():
            print(f"  {role}: {path}")
        print("=" * 60)


def run_startup_validation() -> Dict[str, Any]:
    """Run validation at FastAPI startup. Returns the report."""
    validator = SystemValidator()
    validator.scan_all()
    report = validator.report()
    if report["total_violations"] > 0:
        print(f"[SystemValidator] WARNING: {report['total_violations']} canonical architecture violations detected")
        for v in report["violations"][:10]:
            print(f"  [{v['severity']}] {v['file']}:{v['line']}")
    else:
        print("[SystemValidator] All clear — canonical architecture enforced")
    return report
