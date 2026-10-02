"""Orchestrator OS runtime (ADR-0008: Python >= 3.12, stdlib-first).

Domain-neutral kernel/runtime code only (invariant I-1). Domain behaviour lives in domain packages.
"""
import sys

if sys.version_info < (3, 12):  # ADR-0008
    raise ImportError(
        f"Orchestrator OS requires Python >= 3.12 (found {sys.version.split()[0]}). "
        "Create the project environment with a supported interpreter: python -m venv .venv"
    )

__version__ = "0.1.0"
