"""Aleo program registry — single source of truth for CompliLeo's
local Leo programs.

Each entry maps a logical CompliLeo *module* (``tokenproof``,
``solvencyproof``, ``compliguard``) to the metadata describing the
on-disk Leo program that implements it:

* ``module`` — logical module name used throughout the backend.
* ``program_name`` — the Aleo program identifier (matches the ``program``
  field in the program's ``program.json`` and the ``program <name>``
  declaration in its ``main.leo``).
* ``transition_name`` — the Leo ``transition`` that the backend would
  invoke for this module.
* ``local_path`` — repo-relative path to the program's ``main.leo``
  source file. Stored as written so the registry is human-readable;
  :func:`resolve_local_path` returns the absolute path.
* ``description`` — short human-readable summary of what the program
  proves.

This registry is **the** place that knows about Aleo programs. The Aleo
adapter, the proof-bundle service, and the ``/api/aleo/programs``
endpoints all read from here so program names and transition names
never need to be hardcoded in more than one place.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

#: Repo root (``backend/app/services/`` -> ``backend/app/`` -> ``backend/``
#: -> repo root).
_REPO_ROOT = Path(__file__).resolve().parents[3]


class UnknownAleoModuleError(KeyError):
    """Raised when a caller asks the registry for a module it doesn't know.

    Subclasses :class:`KeyError` so existing ``KeyError``-style callers
    keep working, while routers / services can catch the more specific
    type to translate it into a clean HTTP error.
    """


#: Registry of all Aleo programs known to CompliLeo. Keyed by logical
#: CompliLeo module name. Values are plain dicts so they serialize
#: straight to JSON for the ``/api/aleo/programs`` endpoints.
ALEO_PROGRAMS: Dict[str, Dict[str, str]] = {
    "tokenproof": {
        "module": "tokenproof",
        "program_name": "tokenproofx1.aleo",
        "transition_name": "verify_token",
        "local_path": "../../aleo/tokenproofx1/src/main.leo",
        "description": "verifies asset issuance and eligibility conditions",
    },
    "solvencyproof": {
        "module": "solvencyproof",
        "program_name": "solvencypx1.aleo",
        "transition_name": "prove_solvency",
        "local_path": "../../aleo/solvencypx1/src/main.leo",
        "description": "verifies reserves are greater than or equal to liabilities",
    },
    "compliguard": {
        "module": "compliguard",
        "program_name": "compliguardx1.aleo",
        "transition_name": "prove_health",
        "local_path": "../../aleo/compliguardx1/src/main.leo",
        "description": "verifies system health and operational integrity conditions",
    },
}


def list_programs() -> List[Dict[str, str]]:
    """Return metadata for every registered Aleo program.

    The returned list is a fresh copy of the registry values so callers
    can mutate it without affecting the registry.
    """
    return [dict(entry) for entry in ALEO_PROGRAMS.values()]


def get_program(module: str) -> Dict[str, str]:
    """Return metadata for a single module.

    Raises :class:`UnknownAleoModuleError` (a ``KeyError`` subclass) with
    a clean message when ``module`` is not registered.
    """
    try:
        entry = ALEO_PROGRAMS[module]
    except KeyError:
        raise UnknownAleoModuleError(
            f"Unknown Aleo module '{module}'. "
            f"Known modules: {sorted(ALEO_PROGRAMS)}"
        ) from None
    return dict(entry)


def resolve_local_path(module: str) -> Path:
    """Return the absolute :class:`~pathlib.Path` of a module's ``main.leo``.

    Resolves the registry's ``local_path`` against the repo root so the
    same path works regardless of the caller's current working
    directory.
    """
    entry = get_program(module)
    raw = entry["local_path"]
    # ``local_path`` values are written with ``../../`` prefixes to make
    # them human-readable in the registry. We strip the leading parent
    # segments and anchor the remainder at the repo root so the resolved
    # path is stable regardless of where this code is executed from.
    parts = Path(raw).parts
    rel_parts = [p for p in parts if p != ".."]
    return (_REPO_ROOT / Path(*rel_parts)).resolve()
