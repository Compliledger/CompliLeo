"""SolvencyProof service: validates reserves >= liabilities."""
from __future__ import annotations

from typing import List, Tuple

from app.models import SolvencyProofRequest


def evaluate(req: SolvencyProofRequest) -> Tuple[bool, List[str]]:
    """Return (solvent, reason_codes).

    solvent is True only when reserves >= liabilities.
    """
    reason_codes: List[str] = []
    solvent = req.reserves >= req.liabilities
    if solvent:
        reason_codes.append("RESERVES_SUFFICIENT")
    else:
        reason_codes.append("RESERVES_INSUFFICIENT")
    return solvent, reason_codes
