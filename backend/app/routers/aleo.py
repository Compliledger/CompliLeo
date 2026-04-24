"""Aleo program registry router.

Exposes read-only metadata about the local Leo programs CompliLeo would
execute. No Aleo network calls happen here — this is a thin view over
:mod:`app.services.aleo_program_registry`.
"""
from typing import Dict, List

from fastapi import APIRouter, HTTPException

from app.services import aleo_program_registry

router = APIRouter(prefix="/api/aleo", tags=["aleo"])


@router.get("/programs", response_model=List[Dict[str, str]])
def list_programs() -> List[Dict[str, str]]:
    """Return metadata for every Aleo program registered with CompliLeo."""
    return aleo_program_registry.list_programs()


@router.get("/programs/{module}", response_model=Dict[str, str])
def get_program(module: str) -> Dict[str, str]:
    """Return metadata for a single Aleo program by logical module name.

    Returns ``404`` with a clear message when the module is unknown.
    """
    try:
        return aleo_program_registry.get_program(module)
    except aleo_program_registry.UnknownAleoModuleError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
